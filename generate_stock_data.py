"""
Tạo dữ liệu giả lập giá cổ phiếu "như thật" cho 12 mã cổ phiếu
Sử dụng thuật toán kết hợp Random Walk + Sine Wave + Noise + Shock
"""

import numpy as np
import pandas as pd
import os
import argparse
from datetime import date


def generate_stock(symbol: str, base_price: float, trend_strength: float, volatility: float, days: int = 150):
    """
    Tạo dữ liệu giá cổ phiếu giả lập với dao động tự nhiên
    
    Args:
        symbol: Mã cổ phiếu
        base_price: Giá cơ sở ban đầu
        trend_strength: Độ mạnh xu hướng tăng
        volatility: Độ biến động (0.01 = 1%)
        days: Số ngày giao dịch
        
    Returns:
        DataFrame với cấu trúc: Date,Symbol,Open,High,Low,Close,Volume
    """
    # Set random seed để có thể reproduce
    np.random.seed(hash(symbol) % 2**32)
    
    # Tạo ngày giao dịch (150 ngày gần nhất)
    dates = pd.date_range(end=date.today(), periods=days)
    
    # Xu hướng tăng nhẹ theo thời gian
    trend = np.linspace(0, trend_strength, days)
    
    # Sóng dao động (tạo nhịp tăng giảm)
    wave = 2.5 * np.sin(np.linspace(0, 5 * np.pi, days))
    
    # Nhiễu ngẫu nhiên
    noise = np.random.normal(0, 1.2, days)
    
    # Kết hợp để tạo giá Close ban đầu
    close_prices = base_price + trend + wave + noise
    
    # Random walk để tạo dao động tự nhiên
    for i in range(1, len(close_prices)):
        daily_return = np.random.normal(0.0005, volatility)
        close_prices[i] = close_prices[i - 1] * (1 + daily_return)
    
    # Thêm cú shock (giảm/tăng mạnh bất ngờ)
    if days > 40:  # Chỉ thêm shock nếu có đủ dữ liệu
        shock_count = min(3, days // 50)
        shock_days = np.random.choice(range(30, days - 10), shock_count, replace=False)
        for d in shock_days:
            shock_factor = np.random.choice([0.93, 1.07])  # -7% hoặc +7%
            close_prices[d] *= shock_factor
    
    # Sinh các giá còn lại
    open_prices = close_prices * (1 + np.random.normal(0, 0.002, days))
    high_prices = np.maximum(open_prices, close_prices) * (1 + np.random.uniform(0.002, 0.01, days))
    low_prices = np.minimum(open_prices, close_prices) * (1 - np.random.uniform(0.002, 0.01, days))
    
    # Volume: dao động theo độ biến động giá
    daily_change = np.abs(np.diff(np.insert(close_prices, 0, close_prices[0])))
    vol_factor = (daily_change - np.min(daily_change)) / (np.ptp(daily_change) + 1e-6)
    base_volume = np.random.randint(1_000_000, 6_000_000, days)
    volume = (base_volume * (0.8 + 0.4 * vol_factor)).astype(int)
    
    # Tạo DataFrame
    df = pd.DataFrame({
        "Date": dates.strftime("%Y-%m-%d"),
        "Symbol": symbol,
        "Open": np.round(open_prices, 2),
        "High": np.round(high_prices, 2),
        "Low": np.round(low_prices, 2),
        "Close": np.round(close_prices, 2),
        "Volume": volume
    })
    
    # Đảm bảo logic giá hợp lý
    df["Low"] = np.minimum(df["Low"], df[["Open", "Close"]].min(axis=1))
    df["High"] = np.maximum(df["High"], df[["Open", "Close"]].max(axis=1))
    df["Low"] = df["Low"].clip(lower=1)
    
    return df


def plot_all_stocks(stocks_data: dict):
    """
    Vẽ biểu đồ giá của tất cả mã cổ phiếu
    
    Args:
        stocks_data: Dictionary chứa DataFrame của các mã
    """
    try:
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(15, 8))
        
        colors = plt.cm.tab20(np.linspace(0, 1, len(stocks_data)))
        
        for i, (symbol, df) in enumerate(stocks_data.items()):
            plt.plot(df["Date"], df["Close"], label=symbol, 
                    color=colors[i], linewidth=1.5, alpha=0.8)
        
        plt.title("Biểu đồ giá giả lập 12 mã cổ phiếu", fontsize=16, fontweight='bold')
        plt.xlabel("Ngày")
        plt.ylabel("Giá (VNĐ)")
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        
    except ImportError:
        print("⚠️ Matplotlib không được cài đặt. Bỏ qua việc vẽ biểu đồ.")


