#!/usr/bin/env python3
"""Validate that all imports and configurations work correctly."""

import importlib
import sys


def _check(label: str, module_path: str, attrs: list[str] | None = None) -> str | None:
    """Attempt to import a module and access selected attributes."""
    try:
        module = importlib.import_module(module_path)
        if attrs:
            for attr in attrs:
                getattr(module, attr)
        print(f"[OK] {label}")
        return None
    except Exception as exc:  # pragma: no cover - utility script
        message = f"{label}: {exc}"
        print(f"[ERR] {message}")
        return message


def main() -> None:
    errors: list[str] = []

    print("Validating imports...")

    checks = [
        ("app.config", "app.config", ["get_settings"]),
        ("app.models", "app.models", ["Job", "Transcript", "Video"]),
        ("app.schemas", "app.schemas", None),
        (
            "app.services",
            "app.services",
            [
                "AIAgentService",
                "ExporterService",
                "TranscriberService",
                "VideoDownloaderService",
            ],
        ),
        ("app.workers.download_task", "app.workers.download_task", ["download_video_task"]),
        ("app.workers.transcribe_task", "app.workers.transcribe_task", ["transcribe_video_task"]),
        ("app.api.v1", "app.api.v1", ["router"]),
        ("app.main", "app.main", ["app"]),
    ]

    for label, module_path, attrs in checks:
        result = _check(label, module_path, attrs)
        if result:
            errors.append(result)

    print()
    if errors:
        print(f"Validation failed with {len(errors)} error(s)")
        for error in errors:
            print(f" - {error}")
        sys.exit(1)

    print("All validations passed!")
    sys.exit(0)


if __name__ == "__main__":
    main()
