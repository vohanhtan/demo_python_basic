#!/usr/bin/env python3
"""
Final test script để kiểm tra toàn bộ dự án sau khi chuyển ra thư mục root
"""

import sys
import os
from pathlib import Path

def test_project_structure():
    """Kiểm tra cấu trúc dự án"""
    print("🔍 Kiểm tra cấu trúc dự án...")
    
    required_files = [
        'app.py', 'data_service.py', 'indicators.py', 'predictor.py',
        'ai_module.py', 'logger.py', 'visualizer.py', 'utils.py',
        'demo.py', 'requirements.txt', 'README.md', 'QUICK_START.md'
    ]
    
    required_dirs = ['data', 'reports']
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    missing_dirs = []
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing_dirs.append(dir_name)
    
    if missing_files:
        print(f"❌ Thiếu files: {missing_files}")
        return False
    
    if missing_dirs:
        print(f"❌ Thiếu thư mục: {missing_dirs}")
        return False
    
    print("✅ Cấu trúc dự án OK")
    return True

def test_imports():
    """Kiểm tra imports"""
    print("🔍 Kiểm tra imports...")
    
    try:
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        from sklearn.linear_model import LinearRegression
        import streamlit as st
        print("✅ External libraries imported")
        
        import utils
        import data_service
        import indicators
        import predictor
        import ai_module
        import logger
        import visualizer
        print("✅ Project modules imported")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_data_files():
    """Kiểm tra dữ liệu CSV"""
    print("🔍 Kiểm tra dữ liệu CSV...")
    
    try:
        fpt_file = Path('data/FPT.csv')
        vnm_file = Path('data/VNM.csv')
        
        if not fpt_file.exists():
            print("❌ Thiếu data/FPT.csv")
            return False
        
        if not vnm_file.exists():
            print("❌ Thiếu data/VNM.csv")
            return False
        
        # Kiểm tra nội dung
        import pandas as pd
        df_fpt = pd.read_csv(fpt_file)
        df_vnm = pd.read_csv(vnm_file)
        
        if len(df_fpt) < 50:
            print(f"❌ FPT.csv có quá ít dữ liệu: {len(df_fpt)} ngày")
            return False
        
        if len(df_vnm) < 50:
            print(f"❌ VNM.csv có quá ít dữ liệu: {len(df_vnm)} ngày")
            return False
        
        print(f"✅ FPT.csv: {len(df_fpt)} ngày")
        print(f"✅ VNM.csv: {len(df_vnm)} ngày")
        return True
        
    except Exception as e:
        print(f"❌ Error reading data: {e}")
        return False

def test_basic_functionality():
    """Kiểm tra chức năng cơ bản"""
    print("🔍 Kiểm tra chức năng cơ bản...")
    
    try:
        from datetime import datetime, timedelta
        import data_service
        import indicators
        import predictor
        import ai_module
        
        # Test đọc dữ liệu
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        df = data_service.get_stock_data('FPT', start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        if len(df) == 0:
            print("❌ Không đọc được dữ liệu")
            return False
        
        # Test tính chỉ báo
        df_indicators = indicators.add_indicators(df)
        if 'SMA7' not in df_indicators.columns:
            print("❌ Không tính được SMA7")
            return False
        
        # Test dự đoán
        prediction = predictor.forecast_price_regression(df_indicators, 5)
        if not prediction or 'trend' not in prediction:
            print("❌ Không dự đoán được")
            return False
        
        # Test AI advice
        result_json = {
            'symbol': 'FPT',
            'trend': prediction['trend'],
            'signal': prediction['signal'],
            'technical_indicators': {'RSI14': 65, 'SMA7': 100, 'SMA30': 95}
        }
        ai_advice = ai_module.get_ai_advice(result_json)
        if not ai_advice:
            print("❌ Không tạo được AI advice")
            return False
        
        print("✅ Chức năng cơ bản OK")
        return True
        
    except Exception as e:
        print(f"❌ Error testing functionality: {e}")
        return False

def main():
    """Hàm chính"""
    print("🚀 FINAL TEST - AI Stock Insight")
    print("=" * 50)
    
    tests = [
        ("Cấu trúc dự án", test_project_structure),
        ("Imports", test_imports),
        ("Dữ liệu CSV", test_data_files),
        ("Chức năng cơ bản", test_basic_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"📊 KẾT QUẢ: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 TẤT CẢ TESTS THÀNH CÔNG!")
        print("🚀 Sẵn sàng chạy: streamlit run app.py")
        print("🎯 Hoặc test: python3 demo.py")
    else:
        print("❌ CÓ LỖI! Vui lòng kiểm tra lại.")
        sys.exit(1)

if __name__ == "__main__":
    main()
