import json
import os
import random
import time
from google import genai
from google.genai import types

# 1. Đọc danh sách API Key an toàn từ biến môi trường của hệ thống
API_KEYS_RAW = os.environ.get("GEMINI_API_KEYS", "")
# Tách các key bằng dấu phẩy và loại bỏ khoảng trắng thừa
API_KEYS = [k.strip() for k in API_KEYS_RAW.split(",") if k.strip()]


def analyze_article(title, text):
    """Sử dụng Gemini 2.5 Flash để tóm tắt và phân tích bài báo."""
    if not text.strip():
        return None

    # Nếu không tìm thấy key nào cấu hình trong môi trường hệ thống
    if not API_KEYS:
        print("      [❌] LỖI: Không tìm thấy API Key nào trong biến môi trường GEMINI_API_KEYS.")
        return None

    prompt = f"""
    Bạn là một chuyên gia phân tích dữ liệu chứng khoán và tài chính doanh nghiệp Việt Nam.
    Hãy đọc tiêu đề và nội dung bài báo sau đây, sau đó trích xuất thông tin theo yêu cầu.

    Tiêu đề: {title}
    Nội dung: {text[:8000]}

    Yêu cầu trích xuất cấu trúc JSON với các key sau:
    1. "summary": Tóm tắt ngắn gọn nội dung bài viết (khoảng 2-3 câu bằng tiếng Việt).
    2. "industry_group": Nhóm ngành chính của mã cổ phiếu/doanh nghiệp được nói đến (Ví dụ: Thép, Hóa chất, Phân bón, Cao su, Xi măng, Nhựa & Vật liệu xây dựng, Vĩ mô...).
    3. "tickers": Các mã cổ phiếu chứng khoán Việt Nam được nhắc đến trực tiếp hoặc liên quan mật thiết (Ví dụ: HPG, HSG, NKG, VGS, DGC, DPM, DCM, CSV, LAS, BFC, BMP, NTP, HT1, BCC, GVR, DPR...). Nếu không có, để chuỗi rỗng "". Nhiều mã cách nhau bằng dấu phẩy.
    4. "keywords": 3-5 từ khóa ngành tài chính tìm thấy trong bài viết, cách nhau bằng dấu phẩy (Ví dụ: kết quả kinh doanh, giá urê, xuất khẩu thép, đại hội cổ đông...).
    5. "event_type": Loại sự kiện của tin tức này, chọn một trong các nhóm: "Kết quả kinh doanh", "Giá cả thị trường", "Chính sách - Vĩ mô", "Đầu tư - Dự án", "Tin tức doanh nghiệp", "Khác".
    """

    shuffled_keys = API_KEYS.copy()
    random.shuffle(shuffled_keys)

    for current_key in shuffled_keys:
        try:
            client = genai.Client(api_key=current_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )
            return json.loads(response.text)

        except Exception as e:
            error_msg = str(e)
            print(f"      [!] Key [...{current_key[-8:]}] gặp lỗi: {error_msg[:60]}... Đang tự động đổi key...")
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                time.sleep(1)
            continue
    return None