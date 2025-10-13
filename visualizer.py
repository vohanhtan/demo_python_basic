"""
Module vẽ biểu đồ giá cổ phiếu
Sử dụng matplotlib để tạo biểu đồ hiển thị giá đóng cửa và các đường trung bình động
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List


def make_price_chart(df: pd.DataFrame, symbol: str, forecast_days: Optional[List[float]] = None) -> plt.Figure:
    """
    Tạo biểu đồ giá cổ phiếu với các đường trung bình động
    
    Args:
        df: DataFrame chứa dữ liệu giá với các chỉ báo
        symbol: Mã cổ phiếu
        forecast_days: Danh sách giá dự đoán (tùy chọn)
        
    Returns:
        matplotlib Figure object
    """
    if df.empty:
        raise ValueError("DataFrame rỗng, không thể tạo biểu đồ")
    
    # Tạo figure và axis
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Vẽ đường giá đóng cửa
    ax.plot(df['Date'], df['Close'], label='Giá đóng cửa', 
            color='#1f77b4', linewidth=2, alpha=0.8)
    
    # Vẽ SMA7 nếu có
    if 'SMA7' in df.columns:
        ax.plot(df['Date'], df['SMA7'], label='SMA(7)', 
                color='#ff7f0e', linewidth=1.5, alpha=0.7)
    
    # Vẽ SMA30 nếu có
    if 'SMA30' in df.columns:
        ax.plot(df['Date'], df['SMA30'], label='SMA(30)', 
                color='#2ca02c', linewidth=1.5, alpha=0.7)
    
    # Vẽ dự đoán nếu có
    if forecast_days:
        _add_forecast_to_chart(ax, df, forecast_days)
    
    # Cấu hình biểu đồ
    _configure_chart(ax, symbol, df)
    
    # Thêm grid và legend
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left')
    
    plt.tight_layout()
    return fig


def _add_forecast_to_chart(ax: plt.Axes, df: pd.DataFrame, forecast_days: List[float]) -> None:
    """
    Thêm đường dự đoán vào biểu đồ
    
    Args:
        ax: matplotlib Axes object
        df: DataFrame dữ liệu
        forecast_days: Danh sách giá dự đoán
    """
    if not forecast_days:
        return
    
    # Tạo ngày cho dự đoán
    last_date = df['Date'].iloc[-1]
    forecast_dates = []
    
    for i in range(1, len(forecast_days) + 1):
        # Bỏ qua cuối tuần (giả sử thị trường chỉ mở T2-T6)
        next_date = last_date + timedelta(days=i)
        while next_date.weekday() >= 5:  # Thứ 7 = 5, Chủ nhật = 6
            next_date += timedelta(days=1)
        forecast_dates.append(next_date)
    
    # Vẽ đường dự đoán
    ax.plot(forecast_dates, forecast_days, label='Dự đoán', 
            color='#d62728', linewidth=2, linestyle='--', alpha=0.8)
    
    # Đánh dấu điểm cuối
    ax.scatter(forecast_dates[-1], forecast_days[-1], 
              color='#d62728', s=50, zorder=5)


def _configure_chart(ax: plt.Axes, symbol: str, df: pd.DataFrame) -> None:
    """
    Cấu hình biểu đồ
    
    Args:
        ax: matplotlib Axes object
        symbol: Mã cổ phiếu
        df: DataFrame dữ liệu
    """
    # Tiêu đề
    ax.set_title(f'Biểu đồ giá cổ phiếu {symbol}', fontsize=16, fontweight='bold', pad=20)
    
    # Nhãn trục
    ax.set_xlabel('Ngày', fontsize=12)
    ax.set_ylabel('Giá (VND)', fontsize=12)
    
    # Định dạng trục x (ngày)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    # Định dạng trục y (giá)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(_format_price))
    
    # Thiết lập giới hạn trục
    _set_axis_limits(ax, df)


def _format_price(value: float, pos: int) -> str:
    """
    Format giá để hiển thị trên trục y
    
    Args:
        value: Giá trị cần format
        pos: Vị trí (không sử dụng)
        
    Returns:
        Chuỗi giá đã format
    """
    if value >= 1000:
        return f'{value/1000:.1f}K'
    else:
        return f'{value:.0f}'


def _set_axis_limits(ax: plt.Axes, df: pd.DataFrame) -> None:
    """
    Thiết lập giới hạn trục x và y
    
    Args:
        ax: matplotlib Axes object
        df: DataFrame dữ liệu
    """
    # Giới hạn trục x
    if len(df) > 0:
        date_range = (df['Date'].min(), df['Date'].max())
        ax.set_xlim(date_range)
    
    # Giới hạn trục y với margin
    if len(df) > 0:
        price_min = df['Close'].min()
        price_max = df['Close'].max()
        
        # Thêm margin 5%
        margin = (price_max - price_min) * 0.05
        ax.set_ylim(price_min - margin, price_max + margin)


def create_rsi_chart(df: pd.DataFrame, symbol: str) -> plt.Figure:
    """
    Tạo biểu đồ RSI riêng biệt
    
    Args:
        df: DataFrame chứa dữ liệu với cột RSI14
        symbol: Mã cổ phiếu
        
    Returns:
        matplotlib Figure object
    """
    if 'RSI14' not in df.columns:
        raise ValueError("DataFrame thiếu cột RSI14")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Vẽ đường RSI
    ax.plot(df['Date'], df['RSI14'], label='RSI(14)', 
            color='#9467bd', linewidth=2)
    
    # Vẽ đường ngưỡng
    ax.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Quá mua (70)')
    ax.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='Quá bán (30)')
    ax.axhline(y=50, color='gray', linestyle='-', alpha=0.5, label='Trung tính (50)')
    
    # Tô màu vùng quá mua/quá bán
    ax.fill_between(df['Date'], 70, 100, alpha=0.1, color='red', label='Vùng quá mua')
    ax.fill_between(df['Date'], 0, 30, alpha=0.1, color='green', label='Vùng quá bán')
    
    # Cấu hình biểu đồ
    ax.set_title(f'Chỉ báo RSI - {symbol}', fontsize=14, fontweight='bold')
    ax.set_xlabel('Ngày', fontsize=12)
    ax.set_ylabel('RSI', fontsize=12)
    ax.set_ylim(0, 100)
    
    # Định dạng trục x
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    return fig


def create_volume_chart(df: pd.DataFrame, symbol: str) -> plt.Figure:
    """
    Tạo biểu đồ volume
    
    Args:
        df: DataFrame chứa dữ liệu với cột Volume
        symbol: Mã cổ phiếu
        
    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Vẽ cột volume
    ax.bar(df['Date'], df['Volume'], alpha=0.7, color='lightblue', width=0.8)
    
    # Cấu hình biểu đồ
    ax.set_title(f'Khối lượng giao dịch - {symbol}', fontsize=14, fontweight='bold')
    ax.set_xlabel('Ngày', fontsize=12)
    ax.set_ylabel('Volume', fontsize=12)
    
    # Định dạng trục x
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    # Định dạng trục y
    ax.yaxis.set_major_formatter(plt.FuncFormatter(_format_volume))
    
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    return fig


