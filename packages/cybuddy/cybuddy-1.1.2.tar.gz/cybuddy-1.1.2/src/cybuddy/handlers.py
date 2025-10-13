"""Business logic handlers for Cybuddy commands, shared between CLI and TUI."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GuideResponse:
    """Structured response for guide mode interactions."""
    response_type: str  # "structured" or "simple"
    plan: str
    action: str
    cmd: str
    output: str
    next_step: str
    raw_input: str


@dataclass
class SlashResponse:
    """Response from slash command execution."""
    output: str
    success: bool = True


def handle_user_input(text: str, session: str | None = None) -> GuideResponse:
    """
    Process user input in guide mode and return structured response.

    Args:
        text: User input text
        session: Optional session name for history/todo

    Returns:
        GuideResponse with PLAN/ACTION/CMD/OUT/NEXT fields
    """
    from .data import smart_plan

    plan_text = smart_plan(text)
    action = "Follow the suggested steps below with safe defaults"
    cmd_hint = _guide_command_hint(text)

    # Generate contextual output based on input
    output = _generate_contextual_output(text)
    next_step = _extract_first_step(plan_text)

    return GuideResponse(
        response_type="structured",
        plan=plan_text,
        action=action,
        cmd=cmd_hint,
        output=output,
        next_step=next_step,
        raw_input=text,
    )


def _generate_contextual_output(text: str) -> str:
    """Generate brief contextual analysis of user input."""
    t = text.lower()
    if any(k in t for k in ["nmap", "scan", "port"]):
        return "Start with service version detection (-sV) and document all findings"
    if any(k in t for k in ["web", "http", "xss", "sql"]):
        return "Test inputs methodically, check for injection points, use Burp for inspection"
    if any(k in t for k in ["hash", "crack", "password"]):
        return "Identify hash type first (hashid), then select appropriate tool and wordlist"
    if any(k in t for k in ["shell", "reverse", "access"]):
        return "Stabilize connection, enumerate privileges, look for escalation paths"
    if any(k in t for k in ["found", "discovered"]):
        return "Document the finding, test for related vulnerabilities, plan next enumeration phase"
    return "Break down the objective, choose safe tools, document each step carefully"


def _extract_first_step(plan_text: str) -> str:
    """Extract just the first step from a plan for next_step field."""
    lines = [l.strip() for l in plan_text.split('\n') if l.strip()]
    if lines:
        # Remove numbering if present
        first = lines[0].lstrip('0123456789.)- ')
        return first
    return "Document your findings and proceed methodically"


def handle_slash_command(line: str, session: str | None = None) -> SlashResponse:
    """
    Handle slash commands in guide mode.

    Args:
        line: Slash command line (e.g., "/tip sql injection")
        session: Optional session name

    Returns:
        SlashResponse with output text
    """
    from .cli import (
        CHECKLISTS,
        _now_iso,
        _todo_load,
        _todo_save,
        quick_tip,
        step_planner,
    )

    parts = line[1:].split(maxsplit=1)
    if not parts:
        return SlashResponse("Unknown command. Try /tip, /plan, /checklist, /todo, /run", success=False)

    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    # /tip <topic>
    if cmd == "tip":
        if not arg:
            return SlashResponse("Usage: /tip <topic>", success=False)
        result = quick_tip(arg)
        return SlashResponse(f"TIP:\n{result}")

    # /plan <context>
    if cmd == "plan":
        if not arg:
            return SlashResponse("Usage: /plan <context>", success=False)
        result = step_planner(arg)
        return SlashResponse(f"PLAN:\n{result}")

    # /checklist <topic>
    if cmd == "checklist":
        if not arg:
            topics = ", ".join(sorted(CHECKLISTS.keys()))
            return SlashResponse(f"Available checklists: {topics}")

        key = arg.lower()
        item = CHECKLISTS.get(key)
        if not item:
            return SlashResponse(f"Unknown checklist: {arg}", success=False)

        lines = [f"{item.name} Checklist:"]
        for i, step in enumerate(item.steps, start=1):
            lines.append(f"{i}. {step}")
        return SlashResponse("\n".join(lines))

    # /todo add <text>
    if cmd == "todo":
        subparts = arg.split(maxsplit=1)
        if not subparts:
            # List todos
            items = _todo_load(session)
            if not items:
                return SlashResponse("No TODO items. Add with: /todo add \"description\"")
            lines = []
            for i, it in enumerate(items, 1):
                status = it.get("status", "pending")
                lines.append(f"{i}. [{status}] {it.get('text','')}")
            return SlashResponse("\n".join(lines))

        subcmd = subparts[0].lower()
        subarg = subparts[1] if len(subparts) > 1 else ""

        if subcmd == "add":
            if not subarg:
                return SlashResponse("Usage: /todo add <text>", success=False)
            items = _todo_load(session)
            items.append({"text": subarg, "status": "pending", "added": _now_iso()})
            _todo_save(items, session)
            return SlashResponse(f"Added: {subarg}")

        if subcmd == "done":
            if not subarg:
                return SlashResponse("Usage: /todo done <number>", success=False)
            try:
                idx = int(subarg) - 1
                items = _todo_load(session)
                if idx < 0 or idx >= len(items):
                    return SlashResponse("Invalid todo number", success=False)
                items[idx]["status"] = "completed"
                items[idx]["completed"] = _now_iso()
                _todo_save(items, session)
                return SlashResponse(f"Done: {items[idx]['text']}")
            except ValueError:
                return SlashResponse("Invalid todo number", success=False)

        if subcmd == "clear":
            _todo_save([], session)
            return SlashResponse("Cleared all TODO items")

        return SlashResponse(f"Unknown todo command: {subcmd}", success=False)

    # /run <tool> "<args>"
    if cmd == "run":
        if not arg:
            return SlashResponse("Usage: /run <tool> \"<args>\"", success=False)
        # Parse tool and args
        import shlex
        try:
            tokens = shlex.split(arg)
        except ValueError:
            tokens = arg.split()

        if not tokens:
            return SlashResponse("Usage: /run <tool> \"<args>\"", success=False)

        from .cli import _safety_review
        from .formatters import is_likely_code
        tool = tokens[0]
        rest = tokens[1:]
        joined = " ".join(rest)
        command = f"{tool} {joined}".strip()

        safety, notes = _safety_review(tool, joined)
        lines = ["SAFETY:"]
        for s in safety:
            lines.append(f"- {s}")
        for n in notes:
            lines.append(f"- TIP: {n}")
        lines.append("CMD:")
        # Apply syntax highlighting to the command
        if is_likely_code(command):
            # For slash commands, we need to return text, so we'll use a simple approach
            lines.append(command)
        else:
            lines.append(command)
        lines.append("")
        lines.append("NOT RUN (dry-run). Use 'cybuddy run' CLI for --exec flag.")
        return SlashResponse("\n".join(lines))

    return SlashResponse(f"Unknown command: /{cmd}", success=False)


def _guide_command_hint(text: str) -> str:
    """Generate command hint based on user input context."""
    t = text.lower()
    if any(k in t for k in ["nmap", "scan", "port"]):
        return "nmap -sV -Pn -T2 <target>"
    if any(k in t for k in ["dir", "enum", "hidden", "wordlist"]):
        return "gobuster dir -u http://<host> -w <wordlist>"
    if any(k in t for k in ["vuln", "nikto"]):
        return "nikto -h http://<host>"
    return ""


__all__ = [
    "GuideResponse",
    "SlashResponse",
    "handle_user_input",
    "handle_slash_command",
]