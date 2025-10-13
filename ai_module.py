"""
Module AI tư vấn cổ phiếu (GIẢ LẬP)
Hiện tại sử dụng logic rule-based để tạo lời khuyên
Sau này sẽ thay thế bằng API thật (OpenAI/Gemini/Claude)
"""

import random
from typing import Dict


def get_ai_advice(result_json: Dict) -> str:
    """
    Tạo lời khuyên AI dựa trên kết quả phân tích (GIẢ LẬP)
    
    Args:
        result_json: Dictionary chứa kết quả phân tích với các key:
                    - symbol: mã cổ phiếu
                    - trend: xu hướng
                    - signal: tín hiệu
                    - technical_indicators: chỉ báo kỹ thuật
                    - reason: lý do tín hiệu
                    
    Returns:
        Chuỗi lời khuyên AI bằng tiếng Việt
    """
    symbol = result_json.get('symbol', 'cổ phiếu')
    trend = result_json.get('trend', 'Sideways')
    signal = result_json.get('signal', 'HOLD')
    indicators = result_json.get('technical_indicators', {})
    reason = result_json.get('reason', '')
    
    # Lấy giá trị chỉ báo
    rsi = indicators.get('RSI14', 50)
    sma7 = indicators.get('SMA7', 0)
    sma30 = indicators.get('SMA30', 0)
    
    # Tạo lời khuyên dựa trên tín hiệu và xu hướng
    advice = _generate_advice_by_signal(symbol, signal, trend, rsi, sma7, sma30, reason)
    
    # Thêm cảnh báo rủi ro
    risk_warning = _add_risk_warning(signal, trend)
    
    return f"{advice} {risk_warning}"


def _generate_advice_by_signal(symbol: str, signal: str, trend: str, rsi: float, 
                              sma7: float, sma30: float, reason: str) -> str:
    """
    Tạo lời khuyên dựa trên tín hiệu giao dịch
    
    Args:
        symbol: Mã cổ phiếu
        signal: Tín hiệu (BUY/SELL/HOLD)
        trend: Xu hướng
        rsi: Giá trị RSI
        sma7: Giá trị SMA7
        sma30: Giá trị SMA30
        reason: Lý do tín hiệu
        
    Returns:
        Lời khuyên chính
    """
    if signal == "BUY":
        return _generate_buy_advice(symbol, trend, rsi, sma7, sma30)
    elif signal == "SELL":
        return _generate_sell_advice(symbol, trend, rsi, sma7, sma30)
    else:  # HOLD
        return _generate_hold_advice(symbol, trend, rsi, sma7, sma30)


def _generate_buy_advice(symbol: str, trend: str, rsi: float, sma7: float, sma30: float) -> str:
    """
    Tạo lời khuyên mua
    """
    advice_templates = [
        f"AI nhận định {symbol} có tiềm năng tăng giá ngắn hạn.",
        f"Phân tích kỹ thuật cho thấy {symbol} đang trong xu hướng tích cực.",
        f"Tín hiệu mua xuất hiện cho {symbol} với các chỉ báo hỗ trợ."
    ]
    
    base_advice = random.choice(advice_templates)
    
    # Thêm chi tiết dựa trên chỉ báo
    details = []
    
    if trend == "Uptrend":
        details.append("Xu hướng tăng rõ ràng")
    
    if rsi < 50:
        details.append("RSI chưa quá mua")
    elif rsi < 70:
        details.append("RSI trong vùng an toàn")
    
    if sma7 > sma30:
        details.append("SMA ngắn hạn vượt SMA dài hạn")
    
    if details:
        detail_text = ", ".join(details)
        return f"{base_advice} Các yếu tố hỗ trợ: {detail_text}."
    else:
        return base_advice


def _generate_sell_advice(symbol: str, trend: str, rsi: float, sma7: float, sma30: float) -> str:
    """
    Tạo lời khuyên bán
    """
    advice_templates = [
        f"AI khuyến nghị thận trọng với {symbol} trong ngắn hạn.",
        f"Phân tích cho thấy {symbol} có thể điều chỉnh giảm.",
        f"Tín hiệu bán xuất hiện cho {symbol}, nên xem xét chốt lời."
    ]
    
    base_advice = random.choice(advice_templates)
    
    # Thêm chi tiết dựa trên chỉ báo
    details = []
    
    if trend == "Downtrend":
        details.append("xu hướng giảm")
    
    if rsi > 70:
        details.append("RSI quá mua")
    elif rsi > 50:
        details.append("RSI ở vùng cao")
    
    if sma7 < sma30:
        details.append("SMA ngắn hạn dưới SMA dài hạn")
    
    if details:
        detail_text = ", ".join(details)
        return f"{base_advice} Lý do: {detail_text}."
    else:
        return base_advice


