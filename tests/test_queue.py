import pytest

from app.models import Track
from app.services.queue import MusicQueue, QueueFullError


def track(name: str) -> Track:
    return Track(name, "https://example.com", "https://stream.example.com", 65, "tester")


@pytest.mark.asyncio
async def test_queue_order_and_current() -> None:
    queue = MusicQueue(max_size=3)
    await queue.add(1, track("one"))
    await queue.add(1, track("two"))
    first = await queue.pop_next(1)
    assert first and first.title == "one"
    assert (await queue.current(1)).title == "one"
    assert [item.title for item in await queue.snapshot(1)] == ["two"]


@pytest.mark.asyncio
async def test_queue_limit() -> None:
    queue = MusicQueue(max_size=1)
    await queue.add(1, track("one"))
    with pytest.raises(QueueFullError):
        await queue.add(1, track("two"))


@pytest.mark.asyncio
async def test_clear() -> None:
    queue = MusicQueue()
    await queue.set_current(1, track("current"))
    await queue.add(1, track("waiting"))
    await queue.clear(1)
    assert await queue.current(1) is None
    assert await queue.snapshot(1) == []
