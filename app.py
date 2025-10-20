"""
AI Stock Insight - Ứng dụng phân tích kỹ thuật và dự đoán cổ phiếu
Streamlit UI chính cho việc nhập liệu, phân tích và hiển thị kết quả
"""

import json
from datetime import datetime, timedelta
import traceback

from pathlib import Path

import pandas as pd
import streamlit as st

# Project modules
from data_service import get_stock_data, get_available_symbols, get_data_info
from indicators import add_indicators, get_latest_indicators
from forecast_service import get_forecast
from ai_module import get_ai_advice, get_ai_confidence_score
from logger import append_daily_log, export_today_report
from visualizer import (
    make_price_chart,
    create_combined_chart,
    create_candlestick_chart,
)
from utils import (
    validate_date_range,
    get_current_datetime_iso,
    normalize_symbol,
    get_config,
    is_data_short,
)

# Session state init cho export button
if "export_result" not in st.session_state:
    st.session_state.export_result = ""


def main():
    """Hàm chính của ứng dụng Streamlit"""

    # Cấu hình trang
    st.set_page_config(
        page_title="AI Stock Insight",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Tiêu đề chính
    st.title("AI Stock Insight — Phân tích kỹ thuật & Dự đoán")
    st.markdown("---")

    # Sidebar cho input
    with st.sidebar:
        st.header("Cài đặt phân tích")

        # Input mã cổ phiếu
        available_symbols = get_available_symbols()
        if available_symbols:
            symbol = st.selectbox(
                "Mã cổ phiếu",
                options=available_symbols,
                index=0,
                help="Chọn mã cổ phiếu có sẵn trong hệ thống",
            )
        else:
            symbol = st.text_input(
                "Mã cổ phiếu",
                value="FPT",
                help="Nhập mã cổ phiếu (ví dụ: FPT, VNM, AAPL, MSFT)",
            )

        # Input khoảng ngày
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Ngày bắt đầu",
                value=datetime.now() - timedelta(days=60),
                help="Ngày bắt đầu phân tích",
            )

        with col2:
            end_date = st.date_input(
                "Ngày kết thúc",
                value=datetime.now(),
                help="Ngày kết thúc phân tích",
            )

        # Input số ngày dự đoán + model
        colm1, colm2 = st.columns(2)
        with colm1:
            forecast_days = st.number_input(
                "Số ngày dự đoán",
                min_value=1,
                max_value=10,
                value=5,
                help="Số ngày dự đoán giá (1-10 ngày)",
            )
        with colm2:
            model_choice = st.selectbox(
                "Mô hình dự báo",
                options=["linear", "auto", "chronos"],
                index=0,
                help="linear: nhanh, không cần model; auto/chronos: dùng Chronos nếu có",
            )

        # Nút phân tích
        analyze_button = st.button("Phân tích", type="primary", use_container_width=True)

        # Nút xuất báo cáo (đặt dưới nút phân tích)
        export_button = st.button("Xuất báo cáo hôm nay", key="export_today_btn", use_container_width=True)

        # Thông tin dữ liệu nhanh
        if symbol:
            _show_data_info(symbol)

    # Main content
    if analyze_button:
        _perform_analysis(symbol, start_date, end_date, forecast_days, model_choice)
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
            st.subheader("Thông tin dữ liệu")
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
    st.subheader("Xuất báo cáo hôm nay")

    export_format = get_config("EXPORT_FORMAT", "both")

    try:
        export_result = export_today_report(export_format)
        st.session_state.export_result = export_result
        st.success(export_result)

        # Thêm download buttons
        _show_download_buttons()

    except Exception as e:
        error_msg = f"Lỗi xuất báo cáo: {str(e)}"
        st.session_state.export_result = error_msg
        st.error(error_msg)

    # Hiển thị thông tin về file log
    st.subheader("Thông tin file")
    report_dir = get_config("REPORT_DIR", "reports")
    export_dir = get_config("EXPORT_DIR", "export")
    st.write(f"**Thư mục log:** `{report_dir}/`")
    st.write(f"**Thư mục export:** `{export_dir}/`")
    st.write(f"**Định dạng file:** `YYYY-MM-DD.json`")
    st.write(f"**File xuất:** `YYYY-MM-DD_report.csv/pdf`")


