import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from .database import create_all
from .routers import articles, health
from .services.pipeline import process_new_articles

logging.basicConfig(level=logging.INFO)

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all()
    scheduler.add_job(process_new_articles, "interval", minutes=60)
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="News Commentator", lifespan=lifespan)

app.include_router(articles.router)
app.include_router(health.router)


@app.get("/")
async def root():
    return {"message": "News Commentator API"}
