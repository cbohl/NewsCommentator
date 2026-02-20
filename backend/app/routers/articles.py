from fastapi import APIRouter

from ..services.pipeline import process_new_articles

router = APIRouter()


@router.post("/trigger")
async def trigger_pipeline():
    process_new_articles()
    return {"status": "pipeline triggered"}
