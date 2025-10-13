"""
Module ghi log JSON theo ngày
Chức năng: ghi kết quả phân tích vào file reports/YYYY-MM-DD.json
Mỗi ngày một file, gộp nhiều bản ghi trong ngày
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import pandas as pd
from utils import get_current_datetime_iso, get_config


def append_daily_log(record: Dict) -> Dict:
    """
    Ghi thêm bản ghi vào file log ngày hiện tại
    
    Args:
        record: Dictionary chứa thông tin cần ghi log với các key:
                - symbol: mã cổ phiếu
                - latest_price: giá mới nhất
                - trend: xu hướng
                - signal: tín hiệu
                - reason: lý do
                - ai_advice: lời khuyên AI
                - generated_at: thời gian tạo (tự động thêm nếu chưa có)
                
    Returns:
        Dictionary chứa:
        - file_path: đường dẫn file log
        - total_records_today: tổng số bản ghi trong ngày
    """
    # Tạo thư mục reports nếu chưa có
    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    # Tên file log theo ngày
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = reports_dir / f"{today}.json"
    
    # Đọc dữ liệu hiện có hoặc tạo mới
    daily_data = _load_daily_log(log_file)
    
    # Chuẩn bị bản ghi mới
    new_record = _prepare_log_record(record)
    
    # Thêm bản ghi mới
    daily_data['records'].append(new_record)
    
    # Ghi lại file
    _save_daily_log(log_file, daily_data)
    
    return {
        "file_path": str(log_file),
        "total_records_today": len(daily_data['records'])
    }


def _load_daily_log(log_file: Path) -> Dict:
    """
    Đọc file log ngày hiện tại
    
    Args:
        log_file: Đường dẫn file log
        
    Returns:
        Dictionary chứa dữ liệu log
    """
    if log_file.exists():
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # File bị lỗi, tạo mới
            pass
    
    # Tạo cấu trúc mới
    today = datetime.now().strftime('%Y-%m-%d')
    return {
        'date': today,
        'records': []
    }


def _save_daily_log(log_file: Path, data: Dict) -> None:
    """
    Ghi dữ liệu vào file log
    
    Args:
        log_file: Đường dẫn file log
        data: Dữ liệu cần ghi
    """
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except IOError as e:
        raise IOError(f"Không thể ghi file log: {str(e)}")


def _prepare_log_record(record: Dict) -> Dict:
    """
    Chuẩn bị bản ghi log từ dữ liệu đầu vào
    
    Args:
        record: Dữ liệu đầu vào
        
    Returns:
        Bản ghi đã chuẩn bị
    """
    # Tạo bản ghi mới
    log_record = {
        'symbol': record.get('symbol', ''),
        'latest_price': record.get('latest_price', 0),
        'trend': record.get('trend', ''),
        'signal': record.get('signal', ''),
        'reason': record.get('reason', ''),
        'ai_advice': record.get('ai_advice', ''),
        'generated_at': record.get('generated_at', get_current_datetime_iso())
    }
    
    # Thêm thông tin bổ sung nếu có
    if 'technical_indicators' in record:
        log_record['technical_indicators'] = record['technical_indicators']
    
    if 'forecast_next_days' in record:
        log_record['forecast_next_days'] = record['forecast_next_days']
    
    return log_record


def get_daily_logs(date: str = None) -> Dict:
    """
    Lấy tất cả bản ghi log của một ngày
    
    Args:
        date: Ngày cần lấy (YYYY-MM-DD), mặc định là hôm nay
        
    Returns:
        Dictionary chứa dữ liệu log của ngày
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    reports_dir = Path(__file__).parent / "reports"
    log_file = reports_dir / f"{date}.json"
    
    return _load_daily_log(log_file)


def get_log_statistics(days_back: int = 7) -> Dict:
    """
    Lấy thống kê log trong N ngày gần nhất
    
    Args:
        days_back: Số ngày lùi về trước (mặc định 7)
        
    Returns:
        Dictionary chứa thống kê
    """
    stats = {
        'total_analyses': 0,
        'symbols_analyzed': set(),
        'signals_distribution': {'BUY': 0, 'SELL': 0, 'HOLD': 0},
        'trends_distribution': {'Uptrend': 0, 'Downtrend': 0, 'Sideways': 0},
        'daily_counts': {}
    }
    
    reports_dir = Path(__file__).parent / "reports"
    
    for i in range(days_back):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        log_file = reports_dir / f"{date}.json"
        
        if log_file.exists():
            daily_data = _load_daily_log(log_file)
            records = daily_data.get('records', [])
            
            stats['daily_counts'][date] = len(records)
            stats['total_analyses'] += len(records)
            
            for record in records:
                # Thống kê symbol
                symbol = record.get('symbol', '')
                if symbol:
                    stats['symbols_analyzed'].add(symbol)
                
                # Thống kê signal
                signal = record.get('signal', '')
                if signal in stats['signals_distribution']:
                    stats['signals_distribution'][signal] += 1
                
                # Thống kê trend
                trend = record.get('trend', '')
                if trend in stats['trends_distribution']:
                    stats['trends_distribution'][trend] += 1
    
    # Chuyển set thành list
    stats['symbols_analyzed'] = list(stats['symbols_analyzed'])
    
    return stats