def main():
    """Hàm chính"""
    parser = argparse.ArgumentParser(description="Tạo dữ liệu giả lập cho 12 mã cổ phiếu")
    parser.add_argument("--plot", action="store_true", help="Vẽ biểu đồ preview")
    parser.add_argument("--days", type=int, default=150, help="Số ngày giao dịch (mặc định: 150)")
    args = parser.parse_args()
    
    # Tạo thư mục data nếu chưa có
    os.makedirs("data", exist_ok=True)
    
    # Tham số cho từng mã cổ phiếu (Symbol, Base, Trend, Volatility)
    stocks_config = {
        "FPT": (90, 3.0, 0.013),    # ổn định, tăng đều
        "VNM": (70, 2.0, 0.018),    # dao động trung bình
        "VIC": (52, 1.5, 0.022),    # biến động mạnh
        "HPG": (38, 2.5, 0.020),    # sóng trung bình
        "MWG": (40, 1.8, 0.021),    # dao động ngắn
        "VCB": (95, 3.5, 0.012),    # tăng ổn định
        "SSI": (32, 2.2, 0.024),    # tăng/giảm thất thường
        "PNJ": (90, 3.2, 0.017),    # sóng nhẹ
        "GAS": (85, 1.2, 0.019),    # có shock giảm
        "VHM": (50, 2.8, 0.015),    # ổn định nhẹ
        "STB": (32, 2.0, 0.023),    # dao động mạnh
        "BVH": (47, 1.5, 0.018),    # trung bình
    }
    
    print("🚀 Bắt đầu tạo dữ liệu giả lập cho 12 mã cổ phiếu...")
    print(f"📅 Số ngày giao dịch: {args.days}")
    print()
    
    stocks_data = {}
    
    # Tạo dữ liệu cho từng mã
    for symbol, (base_price, trend_strength, volatility) in stocks_config.items():
        print(f"📈 Tạo dữ liệu cổ phiếu {symbol} ({args.days} ngày)")
        df = generate_stock(symbol, base_price, trend_strength, volatility, args.days)
        
        # Ghi file CSV
        path = f"data/{symbol}.csv"
        df.to_csv(path, index=False)
        print(f"✅ Đã tạo: {path} ({len(df)} dòng)")
        
        # Lưu để plot sau
        stocks_data[symbol] = df
    
    print()
    print("✅ Đã tạo dữ liệu giả lập cho tất cả 12 mã cổ phiếu")
    
    # Hiển thị thống kê tổng quan
    print("\n📊 Thống kê tổng quan:")
    for symbol, df in stocks_data.items():
        final_price = df['Close'].iloc[-1]
        avg_volume = df['Volume'].mean()
        price_change = ((final_price - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
        print(f"{symbol:4s}: {final_price:6.2f} VNĐ ({price_change:+5.1f}%), Volume TB: {avg_volume:,.0f}")
    
    # Vẽ biểu đồ nếu có flag --plot
    if args.plot:
        print("\n📈 Vẽ biểu đồ preview...")
        plot_all_stocks(stocks_data)
    
    print("\n🎉 Hoàn thành! Dữ liệu sẵn sàng sử dụng với Streamlit app.")
    print("📁 Các file CSV đã được tạo trong thư mục data/")


if __name__ == "__main__":
    main()