"""Pydantic schemas for API request/response validation."""

from app.schemas.video import (
    VideoDownloadRequest,
    VideoDownloadResponse,
    VideoMetadata,
)
from app.schemas.transcript import (
    TranscriptCreateRequest,
    TranscriptResponse,
    TranscriptSegment,
    ExportFormat,
)
from app.schemas.ai_tools import (
    AIToolRequest,
    AIToolResponse,
    HookGeneratorInput,
    ScriptRewriterInput,
)
from app.schemas.job import JobResponse, JobStatus

__all__ = [
    "VideoDownloadRequest",
    "VideoDownloadResponse",
    "VideoMetadata",
    "TranscriptCreateRequest",
    "TranscriptResponse",
    "TranscriptSegment",
    "ExportFormat",
    "AIToolRequest",
    "AIToolResponse",
    "HookGeneratorInput",
    "ScriptRewriterInput",
    "JobResponse",
    "JobStatus",
]
