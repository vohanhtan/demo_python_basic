"""
--------------------
Script CLI chạy 1 lần để kiểm tra pipeline ngoài Streamlit:
- Đọc CSV từ notebooks/data
- Dự báo bằng forecast_service (linear/chronos/auto)
- In JSON kết quả ra console
- Tuỳ chọn ghi log vào reports/YYYY-MM-DD.json (append_daily_log)

Ví dụ:
  python run_forecast_once.py --symbol AAPL --start 2023-06-01 --end 2023-09-01 --horizon 5 --model auto --log
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from forecast_service import get_forecast
from logger import append_daily_log
from ai_module import get_ai_advice, get_ai_confidence_score
from utils import normalize_symbol

def main():
    parser = argparse.ArgumentParser(description="Run one-shot forecast for a symbol.")
    parser.add_argument("--symbol", required=True, help="Mã cổ phiếu, ví dụ: AAPL/MSFT/VNINDEX")
    parser.add_argument("--start", required=True, help="Ngày bắt đầu (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="Ngày kết thúc (YYYY-MM-DD)")
    parser.add_argument("--horizon", type=int, default=5, help="Số ngày dự báo (mặc định 5)")
    parser.add_argument("--model", default="linear", choices=["linear", "chronos", "auto"], help="Chọn mô hình")
    parser.add_argument("--chronos_id", default="amazon/chronos-t5-tiny", help="HF model id cho Chronos")
    parser.add_argument("--log", action="store_true", help="Append kết quả vào reports/YYYY-MM-DD.json")
    parser.add_argument("--save_json", type=str, default="", help="Lưu JSON ra file path (tùy chọn)")
    args = parser.parse_args()

    symbol = normalize_symbol(args.symbol)
    start = args.start
    end = args.end
    horizon = int(args.horizon)

    # 1) chạy forecast service
    result = get_forecast(
        symbol=symbol,
        start_date=start,
        end_date=end,
        horizon_days=horizon,
        model=args.model,
        chronos_model_id=args.chronos_id
    )

    # 2) gọi AI advice (giả lập hoặc thực nếu bạn bật USE_REAL_AI sau này)
    advice = get_ai_advice(result)
    result["ai_advice"] = advice
    result["ai_confidence"] = round(get_ai_confidence_score(result), 3)

    # 3) in ra console
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # 4) tuỳ chọn lưu JSON thô
    if args.save_json:
        out_path = Path(args.save_json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n💾 Saved: {out_path}")

    # 5) tuỳ chọn ghi log hằng ngày
    if args.log:
        log_info = append_daily_log(result)
        print(f"\n📝 Logged to: {log_info['file_path']} (records today: {log_info['total_records_today']})")


if __name__ == "__main__":
    main()
