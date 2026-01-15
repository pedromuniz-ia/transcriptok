"""Main API v1 router."""

from fastapi import APIRouter

from app.api.v1 import ai_tools, transcripts, videos

router = APIRouter()

router.include_router(videos.router, prefix="/videos", tags=["videos"])
router.include_router(transcripts.router, prefix="/transcripts", tags=["transcripts"])
router.include_router(ai_tools.router, prefix="/ai", tags=["ai-tools"])
