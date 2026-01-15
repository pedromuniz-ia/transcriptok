# TranscripTok Backend

FastAPI backend for video transcription and AI analysis.

## Setup

```bash
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

## API Docs

- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Docs visibility follows `DEBUG` by default. To force-enable docs when `DEBUG=false` (e.g., in production), set env `DOCS_ENABLED=true`.
