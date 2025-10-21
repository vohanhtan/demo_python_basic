"""
Module tiện ích chung cho AI Stock Insight
Chứa các hàm hỗ trợ: chuẩn hóa ngày, validate input, format số, etc.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_config(key: str, default=None):
    """
    Đọc biến môi trường từ .env, nếu không có thì trả giá trị mặc định
    DEPRECATED: Sử dụng get_secret() từ utils.secrets_helper thay thế
    
    Args:
        key: Tên biến môi trường
        default: Giá trị mặc định nếu không tìm thấy
        
    Returns:
        Giá trị biến môi trường hoặc giá trị mặc định
    """
    return os.getenv(key, default)


def normalize_symbol(symbol: str) -> str:
    """
    Chuẩn hóa mã cổ phiếu về dạng in hoa, xóa khoảng trắng
    
    Args:
        symbol: Mã cổ phiếu cần chuẩn hóa
        
    Returns:
        Mã cổ phiếu đã chuẩn hóa (in hoa)
    """
    return symbol.strip().upper()


def parse_date(date_str: str) -> datetime:
    """
    Parse chuỗi ngày từ định dạng YYYY-MM-DD
    
    Args:
        date_str: Chuỗi ngày dạng YYYY-MM-DD
        
    Returns:
        datetime object
        
    Raises:
        ValueError: Nếu định dạng ngày không hợp lệ
    """
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise ValueError(f"Định dạng ngày không hợp lệ: {date_str}. Vui lòng sử dụng YYYY-MM-DD")


def format_date(date_obj: datetime) -> str:
    """
    Format datetime object thành chuỗi YYYY-MM-DD
    
    Args:
        date_obj: datetime object
        
    Returns:
        Chuỗi ngày dạng YYYY-MM-DD
    """
    return date_obj.strftime('%Y-%m-%d')


def get_default_date_range(days_back: int = 60) -> Tuple[str, str]:
    """
    Lấy khoảng ngày mặc định (từ days_back ngày trước đến hôm nay)
    
    Args:
        days_back: Số ngày lùi về trước (mặc định 60)
        
    Returns:
        Tuple (start_date, end_date) dạng YYYY-MM-DD
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    return format_date(start_date), format_date(end_date)


def validate_date_range(start_date: str, end_date: str) -> None:
    """
    Validate khoảng ngày hợp lệ
    
    Args:
        start_date: Ngày bắt đầu
        end_date: Ngày kết thúc
        
    Raises:
        ValueError: Nếu khoảng ngày không hợp lệ
    """
    start_dt = parse_date(start_date)
    end_dt = parse_date(end_date)
    
    if start_dt > end_dt:
        raise ValueError("Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc")
    
    # Kiểm tra ngày không quá xa trong tương lai
    today = datetime.now()
    if end_dt > today:
        raise ValueError("Ngày kết thúc không được vượt quá hôm nay")


def format_number(value: float, decimals: int = 2) -> str:
    """
    Format số với số chữ số thập phân cố định
    
    Args:
        value: Giá trị số cần format
        decimals: Số chữ số thập phân (mặc định 2)
        
    Returns:
        Chuỗi số đã format
    """
    return f"{value:.{decimals}f}"


def is_sideways_trend(current_price: float, forecast_price: float, threshold: float = 0.02) -> bool:
    """
    Kiểm tra xem có phải xu hướng sideways không
    
    Args:
        current_price: Giá hiện tại
        forecast_price: Giá dự đoán
        threshold: Ngưỡng phần trăm để coi là sideways (mặc định 2%)
        
    Returns:
        True nếu là sideways trend
    """
    change_percent = abs(forecast_price - current_price) / current_price
    return change_percent <= threshold


def get_current_datetime_iso() -> str:
    """
    Lấy thời gian hiện tại dạng ISO format
    
    Returns:
        Chuỗi thời gian dạng YYYY-MM-DDTHH:MM:SS
    """
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')


def validate_symbol(symbol: str) -> str:
    """
    Validate và chuẩn hóa mã cổ phiếu
    
    Args:
        symbol: Mã cổ phiếu cần validate
        
    Returns:
        Mã cổ phiếu đã chuẩn hóa
        
    Raises:
        ValueError: Nếu mã cổ phiếu không hợp lệ
    """
    if not symbol or not symbol.strip():
        raise ValueError("Mã cổ phiếu không được để trống")
    
    normalized = normalize_symbol(symbol)
    
    # Kiểm tra chỉ chứa chữ cái và số
    if not re.match(r'^[A-Z0-9]+$', normalized):
        raise ValueError("Mã cổ phiếu chỉ được chứa chữ cái và số")
    
    if len(normalized) < 2 or len(normalized) > 10:
        raise ValueError("Mã cổ phiếu phải có độ dài từ 2 đến 10 ký tự")
    
    return normalized


def truncate_json_for_display(data: dict, max_length: int = 1000) -> str:
    """
    Rút gọn JSON để hiển thị trên UI
    
    Args:
        data: Dictionary cần rút gọn
        max_length: Độ dài tối đa (mặc định 1000)
        
    Returns:
        Chuỗi JSON đã rút gọn
    """
    import json
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    
    if len(json_str) <= max_length:
        return json_str
    
    # Rút gọn bằng cách cắt bớt
    truncated = json_str[:max_length] + "\n... (đã rút gọn)"
    return truncated


def format_number(n):
    """
    Format số với dấu phẩy ngăn cách hàng nghìn
    
    Args:
        n: Số cần format
        
    Returns:
        Chuỗi số đã format
    """
    return f"{n:,.2f}".replace(",", ".")


def is_data_short(df, min_rows=30):
    """
    Kiểm tra xem dữ liệu có ngắn không
    
    Args:
        df: DataFrame cần kiểm tra
        min_rows: Số hàng tối thiểu (mặc định 30)
        
    Returns:
        True nếu dữ liệu ngắn
    """
    return len(df) < min_rows
