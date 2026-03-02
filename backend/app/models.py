from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    guid: Mapped[str] = mapped_column(String, unique=True, index=True)
    url: Mapped[str] = mapped_column(String, unique=True)
    title: Mapped[str] = mapped_column(String)
    full_text: Mapped[str] = mapped_column(Text)
    feed: Mapped[str] = mapped_column(String, default="world", index=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    comments: Mapped[list["Comment"]] = relationship(
        back_populates="article", order_by="Comment.position"
    )


class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = (
        UniqueConstraint("article_id", "persona", name="uq_article_persona"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"))
    persona: Mapped[str] = mapped_column(String)  # historian | economist | philosopher
    position: Mapped[int] = mapped_column(default=0)  # execution order: 0, 1, 2
    text: Mapped[str] = mapped_column(Text)
    search_queries: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    article: Mapped["Article"] = relationship(back_populates="comments")


class ErrorLog(Base):
    __tablename__ = "error_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    article_url: Mapped[str | None] = mapped_column(String, nullable=True)
    error_message: Mapped[str] = mapped_column(Text)
    traceback: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
