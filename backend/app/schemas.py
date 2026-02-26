import json
from datetime import datetime

from pydantic import BaseModel, field_validator


class CommentOut(BaseModel):
    id: int
    persona: str
    position: int
    text: str
    search_queries: list[str] = []
    created_at: datetime

    @field_validator("search_queries", mode="before")
    @classmethod
    def parse_search_queries(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return json.loads(v)
        return v

    model_config = {"from_attributes": True}


class ArticleOut(BaseModel):
    id: int
    guid: str
    url: str
    title: str
    created_at: datetime
    comments: list[CommentOut]

    model_config = {"from_attributes": True}
