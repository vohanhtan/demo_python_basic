"""
Module tính toán các chỉ báo kỹ thuật
Chức năng: SMA (Simple Moving Average), RSI (Relative Strength Index)
"""

import pandas as pd
import numpy as np
from typing import Tuple


def add_moving_averages(df: pd.DataFrame, short: int = 7, long: int = 30) -> pd.DataFrame:
    """
    Thêm các đường trung bình động SMA vào DataFrame
    
    Args:
        df: DataFrame chứa dữ liệu giá cổ phiếu
        short: Chu kỳ SMA ngắn hạn (mặc định 7)
        long: Chu kỳ SMA dài hạn (mặc định 30)
        
    Returns:
        DataFrame đã thêm cột SMA7 và SMA30
    """
    df = df.copy()
    
    # Tính SMA ngắn hạn với min_periods để tránh NaN
    df[f'SMA{short}'] = df['Close'].rolling(window=short, min_periods=1).mean()
    
    # Tính SMA dài hạn với min_periods để tránh NaN
    df[f'SMA{long}'] = df['Close'].rolling(window=long, min_periods=1).mean()
    
    return df


def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Thêm chỉ báo RSI (Relative Strength Index) vào DataFrame
    
    Công thức RSI:
    RSI = 100 - (100 / (1 + RS))
    RS = Average Gain / Average Loss
    
    Args:
        df: DataFrame chứa dữ liệu giá cổ phiếu
        period: Chu kỳ tính RSI (mặc định 14)
        
    Returns:
        DataFrame đã thêm cột RSI14
    """
    df = df.copy()
    
    try:
        # Kiểm tra dữ liệu đủ để tính RSI
        if len(df) < 15:
            print("⚠️ Dữ liệu quá ngắn, RSI có thể không chính xác.")
        
        if len(df) < period + 1:
            print(f"⚠️ Warning: Dữ liệu không đủ để tính RSI({period}). Cần ít nhất {period + 1} ngày, hiện có {len(df)} ngày.")
            df[f'RSI{period}'] = None
            return df
        
        # Tính thay đổi giá
        delta = df['Close'].diff()
        
        # Tách gain và loss
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Tính trung bình gain và loss (sử dụng exponential moving average)
        avg_gain = gain.ewm(span=period, adjust=False).mean()
        avg_loss = loss.ewm(span=period, adjust=False).mean()
        
        # Tính RS và RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # Thêm cột RSI vào DataFrame với min_periods=1 để tránh NaN
        df[f'RSI{period}'] = rsi
        
    except Exception as e:
        print(f"⚠️ Warning: Không thể tính RSI({period}): {str(e)}")
        df[f'RSI{period}'] = None
    
    return df


def calculate_rsi(prices, period=14):
    """
    Tính RSI với min_periods=1 để tránh NaN
    
    Args:
        prices: Series giá đóng cửa
        period: Chu kỳ RSI
        
    Returns:
        Series RSI
    """
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.ewm(span=period, adjust=False, min_periods=1).mean()
    avg_loss = loss.ewm(span=period, adjust=False, min_periods=1).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Thêm tất cả các chỉ báo kỹ thuật vào DataFrame
    
    Args:
        df: DataFrame chứa dữ liệu giá cổ phiếu
        
    Returns:
        DataFrame đã thêm các cột: SMA7, SMA30, RSI14
    """
    # Kiểm tra DataFrame có dữ liệu
    if df.empty:
        raise ValueError("DataFrame rỗng, không thể tính chỉ báo")
    
    # Kiểm tra cột Close tồn tại
    if 'Close' not in df.columns:
        raise ValueError("DataFrame thiếu cột 'Close'")
    
    # Thêm Moving Averages
    df_with_ma = add_moving_averages(df)
    
    # Thêm RSI
    df_with_indicators = add_rsi(df_with_ma)
    
    return df_with_indicators


def get_latest_indicators(df: pd.DataFrame) -> dict:
    """
    Lấy giá trị chỉ báo mới nhất từ DataFrame
    
    Args:
        df: DataFrame đã có các chỉ báo
        
    Returns:
        Dictionary chứa giá trị chỉ báo mới nhất
    """
    if df.empty:
        return {}
    
    latest = df.iloc[-1]
    
    indicators = {}
    
    # Lấy SMA7 và SMA30
    if 'SMA7' in df.columns:
        indicators['SMA7'] = round(latest['SMA7'], 2)
    
    if 'SMA30' in df.columns:
        indicators['SMA30'] = round(latest['SMA30'], 2)
    
    # Lấy RSI14
    if 'RSI14' in df.columns and latest['RSI14'] is not None:
        indicators['RSI14'] = round(latest['RSI14'], 2)
    
    return indicators


def calculate_rsi_manually(prices: list, period: int = 14) -> float:
    """
    Tính RSI thủ công từ danh sách giá (để test hoặc hiểu rõ công thức)
    
    Args:
        prices: Danh sách giá đóng cửa
        period: Chu kỳ tính RSI
        
    Returns:
        Giá trị RSI
    """
    if len(prices) < period + 1:
        return 50.0  # Giá trị mặc định
    
    # Tính thay đổi giá
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    
    # Tách gain và loss
    gains = [delta if delta > 0 else 0 for delta in deltas]
    losses = [-delta if delta < 0 else 0 for delta in deltas]
    
    # Tính trung bình gain và loss cho period gần nhất
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    # Tránh chia cho 0
    if avg_loss == 0:
        return 100.0
    
    # Tính RS và RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)


def get_rsi_signal(rsi_value: float) -> str:
    """
    Phân tích tín hiệu từ giá trị RSI
    
    Args:
        rsi_value: Giá trị RSI
        
    Returns:
        Tín hiệu: "OVERSOLD", "OVERBOUGHT", "NEUTRAL"
    """
    if rsi_value <= 30:
        return "OVERSOLD"
    elif rsi_value >= 70:
        return "OVERBOUGHT"
    else:
        return "NEUTRAL"


def get_ma_signal(sma_short: float, sma_long: float) -> str:
    """
    Phân tích tín hiệu từ đường trung bình động
    
    Args:
        sma_short: Giá trị SMA ngắn hạn
        sma_long: Giá trị SMA dài hạn
        
    Returns:
        Tín hiệu: "BULLISH", "BEARISH", "NEUTRAL"
    """
    if sma_short > sma_long:
        return "BULLISH"
    elif sma_short < sma_long:
        return "BEARISH"
    else:
        return "NEUTRAL"


def validate_indicators_data(df: pd.DataFrame) -> bool:
    """
    Validate dữ liệu để tính chỉ báo
    
    Args:
        df: DataFrame cần kiểm tra
        
    Returns:
        True nếu dữ liệu hợp lệ
        
    Raises:
        ValueError: Nếu dữ liệu không hợp lệ
    """
    if df.empty:
        raise ValueError("DataFrame rỗng")
    
    if 'Close' not in df.columns:
        raise ValueError("Thiếu cột 'Close'")
    
    if len(df) < 2:
        raise ValueError("Cần ít nhất 2 ngày dữ liệu để tính chỉ báo")
    
    # Kiểm tra giá âm
    if (df['Close'] <= 0).any():
        raise ValueError("Giá đóng cửa không được âm hoặc bằng 0")
    
    return True
