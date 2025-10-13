"""Simple TUI using prompt_toolkit's proper async API."""
from __future__ import annotations

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from rich.console import Console

from .cli import (
    explain_command,
    help_troubleshoot,
    history_append,
    micro_report,
    quick_tip,
    quiz_flashcards,
    step_planner,
)


class SimpleTUI:
    """Minimal TUI with 7 core commands using prompt_toolkit properly."""

    COMMANDS = {
        "explain": "Learn commands (e.g., explain 'nmap -sV')",
        "tip": "Study guide (e.g., tip 'SQL injection')",
        "help": "Troubleshoot (e.g., help 'connection refused')",
        "report": "Practice write-ups (e.g., report 'Found SQLi')",
        "quiz": "Active recall (e.g., quiz 'SQL Injection')",
        "plan": "Next steps (e.g., plan 'found port 80 open')",
        "exit": "Exit Cybuddy",
    }

    def __init__(self, session: str | None = None) -> None:
        self.console = Console()
        self.session_name = session
        self.prompt_session = PromptSession()

    async def run(self) -> None:
        """Run the interactive TUI using prompt_toolkit's async API."""
        self._show_welcome()

        # Main input loop using prompt_async
        while True:
            try:
                # Use patch_stdout to prevent output corruption
                with patch_stdout():
                    text = await self.prompt_session.prompt_async("❯ ", default="")
                    text = text.strip()

                if not text:
                    continue

                if text.lower() in {"exit", "quit"}:
                    self.console.print("[green]Good luck! Document your steps and be safe.[/green]")
                    break

                # Process command
                self._process_command(text)

            except (EOFError, KeyboardInterrupt):
                self.console.print()
                self.console.print("[green]Good luck! Document your steps and be safe.[/green]")
                break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")

    def _show_welcome(self) -> None:
        """Show welcome message."""
        self.console.clear()
        from .tui.logo import render_logo  # type: ignore
        logo = render_logo(self.console.width)
        self.console.print(logo)
        from rich.text import Text
        self.console.print(title, justify="center")

        self.console.print("Your Security Learning Companion", style="dim italic", justify="center")
        self.console.print()

        self.console.print("[cyan]Available commands:[/cyan]")
        for cmd, desc in self.COMMANDS.items():
            self.console.print(f"  [yellow]{cmd:8s}[/yellow] → {desc}")

        self.console.print()
        self.console.print("[dim]Examples:[/dim]")
        self.console.print("  [dim]explain 'nmap -sV target.local'[/dim]")
        self.console.print("  [dim]tip 'SQL injection basics'[/dim]")
        self.console.print("  [dim]help 'connection refused'[/dim]")
        self.console.print()

    def _process_command(self, text: str) -> None:
        """Process user command."""
        # Parse command
        parts = text.split(maxsplit=1)
        if not parts:
            return

        cmd = parts[0].lower()
        arg = parts[1].strip('"\'') if len(parts) > 1 else ""

        # Route to handler
        self.console.print()

        if cmd == "explain":
            if not arg:
                self.console.print("[red]⚠[/red] Usage: explain '<command>'")
            else:
                result = explain_command(arg)
                self._print_response("Explanation", result)

        elif cmd == "tip":
            if not arg:
                self.console.print("[red]⚠[/red] Usage: tip '<topic>'")
            else:
                result = quick_tip(arg)
                self._print_response("Tip", result)

        elif cmd == "help":
            if not arg:
                self.console.print("[red]⚠[/red] Usage: help '<error message>'")
            else:
                result = help_troubleshoot(arg)
                self._print_response("Troubleshooting", result)

        elif cmd == "report":
            if not arg:
                self.console.print("[red]⚠[/red] Usage: report '<finding>'")
            else:
                result = micro_report(arg)
                self._print_response("Report Template", result)

        elif cmd == "quiz":
            if not arg:
                self.console.print("[red]⚠[/red] Usage: quiz '<topic>'")
            else:
                result = quiz_flashcards(arg)
                self._print_response("Quiz", result)

        elif cmd == "plan":
            if not arg:
                self.console.print("[red]⚠[/red] Usage: plan '<context>'")
            else:
                result = step_planner(arg)
                self._print_response("Next Steps", result)

        else:
            self.console.print(f"[red]⚠[/red] Unknown command: {cmd}")
            self.console.print("[dim]Available: " + ", ".join(self.COMMANDS.keys()) + "[/dim]")

        self.console.print()

        # Log to history
        history_append(
            {"type": "tui", "data": {"cmd": cmd, "arg": arg}},
            session=self.session_name
        )

    def _print_response(self, title: str, content: str) -> None:
        """Print formatted response with README-style borders and syntax highlighting."""
        from .formatters import create_syntax_highlight, is_likely_code

        # Top border with title
        border_len = 50 - len(title)
        self.console.print(f"[bold yellow]─── {title} {'─' * border_len}[/bold yellow]")

        # Content with 2-space indent and syntax highlighting for code blocks
        lines = content.split("\n")
        code_buffer = []
        in_code_block = False

        for line in lines:
            # Detect potential code lines (start with common commands or have flags)
            if is_likely_code(line.strip()) and not in_code_block:
                in_code_block = True
                code_buffer = [line]
            elif in_code_block:
                # Continue code block if line looks like code or is empty
                if is_likely_code(line.strip()) or not line.strip():
                    code_buffer.append(line)
                else:
                    # End code block and print it
                    if code_buffer:
                        code_text = "\n".join(code_buffer)
                        syntax = create_syntax_highlight(code_text, line_numbers=False)
                        self.console.print(syntax)
                        code_buffer = []
                    in_code_block = False
                    # Print current line as regular text
                    if line.strip():
                        self.console.print(f"  {line}")
                    else:
                        self.console.print()
            else:
                # Regular text line
                if line.strip():
                    self.console.print(f"  {line}")
                else:
                    self.console.print()

        # Print any remaining code buffer
        if code_buffer:
            code_text = "\n".join(code_buffer)
            syntax = create_syntax_highlight(code_text, line_numbers=False)
            self.console.print(syntax)

        # Bottom border
        self.console.print("[bold yellow]" + "─" * 60 + "[/bold yellow]")


__all__ = ["SimpleTUI"]