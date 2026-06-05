import feedparser
import urllib.parse
import googlenewsdecoder  # Import trực tiếp thư viện để gọi hàm an toàn


def get_news(ticker):
    """
    Tìm kiếm tin tức trên Google News theo mã cổ phiếu và định hướng
    quét các nguồn tin lớn (CafeF, Vietstock, VnEconomy, Tin nhanh chứng khoán, SSI, MBS,...)
    """
    # Ép truy vấn tìm đúng mã cổ phiếu và đi kèm các từ khóa nguồn tin lớn để Google tối ưu thuật toán tìm kiếm
    search_query = f'"{ticker}" (CafeF OR Vietstock OR VnEconomy OR "Tin nhanh chứng khoán" OR SSI OR MBS OR VCBS OR KBSV OR VNDirect)'
    encoded_query = urllib.parse.quote(search_query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=vi&gl=VN&ceid=VN:vi"

    feed = feedparser.parse(rss_url)
    results = []

    # Giới hạn lấy tối đa 5 bài báo tiềm năng nhất cho mỗi mã cổ phiếu
    for entry in feed.entries[:5]:
        original_url = entry.link
        try:
            # Sử dụng hàm gnewsdecoder giải mã URL gốc
            decoded_response = googlenewsdecoder.gnewsdecoder(entry.link)

            if decoded_response and isinstance(decoded_response, str) and decoded_response.startswith("http"):
                original_url = decoded_response
            elif isinstance(decoded_response, dict) and decoded_response.get("status") == True:
                original_url = decoded_response.get("decoded_url")
        except Exception:
            pass

        results.append({
            "title": entry.title,
            "link": original_url
        })

    return results