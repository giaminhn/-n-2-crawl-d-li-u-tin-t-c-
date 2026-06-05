import requests
from selectolax.parser import HTMLParser


def get_article_content(url):
    try:
        # Nếu link vẫn dính cấu trúc Google News do giải mã lỗi thì bỏ qua
        if "news.google.com" in url:
            return ""

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        # Tải trang báo gốc
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = response.apparent_encoding  # Sửa lỗi font tiếng Việt bẻ đôi

        # Dùng selectolax lọc thẻ rác và lấy text cực nhanh
        tree = HTMLParser(response.text)

        for tag in tree.css("script, style, iframe, footer, nav, header, noscript"):
            tag.decompose()

        paragraphs = [p.text().strip() for p in tree.css("p") if len(p.text().strip()) > 20]
        text = " ".join(paragraphs)

        return text[:8000]

    except Exception as e:
        print(f"Lỗi khi cào bài viết: {e}")
        return ""