def _show_download_buttons():
    """Hiển thị nút download file đã export"""
    import os

    today = datetime.now().strftime("%Y-%m-%d")
    export_dir = get_config("EXPORT_DIR", "export")

    st.subheader("Tải xuống file")

    # CSV download
    csv_path = f"{export_dir}/{today}_report.csv"
    if os.path.exists(csv_path):
        with open(csv_path, "rb") as f:
            csv_data = f.read()
        st.download_button(label="Tải xuống CSV", data=csv_data, file_name=f"{today}_report.csv", mime="text/csv")

    # PDF download
    pdf_path = f"{export_dir}/{today}_report.pdf"
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()
        st.download_button(
            label="Tải xuống PDF",
            data=pdf_data,
            file_name=f"{today}_report.pdf",
            mime="application/pdf",
        )


def _show_welcome_message():
    """Hiển thị thông điệp chào mừng"""
    st.markdown(
        """
    ### Chào mừng đến với AI Stock Insight!

    **Ứng dụng này giúp bạn:**
    - Phân tích kỹ thuật cổ phiếu với các chỉ báo SMA và RSI
    - Dự đoán xu hướng ngắn hạn (Linear hoặc Chronos)
    - Nhận lời khuyên từ AI (hiện tại là giả lập)
    - Biểu đồ trực quan
    - Xuất báo cáo CSV/PDF

    **Cách dùng nhanh:**
    1. Chọn mã cổ phiếu
    2. Chọn khoảng thời gian
    3. Chọn mô hình (linear/auto/chronos)
    4. Nhấn **Phân tích**
    """
    )


def _perform_analysis(symbol: str, start_date, end_date, forecast_days: int, model_choice: str):
    """Thực hiện phân tích cổ phiếu (dùng forecast_service)"""

    # Validate input
    try:
        symbol = normalize_symbol(symbol)
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        validate_date_range(start_date_str, end_date_str)
    except ValueError as e:
        st.error(f"Lỗi đầu vào: {str(e)}")
        return

    # Progress UI
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Bước 1: Đọc dữ liệu
        status_text.text("Đang đọc dữ liệu...")
        progress_bar.progress(20)
        df = get_stock_data(symbol, start_date_str, end_date_str)

        if is_data_short(df):
            st.warning("Dữ liệu ngắn, kết quả có thể thiếu ổn định. Một số chỉ báo có thể chưa phản ánh đúng xu hướng.")

        # Bước 2: Tính chỉ báo
        status_text.text("Đang tính chỉ báo kỹ thuật...")
        progress_bar.progress(40)
        df_with_indicators = add_indicators(df)

        # Bước 3: Dự báo (service)
        status_text.text(f"Đang dự đoán ({model_choice})...")
        progress_bar.progress(65)
        result_json = get_forecast(
            symbol=symbol,
            start_date=start_date_str,
            end_date=end_date_str,
            horizon_days=forecast_days,
            model=model_choice,  # "linear" | "auto" | "chronos"
        )

        # Bước 4: Lời khuyên AI
        status_text.text("Đang tạo lời khuyên AI...")
        progress_bar.progress(85)
        ai_advice = get_ai_advice(result_json)
        result_json["ai_advice"] = ai_advice

        # Bước 5: Ghi log
        status_text.text("Đang lưu kết quả...")
        progress_bar.progress(95)
        log_result = append_daily_log(result_json)

        # Hoàn tất
        progress_bar.progress(100)
        status_text.text("Phân tích hoàn thành!")

        # Hiển thị kết quả
        _display_results(result_json, df_with_indicators, log_result)

    except FileNotFoundError:
        st.error(f"Không tìm thấy dữ liệu cho mã {symbol}. Kiểm tra file notebooks/data/{symbol}.csv.")
        st.stop()
    except ValueError as e:
        st.error(f"Lỗi dữ liệu: {str(e)}")
    except Exception:
        st.error("Lỗi không xác định:")
        st.code(traceback.format_exc())
    finally:
        progress_bar.empty()
        status_text.empty()


