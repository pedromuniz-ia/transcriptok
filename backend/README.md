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

## Tests

Tests require Postgres because models use JSONB. Provide a test database and set:

```bash
TEST_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/transcriptok_test"
python -m pytest
```

Example using Docker locally:

```bash
docker run --rm -p 5432:5432 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=transcriptok_test \
  postgres:15-alpine
```
