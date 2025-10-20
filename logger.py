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


def _add_summary_chart_to_pdf(pdf, records):
    """Thêm biểu đồ tổng quan vào PDF"""
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')
        from io import BytesIO
        import tempfile
        import os
        
        # Tạo biểu đồ phân bố tín hiệu
        signals = [r.get('signal', 'HOLD') for r in records]
        signal_counts = {'BUY': signals.count('BUY'), 'SELL': signals.count('SELL'), 'HOLD': signals.count('HOLD')}
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Biểu đồ tín hiệu
        ax1.pie(signal_counts.values(), labels=signal_counts.keys(), autopct='%1.1f%%', startangle=90)
        ax1.set_title('Phan bo tin hieu')
        
        # Biểu đồ giá
        symbols = [r.get('symbol', '') for r in records]
        prices = [r.get('latest_price', 0) for r in records]
        ax2.bar(symbols, prices)
        ax2.set_title('Gia hien tai cac ma')
        ax2.set_ylabel('Gia (USD)')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        # Lưu biểu đồ vào file tạm
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            plt.savefig(tmp_file.name, dpi=150, bbox_inches='tight')
            tmp_path = tmp_file.name
        
        # Thêm vào PDF
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "BIEU DO TONG QUAN", ln=True, align="C")
        pdf.image(tmp_path, x=20, w=170)
        
        # Xóa file tạm
        os.unlink(tmp_path)
        plt.close()
        
    except Exception as e:
        print(f"Lỗi tạo biểu đồ tổng quan: {e}")


