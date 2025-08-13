# Ultroid - UserBot
# Auto Approve Join Requests (Per Chat, Persistent in MongoDB, With List Command & Delay)
# Copyright (C) 2025

import asyncio
from telethon import events
from . import udB  # Ultroid's MongoDB wrapper

COLLECTION = "autoapprove_chats"

async def get_enabled_chats():
    data = await udB.get(COLLECTION)
    return set(data or [])

async def save_enabled_chats(chats):
    await udB.set(COLLECTION, list(chats))

@ultroid_bot.on(events.NewMessage(pattern=r"\.autoapprove ?(.*)?", outgoing=True))
async def toggle_autoapprove(event):
    """Toggle/check/list auto-approve join requests (MongoDB persistent)."""
    args = (event.pattern_match.group(1) or "").lower().strip()
    chats = await get_enabled_chats()

    if not args:
        status = "ON" if event.chat_id in chats else "OFF"
        return await event.edit(f"🔹 Auto-approve is currently **{status}** in this chat.")

    if args == "on":
        chats.add(event.chat_id)
        await save_enabled_chats(chats)
        return await event.edit("✅ Auto-approve **enabled** for this chat.")

    elif args == "off":
        chats.discard(event.chat_id)
        await save_enabled_chats(chats)
        return await event.edit("❌ Auto-approve **disabled** for this chat.")

    elif args == "list":
        if not chats:
            return await event.edit("📭 No chats have auto-approve enabled.")
        
        msg = "📜 **Auto-approve is enabled in:**\n"
        for chat_id in chats:
            try:
                chat = await event.client.get_entity(chat_id)
                name = getattr(chat, "title", getattr(chat, "first_name", str(chat_id)))
                msg += f"• {name} (`{chat_id}`)\n"
            except:
                msg += f"• Unknown Chat (`{chat_id}`)\n"
        return await event.edit(msg)

    else:
        return await event.edit("❓ Usage:\n`.autoapprove on | off | list`")

@ultroid_bot.on(events.ChatJoinRequest)
async def approve_join_request(event):
    """Approve join requests if enabled for this chat, with a 5-second delay."""
    chats = await get_enabled_chats()
    if event.chat_id not in chats:
        return  # Not enabled for this chat

    try:
        await asyncio.sleep(5)  # Delay before approving
        await event.client.approve_chat_join_request(event.chat_id, event.sender_id)
        await event.client.send_message(
            event.chat_id,
            f"✅ Welcome, [{event.sender.first_name}](tg://user?id={event.sender_id})!"
        )
    except Exception as e:
        await event.client.send_message(event.chat_id, f"⚠️ Auto-approve failed: `{e}`")
