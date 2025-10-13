from __future__ import annotations

import asyncio
import contextlib
from dataclasses import dataclass

from .events import CybuddyEvent, DrawEvent


@dataclass
class FrameScheduler:
    """Coalesces frame requests into single draw events, similar to Codex."""

    _queue: asyncio.Queue[CybuddyEvent]
    _pending_deadline: float | None = None
    _task: asyncio.Task[None] | None = None

    def schedule_now(self) -> None:
        self.schedule_in(0.0)

    def schedule_in(self, delay: float) -> None:
        loop = asyncio.get_running_loop()
        target = loop.time() + max(delay, 0.0)
        if self._pending_deadline is not None and target >= self._pending_deadline:
            return
        self._pending_deadline = target
        if self._task is not None:
            self._task.cancel()
        self._task = loop.create_task(self._fire())

    async def _fire(self) -> None:
        try:
            assert self._pending_deadline is not None
            loop = asyncio.get_running_loop()
            delay = max(self._pending_deadline - loop.time(), 0.0)
            await asyncio.sleep(delay)
            await self._queue.put(DrawEvent(requested_at=loop.time()))
        except asyncio.CancelledError:
            pass
        finally:
            self._pending_deadline = None
            self._task = None

    async def aclose(self) -> None:
        if self._task is not None:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            self._task = None
            self._pending_deadline = None

__all__ = ["FrameScheduler"]
