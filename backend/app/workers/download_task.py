"""Video download Celery task."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.celery import celery_app
from app.models.job import Job
from app.models.video import Video
from app.schemas.video import VideoQuality
from app.services.video_downloader import VideoDownloaderService


def get_sync_session() -> Session:
    """Get synchronous database session for Celery tasks."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.config import get_settings

    settings = get_settings()
    # Convert async URL to sync
    sync_url = settings.database_url.replace("+asyncpg", "")
    engine = create_engine(sync_url)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


@celery_app.task(bind=True, max_retries=3)  # type: ignore[untyped-decorator]
def download_video_task(
    self: Any,
    job_id: str,
    url: str,
    quality: str,
    remove_watermark: bool,
) -> dict[str, Any]:
    """Download video in background."""
    session = get_sync_session()

    try:
        # Update job status
        job = session.execute(select(Job).where(Job.id == job_id)).scalar_one()
        job.status = "processing"
        session.commit()

        # Download video
        service = VideoDownloaderService()
        try:
            quality_enum = VideoQuality(quality)
        except ValueError:
            quality_enum = VideoQuality.BEST
        result = service.download(url, quality_enum, remove_watermark)

        # Check if video already exists
        existing = session.execute(
            select(Video).where(Video.original_url == url)
        ).scalar_one_or_none()

        if existing:
            video = existing
        else:
            # Create video record
            video = Video(
                platform=result["platform"],
                original_url=url,
                video_id=result["video_id"],
                title=result["title"],
                author=result["author"],
                duration=result["duration"],
                thumbnail_url=result["thumbnail_url"],
                video_metadata=result["metadata"],
            )
            session.add(video)
            session.flush()

        # Update job with success
        job.status = "completed"
        job.completed_at = datetime.now(UTC)
        job.output_data = {
            "video_id": str(video.id),
            "file_path": result["file_path"],
            "platform": result["platform"],
            "title": result["title"],
            "author": result["author"],
            "duration": result["duration"],
            "thumbnail_url": result["thumbnail_url"],
        }
        session.commit()

        return {"status": "success", "video_id": str(video.id)}

    except Exception as e:
        session.rollback()

        # Update job with failure
        job = session.execute(select(Job).where(Job.id == job_id)).scalar_one()
        job.status = "failed"
        job.error_message = str(e)
        job.completed_at = datetime.now(UTC)
        session.commit()

        # Retry if possible
        raise self.retry(exc=e, countdown=60) from e

    finally:
        session.close()
