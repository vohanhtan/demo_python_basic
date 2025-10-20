"""
data_service.py
----------------
Phiên bản dùng dữ liệu thật từ Yahoo Finance.
Không còn đọc CSV hay giả lập — toàn bộ dữ liệu được tải qua yfinance.

Public function giữ nguyên chữ ký:
    get_stock_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_stock_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Lấy dữ liệu chứng khoán thật từ Yahoo Finance trong khoảng thời gian chỉ định.
    
    Args:
        symbol (str): Mã cổ phiếu (ví dụ: 'AAPL', 'MSFT', 'TSLA', 'NVDA', 'GOOG', 'META', 'AMZN', 'NFLX', 'AMD', 'JPM')
        start_date (str): Ngày bắt đầu, định dạng 'YYYY-MM-DD'
        end_date (str): Ngày kết thúc, định dạng 'YYYY-MM-DD'
    
    Returns:
        pd.DataFrame: DataFrame với các cột:
            Date, Symbol, Open, High, Low, Close, Volume
    """

    # Đảm bảo symbol hợp lệ
    symbol = symbol.strip().upper()

    # Yahoo yêu cầu end_date là exclusive => cộng thêm 1 ngày
    end_plus = (datetime.fromisoformat(end_date) + timedelta(days=1)).strftime("%Y-%m-%d")

    # Tải dữ liệu từ Yahoo
    try:
        df = yf.download(symbol, start=start_date, end=end_plus, progress=False, threads=False)
    except Exception as e:
        raise RuntimeError(f"Lỗi khi tải dữ liệu từ Yahoo Finance: {e}")

    # Kiểm tra kết quả
    if df is None or df.empty:
        raise ValueError(f"Không tìm thấy dữ liệu cho mã '{symbol}' trong khoảng {start_date} đến {end_date}.")

    # Reset index để có cột Date
    df.reset_index(inplace=True)
    
    # Xử lý MultiIndex columns từ yfinance
    if isinstance(df.columns, pd.MultiIndex):
        # Flatten MultiIndex columns: (column_name, ticker) -> column_name
        df.columns = df.columns.get_level_values(0)

    # Chuẩn hóa schema
    df.rename(columns={
        "Date": "Date",
        "Open": "Open",
        "High": "High",
        "Low": "Low",
        "Close": "Close",
        "Adj Close": "Close",  # phòng trường hợp Yahoo trả Adj Close
        "Volume": "Volume"
    }, inplace=True)

    # Giữ đúng thứ tự cột và thêm Symbol
    df["Symbol"] = symbol
    df = df[["Date", "Symbol", "Open", "High", "Low", "Close", "Volume"]]

    # Ép kiểu dữ liệu
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Loại bỏ dòng trống hoặc lỗi
    df = df.dropna(subset=["Open", "High", "Low", "Close"])
    df = df.sort_values("Date").reset_index(drop=True)

    return df


def get_available_symbols() -> list:
    """
    Trả về danh sách các mã cổ phiếu phổ biến có thể phân tích.
    """
    return [
        "AAPL", "MSFT", "TSLA", "NVDA", "GOOG", "META", "AMZN", "NFLX", "AMD", "JPM",
        "BAC", "WMT", "PG", "JNJ", "V", "UNH", "HD", "MA", "DIS", "PYPL",
        "ADBE", "CRM", "INTC", "CSCO", "ORCL", "IBM", "QCOM", "TXN", "AVGO", "AMAT"
    ]


def get_data_info(symbol: str, start_date: str = None, end_date: str = None) -> dict:
    """
    Lấy thông tin tổng quan về mã cổ phiếu từ Yahoo Finance.
    
    Args:
        symbol (str): Mã cổ phiếu
        start_date (str): Ngày bắt đầu (optional, mặc định lấy 1 năm gần nhất)
        end_date (str): Ngày kết thúc (optional, mặc định là hôm nay)
        
    Returns:
        dict: Thông tin cơ bản về mã cổ phiếu
    """
    symbol = symbol.strip().upper()
    
    try:
        # Lấy thông tin cơ bản từ Yahoo
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Nếu không có start_date/end_date, lấy 1 năm gần nhất
        if not start_date or not end_date:
            from datetime import datetime, timedelta
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        # Lấy dữ liệu giá để tính toán thống kê
        df = get_stock_data(symbol, start_date, end_date)
        
        return {
            'symbol': symbol,
            'name': info.get('longName', symbol),
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
            'market_cap': info.get('marketCap', 0),
            'currency': info.get('currency', 'USD'),
            'exchange': info.get('exchange', 'Unknown'),
            # Thêm thông tin thống kê từ dữ liệu giá
            'total_days': len(df),
            'start_date': df['Date'].min().strftime('%Y-%m-%d') if len(df) > 0 else 'N/A',
            'end_date': df['Date'].max().strftime('%Y-%m-%d') if len(df) > 0 else 'N/A',
            'highest_price': df['High'].max() if len(df) > 0 else 0,
            'lowest_price': df['Low'].min() if len(df) > 0 else 0,
            'avg_volume': df['Volume'].mean() if len(df) > 0 else 0
        }
    except Exception as e:
        return {
            'symbol': symbol,
            'name': symbol,
            'sector': 'Unknown',
            'industry': 'Unknown',
            'market_cap': 0,
            'currency': 'USD',
            'exchange': 'Unknown',
            'total_days': 0,
            'start_date': 'N/A',
            'end_date': 'N/A',
            'highest_price': 0,
            'lowest_price': 0,
            'avg_volume': 0
        }


# Test function
if __name__ == "__main__":
    print("🧪 Testing data_service.py with real Yahoo Finance data...")
    
    try:
        # Test với AAPL
        df = get_stock_data("AAPL", "2024-07-01", "2024-10-01")
        print(f"✅ AAPL data loaded: {df.shape}")
        print(f"   Columns: {list(df.columns)}")
        print(f"   Date range: {df['Date'].min()} to {df['Date'].max()}")
        print(f"   Sample data:")
        print(df.head())
        
        # Test với mã khác
        df2 = get_stock_data("MSFT", "2024-08-01", "2024-09-01")
        print(f"\n✅ MSFT data loaded: {df2.shape}")
        
        # Test get_available_symbols
        symbols = get_available_symbols()
        print(f"\n✅ Available symbols: {len(symbols)} symbols")
        
        # Test get_data_info
        info = get_data_info("AAPL")
        print(f"\n✅ AAPL info: {info['name']} ({info['sector']})")
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()