from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Article
from ..schemas import ArticleOut
from ..services.pipeline import process_new_articles

router = APIRouter()


@router.get("/articles", response_model=list[ArticleOut])
async def list_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    feed: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Article)
    if feed is not None:
        query = query.filter(Article.feed == feed)
    articles = (
        query
        .order_by(Article.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return articles


@router.get("/articles/{article_id}", response_model=ArticleOut)
async def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.post("/trigger")
async def trigger_pipeline(
    limit: int = Query(5, ge=1, le=30),
    feed: str | None = Query(None),
):
    process_new_articles(limit=limit, feed=feed)
    return {"status": "pipeline triggered", "limit": limit, "feed": feed}
