# Ultroid - UserBot
# Auto Approve Join Requests (Per Chat, MongoDB Persistent, Logging, Delay)
# Compatible with Ultroid's Telethon version

import asyncio
from telethon import events
from . import udB, ultroid_bot, ultroid_cmd

COLLECTION = "autoapprove_chats"

# ------------------ Helper functions ------------------ #
def get_enabled_chats():
    data = udB.get(COLLECTION)
    return set(data or [])

def save_enabled_chats(chats):
    udB.set(COLLECTION, list(chats))

# ------------------ Commands ------------------ #
@ultroid_cmd(pattern="autoapprove ?(.*)?")
async def toggle_autoapprove(event):
    """Toggle/check/list auto-approve join requests."""
    args = (event.pattern_match.group(1) or "").lower().strip()
    chats = get_enabled_chats()

    if not args:
        status = "ON" if event.chat_id in chats else "OFF"
        return await event.edit(f"🔹 Auto-approve is currently **{status}** in this chat.")

    if args == "on":
        chats.add(event.chat_id)
        save_enabled_chats(chats)
        return await event.edit("✅ Auto-approve **enabled** for this chat.")

    elif args == "off":
        chats.discard(event.chat_id)
        save_enabled_chats(chats)
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

# ------------------ Join Request Handler ------------------ #
@ultroid_bot.on(events.JoinRequest)
async def approve_join_request(event):
    """Approve join requests safely with logging and 5-second delay."""
    chats = get_enabled_chats()
    print(f"[AUTOAPPROVE] Join request from {event.sender_id} in chat {event.chat_id}")

    if event.chat_id not in chats:
        print("[AUTOAPPROVE] Auto-approve not enabled for this chat")
        return

    try:
        print(f"[AUTOAPPROVE] Approving join request for {event.sender_id} after 5s delay")
        await asyncio.sleep(5)
        await event.client.approve_join_request(event.chat_id, event.sender_id)
        await event.client.send_message(
            event.chat_id,
            f"✅ Welcome, [{event.sender.first_name}](tg://user?id={event.sender_id})!"
        )
        print(f"[AUTOAPPROVE] Approved join request for {event.sender_id}")
    except Exception as e:
        print(f"[AUTOAPPROVE] Error approving join request: {e}")
        await event.client.send_message(
            event.chat_id,
            f"⚠️ Auto-approve failed for [{event.sender.first_name}](tg://user?id={event.sender_id}): `{e}`"
        )
