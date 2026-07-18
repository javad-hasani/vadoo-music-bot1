from __future__ import annotations

from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message


async def is_admin(client: Client, message: Message, owner_id: int) -> bool:
    if not message.from_user:
        return False
    if message.from_user.id == owner_id:
        return True
    if message.chat.type.name == "PRIVATE":
        return True
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in {ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR}
