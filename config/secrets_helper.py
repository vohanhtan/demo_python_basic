"""
utils/secrets_helper.py
-----------------------
Hàm tiện ích an toàn để lấy secret trong cả hai môi trường:
1. Local (.env)
2. Streamlit Cloud (st.secrets)
"""

import os

# Import dotenv nếu có
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    load_dotenv = None

# Import streamlit nếu có (có thể không có khi chạy test)
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None

# Tự động load .env nếu chạy local và có dotenv
if DOTENV_AVAILABLE:
    load_dotenv()

def get_secret(key: str, default=None):
    """
    Ưu tiên đọc secret theo thứ tự:
    1. st.secrets (Streamlit Cloud)
    2. os.environ (local .env)
    
    Args:
        key: Tên biến môi trường
        default: Giá trị mặc định nếu không tìm thấy
        
    Returns:
        Giá trị secret hoặc giá trị mặc định
    """
    # Streamlit Cloud secrets
    if STREAMLIT_AVAILABLE:
        try:
            if hasattr(st, "secrets") and st.secrets:
                val = st.secrets.get(key)
                if val is not None:
                    return val
        except Exception:
            pass

    # Local environment fallback
    return os.getenv(key, default)
