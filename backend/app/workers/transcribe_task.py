"""Transcription Celery task."""

import asyncio
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.celery import celery_app
from app.models.job import Job
from app.models.video import Video
from app.models.transcript import Transcript
from app.services.video_downloader import VideoDownloaderService
from app.services.transcriber import TranscriberService


def get_sync_session() -> Session:
    """Get synchronous database session for Celery tasks."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.config import get_settings

    settings = get_settings()
    sync_url = settings.database_url.replace("+asyncpg", "")
    engine = create_engine(sync_url)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


@celery_app.task(bind=True, max_retries=3)
def transcribe_video_task(
    self,
    job_id: str,
    video_url: str | None = None,
    download_job_id: str | None = None,
) -> dict:
    """Transcribe video in background."""
    session = get_sync_session()

    try:
        # Update job status
        job = session.execute(select(Job).where(Job.id == job_id)).scalar_one()
        job.status = "processing"
        session.commit()

        video_path = None
        video_id = None

        # Get video file path
        if download_job_id:
            # Get from previous download job
            download_job = session.execute(
                select(Job).where(Job.id == download_job_id)
            ).scalar_one_or_none()

            if download_job and download_job.output_data:
                video_path = download_job.output_data.get("file_path")
                video_id = download_job.output_data.get("video_id")

        if not video_path and video_url:
            # Download video first
            downloader = VideoDownloaderService()
            result = downloader.download(video_url)
            video_path = result["file_path"]

            # Check/create video record
            existing = session.execute(
                select(Video).where(Video.original_url == video_url)
            ).scalar_one_or_none()

            if existing:
                video_id = str(existing.id)
            else:
                video = Video(
                    platform=result["platform"],
                    original_url=video_url,
                    video_id=result["video_id"],
                    title=result["title"],
                    author=result["author"],
                    duration=result["duration"],
                    thumbnail_url=result["thumbnail_url"],
                    video_metadata=result["metadata"],
                )
                session.add(video)
                session.flush()
                video_id = str(video.id)

        if not video_path:
            raise ValueError("No video file available for transcription")

        # Run transcription (async service in sync context)
        transcriber = TranscriberService()
        result = asyncio.run(transcriber.transcribe(video_path))

        # Create transcript record
        transcript = Transcript(
            video_id=video_id,
            job_id=job_id,
            full_text=result["text"],
            segments=result["segments"],
            language=result["language"],
            confidence=result["confidence"],
        )
        session.add(transcript)
        session.flush()

        # Update job with success
        job.status = "completed"
        job.completed_at = datetime.now(timezone.utc)
        job.output_data = {
            "transcript_id": str(transcript.id),
            "video_id": video_id,
            "text": result["text"],
            "language": result["language"],
            "confidence": result["confidence"],
            "segment_count": len(result["segments"]) if result["segments"] else 0,
        }
        session.commit()

        return {"status": "success", "transcript_id": str(transcript.id)}

    except Exception as e:
        session.rollback()

        # Update job with failure
        job = session.execute(select(Job).where(Job.id == job_id)).scalar_one()
        job.status = "failed"
        job.error_message = str(e)
        job.completed_at = datetime.now(timezone.utc)
        session.commit()

        raise self.retry(exc=e, countdown=60)

    finally:
        session.close()
