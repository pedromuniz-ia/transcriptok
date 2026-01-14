"""Export service for transcripts in various formats."""

import json
from typing import Any


class ExporterService:
    """Service for exporting transcripts to various formats."""

    @staticmethod
    def to_txt(text: str, segments: list[dict[str, Any]] | None = None, include_timestamps: bool = False) -> str:
        """Export to plain text format."""
        if not include_timestamps or not segments:
            return text

        lines = []
        for segment in segments:
            timestamp = ExporterService._format_timestamp(segment["start"])
            lines.append(f"[{timestamp}] {segment['text']}")
        return "\n".join(lines)

    @staticmethod
    def to_json(
        text: str,
        segments: list[dict[str, Any]] | None = None,
        language: str | None = None,
        confidence: float | None = None,
    ) -> str:
        """Export to JSON format."""
        data = {
            "text": text,
            "language": language,
            "confidence": confidence,
            "segments": segments or [],
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    def to_srt(segments: list[dict[str, Any]]) -> str:
        """Export to SRT subtitle format."""
        if not segments:
            return ""

        lines = []
        for i, segment in enumerate(segments, 1):
            start = ExporterService._format_srt_timestamp(segment["start"])
            end = ExporterService._format_srt_timestamp(segment["end"])
            lines.append(str(i))
            lines.append(f"{start} --> {end}")
            lines.append(segment["text"])
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def to_vtt(segments: list[dict[str, Any]]) -> str:
        """Export to WebVTT subtitle format."""
        if not segments:
            return "WEBVTT\n"

        lines = ["WEBVTT", ""]
        for segment in segments:
            start = ExporterService._format_vtt_timestamp(segment["start"])
            end = ExporterService._format_vtt_timestamp(segment["end"])
            lines.append(f"{start} --> {end}")
            lines.append(segment["text"])
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """Format timestamp as MM:SS."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    @staticmethod
    def _format_srt_timestamp(seconds: float) -> str:
        """Format timestamp for SRT (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    @staticmethod
    def _format_vtt_timestamp(seconds: float) -> str:
        """Format timestamp for VTT (HH:MM:SS.mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

    @staticmethod
    def export(
        format: str,
        text: str,
        segments: list[dict[str, Any]] | None = None,
        language: str | None = None,
        confidence: float | None = None,
        include_timestamps: bool = True,
    ) -> tuple[str, str]:
        """Export transcript to specified format. Returns (content, mime_type)."""
        format = format.lower()

        if format == "txt":
            content = ExporterService.to_txt(text, segments, include_timestamps)
            return content, "text/plain"

        elif format == "json":
            content = ExporterService.to_json(text, segments, language, confidence)
            return content, "application/json"

        elif format == "srt":
            if not segments:
                raise ValueError("Segments required for SRT export")
            content = ExporterService.to_srt(segments)
            return content, "application/x-subrip"

        elif format == "vtt":
            if not segments:
                raise ValueError("Segments required for VTT export")
            content = ExporterService.to_vtt(segments)
            return content, "text/vtt"

        else:
            raise ValueError(f"Unsupported format: {format}")
