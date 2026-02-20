from fastapi import APIRouter

from ..services.pipeline import last_successful_run

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "last_successful_run": last_successful_run.isoformat() if last_successful_run else None,
    }
