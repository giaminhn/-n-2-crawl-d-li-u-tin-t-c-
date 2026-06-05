import hashlib
import time
from datetime import datetime

from AI_tong_hop import analyze_article
from lay_noi_dung import get_article_content
from save_news import save_news
from thu_thap_tin_tuc import get_news


def generate_news_id(url):
    """Tạo mã băm MD5 duy nhất từ URL bài viết"""
    return hashlib.md5(url.encode("utf-8")).hexdigest()[:12].upper()


def main_job():
    """Hàm lõi thực hiện toàn bộ tiến trình cào và phân tích tin tức"""
    # 1. Định nghĩa DANH SÁCH MÃ CỔ PHIẾU cần quét theo yêu cầu
    tickers_list = [
        "HPG", "HSG", "NKG", "VGS",  # Thép
        "DGC", "DPM", "DCM", "CSV", "LAS", "BFC",  # Hóa chất - Phân bón
        "BMP", "NTP",  # Nhựa
        "HT1", "BCC",  # Xi măng
        "GVR", "DPR"   # Cao su
    ]

    # 2. Định nghĩa DANH SÁCH NGUỒN TIN được phép lưu (Lọc dữ liệu rác)
    allowed_sources = [
        "Vietstock", "CafeF", "VnEconomy", "Tin nhanh Chứng khoán",
        "SSI Research", "SSI", "MBS", "VCBS", "KBSV", "VNDirect"
    ]

    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] === BẮT ĐẦU QUY TRÌNH CÀO TỰ ĐỘNG ===")
    total_saved = 0

    # 3. Vòng lặp duyệt qua từng mã cổ phiếu
    for ticker_index, ticker in enumerate(tickers_list, start=1):
        print(f"\n Đang xử lý Mã cổ phiếu [{ticker_index}/{len(tickers_list)}]: '{ticker}'")
        print("=" * 60)

        news_list = get_news(ticker)
        print(f"-> Tìm thấy {len(news_list)} bài báo tiềm năng từ Google News.")

        if not news_list:
            print("-> Không có tin mới cho mã này. Chuyển sang mã tiếp theo.")
            continue

        # 4. Duyệt xử lý từng bài viết tìm được
        for index, news in enumerate(news_list, start=1):
            title = news["title"]
            url = news["link"]

            source = "Google News"
            if " - " in title:
                parts = title.split(" - ")
                source = parts[-1].strip()
                title = " - ".join(parts[:-1]).strip()

            is_valid_source = any(allowed.lower() in source.lower() for allowed in allowed_sources)

            if not is_valid_source:
                print(f"  [{index}] Bỏ qua bài do nguồn không thuộc danh mục yêu cầu ({source}): {title}")
                continue

            print(f"  [{index}] Xử lý bài hợp lệ [Nguồn: {source}]: {title}")

            content = get_article_content(url)
            if not content.strip():
                print("      [!] Nội dung trống hoặc trang chặn scrap. Bỏ qua.\n")
                continue

            print("      -> Đang gửi dữ liệu phân tích qua Gemini AI...")
            ai_analysis = analyze_article(title, content)

            # Lọc bỏ và bỏ qua các bài dính lỗi phân tích
            if ai_analysis is None:
                print(f"      [❌] THẤT BẠI: Toàn bộ API Key đều lỗi hoặc hết hạn mức. Bỏ qua không ghi vào CSV.\n")
                continue

            current_now = datetime.now()
            news_data = {
                "news_id": generate_news_id(url),
                "title": title,
                "summary": ai_analysis.get("summary", ""),
                "content": content,
                "published_date": current_now.strftime("%Y-%m-%d"),
                "source": source,
                "url": url,
                "industry_group": ai_analysis.get("industry_group", "Chưa rõ"),
                "tickers": ai_analysis.get("tickers") if ai_analysis.get("tickers") else ticker,
                "keywords": ai_analysis.get("keywords", ""),
                "event_type": ai_analysis.get("event_type", "Khác"),
                "crawl_time": current_now.strftime("%Y-%m-%d %H:%M:%S")
            }

            save_news(news_data)
            total_saved += 1
            print("-" * 40)

            time.sleep(2)

        print(f"-> Hoàn thành quét mã '{ticker}'. Nghỉ giải lao trước khi sang mã tiếp theo...")
        time.sleep(3)

    print(f"\n=== TIẾN TRÌNH HOÀN TẤT! ĐÃ LỌC VÀ LƯU THÀNH CÔNG {total_saved} BÀI BÁO CHẤT LƯỢNG ===")


if __name__ == "__main__":
    # Chạy trực tiếp một lần duy nhất, phù hợp hoàn hảo với cơ chế Cronjob của GitHub Actions
    main_job()