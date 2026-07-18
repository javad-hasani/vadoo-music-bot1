from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Track:
    title: str
    webpage_url: str
    stream_url: str
    duration: int
    requested_by: str
    thumbnail: str | None = None

    @property
    def duration_text(self) -> str:
        minutes, seconds = divmod(max(0, self.duration), 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:02d}:{seconds:02d}"
