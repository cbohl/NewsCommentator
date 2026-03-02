import logging
import sqlite3
from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import DATABASE_URL, create_all
from .routers import articles, chat, health
from .services.pipeline import process_new_articles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def _migrate_feed_column():
    """Add 'feed' column to articles table if it doesn't exist (SQLite only)."""
    db_path = DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("PRAGMA table_info(articles)")
    columns = {row[1] for row in cursor.fetchall()}
    if "feed" not in columns:
        conn.execute("ALTER TABLE articles ADD COLUMN feed TEXT DEFAULT 'world'")
        conn.commit()
        logger.info("Migrated: added 'feed' column to articles table")
    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all()
    _migrate_feed_column()
    scheduler.add_job(process_new_articles, "interval", minutes=60)
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="News Commentator", lifespan=lifespan)

import os

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(articles.router)
app.include_router(chat.router)
app.include_router(health.router)


@app.get("/")
async def root():
    return {"message": "News Commentator API"}
