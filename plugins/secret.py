# secret.py
# Ultroid - UserBot
# Custom Secret Plugin

import os
from . import ULTConfig, ultroid_cmd

# Detect log chat ID safely
LOG_CHAT = getattr(ULTConfig, "LOGGER_ID", None) or getattr(ULTConfig, "LOG_CHANNEL", None) or getattr(ULTConfig, "LOG_CHAT", None)

@ultroid_cmd(pattern="sd$")
async def secret_download(event):
    """
    Reply-only command:
    Downloads the replied photo/video and uploads it to Log Chat
    """
    if not event.reply_to_msg_id:
        return await event.eor("Reply to a photo or video...", time=5)

    reply = await event.get_reply_message()
    if not reply or not reply.media:
        return await event.eor("No media found in replied message.", time=5)

    # Delete the command instantly
    await event.try_delete()

    download_path = "resources/secret/"
    os.makedirs(download_path, exist_ok=True)

    if not LOG_CHAT:
        return await event.respond("❌ No log chat configured in ULTConfig.")

    # --- Download ---
    try:
        file_name = await event.client.download_media(reply, download_path)
    except Exception as err:
        return await event.client.send_message(
            LOG_CHAT, f"❌ **Secret Plugin Error (Download)**:\n`{err}`"
        )

    # --- Upload ---
    try:
        await event.client.send_file(
            LOG_CHAT,
            file_name,
            caption=f"✅ **Secret Upload:** `{os.path.basename(file_name)}`",
        )
    except Exception as err:
        await event.client.send_message(
            LOG_CHAT, f"❌ **Secret Plugin Error (Upload)**:\n`{err}`"
        )

    # --- Cleanup ---
    try:
        os.remove(file_name)
    except Exception:
        pass
