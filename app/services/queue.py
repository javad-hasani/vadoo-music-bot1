from __future__ import annotations

import asyncio
from collections import deque

from app.models import Track


class QueueFullError(RuntimeError):
    pass


class MusicQueue:
    """صف مستقل برای هر گفت‌وگو با قفل async."""

    def __init__(self, max_size: int = 50) -> None:
        self._queues: dict[int, deque[Track]] = {}
        self._current: dict[int, Track] = {}
        self._locks: dict[int, asyncio.Lock] = {}
        self.max_size = max_size

    def _lock(self, chat_id: int) -> asyncio.Lock:
        return self._locks.setdefault(chat_id, asyncio.Lock())

    async def add(self, chat_id: int, track: Track) -> int:
        async with self._lock(chat_id):
            queue = self._queues.setdefault(chat_id, deque())
            if len(queue) >= self.max_size:
                raise QueueFullError("صف پر است")
            queue.append(track)
            return len(queue)

    async def pop_next(self, chat_id: int) -> Track | None:
        async with self._lock(chat_id):
            queue = self._queues.setdefault(chat_id, deque())
            track = queue.popleft() if queue else None
            if track is None:
                self._current.pop(chat_id, None)
            else:
                self._current[chat_id] = track
            return track

    async def set_current(self, chat_id: int, track: Track | None) -> None:
        async with self._lock(chat_id):
            if track is None:
                self._current.pop(chat_id, None)
            else:
                self._current[chat_id] = track

    async def current(self, chat_id: int) -> Track | None:
        async with self._lock(chat_id):
            return self._current.get(chat_id)

    async def snapshot(self, chat_id: int) -> list[Track]:
        async with self._lock(chat_id):
            return list(self._queues.get(chat_id, ()))

    async def clear(self, chat_id: int) -> None:
        async with self._lock(chat_id):
            self._queues.pop(chat_id, None)
            self._current.pop(chat_id, None)
