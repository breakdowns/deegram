from asyncio.tasks import Task
import logging
import time
import asyncio
from typing import Optional

from telethon.errors import MessageNotModifiedError

from ..utils.bot_utils import get_readable_file_size
from .. import bot


logger = logging.getLogger(__name__)


class UploadStatus:
    def __init__(self, event, track_count: int = None, total_tracks: int = None):
        self._current = 0
        self._total = 0
        self._event = event
        self._message = None
        self._track_count = track_count
        self._total_tracks = total_tracks
        self.task: Optional[Task] = None

    def speed(self) -> float:
        return self._current / (time.time() - self._start_time)

    async def start(self) -> None:
        self._start_time = time.time()
        self._message = await self._event.reply("Uploading...")
        self.task = bot.loop.create_task(self._on_upload_progress())

    async def _on_upload_progress(self) -> None:
        try:
            while True:
                if self._total:
                    msg = ""
                    if self._track_count:
                        msg += f" 💿 Track {self._track_count} of {self._total_tracks}\n"
                    msg += (
                        f"🔼 Uploading... {(self._current / self._total):.1%}\n"
                        f"⚡ Speed: {get_readable_file_size(self.speed())}/s"
                    )
                    try:
                        await self._message.edit(msg)
                    except MessageNotModifiedError:
                        logger.debug("Message not modified")
                    except ZeroDivisionError:
                        logger.debug("Divided zero")
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            await self._message.delete()

    def progress(self, current: int, total: int) -> None:
        self._current = current
        self._total = total

    def finished(self) -> None:
        self.task.cancel()