def cleanup_old_logs(days_to_keep: int = 30) -> int:
    """
    Dọn dẹp file log cũ
    
    Args:
        days_to_keep: Số ngày giữ lại (mặc định 30)
        
    Returns:
        Số file đã xóa
    """
    reports_dir = Path(__file__).parent / "reports"
    
    if not reports_dir.exists():
        return 0
    
    deleted_count = 0
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    
    for log_file in reports_dir.glob("*.json"):
        try:
            # Lấy ngày từ tên file
            date_str = log_file.stem
            file_date = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Xóa file cũ
            if file_date < cutoff_date:
                log_file.unlink()
                deleted_count += 1
                
        except ValueError:
            # Tên file không đúng định dạng, bỏ qua
            continue
    
    return deleted_count


def export_logs_to_csv(start_date: str, end_date: str, output_file: str = None) -> str:
    """
    Xuất logs ra file CSV
    
    Args:
        start_date: Ngày bắt đầu (YYYY-MM-DD)
        end_date: Ngày kết thúc (YYYY-MM-DD)
        output_file: Tên file output (mặc định auto-generate)
        
    Returns:
        Đường dẫn file CSV đã tạo
    """
    import pandas as pd
    from datetime import datetime, timedelta
    
    if output_file is None:
        output_file = f"stock_analysis_logs_{start_date}_to_{end_date}.csv"
    
    reports_dir = Path(__file__).parent / "reports"
    output_path = reports_dir / output_file
    
    # Thu thập dữ liệu
    all_records = []
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    current_date = start_dt
    while current_date <= end_dt:
        date_str = current_date.strftime('%Y-%m-%d')
        log_file = reports_dir / f"{date_str}.json"
        
        if log_file.exists():
            daily_data = _load_daily_log(log_file)
            for record in daily_data.get('records', []):
                record['log_date'] = date_str
                all_records.append(record)
        
        current_date += timedelta(days=1)
    
    # Tạo DataFrame và lưu CSV
    if all_records:
        df = pd.DataFrame(all_records)
        df.to_csv(output_path, index=False, encoding='utf-8')
        return str(output_path)
    else:
        raise ValueError("Không có dữ liệu log trong khoảng thời gian đã chọn")


def export_today_report(fmt="both"):
    """
    Xuất báo cáo hôm nay ra CSV và/hoặc PDF
    
    Args:
        fmt: Định dạng xuất ("csv", "pdf", "both")
        
    Returns:
        Chuỗi thông báo kết quả
    """
    report_dir = get_config("REPORT_DIR", "reports")
    today = datetime.now().strftime("%Y-%m-%d")
    json_file = f"{report_dir}/{today}.json"

    if not os.path.exists(json_file):
        return f"Không tìm thấy log ngày {today}."

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data["records"])
    output_text = []

    if fmt in ["csv", "both"]:
        csv_path = f"{report_dir}/{today}_report.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        output_text.append(f"📄 Đã xuất CSV: {csv_path}")

    if fmt in ["pdf", "both"]:
        try:
            from fpdf import FPDF

            pdf_path = f"{report_dir}/{today}_report.pdf"
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, f"BÁO CÁO PHÂN TÍCH CỔ PHIẾU {today}", ln=True, align="C")

            pdf.set_font("Arial", size=11)
            for record in data["records"]:
                pdf.multi_cell(0, 8, f"""
Mã: {record['symbol']}
Giá hiện tại: {record['latest_price']}
Xu hướng: {record['trend']}
Tín hiệu: {record['signal']}
Lý do: {record['reason']}
AI: {record['ai_advice']}
-------------------------------
""")

            pdf.output(pdf_path)
            output_text.append(f"📘 Đã xuất PDF: {pdf_path}")
        except ImportError:
            output_text.append("❌ Không thể xuất PDF: thiếu thư viện fpdf")

    return "\n".join(output_text)


# Import cần thiết cho các hàm
from datetime import timedelta
