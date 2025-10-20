"""
Module đọc và xử lý dữ liệu cổ phiếu từ CSV (chuẩn hoá cho notebooks/data)
- Đọc file CSV đã clean trong notebooks/data
- Chuẩn hoá schema về: Date, Symbol, Open, High, Low, Close, Volume
- Lọc theo khoảng ngày và validate dữ liệu
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict

from utils import normalize_symbol, parse_date, validate_date_range

# Thư mục dữ liệu cố định: notebooks/data
DATA_DIR = Path("notebooks/data")


# ---------- Public APIs ----------

def get_stock_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Đọc dữ liệu cổ phiếu từ file CSV, lọc theo khoảng ngày và chuẩn hoá schema.

    Args:
        symbol: Mã cổ phiếu (ví dụ: AAPL, MSFT, VNINDEX)
        start_date: Ngày bắt đầu (YYYY-MM-DD)
        end_date  : Ngày kết thúc (YYYY-MM-DD)

    Returns:
        DataFrame đã chuẩn hoá cột, lọc theo ngày và sắp xếp tăng dần theo 'Date'.

    Raises:
        FileNotFoundError: Nếu không tìm thấy file CSV trong notebooks/data
        ValueError       : Nếu dữ liệu không hợp lệ hoặc khoảng ngày rỗng
    """
    # Chuẩn hoá input
    symbol = normalize_symbol(symbol)
    validate_date_range(start_date, end_date)

    csv_path = _resolve_csv_path(symbol)
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy dữ liệu cho mã {symbol}. "
            f"Vui lòng kiểm tra file: {csv_path}"
        )

    try:
        # Đọc CSV
        df = pd.read_csv(csv_path)

        # Chuẩn hoá schema về định dạng chuẩn của dự án
        df = _standardize_schema(df, symbol)

        # Parse datetime
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        # Loại bỏ dòng lệch schema
        df = df.dropna(subset=["Date", "Close"]).copy()

        # Lọc theo khoảng ngày
        start_dt = parse_date(start_date)
        end_dt = parse_date(end_date)

        df = df[(df["Date"] >= start_dt) & (df["Date"] <= end_dt)].copy()
        if df.empty:
            raise ValueError(
                f"Không có dữ liệu cho mã {symbol} trong khoảng ngày {start_date} → {end_date}"
            )

        # Sắp xếp và reset index
        df = df.sort_values("Date").reset_index(drop=True)

        # Validate chất lượng dữ liệu cơ bản
        _validate_data_quality(df, symbol)

        return df

    except pd.errors.EmptyDataError:
        raise ValueError(f"File CSV rỗng hoặc không có dữ liệu hợp lệ: {csv_path}")
    except pd.errors.ParserError as e:
        raise ValueError(f"Lỗi parse CSV {csv_path.name}: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Lỗi khi tải dữ liệu từ Yahoo Finance: {e}")

    # Kiểm tra kết quả
    if df is None or df.empty:
        raise ValueError(f"Không tìm thấy dữ liệu cho mã '{symbol}' trong khoảng {start_date} đến {end_date}.")

def get_available_symbols() -> List[str]:
    """
    Lấy danh sách mã có sẵn trong notebooks/data.
    Ưu tiên file pattern '*_cleaned.csv'. Nếu không có, lấy tất cả '*.csv'.

    Returns:
        Danh sách symbol (IN HOA) đã suy ra từ tên file.
    """
    if not DATA_DIR.exists():
        return []

    cleaned = list(DATA_DIR.glob("*_cleaned.csv"))
    targets = cleaned if cleaned else list(DATA_DIR.glob("*.csv"))

    symbols = []
    for p in targets:
        sym = _symbol_from_filename(p.name)
        if sym:
            symbols.append(sym)

    return sorted(set(symbols))


def get_data_info(symbol: str) -> Dict:
    """
    Lấy thông tin tổng quan về dữ liệu một mã (từ toàn bộ file, không lọc ngày).

    Returns:
        {
            'symbol': str,
            'total_days': int,
            'start_date': 'YYYY-MM-DD',
            'end_date': 'YYYY-MM-DD',
            'highest_price': float,
            'lowest_price': float,
            'avg_volume': float
        }
        Hoặc {} nếu lỗi.
    """
    symbol = normalize_symbol(symbol)
    csv_path = _resolve_csv_path(symbol)
    if not csv_path.exists():
        return {}

    try:
        df = pd.read_csv(csv_path)
        df = _standardize_schema(df, symbol)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date", "Close"]).copy()

        return {
            "symbol": symbol,
            "total_days": int(len(df)),
            "start_date": df["Date"].min().strftime("%Y-%m-%d"),
            "end_date": df["Date"].max().strftime("%Y-%m-%d"),
            "highest_price": float(df["High"].max()) if "High" in df.columns else float(df["Close"].max()),
            "lowest_price": float(df["Low"].min()) if "Low" in df.columns else float(df["Close"].min()),
            "avg_volume": float(df["Volume"].mean()) if "Volume" in df.columns else 0.0,
        }
    except Exception:
        return {}


# ---------- Internal helpers ----------

