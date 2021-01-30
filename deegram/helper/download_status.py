import asyncio
import logging
import time

from telethon.errors import MessageNotModifiedError

from .. import bot
from ..utils.bot_utils import get_readable_file_size

logger = logging.getLogger(__name__)


class DownloadStatus:
    def __init__(self, event):
        self._current = 0
        self._total = 0
        self._event = event
        self._message = None
        self._start_time = 0.0

    def speed(self) -> float:
        return self._current / (time.time() - self._start_time)

    async def start(self) -> None:
        self._message = await self._event.reply("Downloading...")
        self._start_time = time.time()
        self._task = bot.loop.create_task(self._on_progress())

    async def _on_progress(self) -> None:
        try:
            while True:
                if self._total:
                    try:
                        await self._message.edit(
                            f"🔽 Downloading... {(self._current / self._total):.1%}\n"
                            f"⚡ Speed: {get_readable_file_size(self.speed())}/s")
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
        self._task.cancel()
