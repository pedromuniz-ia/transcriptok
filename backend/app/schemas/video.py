"""Video-related schemas."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, HttpUrl, field_validator


class VideoQuality(str, Enum):
    """Video quality options."""

    BEST = "best"
    HD_720P = "720p"
    SD_480P = "480p"


class Platform(str, Enum):
    """Supported video platforms."""

    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"


class VideoDownloadRequest(BaseModel):
    """Request schema for video download."""

    url: HttpUrl
    quality: VideoQuality = VideoQuality.BEST
    remove_watermark: bool = True

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: HttpUrl) -> HttpUrl:
        """Validate that URL is from a supported platform."""
        url_str = str(v).lower()
        supported = ["tiktok.com", "instagram.com", "youtube.com", "youtu.be"]
        if not any(domain in url_str for domain in supported):
            raise ValueError("URL must be from TikTok, Instagram, or YouTube")
        return v


class VideoDownloadResponse(BaseModel):
    """Response schema for video download initiation."""

    job_id: UUID
    status: str = "processing"
    estimated_time: int = 15  # seconds


class VideoMetadata(BaseModel):
    """Video metadata schema."""

    id: UUID
    platform: Platform
    original_url: str
    video_id: str | None = None
    title: str | None = None
    author: str | None = None
    duration: int | None = None
    thumbnail_url: str | None = None
    metadata: dict[str, Any] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
