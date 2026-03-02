import json
from datetime import datetime

from pydantic import BaseModel, field_validator, model_validator


class SourceLink(BaseModel):
    url: str
    title: str


class SearchQuery(BaseModel):
    query: str
    source: str
    urls: list[SourceLink] = []

    @model_validator(mode="before")
    @classmethod
    def normalize_url_fields(cls, data):
        if not isinstance(data, dict):
            return data
        # Convert old single "url" string to urls list
        if "url" in data and "urls" not in data:
            url = data.pop("url")
            data["urls"] = [{"url": url, "title": data.get("query", "")}] if url else []
        # Convert old urls-as-plain-strings to {url, title} dicts
        if "urls" in data and data["urls"] and isinstance(data["urls"][0], str):
            data["urls"] = [{"url": u, "title": u} for u in data["urls"]]
        return data


class CommentOut(BaseModel):
    id: int
    persona: str
    position: int
    text: str
    search_queries: list[SearchQuery] = []
    created_at: datetime

    @field_validator("search_queries", mode="before")
    @classmethod
    def parse_search_queries(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            v = json.loads(v)
        # Backwards compat: convert old list[str] to list[dict]
        if v and isinstance(v[0], str):
            return [{"query": s, "source": "Web"} for s in v]
        return v

    model_config = {"from_attributes": True}


class ArticleOut(BaseModel):
    id: int
    guid: str
    url: str
    title: str
    feed: str
    created_at: datetime
    comments: list[CommentOut]

    model_config = {"from_attributes": True}
