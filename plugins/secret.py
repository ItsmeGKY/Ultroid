# secret.py

import os
from . import ULTConfig, ultroid_cmd

# Detect log chat ID
LOG_CHAT = (
    getattr(ULTConfig, "LOGGER_ID", None)
    or getattr(ULTConfig, "LOG_CHAT", None)
    or getattr(ULTConfig, "LOG_CHANNEL", None)
    or os.environ.get("LOGGER_ID")
    or os.environ.get("LOG_CHAT")
    or os.environ.get("LOG_CHANNEL")
)

@ultroid_cmd(pattern="sd$")
async def secret_download(event):
    if not event.reply_to_msg_id:
        return await event.eor("Reply to a photo or video...", time=5)

    reply = await event.get_reply_message()
    if not reply or not reply.media:
        return await event.eor("No media found in replied message.", time=5)

    await event.try_delete()

    download_path = "resources/secret/"
    os.makedirs(download_path, exist_ok=True)

    if not LOG_CHAT:
        return await event.respond("❌ No log chat configured. Please set `LOG_CHANNEL` in config.env")

    try:
        file_name = await event.client.download_media(reply, download_path)
    except Exception as err:
        return await event.client.send_message(
            int(LOG_CHAT), f"❌ **Secret Plugin Error (Download)**:\n`{err}`"
        )

    try:
        await event.client.send_file(
            int(LOG_CHAT),
            file_name,
            caption=f"✅ **Secret Upload:** `{os.path.basename(file_name)}`",
        )
    except Exception as err:
        await event.client.send_message(
            int(LOG_CHAT), f"❌ **Secret Plugin Error (Upload)**:\n`{err}`"
        )

    try:
        os.remove(file_name)
    except Exception:
        pass
