from __future__ import annotations

import asyncio
import contextlib
import sys
import time
from collections.abc import AsyncIterator
from contextlib import ExitStack

from prompt_toolkit.input.defaults import create_input
from prompt_toolkit.key_binding import KeyPress
from prompt_toolkit.keys import Keys
from prompt_toolkit.output.defaults import create_output
from rich.console import Console, RenderableType

from .events import (
    CybuddyEvent,
    DrawEvent,
    FocusEvent,
    KeyEvent,
    PasteEvent,
    ResizeEvent,
)


class TerminalController:
    """Low-level terminal glue around prompt_toolkit and Rich rendering."""

    def __init__(self) -> None:
        self._input = create_input(sys.stdin)
        self._output = create_output(stdout=sys.stdout)
        self.console = Console(force_terminal=True, highlight=False)
        self._event_queue: asyncio.Queue[CybuddyEvent] = asyncio.Queue()
        self._reader_task: asyncio.Task[None] | None = None
        self._exit_stack = ExitStack()
        self._alt_active = False

    async def __aenter__(self) -> TerminalController:
        self._enter_terminal_modes()
        self._reader_task = asyncio.create_task(self._read_input(), name="cybuddy-tui-input")
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._reader_task is not None:
            self._reader_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._reader_task
        self._reader_task = None
        self.leave_alt_screen()
        self._exit_stack.close()

    def _enter_terminal_modes(self) -> None:
        """Enter raw mode and set up terminal properly."""
        self._exit_stack.enter_context(self._input.raw_mode())

        # Bracketed paste mode is optional - not all input types support it
        if hasattr(self._input, 'bracketed_paste_mode'):
            try:
                self._exit_stack.enter_context(self._input.bracketed_paste_mode())
            except Exception:
                pass  # Ignore if not supported

        # Attach input to event loop - creates callback for reading
        # The callback should be the input's read handler, not the output
        if hasattr(self._input, 'attach'):
            try:
                # Create a callback that will trigger on input
                def input_ready() -> None:
                    pass  # The read_keys() call will handle actual reading

                self._exit_stack.enter_context(self._input.attach(input_ready))
            except Exception:
                pass  # Not critical if attach fails

    async def _read_input(self) -> None:
        """
        Read input keys asynchronously.

        read_keys() is blocking, so we run it in a thread executor to avoid
        blocking the event loop.
        """
        try:
            loop = asyncio.get_running_loop()
            while True:
                # Run the blocking read_keys() in a thread executor
                key_presses = await loop.run_in_executor(None, self._input.read_keys)

                for key_press in key_presses:
                    event = self._convert_key_press(key_press)
                    if event is not None:
                        await self._event_queue.put(event)
        except asyncio.CancelledError:
            pass

    def _convert_key_press(self, key_press: KeyPress) -> CybuddyEvent | None:
        if key_press.key == Keys.BracketedPaste:
            text = key_press.data or ""
            return PasteEvent(text=text)
        if key_press.key == Keys.CPRResponse:
            return None
        if key_press.key == Keys.Vt100_MouseEvent:
            return None
        modifiers = key_press.key
        ctrl = "c-" in str(modifiers)
        alt = "a-" in str(modifiers)
        shift = "s-" in str(modifiers)
        key_name = key_press.key.value if hasattr(key_press.key, "value") else str(key_press.key)
        data = key_press.data or None
        return KeyEvent(key=key_name, data=data, ctrl=ctrl, alt=alt, shift=shift)

    async def event_stream(self) -> AsyncIterator[CybuddyEvent]:
        while True:
            event = await self._event_queue.get()
            yield event

    def schedule_draw(self) -> None:
        event = DrawEvent(requested_at=time.time())
        self._event_queue.put_nowait(event)

    @property
    def event_queue(self) -> asyncio.Queue[CybuddyEvent]:
        return self._event_queue

    def send_focus(self, gained: bool) -> None:
        self._event_queue.put_nowait(FocusEvent(gained=gained))

    def send_resize(self, width: int, height: int) -> None:
        self._event_queue.put_nowait(ResizeEvent(width=width, height=height))

    def enter_alt_screen(self) -> None:
        if self._alt_active:
            return
        self._output.write_raw("\x1b[?1049h")
        self._output.flush()
        self._alt_active = True

    def leave_alt_screen(self) -> None:
        if not self._alt_active:
            return
        self._output.write_raw("\x1b[?1049l")
        self._output.flush()
        self._alt_active = False

    def draw_renderable(self, renderable: RenderableType) -> None:
        """Draw a renderable to the screen, clearing and positioning first."""
        # Hide cursor during drawing
        self._output.write_raw("\x1b[?25l")  # Hide cursor

        # Clear screen and move cursor to home position
        self._output.write_raw("\x1b[2J")  # Clear entire screen
        self._output.write_raw("\x1b[H")   # Move cursor to home (1,1)
        self._output.flush()

        # Render with Rich
        self.console.print(renderable, soft_wrap=True, end="")

        # Show cursor again
        self._output.write_raw("\x1b[?25h")  # Show cursor

        # Make sure output is flushed
        self._output.flush()
        if hasattr(self.console.file, 'flush'):
            self.console.file.flush()

    async def aclose(self) -> None:
        if self._reader_task is not None:
            self._reader_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._reader_task
        self._reader_task = None
        self.leave_alt_screen()
        self._exit_stack.close()

__all__ = ["TerminalController"]
