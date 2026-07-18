from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pytgcalls import PyTgCalls
else:
    PyTgCalls = Any

from app.models import Track
from app.services.queue import MusicQueue


class MusicPlayer:
    def __init__(self, calls: PyTgCalls, queue: MusicQueue) -> None:
        self.calls = calls
        self.queue = queue

    async def enqueue_or_play(self, chat_id: int, track: Track) -> tuple[str, int]:
        current = await self.queue.current(chat_id)
        if current is not None:
            position = await self.queue.add(chat_id, track)
            return "queued", position
        await self.queue.set_current(chat_id, track)
        try:
            await self.calls.play(chat_id, track.stream_url)
        except Exception:
            await self.queue.set_current(chat_id, None)
            raise
        return "playing", 0

    async def skip(self, chat_id: int) -> Track | None:
        next_track = await self.queue.pop_next(chat_id)
        if next_track is None:
            try:
                await self.calls.leave_call(chat_id)
            finally:
                await self.queue.set_current(chat_id, None)
            return None
        await self.calls.play(chat_id, next_track.stream_url)
        return next_track

    async def stop(self, chat_id: int) -> None:
        await self.queue.clear(chat_id)
        await self.calls.leave_call(chat_id)

    async def pause(self, chat_id: int) -> None:
        await self.calls.pause(chat_id)

    async def resume(self, chat_id: int) -> None:
        await self.calls.resume(chat_id)

    async def volume(self, chat_id: int, value: int) -> None:
        await self.calls.change_volume_call(chat_id, value)
