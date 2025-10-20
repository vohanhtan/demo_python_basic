"""
-------------------
Service lớp giữa cho dự báo:
- Đọc CSV từ notebooks/data qua data_service
- Tính chỉ báo (SMA, RSI)
- Dự báo bằng Linear Regression (mặc định) hoặc Chronos-T5 (nếu chọn và có sẵn)
- Trả về kết quả theo schema chuẩn + kèm min/max mỗi ngày (forecast_bounds)
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from data_service import get_stock_data
from indicators import add_indicators, get_latest_indicators
from predictor import forecast_price_regression
from utils import get_current_datetime_iso, is_sideways_trend

# ---- Optional Chronos (Hugging Face) support (fallback nếu thiếu) ----
_CHRONOS_AVAILABLE = False
try:
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM  # type: ignore
    _CHRONOS_AVAILABLE = True
except Exception:
    _CHRONOS_AVAILABLE = False


def _forecast_with_chronos(close: pd.Series, horizon: int, model_id: str = "amazon/chronos-t5-tiny") -> List[float]:
    """
    Dự báo với Chronos-T5 (nếu transformers khả dụng). Đầu vào là chuỗi Close đã scale nhẹ.
    Trả về list float độ dài = horizon. Nếu có lỗi -> raise và caller sẽ fallback.
    """
    if not _CHRONOS_AVAILABLE:
        raise ImportError("transformers chưa được cài — không thể chạy Chronos")

    # Chuẩn hoá dữ liệu thành chuỗi space-separated theo chuẩn Chronos
    # (Ở demo, ta dùng normalized chuỗi; mô hình tiny có thể cho kết quả thô nhưng đủ demo)
    values = close.astype(float).tolist()
    series_text = " ".join([f"{v:.4f}" for v in values])

    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_id)

    prompt = f"forecast: {series_text} horizon={horizon}"
    inputs = tok(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=64)
    text = tok.decode(outputs[0], skip_special_tokens=True)

    # Kỳ vọng mô hình trả về dãy số dạng "y1 y2 ... yH" (tuỳ checkpoint).
    # Đơn giản tách số; nếu không parse được -> raise để fallback.
    parts = [p for p in text.strip().replace(",", " ").split() if _is_number(p)]
    preds = [float(p) for p in parts[:horizon]]
    if len(preds) != horizon:
        raise RuntimeError(f"Chronos output không đủ {horizon} điểm: '{text}'")
    return preds


def _is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except Exception:
        return False


def _compute_bounds_from_volatility(
    preds: List[float],
    close: pd.Series,
    lookback: int = 20,
    k_sigma: float = 1.0
) -> List[Dict[str, float]]:
    """
    Tính min/max mỗi ngày dựa trên độ biến động gần (absolute return) 20 ngày:
    - sigma = std(|pct_change|) ở lookback
    - min = pred * (1 - k*sigma), max = pred * (1 + k*sigma)
    """
    if len(close) < 2:
        sigma = 0.02  # fallback 2%
    else:
        ret = close.pct_change().abs().dropna()
        window = ret.tail(lookback)
        sigma = float(window.std()) if len(window) >= 2 else float(ret.std() or 0.02)
        if np.isnan(sigma) or sigma == 0:
            sigma = 0.02

    bounds = []
    for p in preds:
        lo = max(0.0, p * (1.0 - k_sigma * sigma))
        hi = p * (1.0 + k_sigma * sigma)
        bounds.append({"min": round(lo, 2), "max": round(hi, 2)})
    return bounds


def _derive_trend_and_signal(current_price: float, forecast_price: float, rsi: Optional[float], sma7: float, sma30: float) -> Tuple[str, str, str]:
    """
    Suy luận xu hướng + tín hiệu cơ bản để dùng khi chạy Chronos (không dùng predictor.py).
    """
    if is_sideways_trend(current_price, forecast_price, threshold=0.02):
        trend = "Sideways"
    else:
        trend = "Uptrend" if forecast_price > current_price else "Downtrend"

    # Lấy RSI an toàn
    rsi = 50.0 if (rsi is None or np.isnan(rsi)) else float(rsi)

    # Logic tín hiệu tương tự predictor.py (rút gọn)
    if trend == "Uptrend":
        if rsi < 70 and sma7 >= sma30:
            signal = "BUY"
            reason = "Xu hướng tăng, RSI chưa quá mua, SMA7 ≥ SMA30"
        else:
            signal = "HOLD"
            reason = "Xu hướng tăng nhưng điều kiện chỉ báo chưa đồng thuận"
    elif trend == "Downtrend":
        if rsi > 30 and sma7 <= sma30:
            signal = "SELL"
            reason = "Xu hướng giảm, RSI chưa quá bán, SMA7 ≤ SMA30"
        else:
            signal = "HOLD"
            reason = "Xu hướng giảm nhưng điều kiện chỉ báo chưa đồng thuận"
    else:
        if rsi < 30:
            signal = "BUY"
            reason = "Sideways, RSI quá bán"
        elif rsi > 70:
            signal = "SELL"
            reason = "Sideways, RSI quá mua"
        else:
            signal = "HOLD"
            reason = "Sideways, RSI trung tính"
    return trend, signal, reason


def get_forecast(
    symbol: str,
    start_date: str,
    end_date: str,
    horizon_days: int = 5,
    model: str = "linear",             # "linear" | "chronos" | "auto"
    chronos_model_id: str = "amazon/chronos-t5-tiny"
) -> Dict:
    """
    Hàm dự báo chính cho dịch vụ:
    - Đọc data -> add indicators
    - Tuỳ chọn mô hình:
        + linear: dùng forecast_price_regression (scikit-learn)
        + chronos: dùng Chronos-T5 nếu có, nếu lỗi -> fallback linear
        + auto: chronos nếu khả dụng, ngược lại linear
    - Thêm forecast_bounds (min/max) theo độ biến động gần
    - Trả JSON đầy đủ để đưa thẳng vào app hoặc logger

    Returns:
        dict:
          symbol, date_range, latest_price, technical_indicators,
          trend, forecast_horizon_days, forecast_next_days, signal, reason,
          forecast_bounds, generated_at
    """
    # 1) Load & indicators
    df = get_stock_data(symbol, start_date, end_date)
    df = add_indicators(df)
    latest = get_latest_indicators(df)
    last_close = float(df["Close"].iloc[-1])

    # 2) chọn mô hình
    chosen = model.lower()
    if chosen not in {"linear", "chronos", "auto"}:
        chosen = "linear"

    preds: List[float] = []
    trend = "Sideways"
    signal = "HOLD"
    reason = ""

    if chosen in {"chronos", "auto"}:
        tried_chronos = False
        if chosen == "chronos" or (chosen == "auto" and _CHRONOS_AVAILABLE):
            tried_chronos = True
            try:
                preds = _forecast_with_chronos(df["Close"], horizon_days, model_id=chronos_model_id)
                # Suy luận xu hướng + tín hiệu từ dự báo
                trend, signal, reason = _derive_trend_and_signal(
                    last_close,
                    preds[-1],
                    latest.get("RSI14", 50.0),
                    latest.get("SMA7", last_close),
                    latest.get("SMA30", last_close),
                )
                reason = f"{reason}. avg_pred={np.mean(preds):.2f} vs last={last_close:.2f}"
            except Exception as e:
                # Fallback linear
                preds = []
                tried_chronos = True

        if (chosen == "auto" and (not preds)) or (chosen == "chronos" and not preds):
            linear = forecast_price_regression(df, horizon_days)
            preds = list(map(float, linear.get("forecast_next_days", [])))
            trend = linear.get("trend", "Sideways")
            signal = linear.get("signal", "HOLD")
            reason = f"[Fallback Linear] {linear.get('reason', '')}"

    if chosen == "linear" or not preds:
        linear = forecast_price_regression(df, horizon_days)
        preds = list(map(float, linear.get("forecast_next_days", [])))
        trend = linear.get("trend", "Sideways")
        signal = linear.get("signal", "HOLD")
        reason = linear.get("reason", "")

    # 3) bounds theo volatility gần
    bounds = _compute_bounds_from_volatility(preds, df["Close"], lookback=20, k_sigma=1.0)

    # 4) build result
    result = {
        "symbol": symbol,
        "date_range": [start_date, end_date],
        "latest_price": round(last_close, 2),
        "technical_indicators": latest,
        "trend": trend,
        "forecast_horizon_days": int(horizon_days),
        "forecast_next_days": [round(x, 2) for x in preds],
        "forecast_bounds": bounds,  # NEW: list[{min,max}]
        "signal": signal,
        "reason": reason,
        "generated_at": get_current_datetime_iso(),
        "model_used": ("chronos" if (chosen in {"chronos", "auto"} and _CHRONOS_AVAILABLE and "Fallback" not in reason) else "linear")
    }
    return result