def _format_volume(value: float, pos: int) -> str:
    """
    Format volume để hiển thị
    
    Args:
        value: Giá trị volume
        pos: Vị trí (không sử dụng)
        
    Returns:
        Chuỗi volume đã format
    """
    if value >= 1e6:
        return f'{value/1e6:.1f}M'
    elif value >= 1e3:
        return f'{value/1e3:.0f}K'
    else:
        return f'{value:.0f}'


def create_combined_chart(df: pd.DataFrame, symbol: str, forecast_days: Optional[List[float]] = None) -> plt.Figure:
    """
    Tạo biểu đồ kết hợp: giá + RSI + Volume
    
    Args:
        df: DataFrame chứa dữ liệu
        symbol: Mã cổ phiếu
        forecast_days: Danh sách giá dự đoán (tùy chọn)
        
    Returns:
        matplotlib Figure object
    """
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12), 
                                        gridspec_kw={'height_ratios': [3, 1, 1]})
    
    # Biểu đồ giá (trên cùng)
    ax1.plot(df['Date'], df['Close'], label='Giá đóng cửa', 
            color='#1f77b4', linewidth=2)
    
    if 'SMA7' in df.columns:
        ax1.plot(df['Date'], df['SMA7'], label='SMA(7)', 
                color='#ff7f0e', linewidth=1.5, alpha=0.7)
    
    if 'SMA30' in df.columns:
        ax1.plot(df['Date'], df['SMA30'], label='SMA(30)', 
                color='#2ca02c', linewidth=1.5, alpha=0.7)
    
    if forecast_days:
        _add_forecast_to_chart(ax1, df, forecast_days)
    
    ax1.set_title(f'Phân tích kỹ thuật {symbol}', fontsize=16, fontweight='bold')
    ax1.set_ylabel('Giá (VND)', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left')
    
    # Biểu đồ RSI (giữa)
    if 'RSI14' in df.columns:
        ax2.plot(df['Date'], df['RSI14'], color='#9467bd', linewidth=2)
        ax2.axhline(y=70, color='red', linestyle='--', alpha=0.7)
        ax2.axhline(y=30, color='green', linestyle='--', alpha=0.7)
        ax2.axhline(y=50, color='gray', linestyle='-', alpha=0.5)
        ax2.fill_between(df['Date'], 70, 100, alpha=0.1, color='red')
        ax2.fill_between(df['Date'], 0, 30, alpha=0.1, color='green')
    
    ax2.set_ylabel('RSI', fontsize=12)
    ax2.set_ylim(0, 100)
    ax2.grid(True, alpha=0.3)
    
    # Biểu đồ Volume (dưới cùng)
    ax3.bar(df['Date'], df['Volume'], alpha=0.7, color='lightblue', width=0.8)
    ax3.set_ylabel('Volume', fontsize=12)
    ax3.set_xlabel('Ngày', fontsize=12)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Định dạng trục x cho tất cả subplot
    for ax in [ax1, ax2, ax3]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    return fig


def save_chart(fig: plt.Figure, filename: str, dpi: int = 300) -> str:
    """
    Lưu biểu đồ ra file
    
    Args:
        fig: matplotlib Figure object
        filename: Tên file (không cần extension)
        dpi: Độ phân giải (mặc định 300)
        
    Returns:
        Đường dẫn file đã lưu
    """
    from pathlib import Path
    
    # Tạo thư mục charts nếu chưa có
    charts_dir = Path(__file__).parent / "charts"
    charts_dir.mkdir(exist_ok=True)
    
    # Đường dẫn file
    file_path = charts_dir / f"{filename}.png"
    
    # Lưu file
    fig.savefig(file_path, dpi=dpi, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    return str(file_path)
