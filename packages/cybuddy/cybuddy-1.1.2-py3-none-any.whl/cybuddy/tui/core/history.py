from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from rich.console import RenderableType
from rich.panel import Panel
from rich.text import Text


@dataclass
class HistoryBuffer:
    """Simple in-memory transcript mirroring the inline viewport concept."""

    max_items: int = 200
    _entries: list[str] = field(default_factory=list)

    def append(self, line: str) -> None:
        self._entries.append(line)
        if len(self._entries) > self.max_items:
            # Drop oldest items to keep rendering lightweight.
            overflow = len(self._entries) - self.max_items
            del self._entries[:overflow]

    def extend(self, lines: Iterable[str]) -> None:
        for line in lines:
            self.append(line)

    def clear(self) -> None:
        self._entries.clear()

    def render(self, *, title: str = "Session History", placeholder: str = "Start typing to record notes...") -> RenderableType:
        if not self._entries:
            body = Text(placeholder, style="dim")
        else:
            body = Text()
            for index, line in enumerate(self._entries):
                style = "cyan" if index == len(self._entries) - 1 else ""
                body.append(line, style=style)
                if index < len(self._entries) - 1:
                    body.append("\n")
        return Panel(body, title=title)

    def snapshot(self) -> list[str]:
        return list(self._entries)

__all__ = ["HistoryBuffer"]