def _display_results(result_json: dict, df: pd.DataFrame, log_result: dict):
    """Hiển thị kết quả phân tích"""

    st.success(f"Đã ghi vào {log_result['file_path']} — Tổng số hôm nay: {log_result['total_records_today']}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Tổng quan", "Biểu đồ", "Kết quả JSON", "Lời khuyên AI", "So sánh / Correlation"])

    with tab1:
        _show_overview(result_json, df)

    with tab2:
        _show_charts(result_json, df)

    with tab3:
        _show_json_result(result_json)

    with tab4:
        _show_ai_advice(result_json)
        
    with tab5:
        # SỬA LỖI: Thụt lề hàm này vào trong 'with tab5:'
        _show_compare_tab()


def _show_overview(result_json: dict, df: pd.DataFrame):
    """Hiển thị tổng quan kết quả"""

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Giá hiện tại", f"{result_json['latest_price']:,.0f} VND")

    with col2:
        trend = result_json["trend"]
        trend_display = "Tăng" if trend == "Uptrend" else "Giảm" if trend == "Downtrend" else "Đi ngang"
        st.metric("Xu hướng", trend_display)

    with col3:
        signal = result_json["signal"]
        signal_display = "MUA" if signal == "BUY" else "BÁN" if signal == "SELL" else "GIỮ"
        st.metric("Tín hiệu", signal_display)

    with col4:
        from ai_module import get_market_sentiment

        sentiment = get_market_sentiment(result_json["symbol"], result_json)
        st.metric("Sentiment", sentiment)

    # Chỉ báo
    st.subheader("Chỉ báo kỹ thuật")
    indicators = result_json["technical_indicators"]
    c1, c2, c3 = st.columns(3)
    with c1:
        if "SMA7" in indicators:
            st.metric("SMA(7)", f"{indicators['SMA7']:,.2f}")
    with c2:
        if "SMA30" in indicators:
            st.metric("SMA(30)", f"{indicators['SMA30']:,.2f}")
    with c3:
        if "RSI14" in indicators:
            rsi = indicators["RSI14"]
            rsi_status = "Quá mua" if rsi > 70 else "Quá bán" if rsi < 30 else "Bình thường"
            st.metric("RSI(14)", f"{rsi:.2f}", delta=rsi_status)

    # Dự đoán + bounds
    st.subheader("Dự đoán giá (kèm min/max)")
    preds = result_json.get("forecast_next_days", [])
    bounds = result_json.get("forecast_bounds", [])
    if preds:
        rows = []
        for i, p in enumerate(preds, start=1):
            lo = bounds[i - 1]["min"] if i - 1 < len(bounds) else None
            hi = bounds[i - 1]["max"] if i - 1 < len(bounds) else None
            rows.append({"Ngày": f"T+{i}", "Dự đoán": p, "Min": lo, "Max": hi})
        forecast_df = pd.DataFrame(rows)
        st.dataframe(forecast_df, use_container_width=True)

    # Lý do tín hiệu
    st.subheader("Lý do tín hiệu")
    st.info(result_json.get("reason", ""))

    # Model dùng
    st.caption(f"Model used: **{result_json.get('model_used', 'linear')}**")


def _show_charts(result_json: dict, df: pd.DataFrame):
    """Hiển thị biểu đồ"""

    st.subheader("Biểu đồ phân tích")

    preds = result_json.get("forecast_next_days", None)

    # Biểu đồ giá + MA + dự báo
    st.markdown("### Biểu đồ giá (Close + MA + Forecast)")
    fig1 = make_price_chart(df, result_json["symbol"], forecast_days=preds)
    st.pyplot(fig1)

    # Candlestick
    st.markdown("### Biểu đồ Candlestick (OHLC + MA + Volume)")
    try:
        fig2 = create_candlestick_chart(df, result_json["symbol"], forecast_days=preds)
        st.pyplot(fig2)
    except ValueError as e:
        st.warning(f"Không thể tạo biểu đồ Candlestick: {str(e)}")
        st.info("Biểu đồ Candlestick cần dữ liệu OHLCV đầy đủ (Open, High, Low, Close, Volume)")

    # Combined
    st.markdown("### Biểu đồ tổng hợp (Close + MA + RSI + Volume + Forecast)")
    fig3 = create_combined_chart(df, result_json["symbol"], forecast_days=preds)
    st.pyplot(fig3)


