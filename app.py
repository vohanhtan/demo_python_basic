"""
AI Stock Insight - Ứng dụng phân tích kỹ thuật và dự đoán cổ phiếu
Streamlit UI chính cho việc nhập liệu, phân tích và hiển thị kết quả
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import traceback

# Import các module của dự án
from data_service import get_stock_data, get_available_symbols, get_data_info
from indicators import add_indicators, get_latest_indicators
from predictor import forecast_price_regression
from ai_module import get_ai_advice, get_ai_confidence_score
from logger import append_daily_log
from visualizer import make_price_chart, create_combined_chart, create_candlestick_chart
from utils import (
    get_default_date_range, validate_symbol, validate_date_range,
    get_current_datetime_iso, truncate_json_for_display, normalize_symbol,
    get_config, is_data_short
)

# Import cho export functionality
from logger import export_today_report

# Session state initialization cho export button
if "export_result" not in st.session_state:
    st.session_state.export_result = ""


def main():
    """Hàm chính của ứng dụng Streamlit"""
    
    # Cấu hình trang
    st.set_page_config(
        page_title="AI Stock Insight",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Tiêu đề chính
    st.title("📈 AI Stock Insight — Phân tích kỹ thuật & Dự đoán")
    st.markdown("---")
    
    # Sidebar cho input
    with st.sidebar:
        st.header("🔧 Cài đặt phân tích")
        
        # Input mã cổ phiếu
        available_symbols = get_available_symbols()
        if available_symbols:
            symbol = st.selectbox(
                "Mã cổ phiếu",
                options=available_symbols,
                index=0 if 'FPT' in available_symbols else 0,
                help="Chọn mã cổ phiếu có sẵn trong hệ thống"
            )
        else:
            symbol = st.text_input(
                "Mã cổ phiếu",
                value="FPT",
                help="Nhập mã cổ phiếu (ví dụ: FPT, VNM)"
            )
        
        # Input khoảng ngày
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Ngày bắt đầu",
                value=datetime.now() - timedelta(days=60),
                help="Ngày bắt đầu phân tích"
            )
        
        with col2:
            end_date = st.date_input(
                "Ngày kết thúc",
                value=datetime.now(),
                help="Ngày kết thúc phân tích"
            )
        
        # Input số ngày dự đoán
        forecast_days = st.number_input(
            "Số ngày dự đoán",
            min_value=1,
            max_value=10,
            value=5,
            help="Số ngày dự đoán giá (1-10 ngày)"
        )
        
        # Nút phân tích
        analyze_button = st.button(
            "🚀 Phân tích",
            type="primary",
            width='stretch'
        )
        
        # Nút xuất báo cáo (đặt dưới nút phân tích)
        export_button = st.button(
            "📄 Xuất báo cáo hôm nay",
            key="export_today_btn",
            width='stretch'
        )
        
        # Hiển thị thông tin dữ liệu
        if symbol:
            _show_data_info(symbol)
    
    # Main content
    if analyze_button:
        _perform_analysis(symbol, start_date, end_date, forecast_days)
    elif export_button:
        _handle_export()
    else:
        _show_welcome_message()


def _show_data_info(symbol: str):
    """Hiển thị thông tin dữ liệu của mã cổ phiếu"""
    try:
        info = get_data_info(symbol)
        if info:
            st.markdown("---")
            st.subheader("📊 Thông tin dữ liệu")
            st.write(f"**Mã:** {info['symbol']}")
            st.write(f"**Số ngày:** {info['total_days']}")
            st.write(f"**Từ:** {info['start_date']}")
            st.write(f"**Đến:** {info['end_date']}")
            st.write(f"**Giá cao nhất:** {info['highest_price']:,.0f} VND")
            st.write(f"**Giá thấp nhất:** {info['lowest_price']:,.0f} VND")
            st.write(f"**Volume TB:** {info['avg_volume']:,.0f}")
    except Exception:
        pass


def _handle_export():
    """Xử lý xuất báo cáo"""
    st.subheader("📤 Xuất báo cáo hôm nay")
    
    export_format = get_config("EXPORT_FORMAT", "both")
    
    try:
        export_result = export_today_report(export_format)
        st.session_state.export_result = export_result
        st.success(export_result)
        
        # Thêm download buttons
        _show_download_buttons()
        
    except Exception as e:
        error_msg = f"❌ Lỗi xuất báo cáo: {str(e)}"
        st.session_state.export_result = error_msg
        st.error(error_msg)
    
    # Hiển thị thông tin về file log
    st.subheader("📁 Thông tin file")
    report_dir = get_config("REPORT_DIR", "reports")
    export_dir = get_config("EXPORT_DIR", "export")
    st.write(f"**Thư mục log:** `{report_dir}/`")
    st.write(f"**Thư mục export:** `{export_dir}/`")
    st.write(f"**Định dạng file:** `YYYY-MM-DD.json`")
    st.write(f"**File xuất:** `YYYY-MM-DD_report.csv/pdf`")


def _show_download_buttons():
    """Hiển thị nút download file đã export"""
    import os
    from datetime import datetime
    
    today = datetime.now().strftime("%Y-%m-%d")
    export_dir = get_config("EXPORT_DIR", "export")
    
    st.subheader("💾 Tải xuống file")
    
    # CSV download
    csv_path = f"{export_dir}/{today}_report.csv"
    if os.path.exists(csv_path):
        with open(csv_path, "rb") as f:
            csv_data = f.read()
        st.download_button(
            label="📄 Tải xuống CSV",
            data=csv_data,
            file_name=f"{today}_report.csv",
            mime="text/csv"
        )
    
    # PDF download
    pdf_path = f"{export_dir}/{today}_report.pdf"
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()
        st.download_button(
            label="📘 Tải xuống PDF",
            data=pdf_data,
            file_name=f"{today}_report.pdf",
            mime="application/pdf"
        )


def _show_welcome_message():
    """Hiển thị thông điệp chào mừng"""
    st.markdown("""
    ### 🎯 Chào mừng đến với AI Stock Insight!
    
    **Ứng dụng này giúp bạn:**
    - 📊 Phân tích kỹ thuật cổ phiếu với các chỉ báo SMA và RSI
    - 🔮 Dự đoán xu hướng ngắn hạn bằng Linear Regression
    - 🤖 Nhận lời khuyên từ AI (hiện tại là giả lập)
    - 📈 Xem biểu đồ trực quan và chi tiết
    - 📄 Xuất báo cáo CSV/PDF
    
    **Cách sử dụng:**
    1. Chọn mã cổ phiếu từ danh sách
    2. Thiết lập khoảng thời gian phân tích
    3. Nhấn nút "Phân tích" để bắt đầu
    4. Nhấn nút "Xuất báo cáo hôm nay" để xuất file
    
    **Dữ liệu mẫu có sẵn:** FPT, VNM
    """)


def _perform_analysis(symbol: str, start_date, end_date, forecast_days: int):
    """Thực hiện phân tích cổ phiếu"""
    
    # Validate input
    try:
        symbol = normalize_symbol(symbol)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        validate_date_range(start_date_str, end_date_str)
    except ValueError as e:
        st.error(f"❌ Lỗi đầu vào: {str(e)}")
        return
    
    # Hiển thị progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Bước 1: Đọc dữ liệu
        status_text.text("📥 Đang đọc dữ liệu...")
        progress_bar.progress(20)
        
        df = get_stock_data(symbol, start_date_str, end_date_str)
        
        if is_data_short(df):
            st.warning("⚠️ Dữ liệu ngắn, kết quả có thể thiếu ổn định. Một số chỉ báo có thể chưa phản ánh đúng xu hướng.")
        
        # Bước 2: Tính chỉ báo kỹ thuật
        status_text.text("📊 Đang tính chỉ báo kỹ thuật...")
        progress_bar.progress(40)
        
        df_with_indicators = add_indicators(df)
        
        # Bước 3: Dự đoán
        status_text.text("🔮 Đang dự đoán xu hướng...")
        progress_bar.progress(60)
        
        prediction = forecast_price_regression(df_with_indicators, forecast_days)
        
        # Bước 4: Tạo kết quả JSON
        status_text.text("📋 Đang tạo báo cáo...")
        progress_bar.progress(80)
        
        result_json = _create_result_json(
            symbol, start_date_str, end_date_str, 
            df_with_indicators, prediction
        )
        
        # Bước 5: Lấy lời khuyên AI
        status_text.text("🤖 Đang tạo lời khuyên AI...")
        progress_bar.progress(90)
        
        ai_advice = get_ai_advice(result_json)
        result_json['ai_advice'] = ai_advice
        
        # Bước 6: Ghi log
        status_text.text("💾 Đang lưu kết quả...")
        progress_bar.progress(95)
        
        log_result = append_daily_log(result_json)
        
        # Hoàn thành
        progress_bar.progress(100)
        status_text.text("✅ Phân tích hoàn thành!")
        
        # Hiển thị kết quả
        _display_results(result_json, df_with_indicators, log_result)
        
    except FileNotFoundError as e:
        st.error(f"❌ Không tìm thấy dữ liệu cho mã {symbol}. Kiểm tra file data/{symbol}.csv.")
        st.stop()
    except ValueError as e:
        st.error(f"❌ Lỗi dữ liệu: {str(e)}")
    except Exception as e:
        st.error(f"❌ Lỗi không xác định: {str(e)}")
        st.code(traceback.format_exc())
    finally:
        # Xóa progress
        progress_bar.empty()
        status_text.empty()


def _create_result_json(symbol: str, start_date: str, end_date: str, 
                       df: pd.DataFrame, prediction: dict) -> dict:
    """Tạo JSON kết quả theo schema chuẩn"""
    
    # Lấy chỉ báo mới nhất
    latest_indicators = get_latest_indicators(df)
    
    # Tạo JSON kết quả
    result = {
        "symbol": symbol,
        "date_range": [start_date, end_date],
        "latest_price": round(df['Close'].iloc[-1], 2),
        "technical_indicators": latest_indicators,
        "trend": prediction.get("trend", "Sideways"),
        "forecast_horizon_days": prediction.get("forecast_horizon_days", 5),
        "forecast_next_days": prediction.get("forecast_next_days", []),
        "signal": prediction.get("signal", "HOLD"),
        "reason": prediction.get("reason", ""),
        "generated_at": get_current_datetime_iso()
    }
    
    return result


def _display_results(result_json: dict, df: pd.DataFrame, log_result: dict):
    """Hiển thị kết quả phân tích"""
    
    # Thông báo log
    st.success(f"✅ Đã ghi vào {log_result['file_path']} — Tổng số hôm nay: {log_result['total_records_today']}")
    
    # Tabs cho kết quả
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Tổng quan", "📈 Biểu đồ", "📋 Kết quả JSON", "🤖 Lời khuyên AI"])
    
    with tab1:
        _show_overview(result_json, df)
    
    with tab2:
        _show_charts(result_json, df)
    
    with tab3:
        _show_json_result(result_json)
    
    with tab4:
        _show_ai_advice(result_json)


def _show_overview(result_json: dict, df: pd.DataFrame):
    """Hiển thị tổng quan kết quả"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 Giá hiện tại",
            f"{result_json['latest_price']:,.0f} VND"
        )
    
    with col2:
        trend = result_json['trend']
        trend_display = "📈 Tăng" if trend == "Uptrend" else "📉 Giảm" if trend == "Downtrend" else "➖ Đi ngang"
        st.metric("📈 Xu hướng", trend_display, delta=None)
    
    with col3:
        signal = result_json['signal']
        signal_display = "🟢 MUA" if signal == "BUY" else "🔴 BÁN" if signal == "SELL" else "⚪ GIỮ"
        st.metric("💡 Tín hiệu", signal_display, delta=None)
    
    with col4:
        from ai_module import get_market_sentiment
        sentiment = get_market_sentiment(result_json['symbol'], result_json)
        sentiment_display = "😊 Tích cực" if sentiment == "Tích cực" else "😐 Trung lập" if sentiment == "Trung lập" else "😟 Tiêu cực"
        st.metric("🧠 Sentiment", sentiment_display, delta=None)
    
    # Chỉ báo kỹ thuật
    st.subheader("📊 Chỉ báo kỹ thuật")
    indicators = result_json['technical_indicators']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'SMA7' in indicators:
            st.metric("SMA(7)", f"{indicators['SMA7']:,.2f}")
    
    with col2:
        if 'SMA30' in indicators:
            st.metric("SMA(30)", f"{indicators['SMA30']:,.2f}")
    
    with col3:
        if 'RSI14' in indicators:
            rsi = indicators['RSI14']
            rsi_status = "Quá mua" if rsi > 70 else "Quá bán" if rsi < 30 else "Bình thường"
            st.metric("RSI(14)", f"{rsi:.2f}", delta=rsi_status)
    
    # Dự đoán
    st.subheader("🔮 Dự đoán giá")
    forecast_days = result_json['forecast_next_days']
    if forecast_days:
        forecast_df = pd.DataFrame({
            'Ngày': [f"T+{i+1}" for i in range(len(forecast_days))],
            'Giá dự đoán (VND)': [f"{price:,.0f}" for price in forecast_days]
        })
        st.dataframe(forecast_df, width='stretch')
    
    # Lý do tín hiệu
    st.subheader("💡 Lý do tín hiệu")
    st.info(result_json['reason'])


