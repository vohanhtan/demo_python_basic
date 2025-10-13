# 📈 AI Stock Insight

Ứng dụng phân tích kỹ thuật và dự đoán cổ phiếu sử dụng Python + Streamlit

## 🎯 Tính năng chính

- **Phân tích kỹ thuật**: SMA(7), SMA(30), RSI(14) với tính toán chính xác
- **Dự đoán ngắn hạn**: Linear Regression + fallback thông minh cho 3-10 ngày
- **AI Advice**: Lời khuyên giả lập thông minh (chuẩn bị cho API thật)
- **Biểu đồ trực quan**: matplotlib với xử lý lỗi tốt, không crash
- **Logging**: Ghi kết quả JSON theo ngày với cấu trúc chuẩn
- **UI thân thiện**: Streamlit với giao diện tiếng Việt, xử lý lỗi tốt

## 🚀 Cài đặt và chạy

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

**Các thư viện chính:**
- **pandas>=2.0.0**: Xử lý dữ liệu CSV và DataFrame
- **numpy>=1.24.0**: Tính toán số học và mảng
- **scikit-learn>=1.3.0**: Machine learning (Linear Regression)
- **matplotlib>=3.7.0**: Vẽ biểu đồ
- **streamlit>=1.28.0**: Web framework cho UI
- **python-dateutil>=2.8.2**: Xử lý ngày tháng

### 2. Chạy ứng dụng

```bash
streamlit run app.py
```

### 3. Truy cập

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
├── requirements.txt       # Dependencies
├── README.md              # Hướng dẫn chi tiết
├── data/                  # Dữ liệu CSV
│   ├── FPT.csv
│   └── VNM.csv
└── reports/               # Log files (tự động tạo)
    └── YYYY-MM-DD.json
```

## 📊 Chỉ báo kỹ thuật

### SMA (Simple Moving Average) - Đường trung bình động đơn giản

#### SMA(7) - Đường trung bình 7 ngày
- **Là gì**: Giá trị trung bình của giá đóng cửa trong 7 ngày gần nhất
- **Ý nghĩa**: Phản ánh xu hướng ngắn hạn, nhạy cảm với biến động giá
- **Tại sao sử dụng**: 
  - Xác định xu hướng ngắn hạn (1-2 tuần)
  - Tín hiệu mua/bán nhanh
  - Lọc nhiễu giá ngắn hạn
- **Cách tính**: `SMA(7) = (P1 + P2 + ... + P7) / 7`
- **Tại sao 7 ngày**: Tương ứng với 1 tuần giao dịch, phù hợp cho phân tích ngắn hạn

#### SMA(30) - Đường trung bình 30 ngày  
- **Là gì**: Giá trị trung bình của giá đóng cửa trong 30 ngày gần nhất
- **Ý nghĩa**: Phản ánh xu hướng trung hạn, ổn định hơn SMA(7)
- **Tại sao sử dụng**:
  - Xác định xu hướng chính (1-2 tháng)
  - Tín hiệu mua/bán đáng tin cậy hơn
  - Hỗ trợ/kháng cự động
- **Cách tính**: `SMA(30) = (P1 + P2 + ... + P30) / 30`
- **Tại sao 30 ngày**: Tương ứng với 1 tháng giao dịch, phù hợp cho phân tích trung hạn

#### Quy tắc giao dịch SMA:
- **Tín hiệu MUA**: SMA(7) cắt lên trên SMA(30) (Golden Cross)
- **Tín hiệu BÁN**: SMA(7) cắt xuống dưới SMA(30) (Death Cross)
- **Xu hướng TĂNG**: Giá > SMA(7) > SMA(30)
- **Xu hướng GIẢM**: Giá < SMA(7) < SMA(30)

### RSI (Relative Strength Index) - Chỉ số sức mạnh tương đối

#### RSI(14) - Chỉ số RSI 14 ngày
- **Là gì**: Chỉ báo momentum đo lường tốc độ và độ lớn của biến động giá
- **Ý nghĩa**: Xác định trạng thái quá mua/quá bán của cổ phiếu
- **Tại sao sử dụng**:
  - Phát hiện điểm đảo chiều tiềm năng
  - Xác nhận tín hiệu từ SMA
  - Quản lý rủi ro (tránh mua đỉnh, bán đáy)
- **Cách tính**:
  ```
  RSI = 100 - (100 / (1 + RS))
  RS = Average Gain / Average Loss
  Average Gain = Trung bình tăng giá trong 14 ngày
  Average Loss = Trung bình giảm giá trong 14 ngày
  ```
- **Tại sao 14 ngày**: 
  - Đủ dài để lọc nhiễu ngắn hạn
  - Đủ ngắn để phản ứng kịp thời với thay đổi
  - Chuẩn công nghiệp được sử dụng rộng rãi

#### Quy tắc giao dịch RSI:
- **Quá mua (Overbought)**: RSI > 70 → Có thể bán
- **Quá bán (Oversold)**: RSI < 30 → Có thể mua  
- **Vùng trung tính**: 30 ≤ RSI ≤ 70 → Chờ tín hiệu
- **Phân kỳ**: RSI và giá di chuyển ngược chiều → Tín hiệu đảo chiều

### Kết hợp các chỉ báo

#### Chiến lược phân tích:
1. **Xác định xu hướng**: Dùng SMA(7) và SMA(30)
2. **Tìm điểm vào**: Dùng RSI để xác định thời điểm
3. **Quản lý rủi ro**: Kết hợp cả 3 chỉ báo

#### Ví dụ tín hiệu:
- **MUA**: SMA(7) > SMA(30) + RSI < 70 (chưa quá mua)
- **BÁN**: SMA(7) < SMA(30) + RSI > 30 (chưa quá bán)
- **HOLD**: Các chỉ báo mâu thuẫn hoặc không rõ ràng

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

1. **Chọn mã cổ phiếu**: FPT hoặc VNM (có sẵn dữ liệu mẫu)
2. **Thiết lập khoảng thời gian**: Ngày bắt đầu và kết thúc (mặc định 60 ngày gần nhất)
3. **Số ngày dự đoán**: 1-10 ngày (mặc định 5 ngày)
4. **Nhấn "Phân tích"**: Xem kết quả chi tiết
5. **Xem biểu đồ**: Chọn "Biểu đồ giá" hoặc "Biểu đồ tổng hợp"
6. **Tải kết quả**: JSON được lưu tự động và có thể tải xuống

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
- **AI giả lập**: Lời khuyên hiện tại là rule-based thông minh
- **Không phải lời khuyên đầu tư**: Chỉ là phân tích kỹ thuật
- **Dữ liệu mẫu**: CSV được tạo giả lập cho demo (~90 ngày)
- **Xử lý lỗi tốt**: Ứng dụng không crash, có fallback thông minh
- **Dự đoán ổn định**: Linear Regression + fallback dựa trên xu hướng thực tế

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
# Đảm bảo đang ở thư mục demo_python_basic
cd demo_python_basic
streamlit run app.py
```

