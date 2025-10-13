from __future__ import annotations

from abc import ABC, abstractmethod

from rich.console import Console, RenderableType

from cybuddy.tui.core.events import CybuddyEvent


class Overlay(ABC):
    """Base overlay interface mirroring Codex' render/handle pattern."""

    name: str = "overlay"

    def on_show(self) -> None:  # pragma: no cover - hook for subclasses
        """Hook executed when the overlay becomes active."""

    def on_hide(self) -> None:  # pragma: no cover - hook for subclasses
        """Hook executed when the overlay is removed."""

    @abstractmethod
    def handle_event(self, event: CybuddyEvent) -> bool:
        """Process an incoming event; return True when consumed."""

    @abstractmethod
    def render(self, console: Console, width: int) -> RenderableType:
        """Return the renderable for the overlay given the viewport width."""

    def status_bar(self) -> RenderableType | None:  # pragma: no cover - optional
        return None

__all__ = ["Overlay"]
