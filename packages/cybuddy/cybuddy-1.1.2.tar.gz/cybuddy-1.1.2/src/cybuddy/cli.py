from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

# === Student-focused helpers (uses rich mockup data) ===

def explain_command(command_text: str) -> str:
    from .data import smart_explain
    return smart_explain(command_text)


def quick_tip(topic: str) -> str:
    from .data import smart_tip
    return smart_tip(topic)


def help_troubleshoot(issue: str) -> str:
    from .data import smart_assist
    return smart_assist(issue)


def micro_report(finding: str) -> str:
    from .data import smart_report
    return smart_report(finding)


def quiz_flashcards(topic: str) -> str:
    from .data import smart_quiz
    return smart_quiz(topic)


def step_planner(context: str) -> str:
    from .data import smart_plan
    return smart_plan(context)


# === Lightweight session history and TODO tracker ===

def _app_dir() -> Path:
    # Respect HOME override; do not create directories unless needed later
    home = os.environ.get("HOME") or os.path.expanduser("~")
    return Path(home) / ".cybuddy"


def _history_file(session: str | None = None) -> Path:
    cfg = load_config()
    if session:
        base = _app_dir() / "sessions" / session
        path = base / "history.jsonl"
    else:
        path = Path(os.path.expanduser(cfg.get("history.path", str(_app_dir() / "history.jsonl"))))
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return path




def _config_file() -> Path:
    """Legacy config file path for backward compatibility."""
    return _app_dir() / "config.toml"


def load_config() -> dict:
    """Load configuration using the new config system."""
    from .config import load_config as load_new_config
    
    # Load new config system
    new_config = load_new_config()
    
    # Convert to old format for backward compatibility
    cfg = {
        "history.enabled": new_config.get("history", {}).get("enabled", True),
        "history.path": new_config.get("history", {}).get("path", str(_app_dir() / "history.jsonl")),
        "output.truncate_lines": new_config.get("output", {}).get("truncate_lines", 60),
        "history.verbatim": new_config.get("history", {}).get("verbatim", False),
    }
    
    return cfg




def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def history_append(event: dict, session: str | None = None) -> None:
    cfg = load_config()
    if not cfg.get("history.enabled", True):
        return
    try:
        payload = {"ts": _now_iso(), **event}
        with _history_file(session).open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
    except Exception:
        pass














