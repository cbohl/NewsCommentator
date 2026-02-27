import random

import feedparser


BBC_FEEDS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.bbci.co.uk/news/business/rss.xml",
]


def fetch_rss_articles(limit: int = 1) -> list[dict]:
    seen_guids = set()
    articles = []
    for url in BBC_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            guid = getattr(entry, "id", entry.link)
            if guid in seen_guids:
                continue
            # Skip non-article content (podcasts, audio, video)
            if "/audio/" in entry.link or "/sounds/" in entry.link or "/video/" in entry.link:
                continue
            seen_guids.add(guid)
            articles.append({
                "guid": guid,
                "url": entry.link,
                "title": entry.title,
            })
    random.shuffle(articles)
    return articles[:limit]