### Lỗi dữ liệu
- Kiểm tra file CSV trong thư mục `data/`
- Đảm bảo format đúng: Date,Symbol,Open,High,Low,Close,Volume
- Dữ liệu mẫu FPT.csv và VNM.csv đã có sẵn

### Lỗi matplotlib
```bash
pip install --upgrade matplotlib
```

### Lỗi biểu đồ
- Ứng dụng có xử lý lỗi tốt, không crash
- Nếu "Biểu đồ tổng hợp" không hiển thị, thử "Biểu đồ giá"
- Tất cả lỗi đều có thông báo rõ ràng bằng tiếng Việt

### Lỗi dự đoán
- Dự đoán có fallback thông minh
- Nếu Linear Regression lỗi, sẽ dùng xu hướng đơn giản
- Giá dự đoán luôn dựa trên giá thực tế, không phải giá mặc định

## 📞 Hỗ trợ

Nếu gặp vấn đề, vui lòng kiểm tra:
1. Python version >= 3.10
2. Đã cài đặt đầy đủ dependencies
3. File CSV có đúng format
4. Port 8501 không bị chiếm dụng

---

## 🎉 Trạng thái dự án

**✅ HOÀN THÀNH**: Dự án đã được test kỹ lưỡng và sẵn sàng sử dụng

**🚀 Sẵn sàng demo**: 
1. Chạy `streamlit run app.py`
2. Chọn mã 'FPT' hoặc 'VNM'
3. Thiết lập khoảng thời gian (mặc định 60 ngày)
4. Nhấn "Phân tích" để xem kết quả

**🔧 Đã sửa các lỗi**:
- ✅ Biểu đồ tổng hợp hoạt động ổn định
- ✅ Giá dự đoán hiển thị giá thực tế (không còn 0 hoặc 100)
- ✅ Xử lý lỗi tốt, không crash
- ✅ Fallback thông minh cho tất cả chức năng