def _resolve_csv_path(symbol: str) -> Path:
    """
    Tìm file CSV tương ứng với symbol trong notebooks/data theo thứ tự ưu tiên:
    1) {symbol_lower}_cleaned.csv
    2) {symbol_upper}_cleaned.csv
    3) {symbol_lower}.csv
    4) {symbol_upper}.csv
    """
    candidates = [
        DATA_DIR / f"{symbol.lower()}_cleaned.csv",
        DATA_DIR / f"{symbol.upper()}_cleaned.csv",
        DATA_DIR / f"{symbol.lower()}.csv",
        DATA_DIR / f"{symbol.upper()}.csv",
    ]
    for p in candidates:
        if p.exists():
            return p
    # Nếu không khớp đúng, thử quét toàn bộ để bắt các tên đặc thù (vd: 'aapl_cleaned_v1.csv')
    for p in DATA_DIR.glob("*.csv"):
        if p.stem.lower().startswith(symbol.lower()):
            return p
    # Trả về path ưu tiên đầu tiên (để hiển thị thông báo chuẩn)
    return candidates[0]


def _symbol_from_filename(filename: str) -> Optional[str]:
    """
    Suy ra symbol từ tên file CSV trong notebooks/data.
    Ví dụ:
      - aapl_cleaned.csv  -> AAPL
      - msft.csv          -> MSFT
      - vnindex_cleaned_v2.csv -> VNINDEX
    """
    name = filename.lower().replace(".csv", "")
    # Cắt hậu tố phổ biến
    for suffix in ["_cleaned", "_clean", "_v1", "_v2", "_v3"]:
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    # Lấy token đầu tiên trước dấu gạch dưới nếu còn
    base = name.split("_")[0]
    if base and base.isalnum():
        return base.upper()
    return None


def _standardize_schema(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """
    Chuẩn hoá tên cột về schema chuẩn dự án:
        Date, Symbol, Open, High, Low, Close, Volume
    - Hỗ trợ input lowercase: date/open/high/low/close/volume
    - Nếu thiếu Symbol: tự thêm bằng mã truyền vào
    - Giữ lại các cột thừa (Value, Market_Cap, Change, ...) nếu có

    Returns:
        DataFrame đã rename cột + sắp xếp cột chuẩn (nếu đủ)
    """
    # Map lowercase -> TitleCase
    rename_map = {
        "date": "Date",
        "datetime": "Date",
        "timestamp": "Date",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "adj close": "Close",
        "adjusted close": "Close",
        "close/last": "Close",
        "close price": "Close",
        "close*": "Close",
        "volume": "Volume",
        "symbol": "Symbol",
        # một số cột extra giữ nguyên nhưng chuẩn hoá tên cho đẹp
        "market_cap": "Market_Cap",
        "value": "Value",
        "change": "Change",
    }

    # Tạo dict rename theo thực tế cột
    actual_rename = {}
    for col in df.columns:
        key = col.strip().lower()
        if key in rename_map:
            actual_rename[col] = rename_map[key]

    df = df.rename(columns=actual_rename)

    # Bắt buộc phải có Date & Close
    if "Date" not in df.columns or "Close" not in df.columns:
        raise ValueError("Dataset thiếu cột bắt buộc 'Date' hoặc 'Close' sau khi chuẩn hoá.")

    # Thêm Symbol nếu thiếu
    if "Symbol" not in df.columns:
        df["Symbol"] = symbol

    # Chuyển numeric cột giá/volume nếu cần
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace("$", "", regex=False)
                .str.replace("%", "", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Sắp xếp lại cột nếu đủ
    ordered_cols = ["Date", "Symbol", "Open", "High", "Low", "Close", "Volume"]
    front = [c for c in ordered_cols if c in df.columns]
    back = [c for c in df.columns if c not in front]
    df = df[front + back]

    return df


def _validate_data_quality(df: pd.DataFrame, symbol: str) -> None:
    """
    Kiểm tra chất lượng dữ liệu cơ bản:
    - Không null ở Date/Close
    - Giá > 0
    - Logic OHLC: High >= Open/Close/Low và Low <= Open/Close
    - Volume không âm (nếu có)
    """
    # Null check
    nulls = df[["Date", "Close"]].isnull().sum()
    if nulls.any():
        raise ValueError(f"Dữ liệu {symbol} có giá trị null ở cột: "
                         + ", ".join(nulls[nulls > 0].index.tolist()))

    # Giá âm/0
    for col in ["Open", "High", "Low", "Close"]:
        if col in df.columns and (df[col] <= 0).any():
            raise ValueError(f"Dữ liệu {symbol} có giá âm hoặc bằng 0 ở cột {col}")

    # Volume âm
    if "Volume" in df.columns and (df["Volume"] < 0).any():
        raise ValueError(f"Dữ liệu {symbol} có Volume âm")

    # Logic OHLC nếu đủ cột
    if set(["High", "Low", "Open", "Close"]).issubset(df.columns):
        if (df["High"] < df["Low"]).any():
            raise ValueError(f"Dữ liệu {symbol} có High < Low")
        if (df["High"] < df["Open"]).any():
            raise ValueError(f"Dữ liệu {symbol} có High < Open")
        if (df["High"] < df["Close"]).any():
            raise ValueError(f"Dữ liệu {symbol} có High < Close")
        if (df["Low"] > df["Open"]).any():
            raise ValueError(f"Dữ liệu {symbol} có Low > Open")
        if (df["Low"] > df["Close"]).any():
            raise ValueError(f"Dữ liệu {symbol} có Low > Close")
