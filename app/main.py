from __future__ import annotations

import asyncio
import logging

from pyrogram import Client, idle
from pytgcalls import PyTgCalls

from app.config import get_settings
from app.handlers.music import register_music_handlers
from app.services.player import MusicPlayer
from app.services.queue import MusicQueue
from app.services.youtube import YouTubeResolver


async def main() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    bot = Client(
        "vadoo_bot",
        api_id=settings.api_id,
        api_hash=settings.api_hash,
        bot_token=settings.bot_token,
        in_memory=True,
    )
    assistant = Client(
        "vadoo_assistant",
        api_id=settings.api_id,
        api_hash=settings.api_hash,
        session_string=settings.session_string,
        in_memory=True,
    )
    calls = PyTgCalls(assistant)
    queue = MusicQueue(max_size=settings.max_queue_size)
    resolver = YouTubeResolver(settings.max_track_minutes, settings.cookies_file)
    player = MusicPlayer(calls, queue)
    register_music_handlers(bot, settings, resolver, player)

    await assistant.start()
    await calls.start()
    await bot.start()
    me = await bot.get_me()
    logging.getLogger(__name__).info("ربات @%s اجرا شد", me.username)
    try:
        await idle()
    finally:
        await bot.stop()
        await calls.stop()
        await assistant.stop()


if __name__ == "__main__":
    asyncio.run(main())
