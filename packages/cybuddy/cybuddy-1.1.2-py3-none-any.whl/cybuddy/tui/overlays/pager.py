from __future__ import annotations

import re
from typing import cast

from rich.console import Console, RenderableType
from rich.panel import Panel
from rich.text import Text

from cybuddy.tui.core.events import CybuddyEvent, EventType, KeyEvent, PasteEvent

from .base import Overlay


class PagerOverlay(Overlay):
    """Scrollable transcript overlay akin to the Codex pager."""

    name = "transcript"

    def __init__(self, lines: list[str], *, page_size: int = 12) -> None:
        self._lines = lines
        self._page_size = max(page_size, 1)
        self._offset = max(len(lines) - self._page_size, 0)
        self._search_term: str | None = None
        self._match_indices: list[int] = []
        self._active_match: int = 0

    def handle_event(self, event: CybuddyEvent) -> bool:
        if event.event_type is EventType.KEY:
            return self._handle_key(cast(KeyEvent, event))
        if event.event_type is EventType.PASTE:
            self._search_term = cast(PasteEvent, event).text.strip() or None
            if self._search_term:
                self._prepare_search_matches(self._search_term)
                self._jump_to_match(0)
            return True
        return False

    def _handle_key(self, event: KeyEvent) -> bool:
        if event.key in {"up", "k"}:
            self._scroll(-1)
            return True
        if event.key in {"down", "j"}:
            self._scroll(1)
            return True
        if event.key in {"pageup", "p"}:
            self._scroll(-self._page_size)
            return True
        if event.key in {"pagedown", "n"}:
            self._scroll(self._page_size)
            return True
        if event.key in {"g"} and not (event.ctrl or event.alt):
            self._offset = 0
            return True
        if event.key in {"G"}:
            self._offset = max(len(self._lines) - self._page_size, 0)
            return True
        if event.key == "/":
            self._search_term = ""
            self._match_indices = []
            self._active_match = 0
            return True
        if event.key in {"n"} and self._match_indices:
            self._active_match = (self._active_match + 1) % len(self._match_indices)
            self._jump_to_match(self._active_match)
            return True
        if event.key in {"N"} and self._match_indices:
            self._active_match = (self._active_match - 1) % len(self._match_indices)
            self._jump_to_match(self._active_match)
            return True
        return False

    def render(self, console: Console, width: int) -> RenderableType:
        visible = self._lines[self._offset : self._offset + self._page_size]
        if not visible:
            text = Text("<empty transcript>", style="dim")
        else:
            text = Text()
            for idx, line in enumerate(visible):
                text.append(line)
                if idx < len(visible) - 1:
                    text.append("\n")
        if self._search_term:
            pattern = re.escape(self._search_term)
            if pattern:
                text.highlight_regex(pattern, style="bold cyan")
        return Panel(
            text,
            title=f"Transcript ({self._offset + 1}-{self._offset + len(visible)} / {len(self._lines)})",
            border_style="cyan",
        )

    def status_bar(self) -> RenderableType:
        helper = Text(
            self._status_text(),
            style="cyan",
        )
        return Panel(helper, title="Transcript Controls")

    def _scroll(self, delta: int) -> None:
        if not self._lines:
            self._offset = 0
            return
        self._offset = max(0, min(self._offset + delta, max(len(self._lines) - self._page_size, 0)))

    def _prepare_search_matches(self, term: str) -> None:
        lowered = term.lower()
        self._match_indices = [idx for idx, line in enumerate(self._lines) if lowered in line.lower()]
        self._active_match = 0 if self._match_indices else 0

    def _jump_to_match(self, index: int) -> None:
        if not self._match_indices:
            return
        idx = self._match_indices[index % len(self._match_indices)]
        self._offset = max(idx - 1, 0)

    def _status_text(self) -> str:
        if not self._search_term:
            return "Up/Down scroll  PgUp/PgDn jump  g/G home/end  paste text to search"
        total = len(self._match_indices)
        position = (self._active_match + 1) if total else 0
        return f"Matches {position}/{total} - n/N cycle, paste to replace search"
 
__all__ = ["PagerOverlay"]
