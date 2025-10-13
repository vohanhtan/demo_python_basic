# 📈 AI Stock Insight

Ứng dụng phân tích kỹ thuật và dự đoán cổ phiếu sử dụng Python + Streamlit

## 🎯 Tính năng chính

- **Phân tích kỹ thuật**: SMA(7), SMA(30), RSI(14)
- **Dự đoán ngắn hạn**: Linear Regression cho 3-5 ngày
- **AI Advice**: Lời khuyên giả lập (chuẩn bị cho API thật)
- **Biểu đồ trực quan**: matplotlib với nhiều loại chart
- **Logging**: Ghi kết quả JSON theo ngày
- **UI thân thiện**: Streamlit với giao diện tiếng Việt

## 🚀 Cài đặt và chạy

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Test nhanh

```bash
python3 demo.py
```

### 3. Chạy ứng dụng

```bash
streamlit run app.py
```

### 4. Truy cập

Mở trình duyệt và truy cập: `http://localhost:8501`

## 📁 Cấu trúc dự án

```
demo_python_basic/
├── app.py                 # UI Streamlit chính
├── data_service.py        # Đọc và lọc dữ liệu CSV
├── indicators.py          # Tính SMA và RSI
├── predictor.py           # Dự đoán bằng Linear Regression
├── ai_module.py           # AI advice (giả lập)
├── logger.py              # Ghi log JSON theo ngày
├── visualizer.py          # Vẽ biểu đồ matplotlib
├── utils.py               # Hàm tiện ích
├── demo.py                # Script test nhanh
├── requirements.txt       # Dependencies
├── README.md              # Hướng dẫn chi tiết
├── QUICK_START.md         # Hướng dẫn nhanh
├── data/                  # Dữ liệu CSV
│   ├── FPT.csv
│   └── VNM.csv
└── reports/               # Log files (tự động tạo)
    └── YYYY-MM-DD.json
```

## 📊 Dữ liệu mẫu

Dự án đi kèm dữ liệu mẫu cho 2 mã cổ phiếu:
- **FPT**: ~90 ngày giao dịch
- **VNM**: ~90 ngày giao dịch

Format CSV:
```csv
Date,Symbol,Open,High,Low,Close,Volume
2025-07-15,FPT,120.5,122.0,119.5,121.7,450000
```

## 🔧 Cách sử dụng

1. **Chọn mã cổ phiếu**: FPT hoặc VNM
2. **Thiết lập khoảng thời gian**: Ngày bắt đầu và kết thúc
3. **Số ngày dự đoán**: 1-10 ngày
4. **Nhấn "Phân tích"**: Xem kết quả

## 📈 Kết quả phân tích

### JSON Schema
```json
{
  "symbol": "FPT",
  "date_range": ["2025-08-01", "2025-10-01"],
  "latest_price": 123.45,
  "technical_indicators": {
    "SMA7": 121.80,
    "SMA30": 118.60,
    "RSI14": 68.20
  },
  "trend": "Uptrend",
  "forecast_horizon_days": 5,
  "forecast_next_days": [124.0, 124.6, 125.1, 125.8, 126.3],
  "signal": "BUY",
  "reason": "Giá đang trong xu hướng tăng, RSI chưa vào vùng quá mua.",
  "generated_at": "2025-10-14T21:05:00",
  "ai_advice": "AI nhận định FPT có xu hướng tăng ngắn hạn..."
}
```

### Tín hiệu giao dịch
- **BUY**: Mua (xu hướng tăng, RSI < 70)
- **SELL**: Bán (xu hướng giảm, RSI > 30)
- **HOLD**: Giữ (chờ tín hiệu rõ ràng)

## 🤖 AI Module

Hiện tại sử dụng logic rule-based để tạo lời khuyên. Có thể dễ dàng thay thế bằng API thật:

```python
# Trong ai_module.py
def call_real_ai_api(result_json: dict) -> str:
    # TODO: Implement với OpenAI/Gemini/Claude
    pass
```

## 📝 Logging

Kết quả phân tích được ghi vào `reports/YYYY-MM-DD.json`:

```json
{
  "date": "2025-10-14",
  "records": [
    {
      "symbol": "FPT",
      "latest_price": 123.45,
      "trend": "Uptrend",
      "signal": "BUY",
      "reason": "...",
      "ai_advice": "...",
      "generated_at": "2025-10-14T21:05:00"
    }
  ]
}
```

## ⚠️ Lưu ý quan trọng

- **Không kết nối API thật**: Chỉ sử dụng dữ liệu CSV nội bộ
- **AI giả lập**: Lời khuyên hiện tại là rule-based
- **Không phải lời khuyên đầu tư**: Chỉ là phân tích kỹ thuật
- **Dữ liệu mẫu**: CSV được tạo giả lập cho demo

## 🔮 Mở rộng tương lai

- [ ] Tích hợp API thật (OpenAI, Gemini, Claude)
- [ ] Thêm nhiều chỉ báo kỹ thuật (MACD, Bollinger Bands)
- [ ] Kết nối dữ liệu thời gian thực
- [ ] Thêm machine learning models (LSTM, Prophet)
- [ ] Portfolio analysis
- [ ] Alert system

## 🐛 Troubleshooting

### Lỗi import module
```bash
# Đảm bảo đang ở thư mục ai_stock_insight
cd ai_stock_insight
streamlit run app.py
```

### Lỗi dữ liệu
- Kiểm tra file CSV trong thư mục `data/`
- Đảm bảo format đúng: Date,Symbol,Open,High,Low,Close,Volume

### Lỗi matplotlib
```bash
pip install --upgrade matplotlib
```

## 📞 Hỗ trợ

Nếu gặp vấn đề, vui lòng kiểm tra:
1. Python version >= 3.10
2. Đã cài đặt đầy đủ dependencies
3. File CSV có đúng format
4. Port 8501 không bị chiếm dụng

---

**🎉 Sẵn sàng demo: nhập mã 'FPT' trong 60 ngày gần nhất và nhấn Phân tích.**
