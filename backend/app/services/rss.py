import feedparser


BBC_WORLD_RSS_URL = "https://feeds.bbci.co.uk/news/world/rss.xml"


def fetch_rss_articles(url: str = BBC_WORLD_RSS_URL, limit: int = 1) -> list[dict]:
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries:
        articles.append({
            "guid": getattr(entry, "id", entry.link),
            "url": entry.link,
            "title": entry.title,
        })
    return articles[:limit]
