import pytest

from app.models import Track
from app.services.player import MusicPlayer
from app.services.queue import MusicQueue


class FakeCalls:
    def __init__(self) -> None:
        self.actions = []

    async def play(self, chat_id, url): self.actions.append(("play", chat_id, url))
    async def leave_call(self, chat_id): self.actions.append(("leave", chat_id))
    async def pause(self, chat_id): self.actions.append(("pause", chat_id))
    async def resume(self, chat_id): self.actions.append(("resume", chat_id))
    async def change_volume_call(self, chat_id, value): self.actions.append(("volume", chat_id, value))


def track(name: str) -> Track:
    return Track(name, "https://example.com", f"https://stream/{name}", 120, "tester")


@pytest.mark.asyncio
async def test_play_then_queue_then_skip() -> None:
    calls = FakeCalls()
    player = MusicPlayer(calls, MusicQueue())
    assert await player.enqueue_or_play(10, track("a")) == ("playing", 0)
    assert await player.enqueue_or_play(10, track("b")) == ("queued", 1)
    next_track = await player.skip(10)
    assert next_track and next_track.title == "b"
    assert calls.actions == [
        ("play", 10, "https://stream/a"),
        ("play", 10, "https://stream/b"),
    ]


@pytest.mark.asyncio
async def test_skip_empty_leaves_call() -> None:
    calls = FakeCalls()
    player = MusicPlayer(calls, MusicQueue())
    assert await player.skip(10) is None
    assert calls.actions == [("leave", 10)]
