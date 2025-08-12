# alwaysonline.py - Keep your account always online in Ultroid
# Copyright (C) 2025
# This file is part of Ultroid Plugins
#
# License: AGPL-3.0-or-later

import asyncio
from telethon import functions
from . import ultroid_cmd, LOGS

# Variable to store the task
alwayson_task = None

async def keep_online(client):
    """Loop to keep the account online."""
    try:
        while True:
            await client(functions.account.UpdateStatusRequest(offline=False))
            await asyncio.sleep(60)  # every 1 minute
    except asyncio.CancelledError:
        LOGS.info("Always Online task stopped.")

@ultroid_cmd(pattern="alwayson$", fullsudo=True)
async def always_on_cmd(event):
    """Start keeping account online."""
    global alwayson_task
    if alwayson_task and not alwayson_task.done():
        return await event.eor("✅ Already keeping you online.")
    alwayson_task = asyncio.create_task(keep_online(event.client))
    await event.eor("💡 Always Online mode **started**.")

@ultroid_cmd(pattern="stopalwayson$", fullsudo=True)
async def stop_always_on_cmd(event):
    """Stop keeping account online."""
    global alwayson_task
    if alwayson_task and not alwayson_task.done():
        alwayson_task.cancel()
        alwayson_task = None
        await event.eor("🛑 Always Online mode **stopped**.")
    else:
        await event.eor("ℹ️ Always Online was not running.")
