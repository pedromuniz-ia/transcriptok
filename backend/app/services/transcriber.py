"""Transcription service using Whisper (local or API)."""

import subprocess
from pathlib import Path
from typing import Any

from app.config import get_settings

settings = get_settings()


class TranscriberService:
    """Service for transcribing audio using Whisper."""

    def __init__(self) -> None:
        self.mode = settings.whisper_mode
        self.model = settings.whisper_model
        self._local_model: Any | None = None

    def _get_local_model(self) -> Any:
        """Lazy load local Whisper model."""
        if self._local_model is None:
            import whisper
            self._local_model = whisper.load_model(self.model)
        return self._local_model

    def extract_audio(self, video_path: str) -> str:
        """Extract audio from video using FFmpeg."""
        video_path_obj = Path(video_path)
        audio_path = video_path_obj.with_suffix(".mp3")

        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-vn",  # No video
            "-acodec", "libmp3lame",
            "-ar", "16000",  # 16kHz sample rate for Whisper
            "-ac", "1",  # Mono
            "-y",  # Overwrite
            str(audio_path),
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return str(audio_path)

    def transcribe_local(self, audio_path: str) -> dict[str, Any]:
        """Transcribe using local Whisper model."""
        model = self._get_local_model()
        result = model.transcribe(
            audio_path,
            verbose=False,
            word_timestamps=True,
        )

        segments = [
            {
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip(),
            }
            for segment in result.get("segments", [])
        ]

        return {
            "text": result["text"].strip(),
            "segments": segments,
            "language": result.get("language"),
            "confidence": self._calculate_confidence(result),
        }

    async def transcribe_api(self, audio_path: str) -> dict[str, Any]:
        """Transcribe using OpenAI Whisper API."""
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)

        with open(audio_path, "rb") as audio_file:
            # Get transcription with timestamps
            response = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"],
            )

        segments = [
            {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
            }
            for segment in (response.segments or [])
        ]

        return {
            "text": response.text.strip(),
            "segments": segments,
            "language": response.language,
            "confidence": None,  # API doesn't provide confidence
        }

    async def transcribe(self, video_path: str) -> dict[str, Any]:
        """Transcribe video file."""
        # Extract audio first
        audio_path = self.extract_audio(video_path)

        try:
            if self.mode == "api":
                result = await self.transcribe_api(audio_path)
            else:
                result = self.transcribe_local(audio_path)
            return result
        finally:
            # Cleanup audio file
            Path(audio_path).unlink(missing_ok=True)

    def _calculate_confidence(self, result: dict[str, Any]) -> float | None:
        """Calculate average confidence from segments."""
        segments = result.get("segments", [])
        if not isinstance(segments, list) or not segments:
            return None

        probs: list[float] = []
        for segment in segments:
            if isinstance(segment, dict):
                prob = segment.get("no_speech_prob")
                if isinstance(prob, (int, float)):
                    # Convert no_speech_prob to speech confidence
                    probs.append(1.0 - float(prob))

        if probs:
            return sum(probs) / len(probs)
        return None
