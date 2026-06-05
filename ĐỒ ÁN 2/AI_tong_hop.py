import json
import random
import time
from google import genai
from google.genai import types

# 1. Danh sách các API Key của bạn
API_KEYS = [
    "AQ.Ab8RN6IcOFA7dUwzFzrxf6FXJYw4qsWYedGIeCgBBreyLxHDIg",
    "AQ.Ab8RN6KrY-dPLSCRBzwfHqIpNxKn0-DwDRezb9bEytWuKfId1Q",
    "AQ.Ab8RN6JD8Cikx6TfyJLlroNhWZNAd6NcAwLd7tbSTIRWdmvkbw",
    # Bạn có thể thêm các key dự phòng khác vào đây
]


def analyze_article(title, text):
    """Sử dụng Gemini 2.5 Flash để tóm tắt và phân tích bài báo.

    Tự động xoay vòng và thử lại với Key khác nếu dính lỗi (429, 403, rỗng...).
    Trả về None nếu TẤT CẢ các key đều thất bại.
    """
    if not text.strip():
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

    # Tạo bản sao và xáo trộn ngẫu nhiên danh sách key để phân phối đều tải tải
    shuffled_keys = API_KEYS.copy()
    random.shuffle(shuffled_keys)

    # Duyệt qua từng key để thử
    for current_key in shuffled_keys:
        # Loại bỏ các phần tử trống vô tình lọt vào danh sách
        if not current_key or not current_key.strip():
            continue

        try:
            # Khởi tạo client với key hiện tại
            client = genai.Client(api_key=current_key)

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )

            # Nếu thành công, parse JSON và trả về kết quả chuẩn
            analysis_data = json.loads(response.text)
            return analysis_data

        except Exception as e:
            error_msg = str(e)
            # In cảnh báo lỗi ngắn gọn kèm 8 ký tự cuối của key lỗi để bạn tiện tracking
            print(
                f"      [!] Key [...{current_key[-8:]}] gặp lỗi: {error_msg[:80]}... Đang tự động đổi sang key khác..."
            )

            # Nếu dính hạn mức tốc độ (429), cho hệ thống nghỉ 1 giây trước khi đổi sang key tiếp theo
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                time.sleep(1)
            continue

    # Nếu chạy hết cả danh sách key mà không key nào hoạt động thành công
    return None