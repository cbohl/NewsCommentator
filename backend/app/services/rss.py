import feedparser


REUTERS_RSS_URL = "https://www.rss.reuters.com/news/world"


def fetch_rss_articles(url: str = REUTERS_RSS_URL) -> list[dict]:
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries:
        articles.append({
            "guid": getattr(entry, "id", entry.link),
            "url": entry.link,
            "title": entry.title,
        })
    return articles
