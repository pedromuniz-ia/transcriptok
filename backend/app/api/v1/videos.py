"""Video download endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.api.deps import ClientIP, DbSession, download_rate_limit
from app.models.job import Job
from app.models.video import Video
from app.schemas.job import JobResponse
from app.schemas.video import VideoDownloadRequest, VideoDownloadResponse, VideoMetadata
from app.workers.download_task import download_video_task

router = APIRouter()


@router.post(
    "/download",
    response_model=VideoDownloadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(download_rate_limit)],
)
async def download_video(
    request: VideoDownloadRequest,
    db: DbSession,
    client_ip: ClientIP,
) -> VideoDownloadResponse:
    """Initiate video download."""
    # Check if video was already processed
    existing = await db.execute(
        select(Video).where(Video.original_url == str(request.url))
    )
    existing_video = existing.scalar_one_or_none()

    # Create job
    job = Job(
        type="download",
        status="pending",
        input_data={
            "url": str(request.url),
            "quality": request.quality.value,
            "remove_watermark": request.remove_watermark,
        },
        ip_address=client_ip,
    )
    db.add(job)
    await db.flush()

    # Queue background task
    download_video_task.delay(
        job_id=str(job.id),
        url=str(request.url),
        quality=request.quality.value,
        remove_watermark=request.remove_watermark,
    )

    return VideoDownloadResponse(
        job_id=job.id,
        status="processing",
        estimated_time=15 if existing_video is None else 5,
    )


@router.get("/job/{job_id}", response_model=JobResponse)
async def get_download_job(
    job_id: UUID,
    db: DbSession,
) -> JobResponse:
    """Get download job status."""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    return JobResponse.model_validate(job)


@router.get("/{video_id}", response_model=VideoMetadata)
async def get_video(
    video_id: UUID,
    db: DbSession,
) -> VideoMetadata:
    """Get video metadata."""
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()

    if video is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )

    return VideoMetadata.model_validate(video)