def _show_json_result(result_json: dict):
    """Hiển thị kết quả JSON"""

    st.subheader("Kết quả phân tích (JSON)")
    st.json(result_json)

    json_str = json.dumps(result_json, indent=2, ensure_ascii=False)
    st.download_button(
        label="Tải xuống JSON",
        data=json_str,
        file_name=f"stock_analysis_{result_json['symbol']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
    )


def _show_ai_advice(result_json: dict):
    """Hiển thị lời khuyên AI"""

    st.subheader("Gợi ý từ AI")
    st.info(result_json.get("ai_advice", ""))

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Độ tin cậy AI", f"{get_ai_confidence_score(result_json):.1%}")

    with col2:
        from ai_module import get_market_sentiment

        sentiment = get_market_sentiment(result_json["symbol"], result_json)
        st.metric("Tâm lý thị trường", sentiment)

    st.warning(
        "Lưu ý: Đây chỉ là phân tích kỹ thuật và dự đoán AI. "
        "Không phải lời khuyên đầu tư. Hãy tham khảo thêm nhiều nguồn khác."
    )
    
def _show_compare_tab():
    """Hiển thị ma trận tương quan & so sánh giữa các mã từ aligned.csv trong notebooks/data."""
    st.subheader("So sánh / Correlation (aligned)")

    data_dir = Path("notebooks/data")
    candidates = [
        ("AAPL", data_dir / "aapl_aligned.csv"),
        ("MSFT", data_dir / "msft_aligned.csv"),
        ("VNINDEX", data_dir / "vnindex_aligned.csv"),
    ]

    # Lọc file tồn tại
    avail = [(sym, p) for sym, p in candidates if p.exists()]

    if not avail:
        st.info("Chưa thấy *_aligned.csv trong notebooks/data. Hãy chạy notebook `final_data_check.ipynb` (Cell 6).")
        return

    # Chọn mã để so sánh
    syms = [sym for sym, _ in avail]
    selected = st.multiselect(
        "Chọn các mã để so sánh", syms, default=syms,
        help="Chỉ hiển thị những mã đã có *_aligned.csv"
    )
    if not selected:
        st.warning("Chọn ít nhất 2 mã để xem tương quan.")
        return

    # Load & merge theo 'date'
    merged = None
    for sym, path in avail:
        if sym not in selected:
            continue
        try:
            df = pd.read_csv(path, parse_dates=["date"])
            if "close" not in df.columns:
                st.warning(f"{sym}: thiếu cột 'close' trong {path.name}")
                continue
            df = df[["date", "close"]].rename(columns={"close": sym})
            merged = df if merged is None else merged.merge(df, on="date", how="inner")
        except Exception as e:
            st.warning(f"Lỗi đọc {path.name}: {e}")

    if merged is None or merged.empty or len(merged.columns) < 3:
        st.info("Không đủ dữ liệu trùng ngày để tính tương quan.")
        return

    st.markdown("#### Ma trận tương quan (Pearson)")
    corr = merged.drop(columns=["date"]).corr()
    st.dataframe(corr.style.background_gradient(cmap="coolwarm"), use_container_width=True)

    st.markdown("#### Chuỗi giá đã căn chỉnh (Close)")
    st.line_chart(merged.set_index("date").dropna())

    st.caption("Nguồn: `notebooks/data/*_aligned.csv` — cùng khoảng overlap giữa các mã.")

if __name__ == "__main__":
    main()
    st.caption(
        "Project AI Stock Insight: chọn mô hình *linear* để chạy nhanh, hoặc *auto/chronos* nếu đã cài transformers."
    )