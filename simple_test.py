#!/usr/bin/env python3
"""
Simple test script
"""

print("Testing basic imports...")

try:
    import pandas as pd
    print("✅ pandas")
    
    import numpy as np
    print("✅ numpy")
    
    import matplotlib.pyplot as plt
    print("✅ matplotlib")
    
    from sklearn.linear_model import LinearRegression
    print("✅ scikit-learn")
    
    import streamlit as st
    print("✅ streamlit")
    
    print("\nTesting project modules...")
    
    import utils
    print("✅ utils")
    
    import data_service
    print("✅ data_service")
    
    import indicators
    print("✅ indicators")
    
    import predictor
    print("✅ predictor")
    
    import ai_module
    print("✅ ai_module")
    
    import logger
    print("✅ logger")
    
    import visualizer
    print("✅ visualizer")
    
    print("\n🎉 All imports successful!")
    print("Ready to run: streamlit run app.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Error: {e}")