def _add_stock_chart_to_pdf(pdf, symbol, record):
    """Thêm biểu đồ cho từng mã cổ phiếu vào PDF"""
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')
        import tempfile
        import os
        from data_service import get_stock_data
        from indicators import add_indicators
        from datetime import datetime, timedelta
        
        # Lấy dữ liệu 30 ngày gần nhất
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        df = get_stock_data(symbol, start_date, end_date)
        if df.empty or len(df) < 5:
            return
            
        df_with_indicators = add_indicators(df)
        
        # Tạo biểu đồ
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Vẽ giá Close và SMA
        ax.plot(df_with_indicators.index, df_with_indicators['Close'], label='Gia Close', linewidth=2)
        if 'SMA7' in df_with_indicators.columns:
            ax.plot(df_with_indicators.index, df_with_indicators['SMA7'], label='SMA7', alpha=0.7)
        if 'SMA30' in df_with_indicators.columns:
            ax.plot(df_with_indicators.index, df_with_indicators['SMA30'], label='SMA30', alpha=0.7)
        
        ax.set_title(f'Bieu do gia {symbol}')
        ax.set_ylabel('Gia (USD)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Lưu biểu đồ vào file tạm
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            plt.savefig(tmp_file.name, dpi=150, bbox_inches='tight')
            tmp_path = tmp_file.name
        
        # Thêm vào PDF
        pdf.ln(5)
        pdf.image(tmp_path, x=20, w=170)
        
        # Xóa file tạm
        os.unlink(tmp_path)
        plt.close()
        
    except Exception as e:
        print(f"Lỗi tạo biểu đồ cho {symbol}: {e}")


def _get_latest_records_by_symbol(records):
    """
    Lấy bản ghi mới nhất cho mỗi mã cổ phiếu
    
    Args:
        records: Danh sách tất cả bản ghi
        
    Returns:
        Danh sách bản ghi mới nhất cho mỗi mã
    """
    symbol_records = {}
    
    for record in records:
        symbol = record.get('symbol', '')
        if not symbol:
            continue
            
        # Nếu chưa có hoặc bản ghi này mới hơn
        if symbol not in symbol_records:
            symbol_records[symbol] = record
        else:
            # So sánh thời gian generated_at
            current_time = record.get('generated_at', '')
            existing_time = symbol_records[symbol].get('generated_at', '')
            
            if current_time > existing_time:
                symbol_records[symbol] = record
    
    return list(symbol_records.values())


def export_today_report(fmt="both"):
    """
    Xuất báo cáo hôm nay ra CSV và/hoặc PDF
    
    Args:
        fmt: Định dạng xuất ("csv", "pdf", "both")
        
    Returns:
        Chuỗi thông báo kết quả
    """
    report_dir = get_config("REPORT_DIR", "reports")
    export_dir = get_config("EXPORT_DIR", "export")
    
    # Tạo thư mục export nếu chưa có
    os.makedirs(export_dir, exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    json_file = f"{report_dir}/{today}.json"

    if not os.path.exists(json_file):
        return f"Không tìm thấy log ngày {today}."

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("records", [])
    if not records:
        return f"Không có bản ghi nào trong ngày {today}."

    # Lấy bản ghi mới nhất cho mỗi mã cổ phiếu
    latest_records = _get_latest_records_by_symbol(records)
    df = pd.DataFrame(latest_records)
    
    output_text = []

    if fmt in ["csv", "both"]:
        csv_path = f"{export_dir}/{today}_report.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        output_text.append(f"📄 Đã xuất CSV: {csv_path}")

    if fmt in ["pdf", "both"]:
        try:
            from fpdf import FPDF
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            from io import BytesIO
            import base64

            pdf_path = f"{export_dir}/{today}_report.pdf"
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, f"BAO CAO PHAN TICH CO PHIEU {today}", ln=True, align="C")

            pdf.set_font("Arial", size=11)
            
            # Thống kê tổng quan
            pdf.cell(0, 8, f"Tong so ma co phieu: {len(latest_records)}", ln=True)
            pdf.cell(0, 8, f"Ngay tao bao cao: {today}", ln=True)
            pdf.ln(5)
            
            # Chuyển đổi các ký tự tiếng Việt thành ASCII
            def to_ascii(text):
                if not text:
                    return ""
                replacements = {
                    'á': 'a', 'à': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
                    'ă': 'a', 'ắ': 'a', 'ằ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
                    'â': 'a', 'ấ': 'a', 'ầ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
                    'é': 'e', 'è': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
                    'ê': 'e', 'ế': 'e', 'ề': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
                    'í': 'i', 'ì': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
                    'ó': 'o', 'ò': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
                    'ô': 'o', 'ố': 'o', 'ồ': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
                    'ơ': 'o', 'ớ': 'o', 'ờ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
                    'ú': 'u', 'ù': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
                    'ư': 'u', 'ứ': 'u', 'ừ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
                    'ý': 'y', 'ỳ': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
                    'đ': 'd',
                    'Á': 'A', 'À': 'A', 'Ả': 'A', 'Ã': 'A', 'Ạ': 'A',
                    'Ă': 'A', 'Ắ': 'A', 'Ằ': 'A', 'Ẳ': 'A', 'Ẵ': 'A', 'Ặ': 'A',
                    'Â': 'A', 'Ấ': 'A', 'Ầ': 'A', 'Ẩ': 'A', 'Ẫ': 'A', 'Ậ': 'A',
                    'É': 'E', 'È': 'E', 'Ẻ': 'E', 'Ẽ': 'E', 'Ẹ': 'E',
                    'Ê': 'E', 'Ế': 'E', 'Ề': 'E', 'Ể': 'E', 'Ễ': 'E', 'Ệ': 'E',
                    'Í': 'I', 'Ì': 'I', 'Ỉ': 'I', 'Ĩ': 'I', 'Ị': 'I',
                    'Ó': 'O', 'Ò': 'O', 'Ỏ': 'O', 'Õ': 'O', 'Ọ': 'O',
                    'Ô': 'O', 'Ố': 'O', 'Ồ': 'O', 'Ổ': 'O', 'Ỗ': 'O', 'Ộ': 'O',
                    'Ơ': 'O', 'Ớ': 'O', 'Ờ': 'O', 'Ở': 'O', 'Ỡ': 'O', 'Ợ': 'O',
                    'Ú': 'U', 'Ù': 'U', 'Ủ': 'U', 'Ũ': 'U', 'Ụ': 'U',
                    'Ư': 'U', 'Ứ': 'U', 'Ừ': 'U', 'Ử': 'U', 'Ữ': 'U', 'Ự': 'U',
                    'Ý': 'Y', 'Ỳ': 'Y', 'Ỷ': 'Y', 'Ỹ': 'Y', 'Ỵ': 'Y',
                    'Đ': 'D'
                }
                result = text
                for viet, ascii in replacements.items():
                    result = result.replace(viet, ascii)
                return result
            
            # Tạo biểu đồ tổng quan (chỉ khi có đủ số lượng mã)
            min_symbols_for_chart = int(get_config("MIN_SYMBOLS_FOR_CHART", "2"))
            if len(latest_records) >= min_symbols_for_chart:
                _add_summary_chart_to_pdf(pdf, latest_records)
            else:
                pdf.ln(5)
                pdf.set_font("Arial", "I", 10)
                pdf.cell(0, 8, f"Khong ve bieu do tong quan (can it nhat {min_symbols_for_chart} ma, hien co {len(latest_records)} ma)", ln=True, align="C")
            
            # Chi tiết từng mã cổ phiếu
            for i, record in enumerate(latest_records, 1):
                symbol = record.get('symbol', '')
                price = record.get('latest_price', '')
                trend = record.get('trend', '')
                signal = record.get('signal', '')
                reason = record.get('reason', '')
                ai_advice = record.get('ai_advice', '')
                generated_at = record.get('generated_at', '')
                
                # Tiêu đề cho mỗi mã
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 8, f"[{i}] MA CO PHIEU: {to_ascii(symbol)}", ln=True)
                
                # Chi tiết
                pdf.set_font("Arial", size=10)
                text = f"""
Gia hien tai: ${price:,.2f}
Xu huong: {to_ascii(trend)}
Tin hieu: {to_ascii(signal)}
Ly do: {to_ascii(reason)}
AI tu van: {to_ascii(ai_advice)}
Thoi gian phan tich: {generated_at}
"""
                pdf.multi_cell(0, 6, text)
                pdf.ln(3)
                
                # Thêm biểu đồ cho mã này nếu có dữ liệu
                _add_stock_chart_to_pdf(pdf, symbol, record)
                
                # Ngắt trang nếu cần
                if i % 2 == 0 and i < len(latest_records):
                    pdf.add_page()

            pdf.output(pdf_path)
            output_text.append(f"📘 Đã xuất PDF: {pdf_path}")
        except ImportError:
            output_text.append("❌ Không thể xuất PDF: thiếu thư viện fpdf")
        except Exception as e:
            output_text.append(f"❌ Lỗi tạo PDF: {str(e)}")

    return "\n".join(output_text)


# Import cần thiết cho các hàm
from datetime import timedelta
