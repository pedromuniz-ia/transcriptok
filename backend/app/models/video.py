"""Video model for metadata caching."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Video(Base):
    """Cached video metadata from supported platforms."""

    __tablename__ = "videos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    platform: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )  # tiktok | instagram | youtube
    original_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
    )
    video_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    title: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    author: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    duration: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )  # seconds
    thumbnail_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    transcripts: Mapped[list["Transcript"]] = relationship(
        "Transcript",
        back_populates="video",
        lazy="selectin",
    )
