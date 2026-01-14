"""Job-related schemas."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class JobStatus(str, Enum):
    """Possible job statuses."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobResponse(BaseModel):
    """Response schema for job status."""

    id: UUID
    type: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    output_data: dict[str, Any] | None = None
    error_message: str | None = None

    model_config = {"from_attributes": True}
