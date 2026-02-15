"""Transcript endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import func, or_, select

from app.api.deps import ClientIP, DbSession, transcript_rate_limit
from app.models.job import Job
from app.models.transcript import Transcript
from app.models.video import Video
from app.schemas.job import JobResponse
from app.schemas.transcript import (
    TranscriptCreateRequest,
    TranscriptCreateResponse,
    TranscriptExportRequest,
    TranscriptListItem,
    TranscriptListResponse,
    TranscriptResponse,
)
from app.services.exporter import ExporterService
from app.workers.transcribe_task import transcribe_video_task

router = APIRouter()


@router.get("/", response_model=TranscriptListResponse)
async def list_transcripts(
    db: DbSession,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: str | None = Query(None, alias="status"),
    platform: str | None = Query(None),
    search: str | None = Query(None),
) -> TranscriptListResponse:
    """List transcripts with pagination and filters."""
    query = (
        select(
            Transcript.id,
            Transcript.video_id,
            Video.title.label("video_title"),
            Video.author.label("video_author"),
            Video.platform,
            Video.duration,
            Transcript.language,
            Transcript.confidence,
            Job.status.label("job_status"),
            Transcript.created_at,
        )
        .join(Video, Transcript.video_id == Video.id)
        .outerjoin(Job, Transcript.job_id == Job.id)
    )

    count_query = (
        select(func.count(Transcript.id))
        .join(Video, Transcript.video_id == Video.id)
        .outerjoin(Job, Transcript.job_id == Job.id)
    )

    if status_filter:
        query = query.where(Job.status == status_filter)
        count_query = count_query.where(Job.status == status_filter)

    if platform:
        query = query.where(Video.platform == platform)
        count_query = count_query.where(Video.platform == platform)

    if search:
        search_filter = or_(
            Transcript.full_text.ilike(f"%{search}%"),
            Video.title.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Transcript.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    rows = result.all()

    items = [
        TranscriptListItem(
            id=row.id,
            video_id=row.video_id,
            video_title=row.video_title,
            video_author=row.video_author,
            platform=row.platform,
            duration=row.duration,
            language=row.language,
            confidence=row.confidence,
            job_status=row.job_status,
            created_at=row.created_at,
        )
        for row in rows
    ]

    return TranscriptListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/create",
    response_model=TranscriptCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(transcript_rate_limit)],
)
async def create_transcript(
    request: TranscriptCreateRequest,
    db: DbSession,
    client_ip: ClientIP,
) -> TranscriptCreateResponse:
    """Initiate video transcription."""
    # Create job
    job = Job(
        type="transcription",
        status="pending",
        input_data={
            "video_url": str(request.video_url) if request.video_url else None,
            "job_id": str(request.job_id) if request.job_id else None,
        },
        ip_address=client_ip,
    )
    db.add(job)
    await db.flush()

    # Queue background task
    transcribe_video_task.delay(
        job_id=str(job.id),
        video_url=str(request.video_url) if request.video_url else None,
        download_job_id=str(request.job_id) if request.job_id else None,
    )

    return TranscriptCreateResponse(
        job_id=job.id,
        status="processing",
    )


@router.get("/job/{job_id}", response_model=JobResponse)
async def get_transcript_job(
    job_id: UUID,
    db: DbSession,
) -> JobResponse:
    """Get transcription job status."""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    return JobResponse.model_validate(job)


@router.get("/{transcript_id}", response_model=TranscriptResponse)
async def get_transcript(
    transcript_id: UUID,
    db: DbSession,
) -> TranscriptResponse:
    """Get transcript by ID."""
    result = await db.execute(select(Transcript).where(Transcript.id == transcript_id))
    transcript = result.scalar_one_or_none()

    if transcript is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found",
        )

    return TranscriptResponse.model_validate(transcript)


@router.get("/video/{video_id}", response_model=TranscriptResponse)
async def get_transcript_by_video(
    video_id: UUID,
    db: DbSession,
) -> TranscriptResponse:
    """Get transcript by video ID."""
    result = await db.execute(
        select(Transcript)
        .where(Transcript.video_id == video_id)
        .order_by(Transcript.created_at.desc())
    )
    transcript = result.scalar_one_or_none()

    if transcript is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found for this video",
        )

    return TranscriptResponse.model_validate(transcript)


@router.post("/{transcript_id}/export")
async def export_transcript(
    transcript_id: UUID,
    request: TranscriptExportRequest,
    db: DbSession,
) -> Response:
    """Export transcript in specified format."""
    result = await db.execute(select(Transcript).where(Transcript.id == transcript_id))
    transcript = result.scalar_one_or_none()

    if transcript is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found",
        )

    content, mime_type = ExporterService.export(
        format=request.format.value,
        text=transcript.full_text,
        segments=transcript.segments,
        language=transcript.language,
        confidence=transcript.confidence,
        include_timestamps=request.include_timestamps,
    )

    extension = request.format.value
    filename = f"transcript_{transcript_id}.{extension}"

    return Response(
        content=content,
        media_type=mime_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
