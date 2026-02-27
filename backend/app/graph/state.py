from typing import TypedDict


class CommentaryState(TypedDict):
    article_title: str
    article_text: str
    article_url: str
    historian_comment: str
    economist_comment: str
    philosopher_comment: str
    historian_searches: list[dict]
    economist_searches: list[dict]
    philosopher_searches: list[dict]
    error_flag: bool
    execution_order: list[str]
