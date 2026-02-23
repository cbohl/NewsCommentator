import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

import os

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(articles.router)
app.include_router(health.router)


@app.get("/")
async def root():
    return {"message": "News Commentator API"}
