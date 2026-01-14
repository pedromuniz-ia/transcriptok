"""Video download Celery task."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.celery import celery_app
from app.models.job import Job
from app.models.video import Video
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


@celery_app.task(bind=True, max_retries=3)
def download_video_task(
    self,
    job_id: str,
    url: str,
    quality: str,
    remove_watermark: bool,
) -> dict:
    """Download video in background."""
    session = get_sync_session()

    try:
        # Update job status
        job = session.execute(select(Job).where(Job.id == job_id)).scalar_one()
        job.status = "processing"
        session.commit()

        # Download video
        service = VideoDownloaderService()
        result = service.download(url, quality, remove_watermark)

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
                metadata=result["metadata"],
            )
            session.add(video)
            session.flush()

        # Update job with success
        job.status = "completed"
        job.completed_at = datetime.now(timezone.utc)
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
        job.completed_at = datetime.now(timezone.utc)
        session.commit()

        # Retry if possible
        raise self.retry(exc=e, countdown=60)

    finally:
        session.close()
