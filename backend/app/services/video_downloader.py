"""Video download service using yt-dlp."""

import re
from pathlib import Path
from typing import Any

import yt_dlp

from app.config import get_settings
from app.schemas.video import Platform, VideoQuality

settings = get_settings()


class VideoDownloaderService:
    """Service for downloading videos from supported platforms."""

    QUALITY_MAP = {
        VideoQuality.BEST: "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        VideoQuality.HD_720P: "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]",
        VideoQuality.SD_480P: "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]",
    }

    def __init__(self, storage_path: str | None = None):
        self.storage_path = Path(storage_path or settings.storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def detect_platform(self, url: str) -> Platform:
        """Detect the platform from URL."""
        url_lower = url.lower()
        if "tiktok.com" in url_lower:
            return Platform.TIKTOK
        elif "instagram.com" in url_lower:
            return Platform.INSTAGRAM
        elif "youtube.com" in url_lower or "youtu.be" in url_lower:
            return Platform.YOUTUBE
        raise ValueError(f"Unsupported platform for URL: {url}")

    def extract_video_id(self, url: str, platform: Platform) -> str | None:
        """Extract video ID from URL."""
        patterns = {
            Platform.TIKTOK: r"/video/(\d+)",
            Platform.INSTAGRAM: r"/(?:reel|p)/([A-Za-z0-9_-]+)",
            Platform.YOUTUBE: r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})",
        }
        pattern = patterns.get(platform)
        if pattern:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_metadata(self, url: str) -> dict[str, Any]:
        """Extract video metadata without downloading."""
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info is None:
                raise ValueError("Could not extract video information")
            return {
                "title": info.get("title"),
                "author": info.get("uploader") or info.get("channel"),
                "duration": info.get("duration"),
                "thumbnail_url": info.get("thumbnail"),
                "view_count": info.get("view_count"),
                "like_count": info.get("like_count"),
                "description": info.get("description"),
            }

    def download(
        self,
        url: str,
        quality: VideoQuality = VideoQuality.BEST,
        remove_watermark: bool = True,
    ) -> dict[str, Any]:
        """Download video and return file path with metadata."""
        platform = self.detect_platform(url)
        video_id = self.extract_video_id(url, platform) or "unknown"

        output_template = str(self.storage_path / f"{platform.value}_{video_id}.%(ext)s")

        ydl_opts = {
            "format": self.QUALITY_MAP.get(quality, self.QUALITY_MAP[VideoQuality.BEST]),
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
            "merge_output_format": "mp4",
        }

        # TikTok-specific options for watermark removal
        if platform == Platform.TIKTOK and remove_watermark:
            ydl_opts["extractor_args"] = {"tiktok": {"api_hostname": "api22-normal-c-useast2a.tiktokv.com"}}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info is None:
                raise ValueError("Download failed")

            downloaded_file = ydl.prepare_filename(info)
            # Handle potential format changes
            if not Path(downloaded_file).exists():
                downloaded_file = downloaded_file.rsplit(".", 1)[0] + ".mp4"

            return {
                "file_path": downloaded_file,
                "platform": platform.value,
                "video_id": video_id,
                "title": info.get("title"),
                "author": info.get("uploader") or info.get("channel"),
                "duration": info.get("duration"),
                "thumbnail_url": info.get("thumbnail"),
                "metadata": {
                    "view_count": info.get("view_count"),
                    "like_count": info.get("like_count"),
                    "description": info.get("description"),
                },
            }

    def download_thumbnail(self, url: str) -> str | None:
        """Download video thumbnail."""
        try:
            metadata = self.get_metadata(url)
            thumbnail_url = metadata.get("thumbnail_url")
            if thumbnail_url:
                # Download thumbnail using yt-dlp
                platform = self.detect_platform(url)
                video_id = self.extract_video_id(url, platform) or "unknown"
                output_path = str(self.storage_path / f"{platform.value}_{video_id}_thumb.jpg")

                ydl_opts = {
                    "quiet": True,
                    "skip_download": True,
                    "writethumbnail": True,
                    "outtmpl": output_path.replace("_thumb.jpg", ""),
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                return output_path
        except Exception:
            pass
        return None
