import random

import feedparser


FEEDS = {
    "business": "https://feeds.bbci.co.uk/news/business/rss.xml",
    "technology": "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "world": "https://feeds.bbci.co.uk/news/world/rss.xml",
}


def _parse_feed(url: str, feed_name: str, limit: int) -> list[dict]:
    seen_guids: set[str] = set()
    articles: list[dict] = []
    feed = feedparser.parse(url)
    for entry in feed.entries:
        guid = getattr(entry, "id", entry.link)
        if guid in seen_guids:
            continue
        if "/audio/" in entry.link or "/sounds/" in entry.link or "/video/" in entry.link:
            continue
        seen_guids.add(guid)
        articles.append({
            "guid": guid,
            "url": entry.link,
            "title": entry.title,
            "feed": feed_name,
        })
    random.shuffle(articles)
    return articles[:limit]


def fetch_rss_articles(limit: int = 1, feed: str | None = None) -> list[dict]:
    if feed is not None:
        url = FEEDS.get(feed)
        if url is None:
            raise ValueError(f"Unknown feed: {feed!r}. Valid feeds: {list(FEEDS)}")
        return _parse_feed(url, feed, limit)

    articles: list[dict] = []
    for name, url in FEEDS.items():
        articles.extend(_parse_feed(url, name, limit))
    return articles
