from datetime import datetime

from pydantic import BaseModel


class CommentOut(BaseModel):
    id: int
    persona: str
    position: int
    text: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ArticleOut(BaseModel):
    id: int
    guid: str
    url: str
    title: str
    created_at: datetime
    comments: list[CommentOut]

    model_config = {"from_attributes": True}
