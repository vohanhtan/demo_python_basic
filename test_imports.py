#!/usr/bin/env python3
"""
Test script để kiểm tra imports và chức năng cơ bản
"""

try:
    print("🔄 Đang test imports...")
    
    import data_service
    print("✅ data_service imported")
    
    import indicators
    print("✅ indicators imported")
    
    import predictor
    print("✅ predictor imported")
    
    import ai_module
    print("✅ ai_module imported")
    
    import logger
    print("✅ logger imported")
    
    import visualizer
    print("✅ visualizer imported")
    
    import utils
    print("✅ utils imported")
    
    print("\n🔄 Đang test chức năng cơ bản...")
    
    # Test đọc dữ liệu
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    df = data_service.get_stock_data('FPT', start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    print(f"✅ Đọc dữ liệu FPT: {len(df)} ngày")
    
    # Test tính chỉ báo
    df_indicators = indicators.add_indicators(df)
    print("✅ Tính chỉ báo thành công")
    
    # Test dự đoán
    prediction = predictor.forecast_price_regression(df_indicators, 5)
    print(f"✅ Dự đoán: {prediction['trend']}, Signal: {prediction['signal']}")
    
    # Test AI advice
    result_json = {
        'symbol': 'FPT',
        'trend': prediction['trend'],
        'signal': prediction['signal'],
        'technical_indicators': {'RSI14': 65, 'SMA7': 100, 'SMA30': 95}
    }
    ai_advice = ai_module.get_ai_advice(result_json)
    print(f"✅ AI Advice: {ai_advice[:50]}...")
    
    print("\n🎉 TẤT CẢ TEST THÀNH CÔNG!")
    print("🚀 Có thể chạy: streamlit run app.py")
    
except Exception as e:
    print(f"❌ Lỗi: {str(e)}")
    import traceback
    traceback.print_exc()
