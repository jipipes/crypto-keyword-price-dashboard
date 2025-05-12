import feedparser
from datetime import datetime
import os
import pandas as pd

# ❶ 수집할 RSS 피드 목록
RSS_FEEDS = [
    "https://cointelegraph.com/rss",
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cryptoslate.com/feed/",
    "https://www.blockmedia.co.kr/feed"
]

def fetch_news():
    """각 RSS 피드를 읽어서 뉴스 아이템을 DataFrame으로 반환"""
    news_items = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            news_items.append({
                "title": entry.title,
                "summary": entry.get("summary", ""),
                "link": entry.link,
                "published": entry.get("published", ""),
                "source": url
            })
    return pd.DataFrame(news_items)

def save_news(df):
    """DataFrame을 CSV 파일로 저장"""
    now = datetime.now().strftime("%Y%m%d_%H%M")
    os.makedirs("data/news", exist_ok=True)
    path = f"data/news/news_{now}.csv"
    df.to_csv(path, index=False)
    print(f"✅ 뉴스 {len(df)}건 저장 완료: {path}")

if __name__ == "__main__":
    df = fetch_news()
    save_news(df)
