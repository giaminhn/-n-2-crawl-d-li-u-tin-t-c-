import os
import pandas as pd

# Xác định đường dẫn tuyệt đối đến file CSV để đảm bảo GitHub Actions luôn tìm thấy file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "steel_news.csv")

# Định nghĩa danh sách 12 cột cố định theo đúng thứ tự yêu cầu
COLUMNS = [
    "news_id", "title", "summary", "content", "published_date",
    "source", "url", "industry_group", "tickers", "keywords",
    "event_type", "crawl_time"
]


def save_news(data):
    # Tạo DataFrame từ dictionary dữ liệu và sắp xếp chuẩn theo các cột định sẵn
    df_new = pd.DataFrame([data], columns=COLUMNS)

    # Nếu file chưa tồn tại thì tạo mới kèm Header đầy đủ
    if not os.path.exists(CSV_FILE):
        df_new.to_csv(
            CSV_FILE,
            index=False,
            encoding="utf-8-sig"
        )
        print("    -> Đã tạo mới file CSV với 12 trường thông tin.")
        return

    # Nếu file đã tồn tại, kiểm tra trùng URL để tránh lưu lặp dữ liệu
    try:
        old_df = pd.read_csv(CSV_FILE, usecols=["url"])
        if data["url"] in old_df["url"].values:
            print("    -> Bản tin đã tồn tại trong CSV (Trùng URL). Bỏ qua.")
            return
    except Exception:
        pass  # Phòng trường hợp file lỗi hoặc trống thì cứ ghi tiếp

    # Ghi thêm dòng mới vào cuối file (mode "a"), không lặp lại dòng tiêu đề (header=False)
    df_new.to_csv(
        CSV_FILE,
        mode="a",
        header=False,
        index=False,
        encoding="utf-8-sig"
    )
    print("    -> Đã phân tích và lưu thành công vào file CSV.")