# 🚀 Quick Start - AI Stock Insight

## Cài đặt nhanh

```bash
# 1. Cài đặt dependencies
pip install -r requirements.txt

# 2. Test demo
python3 demo.py

# 3. Chạy UI
streamlit run app.py
```

## Lưu ý

- Tất cả files đã được chuyển ra thư mục root `demo_python_basic`
- Không cần thư mục con `ai_stock_insight` nữa
- Chạy trực tiếp từ thư mục hiện tại

## Truy cập ứng dụng

Mở trình duyệt: `http://localhost:8501`

## Demo nhanh

1. **Chọn mã cổ phiếu**: FPT hoặc VNM
2. **Thiết lập ngày**: Mặc định 60 ngày gần nhất
3. **Nhấn "Phân tích"**
4. **Xem kết quả**: JSON, biểu đồ, AI advice

## Kết quả mẫu

- **FPT**: Xu hướng tăng, RSI quá mua → HOLD
- **VNM**: Xu hướng tăng, RSI quá mua → HOLD

## Files quan trọng

- `app.py` - UI chính
- `demo.py` - Test nhanh
- `data/FPT.csv` - Dữ liệu FPT
- `data/VNM.csv` - Dữ liệu VNM
- `reports/` - Log files

---

**🎉 Sẵn sàng demo: nhập mã 'FPT' trong 60 ngày gần nhất và nhấn Phân tích.**