def _generate_hold_advice(symbol: str, trend: str, rsi: float, sma7: float, sma30: float) -> str:
    """
    Tạo lời khuyên giữ
    """
    advice_templates = [
        f"AI khuyến nghị giữ nguyên vị thế {symbol} hiện tại.",
        f"Phân tích cho thấy {symbol} đang trong giai đoạn chờ đợi.",
        f"Tín hiệu chưa rõ ràng cho {symbol}, nên quan sát thêm."
    ]
    
    base_advice = random.choice(advice_templates)
    
    # Thêm chi tiết dựa trên tình hình
    if trend == "Sideways":
        return f"{base_advice} Thị trường đang sideways, chờ breakout."
    elif rsi > 70:
        return f"{base_advice} RSI quá mua, chờ điều chỉnh."
    elif rsi < 30:
        return f"{base_advice} RSI quá bán, có thể phục hồi."
    else:
        return f"{base_advice} Các chỉ báo chưa cho tín hiệu rõ ràng."


def _add_risk_warning(signal: str, trend: str) -> str:
    """
    Thêm cảnh báo rủi ro
    
    Args:
        signal: Tín hiệu giao dịch
        trend: Xu hướng
        
    Returns:
        Cảnh báo rủi ro
    """
    warnings = [
        "Lưu ý: Đầu tư có rủi ro, cần quản lý vốn hợp lý.",
        "Khuyến nghị: Chỉ đầu tư số tiền có thể chấp nhận mất.",
        "Cảnh báo: Thị trường biến động, cần theo dõi sát sao."
    ]
    
    base_warning = random.choice(warnings)
    
    # Thêm cảnh báo cụ thể
    if signal == "BUY" and trend == "Uptrend":
        return f"{base_warning} Nên đặt stop-loss để bảo vệ vốn."
    elif signal == "SELL":
        return f"{base_warning} Có thể bỏ lỡ cơ hội nếu thị trường đảo chiều."
    else:
        return f"{base_warning} Cần kiên nhẫn chờ tín hiệu rõ ràng hơn."


def get_ai_confidence_score(result_json: Dict) -> float:
    """
    Tính điểm tin cậy của lời khuyên AI (0-1)
    
    Args:
        result_json: Kết quả phân tích
        
    Returns:
        Điểm tin cậy từ 0 đến 1
    """
    score = 0.5  # Điểm cơ bản
    
    # Tăng điểm dựa trên độ nhất quán của các chỉ báo
    indicators = result_json.get('technical_indicators', {})
    rsi = indicators.get('RSI14', 50)
    sma7 = indicators.get('SMA7', 0)
    sma30 = indicators.get('SMA30', 0)
    trend = result_json.get('trend', 'Sideways')
    signal = result_json.get('signal', 'HOLD')
    
    # Điểm cho RSI
    if 30 <= rsi <= 70:
        score += 0.1  # RSI trong vùng trung tính
    
    # Điểm cho SMA
    if sma7 > sma30 and trend == "Uptrend":
        score += 0.2  # SMA nhất quán với xu hướng
    elif sma7 < sma30 and trend == "Downtrend":
        score += 0.2
    
    # Điểm cho tín hiệu rõ ràng
    if signal in ["BUY", "SELL"]:
        score += 0.1
    
    # Điểm cho xu hướng mạnh
    if trend in ["Uptrend", "Downtrend"]:
        score += 0.1
    
    return min(1.0, max(0.0, score))


def get_market_sentiment(symbol: str, result_json: Dict) -> str:
    """
    Đánh giá tâm lý thị trường cho mã cổ phiếu
    
    Args:
        symbol: Mã cổ phiếu
        result_json: Kết quả phân tích
        
    Returns:
        Tâm lý thị trường: "Bullish", "Bearish", "Neutral"
    """
    signal = result_json.get('signal', 'HOLD')
    trend = result_json.get('trend', 'Sideways')
    indicators = result_json.get('technical_indicators', {})
    rsi = indicators.get('RSI14', 50)
    
    bullish_signals = 0
    bearish_signals = 0
    
    # Đếm tín hiệu bullish
    if signal == "BUY":
        bullish_signals += 2
    elif signal == "HOLD" and trend == "Uptrend":
        bullish_signals += 1
    
    if trend == "Uptrend":
        bullish_signals += 1
    
    if rsi < 70:
        bullish_signals += 1
    
    # Đếm tín hiệu bearish
    if signal == "SELL":
        bearish_signals += 2
    elif signal == "HOLD" and trend == "Downtrend":
        bearish_signals += 1
    
    if trend == "Downtrend":
        bearish_signals += 1
    
    if rsi > 70:
        bearish_signals += 1
    
    # Xác định tâm lý
    if bullish_signals > bearish_signals:
        return "Bullish"
    elif bearish_signals > bullish_signals:
        return "Bearish"
    else:
        return "Neutral"


# Hàm dự phòng cho tương lai khi tích hợp API thật
def call_real_ai_api(result_json: Dict) -> str:
    """
    Hàm dự phòng để gọi API AI thật (chưa implement)
    
    Args:
        result_json: Kết quả phân tích
        
    Returns:
        Lời khuyên từ AI thật
    """
    # TODO: Implement khi có API thật
    # Ví dụ: OpenAI, Gemini, Claude, etc.
    return "API AI thật chưa được tích hợp. Sử dụng logic giả lập."
