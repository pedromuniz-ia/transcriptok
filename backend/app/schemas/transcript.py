"""Transcript-related schemas."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class ExportFormat(str, Enum):
    """Supported export formats."""

    TXT = "txt"
    JSON = "json"
    SRT = "srt"
    VTT = "vtt"


class TranscriptSegment(BaseModel):
    """A single transcript segment with timing."""

    start: float
    end: float
    text: str


class TranscriptCreateRequest(BaseModel):
    """Request schema for creating a transcript."""

    video_url: HttpUrl | None = None
    job_id: UUID | None = None

    def model_post_init(self, __context: object) -> None:
        """Validate that at least one identifier is provided."""
        if self.video_url is None and self.job_id is None:
            raise ValueError("Either video_url or job_id must be provided")


class TranscriptCreateResponse(BaseModel):
    """Response schema for transcript creation initiation."""

    job_id: UUID
    status: str = "processing"


class TranscriptResponse(BaseModel):
    """Response schema for a completed transcript."""

    id: UUID
    video_id: UUID
    full_text: str
    segments: list[TranscriptSegment] | None = None
    language: str | None = None
    confidence: float | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TranscriptExportRequest(BaseModel):
    """Request schema for exporting a transcript."""

    format: ExportFormat = ExportFormat.TXT
    include_timestamps: bool = True
