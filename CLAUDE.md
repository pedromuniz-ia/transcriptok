# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TranscripTok is an open-source platform for automatic transcription, download, and AI analysis of short-form videos (TikTok, Instagram Reels, YouTube Shorts). Monorepo with Python backend and Next.js frontend.

## Tech Stack

**Backend (Python 3.11+):** FastAPI, SQLAlchemy 2.0 (async), yt-dlp, Whisper, Agno, PostgreSQL, Celery + Redis, Pydantic v2

**Frontend (Node 20+):** Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS, TanStack Query, Zustand

## Development Commands

### Backend
```bash
cd backend
pip install -e ".[dev]"           # Install with dev dependencies
uvicorn app.main:app --reload     # Run dev server (port 8000)
pytest                            # Run tests
pytest --cov                      # Run tests with coverage
alembic upgrade head              # Run migrations
alembic revision --autogenerate -m "description"  # Create migration
celery -A app.core.celery worker --loglevel=info  # Run Celery worker
```

### Frontend
```bash
cd frontend
npm install                       # Install dependencies
npm run dev                       # Run dev server (port 3000)
npm run build                     # Production build
npm run lint                      # Lint code
npm run type-check                # TypeScript check
```

### Docker (Full Stack)
```bash
docker-compose up -d              # Start all services
docker-compose logs -f backend    # View backend logs
docker-compose down               # Stop all services
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                       │
│         /app/page.tsx → VideoInput → TranscriptResult       │
└───────────────────────────┬─────────────────────────────────┘
                            │ REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                        │
│  api/v1/videos.py ──┬── api/v1/transcripts.py               │
│                     └── api/v1/ai_tools.py                  │
│         │                    │                              │
│  services/video_downloader ─ services/transcriber           │
│  services/ai_agent ───────── services/exporter              │
│         │                    │                              │
│         └───────── workers/ (Celery) ───────────┘           │
└───────────────────────────┬─────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
    PostgreSQL           Redis            Storage
    (metadata)          (queue)         (video files)
```

## Key Patterns

**API Layer:** Routes in `app/api/v1/`, dependencies in `app/api/deps.py` (rate limiting, DB session)

**Service Layer:** Business logic in `app/services/`, stateless, injected via FastAPI dependencies

**Background Jobs:** Celery tasks in `app/workers/`, sync DB sessions (not async), poll for status via API

**Frontend State:** Server state with TanStack Query, local state with Zustand, custom hooks in `src/hooks/`

## Database

Models in `app/models/` using SQLAlchemy 2.0 declarative style with `Mapped[]` types. Migrations via Alembic in `backend/alembic/`.

Key tables: `jobs` (async task tracking), `videos` (metadata cache), `transcripts` (results)

## Environment Variables

Backend: `DATABASE_URL`, `REDIS_URL`, `WHISPER_MODE` (local|api), `OPENAI_API_KEY`

Frontend: `NEXT_PUBLIC_API_URL`

Copy `.env.example` files in each directory.
