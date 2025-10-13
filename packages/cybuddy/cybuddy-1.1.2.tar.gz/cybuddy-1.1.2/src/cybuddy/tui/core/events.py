from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol, Union


class EventType(str, Enum):
    KEY = "key"
    PASTE = "paste"
    DRAW = "draw"
    FOCUS = "focus"
    RESIZE = "resize"


@dataclass(frozen=True)
class BaseEvent:
    """Common base type carrying the event discriminator."""

    event_type: EventType


@dataclass(frozen=True)
class KeyEvent(BaseEvent):
    """Represents a key press with normalized modifier metadata."""

    event_type: EventType = EventType.KEY
    key: str = ""
    data: str | None = None
    ctrl: bool = False
    alt: bool = False
    shift: bool = False

    def __init__(self, key: str, data: str | None, *, ctrl: bool, alt: bool, shift: bool) -> None:
        object.__setattr__(self, "event_type", EventType.KEY)
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "data", data)
        object.__setattr__(self, "ctrl", ctrl)
        object.__setattr__(self, "alt", alt)
        object.__setattr__(self, "shift", shift)


@dataclass(frozen=True)
class PasteEvent(BaseEvent):
    """Represents a bracketed paste payload."""

    event_type: EventType = EventType.PASTE
    text: str = ""

    def __init__(self, text: str) -> None:
        object.__setattr__(self, "event_type", EventType.PASTE)
        object.__setattr__(self, "text", text)


@dataclass(frozen=True)
class DrawEvent(BaseEvent):
    """Signals that the UI should draw a frame."""

    event_type: EventType = EventType.DRAW
    requested_at: float = 0.0

    def __init__(self, requested_at: float) -> None:
        object.__setattr__(self, "event_type", EventType.DRAW)
        object.__setattr__(self, "requested_at", requested_at)


@dataclass(frozen=True)
class FocusEvent(BaseEvent):
    """Tracks terminal focus transitions where supported by the backend."""

    event_type: EventType = EventType.FOCUS
    gained: bool = False

    def __init__(self, gained: bool) -> None:
        object.__setattr__(self, "event_type", EventType.FOCUS)
        object.__setattr__(self, "gained", gained)


@dataclass(frozen=True)
class ResizeEvent(BaseEvent):
    """Terminal size change notification."""

    event_type: EventType = EventType.RESIZE
    width: int = 0
    height: int = 0

    def __init__(self, width: int, height: int) -> None:
        object.__setattr__(self, "event_type", EventType.RESIZE)
        object.__setattr__(self, "width", width)
        object.__setattr__(self, "height", height)


CybuddyEvent = Union[KeyEvent, PasteEvent, DrawEvent, FocusEvent, ResizeEvent]


class EventConsumer(Protocol):
    """Lightweight protocol so overlays/app can advertise event handling."""

    def handle_event(self, event: CybuddyEvent) -> bool:
        """Handle the event; return True if it was consumed."""


__all__ = [
    "BaseEvent",
    "DrawEvent",
    "EventConsumer",
    "EventType",
    "FocusEvent",
    "KeyEvent",
    "PasteEvent",
    "ResizeEvent",
    "CybuddyEvent",
]
