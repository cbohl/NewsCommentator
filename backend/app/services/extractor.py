import httpx

JINA_READER_PREFIX = "https://r.jina.ai/"


def extract_full_text(article_url: str) -> str:
    jina_url = f"{JINA_READER_PREFIX}{article_url}"
    response = httpx.get(jina_url, timeout=60.0, headers={"Accept": "text/plain"})
    response.raise_for_status()
    return response.text
