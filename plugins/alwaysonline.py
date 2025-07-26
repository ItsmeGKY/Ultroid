# alwaysonline.py - Telethon plugin to stay online

from asyncio import sleep
from telethon import events
from userbot import ultroid


@ultroid.on(events.NewMessage(outgoing=True, pattern=r"\.alwaysonline"))
async def _(event):
    await event.edit("🟢 Staying online forever...")
    while True:
        try:
            await ultroid.send_action("me", "typing")
        except Exception as e:
            await event.respond(f"❌ Error: {e}")
            break
        await sleep(60)
