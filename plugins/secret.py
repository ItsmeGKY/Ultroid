# secret.py
# Ultroid - UserBot
# Custom Secret Plugin
# Uses LOG_CHANNEL directly from .env

import os
from . import ultroid_cmd

# Read the log group/channel ID directly from environment
LOG_CHAT = os.environ.get("LOG_CHANNEL")

@ultroid_cmd(pattern="sd$")
async def secret_download(event):
    """
    Reply-only command:
    Downloads the replied photo/video and uploads it to LOG_CHANNEL
    """
    if not LOG_CHAT:
        return await event.respond(
            "❌ No log chat configured. Please set LOG_CHANNEL in your .env"
        )

    if not event.reply_to_msg_id:
        return await event.eor("Reply to a photo or video...", time=5)

    reply = await event.get_reply_message()
    if not reply or not reply.media:
        return await event.eor("No media found in replied message.", time=5)

    # Delete the command message instantly
    await event.try_delete()

    # Ensure the download folder exists
    download_path = "resources/secret/"
    os.makedirs(download_path, exist_ok=True)

    # Download the media
    try:
        file_name = await event.client.download_media(reply, download_path)
    except Exception as err:
        return await event.client.send_message(
            int(LOG_CHAT), f"❌ **Secret Plugin Error (Download)**:\n`{err}`"
        )

    # Upload to the log group
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

    # Clean up the downloaded file
    try:
        os.remove(file_name)
    except Exception:
        pass
