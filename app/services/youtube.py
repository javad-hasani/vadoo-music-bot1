from __future__ import annotations

import asyncio
from pathlib import Path
from urllib.parse import urlparse

from yt_dlp import YoutubeDL

from app.models import Track


class TrackNotFoundError(RuntimeError):
    pass


class TrackTooLongError(RuntimeError):
    pass


class YouTubeResolver:
    def __init__(self, max_minutes: int = 180, cookies_file: Path | None = None) -> None:
        self.max_seconds = max_minutes * 60
        self.cookies_file = cookies_file

    @staticmethod
    def _is_url(value: str) -> bool:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

    def _extract_sync(self, query: str) -> Track:
        source = query if self._is_url(query) else f"ytsearch1:{query}"
        options: dict[str, object] = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "noplaylist": True,
            "format": "bestaudio[protocol^=http]/bestaudio/best",
            "extract_flat": False,
            "socket_timeout": 20,
            "retries": 3,
        }
        if self.cookies_file:
            options["cookiefile"] = str(self.cookies_file)

        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(source, download=False)

        if info and "entries" in info:
            entries = [entry for entry in info.get("entries") or [] if entry]
            info = entries[0] if entries else None
        if not info:
            raise TrackNotFoundError("آهنگی پیدا نشد")

        duration = int(info.get("duration") or 0)
        if duration and duration > self.max_seconds:
            raise TrackTooLongError("مدت آهنگ بیشتر از حد مجاز است")

        stream_url = info.get("url")
        webpage_url = info.get("webpage_url") or info.get("original_url")
        if not stream_url or not webpage_url:
            raise TrackNotFoundError("لینک پخش معتبر دریافت نشد")

        return Track(
            title=str(info.get("title") or "بدون عنوان"),
            webpage_url=str(webpage_url),
            stream_url=str(stream_url),
            duration=duration,
            requested_by="",
            thumbnail=info.get("thumbnail"),
        )

    async def resolve(self, query: str, requested_by: str) -> Track:
        track = await asyncio.to_thread(self._extract_sync, query.strip())
        return Track(
            title=track.title,
            webpage_url=track.webpage_url,
            stream_url=track.stream_url,
            duration=track.duration,
            requested_by=requested_by,
            thumbnail=track.thumbnail,
        )
