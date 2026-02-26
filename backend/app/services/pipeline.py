import json
import logging
import random
import traceback
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..graph.workflow import build_commentary_graph
from ..models import Article, Comment, ErrorLog
from .extractor import extract_full_text
from .rss import fetch_rss_articles

logger = logging.getLogger(__name__)

last_successful_run: datetime | None = None

PERSONAS = ["historian", "economist", "philosopher"]


def process_new_articles(limit: int = 1):
    global last_successful_run
    db: Session = SessionLocal()
    try:
        rss_articles = fetch_rss_articles(limit=limit)
        logger.info("Fetched %d articles from RSS", len(rss_articles))

        for item in rss_articles:
            existing = db.query(Article).filter(
                (Article.guid == item["guid"]) | (Article.url == item["url"])
            ).first()
            if existing:
                logger.info("Skipping duplicate: %s", item["url"])
                continue

            try:
                full_text = extract_full_text(item["url"])

                order = PERSONAS.copy()
                random.shuffle(order)
                logger.info("Execution order for '%s': %s", item["title"], " → ".join(order))

                graph = build_commentary_graph(order)
                result = graph.invoke({
                    "article_title": item["title"],
                    "article_text": full_text,
                    "article_url": item["url"],
                    "historian_comment": "",
                    "economist_comment": "",
                    "philosopher_comment": "",
                    "historian_searches": [],
                    "economist_searches": [],
                    "philosopher_searches": [],
                    "error_flag": False,
                    "execution_order": order,
                })

                article = Article(
                    guid=item["guid"],
                    url=item["url"],
                    title=item["title"],
                    full_text=full_text,
                )
                db.add(article)
                db.flush()

                for position, persona in enumerate(order):
                    searches = result.get(f"{persona}_searches", [])
                    comment = Comment(
                        article_id=article.id,
                        persona=persona,
                        position=position,
                        text=result[f"{persona}_comment"],
                        search_queries=json.dumps(searches) if searches else None,
                    )
                    db.add(comment)

                db.commit()
                logger.info("Processed article: %s", item["title"])

            except Exception:
                db.rollback()
                tb = traceback.format_exc()
                logger.error("Failed to process %s: %s", item["url"], tb)
                error = ErrorLog(
                    article_url=item["url"],
                    error_message=str(tb)[:500],
                    traceback=tb,
                )
                db.add(error)
                db.commit()

        last_successful_run = datetime.now(timezone.utc)

    except Exception:
        tb = traceback.format_exc()
        logger.error("Pipeline failed: %s", tb)
        error = ErrorLog(
            article_url=None,
            error_message="Pipeline-level failure",
            traceback=tb,
        )
        db.add(error)
        db.commit()
    finally:
        db.close()
