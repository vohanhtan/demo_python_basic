"""
Module đọc và xử lý dữ liệu cổ phiếu từ CSV
Chức năng chính: đọc file CSV, lọc theo mã cổ phiếu và khoảng ngày
"""

import pandas as pd
from pathlib import Path
from typing import Optional
from utils import normalize_symbol, parse_date, validate_date_range


def get_stock_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Đọc dữ liệu cổ phiếu từ file CSV, lọc theo khoảng ngày
    
    Args:
        symbol: Mã cổ phiếu (ví dụ: FPT, VNM)
        start_date: Ngày bắt đầu (YYYY-MM-DD)
        end_date: Ngày kết thúc (YYYY-MM-DD)
        
    Returns:
        DataFrame chứa dữ liệu đã lọc, sắp xếp theo ngày tăng dần
        
    Raises:
        FileNotFoundError: Nếu file CSV không tồn tại
        ValueError: Nếu dữ liệu không hợp lệ hoặc khoảng ngày trống
    """
    # Chuẩn hóa mã cổ phiếu
    symbol = normalize_symbol(symbol)
    
    # Validate khoảng ngày
    validate_date_range(start_date, end_date)
    
    # Đường dẫn file CSV
    data_dir = Path(__file__).parent / "data"
    csv_file = data_dir / f"{symbol}.csv"
    
    # Kiểm tra file tồn tại
    if not csv_file.exists():
        raise FileNotFoundError(
            f"Không tìm thấy dữ liệu cho mã {symbol}. "
            f"Vui lòng kiểm tra file data/{symbol}.csv"
        )
    
    try:
        # Đọc CSV
        df = pd.read_csv(csv_file)
        
        # Kiểm tra cột bắt buộc
        required_columns = ['Date', 'Symbol', 'Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"File CSV thiếu các cột: {', '.join(missing_columns)}")
        
        # Chuyển đổi cột Date thành datetime
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Lọc theo khoảng ngày
        start_dt = parse_date(start_date)
        end_dt = parse_date(end_date)
        
        df_filtered = df[
            (df['Date'] >= start_dt) & 
            (df['Date'] <= end_dt)
        ].copy()
        
        # Kiểm tra có dữ liệu sau khi lọc
        if df_filtered.empty:
            raise ValueError(
                f"Không có dữ liệu cho mã {symbol} trong khoảng ngày "
                f"từ {start_date} đến {end_date}"
            )
        
        # Sắp xếp theo ngày tăng dần
        df_filtered = df_filtered.sort_values('Date').reset_index(drop=True)
        
        # Kiểm tra dữ liệu hợp lệ
        _validate_data_quality(df_filtered, symbol)
        
        return df_filtered
        
    except pd.errors.EmptyDataError:
        raise ValueError(f"File CSV {symbol}.csv rỗng hoặc không có dữ liệu hợp lệ")
    except pd.errors.ParserError as e:
        raise ValueError(f"Lỗi đọc file CSV {symbol}.csv: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Lỗi khi tải dữ liệu từ Yahoo Finance: {e}")

    # Kiểm tra kết quả
    if df is None or df.empty:
        raise ValueError(f"Không tìm thấy dữ liệu cho mã '{symbol}' trong khoảng {start_date} đến {end_date}.")

def _validate_data_quality(df: pd.DataFrame, symbol: str) -> None:
    """
    Validate chất lượng dữ liệu
    
    Args:
        df: DataFrame cần kiểm tra
        symbol: Mã cổ phiếu (để hiển thị lỗi)
        
    Raises:
        ValueError: Nếu dữ liệu không hợp lệ
    """
    # Kiểm tra giá trị null
    null_columns = df.isnull().sum()
    if null_columns.any():
        null_cols = null_columns[null_columns > 0].index.tolist()
        raise ValueError(f"Dữ liệu {symbol} có giá trị null ở cột: {', '.join(null_cols)}")
    
    # Kiểm tra giá âm
    price_columns = ['Open', 'High', 'Low', 'Close']
    for col in price_columns:
        if (df[col] <= 0).any():
            raise ValueError(f"Dữ liệu {symbol} có giá âm hoặc bằng 0 ở cột {col}")
    
    # Kiểm tra Volume âm
    if (df['Volume'] < 0).any():
        raise ValueError(f"Dữ liệu {symbol} có Volume âm")
    
    # Kiểm tra logic giá: High >= Low, High >= Open, High >= Close, Low <= Open, Low <= Close
    if (df['High'] < df['Low']).any():
        raise ValueError(f"Dữ liệu {symbol} có High < Low")
    
    if (df['High'] < df['Open']).any():
        raise ValueError(f"Dữ liệu {symbol} có High < Open")
    
    if (df['High'] < df['Close']).any():
        raise ValueError(f"Dữ liệu {symbol} có High < Close")
    
    if (df['Low'] > df['Open']).any():
        raise ValueError(f"Dữ liệu {symbol} có Low > Open")
    
    if (df['Low'] > df['Close']).any():
        raise ValueError(f"Dữ liệu {symbol} có Low > Close")


def get_available_symbols() -> list:
    """
    Lấy danh sách các mã cổ phiếu có sẵn trong thư mục data
    
    Returns:
        List các mã cổ phiếu có file CSV
    """
    data_dir = Path(__file__).parent / "data"
    
    if not data_dir.exists():
        return []
    
    symbols = []
    for csv_file in data_dir.glob("*.csv"):
        symbol = csv_file.stem.upper()
        symbols.append(symbol)
    
    return sorted(symbols)


def get_data_info(symbol: str) -> dict:
    """
    Lấy thông tin tổng quan về dữ liệu của một mã cổ phiếu
    
    Args:
        symbol: Mã cổ phiếu
        
    Returns:
        Dictionary chứa thông tin: số ngày, ngày đầu, ngày cuối, giá cao nhất, thấp nhất
    """
    symbol = normalize_symbol(symbol)
    data_dir = Path(__file__).parent / "data"
    csv_file = data_dir / f"{symbol}.csv"
    
    if not csv_file.exists():
        return {}
    
    try:
        df = pd.read_csv(csv_file)
        df['Date'] = pd.to_datetime(df['Date'])
        
        return {
            'symbol': symbol,
            'total_days': len(df),
            'start_date': df['Date'].min().strftime('%Y-%m-%d'),
            'end_date': df['Date'].max().strftime('%Y-%m-%d'),
            'highest_price': df['High'].max(),
            'lowest_price': df['Low'].min(),
            'avg_volume': df['Volume'].mean()
        }
    except Exception:
        return {}
