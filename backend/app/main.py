from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import create_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all()
    yield


app = FastAPI(title="News Commentator", lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "News Commentator API"}
