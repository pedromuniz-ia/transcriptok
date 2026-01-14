#!/usr/bin/env python3
"""Validate that all imports and configurations work correctly."""

import sys

def main():
    errors = []

    print("🔍 Validating imports...")

    # Test core imports
    try:
        from app.config import get_settings
        print("  ✓ app.config")
    except Exception as e:
        errors.append(f"app.config: {e}")
        print(f"  ✗ app.config: {e}")

    # Test models
    try:
        from app.models import Job, Video, Transcript
        print("  ✓ app.models")
    except Exception as e:
        errors.append(f"app.models: {e}")
        print(f"  ✗ app.models: {e}")

    # Test schemas
    try:
        from app.schemas import VideoCreate, TranscriptCreate, JobResponse
        print("  ✓ app.schemas")
    except Exception as e:
        errors.append(f"app.schemas: {e}")
        print(f"  ✗ app.schemas: {e}")

    # Test services
    try:
        from app.services.video_downloader import VideoDownloaderService
        from app.services.transcriber import TranscriberService
        from app.services.exporter import ExporterService
        from app.services.ai_agent import AIAgentService
        print("  ✓ app.services")
    except Exception as e:
        errors.append(f"app.services: {e}")
        print(f"  ✗ app.services: {e}")

    # Test workers (celery tasks)
    try:
        from app.workers.download_task import download_video_task
        from app.workers.transcribe_task import transcribe_video_task
        print("  ✓ app.workers")
    except Exception as e:
        errors.append(f"app.workers: {e}")
        print(f"  ✗ app.workers: {e}")

    # Test API routes
    try:
        from app.api.v1 import router
        print("  ✓ app.api.v1")
    except Exception as e:
        errors.append(f"app.api.v1: {e}")
        print(f"  ✗ app.api.v1: {e}")

    # Test main app
    try:
        from app.main import app
        print("  ✓ app.main")
    except Exception as e:
        errors.append(f"app.main: {e}")
        print(f"  ✗ app.main: {e}")

    print()
    if errors:
        print(f"❌ Validation failed with {len(errors)} error(s)")
        for error in errors:
            print(f"   - {error}")
        sys.exit(1)
    else:
        print("✅ All validations passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()
