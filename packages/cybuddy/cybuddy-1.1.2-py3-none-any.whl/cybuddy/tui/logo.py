from __future__ import annotations

import os
from typing import Iterable

from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel
from rich.text import Text


CY_PRIMARY_CYAN = "rgb(0,255,255)"
CY_GRADIENT = (
    "rgb(0,255,136)",
    "rgb(0,255,150)",
    "rgb(0,255,170)",
    "rgb(0,255,190)",
    "rgb(0,255,210)",
    "rgb(0,255,230)",
    "rgb(0,255,245)",
    "rgb(0,255,255)",
)


def _full_logo_lines(ascii_only: bool) -> Iterable[Text]:
    if ascii_only:
        # ASCII-safe approximation (no box drawing)
        raw = [
            "        /^^^^\\",
            "       |  |+|  |",
            "       | --+-- |",
            "       |   |   |",
            "        |     |",
            "         |   |",
            "          | |",
            "           v",
        ]
        for line in raw:
            yield Text(line, style=f"bold {CY_GRADIENT[-1]}")
        return

    shapes = [
        "        ▄▀▀▀▄",
        "       █  │  █",
        "      █ ──┼── █",
        "      █   │   █",
        "       █     █",
        "        █   █",
        "         █ █",
        "          ▀",
    ]
    for idx, line in enumerate(shapes):
        color = CY_GRADIENT[min(idx, len(CY_GRADIENT) - 1)]
        yield Text(line, style=f"bold {color}")


def _compact_logo(ascii_only: bool) -> Text:
    if ascii_only:
        return Text("[CYBUDDY]", style=f"bold {CY_PRIMARY_CYAN}")
    title = Text()
    title.append("CY", style="bold white")
    title.append("BUDDY", style=f"bold {CY_PRIMARY_CYAN}")
    return title


def render_logo(console_width: int, *, ascii_only: bool | None = None) -> RenderableType:
    """Return a responsive logo renderable for the given width.

    - Full shield + title for width >= 40
    - Compact single-line for small widths
    - ASCII-only fallback via env CYBUDDY_ASCII=1 or when explicitly requested
    """
    ascii_mode = ascii_only if ascii_only is not None else (os.getenv("CYBUDDY_ASCII") == "1")

    if console_width < 40:
        compact = _compact_logo(ascii_mode)
        return Align.center(compact)

    # Build vertical stack of shield lines and title
    lines = list(_full_logo_lines(ascii_mode))
    title = Text()
    title.append("CY", style="bold white")
    title.append("BUDDY", style=f"bold {CY_PRIMARY_CYAN}")

    # Compose: Panel with no wrapping, centered
    content = Text()
    for i, line in enumerate(lines):
        content.append_text(line)
        if i < len(lines) - 1:
            content.append("\n")
    content.append("\n\n")
    content.append_text(title)

    panel = Panel.fit(content, border_style=CY_PRIMARY_CYAN)
    return Align.center(panel)


__all__ = ["render_logo"]


