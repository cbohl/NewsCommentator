from typing import TypedDict


class CommentaryState(TypedDict):
    article_title: str
    article_text: str
    article_url: str
    historian_comment: str
    economist_comment: str
    philosopher_comment: str
    error_flag: bool
    execution_order: list[str]
