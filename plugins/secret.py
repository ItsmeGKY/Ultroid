# secret.py
# Ultroid - UserBot
# Custom Secret Plugin

import os
import time
from datetime import datetime as dt

from telethon.errors.rpcerrorlist import MessageNotModifiedError

from . import (
    ULTConfig,
    eor,
    progress,
    time_formatter,
    ultroid_cmd,
)


@ultroid_cmd(pattern="sd$")
async def secret_download(event):
    """
    Reply-only command:
    Downloads the replied photo/video and uploads it to LOG_CHAT
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

    # --- Download ---
    start = time.time()
    try:
        file_name = await event.client.download_media(
            reply,
            download_path,
            progress_callback=lambda d, t: event.client.loop.create_task(
                progress(d, t, event, start, "Downloading...")
            ),
        )
    except MessageNotModifiedError:
        return
    except Exception as err:
        return await event.client.send_message(
            ULTConfig.LOG_CHAT, f"❌ **Secret Plugin Error (Download)**:\n`{err}`"
        )

    # --- Upload ---
    try:
        await event.client.send_file(
            ULTConfig.LOG_CHAT,
            file_name,
            caption=f"✅ **Secret Upload:** `{os.path.basename(file_name)}`",
        )
    except Exception as err:
        await event.client.send_message(
            ULTConfig.LOG_CHAT, f"❌ **Secret Plugin Error (Upload)**:\n`{err}`"
        )

    # --- Cleanup ---
    try:
        os.remove(file_name)
    except Exception:
        pass