def _show_charts(result_json: dict, df: pd.DataFrame):
    """Hiển thị biểu đồ"""
    
    st.subheader("📈 Biểu đồ phân tích")
    
    # Hiển thị cả 3 loại biểu đồ theo chiều dọc
    st.markdown("### 📊 Biểu đồ giá (Close + MA)")
    fig1 = make_price_chart(df, result_json['symbol'])
    st.pyplot(fig1)
    
    st.markdown("### 🕯️ Biểu đồ Candlestick (OHLC + MA + Volume)")
    try:
        fig2 = create_candlestick_chart(df, result_json['symbol'])
        st.pyplot(fig2)
    except ValueError as e:
        st.warning(f"⚠️ Không thể tạo biểu đồ Candlestick: {str(e)}")
        st.info("💡 Biểu đồ Candlestick cần dữ liệu OHLCV đầy đủ (Open, High, Low, Close, Volume)")
    
    st.markdown("### 📈 Biểu đồ tổng hợp (Close + MA + RSI + Volume)")
    fig3 = create_combined_chart(df, result_json['symbol'])
    st.pyplot(fig3)


def _show_json_result(result_json: dict):
    """Hiển thị kết quả JSON"""
    
    st.subheader("📋 Kết quả phân tích (JSON)")
    
    # Hiển thị JSON đầy đủ
    st.json(result_json)
    
    # Nút tải xuống
    json_str = json.dumps(result_json, indent=2, ensure_ascii=False)
    st.download_button(
        label="💾 Tải xuống JSON",
        data=json_str,
        file_name=f"stock_analysis_{result_json['symbol']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )


def _show_ai_advice(result_json: dict):
    """Hiển thị lời khuyên AI"""
    
    st.subheader("🤖 Gợi ý từ AI")
    
    # Lời khuyên chính
    st.info(result_json['ai_advice'])
    
    # Thông tin bổ sung
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Độ tin cậy AI",
            f"{get_ai_confidence_score(result_json):.1%}"
        )
    
    with col2:
        from ai_module import get_market_sentiment
        sentiment = get_market_sentiment(result_json['symbol'], result_json)
        sentiment_emoji = {"Tích cực": "🐂", "Tiêu cực": "🐻", "Trung lập": "😐"}
        st.metric(
            "Tâm lý thị trường",
            f"{sentiment_emoji.get(sentiment, '😐')} {sentiment}"
        )
    
    # Cảnh báo
    st.warning(
        "⚠️ Lưu ý: Đây chỉ là phân tích kỹ thuật và dự đoán AI. "
        "Không phải lời khuyên đầu tư. Hãy tham khảo thêm nhiều nguồn khác."
    )




if __name__ == "__main__":
    main()
    st.caption("🎯 Project AI Stock Insight đã sẵn sàng chạy thử — nhập mã 'FPT' và chọn khoảng 60 ngày gần nhất để phân tích.")
    print("✅ Export button moved outside tabs - should work now!")
