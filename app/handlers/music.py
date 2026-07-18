from __future__ import annotations

import logging

from pyrogram import Client, filters
from pyrogram.types import Message

from app import texts
from app.config import Settings
from app.security import is_admin
from app.services.player import MusicPlayer
from app.services.queue import QueueFullError
from app.services.youtube import TrackNotFoundError, TrackTooLongError, YouTubeResolver

logger = logging.getLogger(__name__)


def _query(message: Message) -> str:
    parts = (message.text or "").split(maxsplit=1)
    return parts[1].strip() if len(parts) == 2 else ""


def register_music_handlers(bot: Client, settings: Settings, resolver: YouTubeResolver, player: MusicPlayer) -> None:
    @bot.on_message(filters.command(["start", "help"]) & filters.incoming)
    async def start_handler(_: Client, message: Message) -> None:
        await message.reply_text(texts.START if message.command[0] == "start" else texts.HELP)

    @bot.on_message(filters.command("play") & filters.group & filters.incoming)
    async def play_handler(_: Client, message: Message) -> None:
        query = _query(message)
        if not query:
            await message.reply_text(texts.NO_QUERY)
            return
        status = await message.reply_text(texts.SEARCHING)
        requester = message.from_user.mention if message.from_user else "کاربر ناشناس"
        try:
            track = await resolver.resolve(query, requester)
            action, position = await player.enqueue_or_play(message.chat.id, track)
        except TrackNotFoundError:
            await status.edit_text("❌ آهنگی با این عبارت پیدا نشد.")
        except TrackTooLongError:
            await status.edit_text("⏱ مدت این فایل بیشتر از حد مجاز ربات است.")
        except QueueFullError:
            await status.edit_text("📚 صف پخش پر شده است؛ چند آهنگ را رد یا متوقف کنید.")
        except Exception as exc:
            logger.exception("play failed", exc_info=exc)
            await status.edit_text("❌ پخش شروع نشد. ویس‌چت، عضویت دستیار و تنظیمات سرور را بررسی کنید.")
        else:
            if action == "playing":
                await status.edit_text(
                    f"▶️ **درحال پخش**\n🎵 [{track.title}]({track.webpage_url})\n"
                    f"⏱ `{track.duration_text}`\n👤 درخواست: {track.requested_by}",
                    disable_web_page_preview=True,
                )
            else:
                await status.edit_text(
                    f"➕ **به صف اضافه شد** (جایگاه {position})\n"
                    f"🎵 [{track.title}]({track.webpage_url})\n⏱ `{track.duration_text}`",
                    disable_web_page_preview=True,
                )

    async def require_admin(client: Client, message: Message) -> bool:
        allowed = await is_admin(client, message, settings.owner_id)
        if not allowed:
            await message.reply_text(texts.ADMIN_ONLY)
        return allowed

    @bot.on_message(filters.command("pause") & filters.group)
    async def pause_handler(client: Client, message: Message) -> None:
        if await require_admin(client, message):
            await player.pause(message.chat.id)
            await message.reply_text("⏸ پخش متوقف شد.")

    @bot.on_message(filters.command("resume") & filters.group)
    async def resume_handler(client: Client, message: Message) -> None:
        if await require_admin(client, message):
            await player.resume(message.chat.id)
            await message.reply_text("▶️ پخش ادامه پیدا کرد.")

    @bot.on_message(filters.command("skip") & filters.group)
    async def skip_handler(client: Client, message: Message) -> None:
        if not await require_admin(client, message):
            return
        track = await player.skip(message.chat.id)
        await message.reply_text("⏭ صف تمام شد و دستیار از ویس‌چت خارج شد." if track is None else f"⏭ آهنگ بعدی: **{track.title}**")

    @bot.on_message(filters.command(["stop", "leave"]) & filters.group)
    async def stop_handler(client: Client, message: Message) -> None:
        if await require_admin(client, message):
            await player.stop(message.chat.id)
            await message.reply_text("⏹ پخش متوقف و صف پاک شد؛ دستیار خارج شد.")

    @bot.on_message(filters.command("volume") & filters.group)
    async def volume_handler(client: Client, message: Message) -> None:
        if not await require_admin(client, message):
            return
        raw = _query(message)
        if not raw.isdigit() or not 1 <= int(raw) <= 200:
            await message.reply_text("🔊 عدد صدا باید بین ۱ تا ۲۰۰ باشد. نمونه: `/volume 80`")
            return
        value = int(raw)
        await player.volume(message.chat.id, value)
        await message.reply_text(f"🔊 میزان صدا روی **{value}٪** تنظیم شد.")

    @bot.on_message(filters.command("queue") & filters.group)
    async def queue_handler(_: Client, message: Message) -> None:
        current = await player.queue.current(message.chat.id)
        waiting = await player.queue.snapshot(message.chat.id)
        if not current and not waiting:
            await message.reply_text("📭 صف پخش خالی است.")
            return
        lines = []
        if current:
            lines.append(f"▶️ اکنون: **{current.title}** — `{current.duration_text}`")
        lines.extend(f"{index}. **{track.title}** — `{track.duration_text}`" for index, track in enumerate(waiting[:15], start=1))
        if len(waiting) > 15:
            lines.append(f"… و {len(waiting) - 15} آهنگ دیگر")
        await message.reply_text("📜 **صف پخش**\n\n" + "\n".join(lines))

    @bot.on_message(filters.command("now") & filters.group)
    async def now_handler(_: Client, message: Message) -> None:
        track = await player.queue.current(message.chat.id)
        if not track:
            await message.reply_text("🔇 اکنون آهنگی پخش نمی‌شود.")
            return
        await message.reply_text(
            f"🎧 **درحال پخش**\n[{track.title}]({track.webpage_url})\n"
            f"⏱ `{track.duration_text}`\n👤 {track.requested_by}",
            disable_web_page_preview=True,
        )
