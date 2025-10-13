"""
Module dự đoán giá cổ phiếu ngắn hạn
Sử dụng Linear Regression để dự đoán xu hướng và tạo tín hiệu giao dịch
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import Dict, List
from utils import is_sideways_trend


def forecast_price_regression(df: pd.DataFrame, horizon_days: int = 5) -> Dict:
    """
    Dự đoán giá cổ phiếu ngắn hạn bằng Linear Regression
    
    Args:
        df: DataFrame chứa dữ liệu giá với các chỉ báo
        horizon_days: Số ngày dự đoán (mặc định 5)
        
    Returns:
        Dictionary chứa:
        - trend: "Uptrend"/"Downtrend"/"Sideways"
        - forecast_horizon_days: số ngày dự đoán
        - forecast_next_days: danh sách giá dự đoán
        - signal: "BUY"/"SELL"/"HOLD"
        - reason: lý do tín hiệu
    """
    if df.empty or len(df) < 10:
        return _get_default_prediction(horizon_days, "Dữ liệu không đủ để dự đoán", df)
    
    try:
        # Chuẩn bị dữ liệu
        X, y = _prepare_regression_data(df)
        
        if len(X) < 5:
            return _get_simple_prediction(df, horizon_days, "Dữ liệu quá ít để huấn luyện mô hình")
        
        # Huấn luyện mô hình Linear Regression
        model = LinearRegression()
        model.fit(X, y)
        
        # Dự đoán các ngày tiếp theo
        forecast_prices = _generate_forecast(model, df, horizon_days)
        
        # Phân tích xu hướng
        current_price = df['Close'].iloc[-1]
        last_forecast_price = forecast_prices[-1]
        
        trend = _determine_trend(current_price, last_forecast_price)
        
        # Tạo tín hiệu giao dịch
        signal, reason = _generate_trading_signal(df, trend, forecast_prices)
        
        return {
            "trend": trend,
            "forecast_horizon_days": horizon_days,
            "forecast_next_days": [round(price, 2) for price in forecast_prices],
            "signal": signal,
            "reason": reason
        }
        
    except Exception as e:
        return _get_simple_prediction(df, horizon_days, f"Lỗi dự đoán: {str(e)}")


def _prepare_regression_data(df: pd.DataFrame) -> tuple:
    """
    Chuẩn bị dữ liệu cho Linear Regression
    
    Args:
        df: DataFrame chứa dữ liệu giá
        
    Returns:
        Tuple (X, y) cho mô hình regression
    """
    # Sử dụng index thời gian và các chỉ báo làm features
    features = []
    targets = []
    
    for i in range(1, len(df)):
        # Features: index, SMA7, SMA30, RSI14 (nếu có)
        feature_row = [i]  # index thời gian
        
        # Thêm chỉ báo với xử lý NaN
        if 'SMA7' in df.columns:
            sma7_val = df['SMA7'].iloc[i-1]
            feature_row.append(sma7_val if not pd.isna(sma7_val) else df['Close'].iloc[i-1])
        
        if 'SMA30' in df.columns:
            sma30_val = df['SMA30'].iloc[i-1]
            feature_row.append(sma30_val if not pd.isna(sma30_val) else df['Close'].iloc[i-1])
        
        if 'RSI14' in df.columns:
            rsi_val = df['RSI14'].iloc[i-1]
            feature_row.append(rsi_val if not pd.isna(rsi_val) else 50.0)  # RSI mặc định 50
        
        features.append(feature_row)
        targets.append(df['Close'].iloc[i])
    
    return np.array(features), np.array(targets)


def _generate_forecast(model: LinearRegression, df: pd.DataFrame, horizon_days: int) -> List[float]:
    """
    Tạo dự đoán giá cho các ngày tiếp theo
    
    Args:
        model: Mô hình Linear Regression đã huấn luyện
        df: DataFrame dữ liệu
        horizon_days: Số ngày dự đoán
        
    Returns:
        Danh sách giá dự đoán
    """
    forecast_prices = []
    last_index = len(df)
    
    for day in range(1, horizon_days + 1):
        # Tạo feature cho ngày dự đoán
        feature_row = [last_index + day - 1]
        
        # Sử dụng giá trị chỉ báo gần nhất với xử lý NaN
        if 'SMA7' in df.columns:
            sma7_val = df['SMA7'].iloc[-1]
            feature_row.append(sma7_val if not pd.isna(sma7_val) else df['Close'].iloc[-1])
        
        if 'SMA30' in df.columns:
            sma30_val = df['SMA30'].iloc[-1]
            feature_row.append(sma30_val if not pd.isna(sma30_val) else df['Close'].iloc[-1])
        
        if 'RSI14' in df.columns:
            rsi_val = df['RSI14'].iloc[-1]
            feature_row.append(rsi_val if not pd.isna(rsi_val) else 50.0)
        
        # Dự đoán giá
        predicted_price = model.predict([feature_row])[0]
        forecast_prices.append(max(predicted_price, 0))  # Đảm bảo giá không âm
    
    return forecast_prices


def _determine_trend(current_price: float, forecast_price: float) -> str:
    """
    Xác định xu hướng dựa trên giá hiện tại và giá dự đoán
    
    Args:
        current_price: Giá hiện tại
        forecast_price: Giá dự đoán cuối cùng
        
    Returns:
        "Uptrend", "Downtrend", hoặc "Sideways"
    """
    if is_sideways_trend(current_price, forecast_price, threshold=0.02):
        return "Sideways"
    elif forecast_price > current_price:
        return "Uptrend"
    else:
        return "Downtrend"


def _generate_trading_signal(df: pd.DataFrame, trend: str, forecast_prices: List[float]) -> tuple:
    """
    Tạo tín hiệu giao dịch dựa trên xu hướng và chỉ báo
    
    Args:
        df: DataFrame chứa dữ liệu
        trend: Xu hướng dự đoán
        forecast_prices: Danh sách giá dự đoán
        
    Returns:
        Tuple (signal, reason)
    """
    # Lấy chỉ báo mới nhất
    latest_rsi = df['RSI14'].iloc[-1] if 'RSI14' in df.columns else 50
    latest_sma7 = df['SMA7'].iloc[-1] if 'SMA7' in df.columns else df['Close'].iloc[-1]
    latest_sma30 = df['SMA30'].iloc[-1] if 'SMA30' in df.columns else df['Close'].iloc[-1]
    
    # Logic tín hiệu
    if trend == "Uptrend":
        if latest_rsi < 70:  # Chưa quá mua
            if latest_sma7 > latest_sma30:  # SMA ngắn > SMA dài
                return "BUY", "Xu hướng tăng, RSI chưa quá mua, SMA7 > SMA30"
            else:
                return "HOLD", "Xu hướng tăng nhưng cần chờ SMA7 vượt SMA30"
        else:
            return "HOLD", "Xu hướng tăng nhưng RSI đã quá mua"
    
    elif trend == "Downtrend":
        if latest_rsi > 30:  # Chưa quá bán
            if latest_sma7 < latest_sma30:  # SMA ngắn < SMA dài
                return "SELL", "Xu hướng giảm, RSI chưa quá bán, SMA7 < SMA30"
            else:
                return "HOLD", "Xu hướng giảm nhưng cần chờ SMA7 xuống dưới SMA30"
        else:
            return "HOLD", "Xu hướng giảm nhưng RSI đã quá bán, có thể phục hồi"
    
    else:  # Sideways
        if latest_rsi < 30:
            return "BUY", "Thị trường sideways, RSI quá bán, cơ hội mua"
        elif latest_rsi > 70:
            return "SELL", "Thị trường sideways, RSI quá mua, nên bán"
        else:
            return "HOLD", "Thị trường sideways, RSI trung tính, chờ tín hiệu rõ ràng"


def _get_default_prediction(horizon_days: int, reason: str, df: pd.DataFrame = None) -> Dict:
    """
    Trả về dự đoán mặc định khi có lỗi
    
    Args:
        horizon_days: Số ngày dự đoán
        reason: Lý do lỗi
        df: DataFrame dữ liệu (tùy chọn)
        
    Returns:
        Dictionary dự đoán mặc định
    """
    # Sử dụng giá thực từ DataFrame nếu có
    if df is not None and not df.empty:
        current_price = df['Close'].iloc[-1]
    else:
        current_price = 100.0  # Giá mặc định chỉ khi không có dữ liệu
    
    forecast_prices = []
    
    for i in range(horizon_days):
        # Dự đoán đơn giản: giá tăng nhẹ theo thời gian
        predicted_price = current_price * (1 + 0.001 * (i + 1))
        forecast_prices.append(round(predicted_price, 2))
    
    return {
        "trend": "Sideways",
        "forecast_horizon_days": horizon_days,
        "forecast_next_days": forecast_prices,
        "signal": "HOLD",
        "reason": reason
    }


def _get_simple_prediction(df: pd.DataFrame, horizon_days: int, reason: str) -> Dict:
    """
    Tạo dự đoán đơn giản dựa trên dữ liệu thực
    
    Args:
        df: DataFrame dữ liệu
        horizon_days: Số ngày dự đoán
        reason: Lý do lỗi
        
    Returns:
        Dictionary dự đoán đơn giản
    """
    if df.empty:
        return _get_default_prediction(horizon_days, reason, df)
    
    # Lấy giá hiện tại
    current_price = df['Close'].iloc[-1]
    
    # Tính xu hướng đơn giản dựa trên 5 ngày gần nhất
    recent_prices = df['Close'].tail(5).values
    if len(recent_prices) >= 2:
        price_change = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
        daily_change = price_change / len(recent_prices)
    else:
        daily_change = 0.001  # Tăng nhẹ mặc định
    
    # Tạo dự đoán
    forecast_prices = []
    for i in range(horizon_days):
        predicted_price = current_price * (1 + daily_change * (i + 1))
        forecast_prices.append(round(predicted_price, 2))
    
    # Xác định xu hướng
    if daily_change > 0.002:
        trend = "Uptrend"
        signal = "BUY"
        signal_reason = "Xu hướng tăng dựa trên dữ liệu gần đây"
    elif daily_change < -0.002:
        trend = "Downtrend"
        signal = "SELL"
        signal_reason = "Xu hướng giảm dựa trên dữ liệu gần đây"
    else:
        trend = "Sideways"
        signal = "HOLD"
        signal_reason = "Xu hướng sideways, biến động nhỏ"
    
    return {
        "trend": trend,
        "forecast_horizon_days": horizon_days,
        "forecast_next_days": forecast_prices,
        "signal": signal,
        "reason": f"{signal_reason}. {reason}"
    }


def calculate_prediction_accuracy(df: pd.DataFrame, horizon_days: int = 5) -> float:
    """
    Tính độ chính xác của dự đoán (để đánh giá mô hình)
    
    Args:
        df: DataFrame dữ liệu
        horizon_days: Số ngày dự đoán
        
    Returns:
        Độ chính xác (0-1)
    """
    if len(df) < horizon_days + 10:
        return 0.0
    
    try:
        # Chia dữ liệu: train và test
        train_df = df.iloc[:-horizon_days]
        test_df = df.iloc[-horizon_days:]
        
        # Dự đoán trên tập train
        prediction = forecast_price_regression(train_df, horizon_days)
        predicted_prices = prediction['forecast_next_days']
        actual_prices = test_df['Close'].tolist()
        
        # Tính độ chính xác (Mean Absolute Percentage Error)
        mape = np.mean([abs(pred - actual) / actual for pred, actual in zip(predicted_prices, actual_prices)])
        accuracy = max(0, 1 - mape)
        
        return round(accuracy, 3)
        
    except Exception:
        return 0.0


def get_trend_strength(df: pd.DataFrame) -> str:
    """
    Đánh giá độ mạnh của xu hướng
    
    Args:
        df: DataFrame dữ liệu
        
    Returns:
        "Strong", "Moderate", "Weak"
    """
    if len(df) < 10:
        return "Weak"
    
    # Tính độ dốc của đường xu hướng
    recent_prices = df['Close'].tail(10).values
    x = np.arange(len(recent_prices))
    
    try:
        slope = np.polyfit(x, recent_prices, 1)[0]
        slope_percent = abs(slope) / recent_prices.mean() * 100
        
        if slope_percent > 2:
            return "Strong"
        elif slope_percent > 0.5:
            return "Moderate"
        else:
            return "Weak"
    except Exception:
        return "Weak"
