#!/usr/bin/env python3
"""
Demo script để test nhanh AI Stock Insight
Chạy: python3 demo.py
"""

from data_service import get_stock_data, get_available_symbols
from indicators import add_indicators, get_latest_indicators
from predictor import forecast_price_regression
from ai_module import get_ai_advice, get_ai_confidence_score
from logger import append_daily_log
from utils import get_current_datetime_iso
import json


def demo_analysis(symbol="FPT", days_back=60):
    """Demo phân tích một mã cổ phiếu"""
    
    print(f"🚀 Demo phân tích {symbol}")
    print("=" * 50)
    
    try:
        # 1. Đọc dữ liệu
        print("📥 Đang đọc dữ liệu...")
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        df = get_stock_data(symbol, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        print(f"✅ Đọc được {len(df)} ngày dữ liệu")
        
        # 2. Tính chỉ báo
        print("📊 Đang tính chỉ báo kỹ thuật...")
        df_indicators = add_indicators(df)
        latest_indicators = get_latest_indicators(df_indicators)
        print(f"✅ SMA7: {latest_indicators.get('SMA7', 0):.2f}")
        print(f"✅ SMA30: {latest_indicators.get('SMA30', 0):.2f}")
        print(f"✅ RSI14: {latest_indicators.get('RSI14', 0):.2f}")
        
        # 3. Dự đoán
        print("🔮 Đang dự đoán...")
        prediction = forecast_price_regression(df_indicators, 5)
        print(f"✅ Xu hướng: {prediction['trend']}")
        print(f"✅ Tín hiệu: {prediction['signal']}")
        print(f"✅ Lý do: {prediction['reason']}")
        
        # 4. Tạo JSON kết quả
        result_json = {
            "symbol": symbol,
            "date_range": [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')],
            "latest_price": round(df['Close'].iloc[-1], 2),
            "technical_indicators": latest_indicators,
            "trend": prediction['trend'],
            "forecast_horizon_days": prediction['forecast_horizon_days'],
            "forecast_next_days": prediction['forecast_next_days'],
            "signal": prediction['signal'],
            "reason": prediction['reason'],
            "generated_at": get_current_datetime_iso()
        }
        
        # 5. AI Advice
        print("🤖 Đang tạo lời khuyên AI...")
        ai_advice = get_ai_advice(result_json)
        result_json['ai_advice'] = ai_advice
        print(f"✅ AI Advice: {ai_advice}")
        
        # 6. Ghi log
        print("💾 Đang ghi log...")
        log_result = append_daily_log(result_json)
        print(f"✅ Đã ghi vào {log_result['file_path']}")
        print(f"✅ Tổng bản ghi hôm nay: {log_result['total_records_today']}")
        
        # 7. Hiển thị kết quả
        print("\n📋 KẾT QUẢ PHÂN TÍCH:")
        print("=" * 50)
        print(json.dumps(result_json, indent=2, ensure_ascii=False))
        
        return result_json
        
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        return None


def main():
    """Hàm chính"""
    print("📈 AI STOCK INSIGHT - DEMO")
    print("=" * 50)
    
    # Kiểm tra symbols có sẵn
    available_symbols = get_available_symbols()
    print(f"📊 Mã cổ phiếu có sẵn: {', '.join(available_symbols)}")
    print()
    
    # Demo FPT
    result_fpt = demo_analysis("FPT", 60)
    print("\n" + "=" * 50)
    
    # Demo VNM
    result_vnm = demo_analysis("VNM", 60)
    
    print("\n🎉 DEMO HOÀN THÀNH!")
    print("🚀 Để chạy UI: streamlit run app.py")


if __name__ == "__main__":
    main()
