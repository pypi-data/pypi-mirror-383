"""Simple TUI using prompt_toolkit's proper async API with smart suggestions."""
from __future__ import annotations

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.patch_stdout import patch_stdout
from rich.console import Console

from ..cli import (
    explain_command,
    help_troubleshoot,
    history_append,
    micro_report,
    quick_tip,
    quiz_flashcards,
    step_planner,
)
from ..history import get_history


class SmartCompleter(Completer):
    """Smart command completer with history-based suggestions."""
    
    def __init__(self):
        self.history = get_history()
        self.base_commands = [
            "explain", "tip", "help", "assist", "report", "quiz", "plan", "history", "clear", "exit"
        ]
    
    def get_completions(self, document, complete_event):
        """Provide smart completions based on context and history."""
        text = document.text_before_cursor
        words = text.split()
        
        # If no words, suggest base commands
        if not words:
            for cmd in self.base_commands:
                yield Completion(cmd, start_position=0, display=cmd, style="class:completion")
            return
        
        # If first word is a command, suggest smart completions
        if words[0].lower() in self.base_commands:
            if len(words) == 1:
                # Suggest common queries for this command
                suggestions = self._get_command_suggestions(words[0].lower())
                for suggestion in suggestions:
                    # Calculate start position to replace the entire current text
                    start_pos = -len(text)
                    yield Completion(
                        f"{words[0]} '{suggestion}'", 
                        start_position=start_pos,
                        display=suggestion,
                        style="class:completion"
                    )
            else:
                # Suggest based on partial input
                partial = " ".join(words[1:])
                suggestions = self.history.get_smart_suggestions(partial, limit=5)
                for suggestion in suggestions:
                    # Calculate start position to replace the entire current text
                    start_pos = -len(text)
                    yield Completion(
                        f"{words[0]} '{suggestion}'",
                        start_position=start_pos,
                        display=suggestion,
                        style="class:completion"
                    )
        else:
            # Suggest base commands - replace only the current word
            current_word = words[0]
            for cmd in self.base_commands:
                if cmd.startswith(current_word.lower()):
                    # Calculate start position to replace only the current word
                    start_pos = -len(current_word)
                    yield Completion(cmd, start_position=start_pos, display=cmd, style="class:completion")
    
    def _get_command_suggestions(self, command: str) -> list[str]:
        """Get common suggestions for specific commands."""
        suggestions = {
            "explain": [
                "nmap -sV", "burp suite", "sqlmap", "metasploit", "wireshark",
                "hydra", "john the ripper", "gobuster", "nikto", "netcat"
            ],
            "tip": [
                "sql injection", "xss", "csrf", "privilege escalation", "buffer overflow",
                "network scanning", "password cracking", "web application testing"
            ],
            "help": [
                "connection refused", "permission denied", "command not found",
                "port already in use", "authentication failed"
            ],
            "report": [
                "found sql injection", "discovered open ports", "identified vulnerabilities",
                "completed penetration test", "security assessment findings"
            ],
            "quiz": [
                "sql injection", "network protocols", "cryptography", "web security",
                "penetration testing", "forensics", "incident response"
            ],
            "plan": [
                "found open port 80", "discovered sql injection", "got initial access",
                "identified admin panel", "found credentials"
            ],
            "clear": []  # Clear command doesn't need suggestions
        }
        return suggestions.get(command, [])


class SimpleTUI:
    """Enhanced TUI with 8 core commands and smart suggestions."""

    COMMANDS = {
        "explain": "Learn commands (e.g., explain 'nmap -sV')",
        "tip": "Study guide (e.g., tip 'SQL injection')",
        "help": "Troubleshoot (e.g., help 'connection refused')",
        "assist": "Troubleshoot (alias for help)",
        "report": "Practice write-ups (e.g., report 'Found SQLi')",
        "quiz": "Active recall (e.g., quiz 'SQL Injection')",
        "plan": "Next steps (e.g., plan 'found port 80 open')",
        "history": "View command history and analytics",
        "clear": "Clear the terminal screen",
        "exit": "Exit Cybuddy",
    }

    def __init__(self, session: str | None = None) -> None:
        self.console = Console()
        self.session_name = session
        self.completer = SmartCompleter()
        self.prompt_session = PromptSession(completer=self.completer)

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
        self.console.print()
        
        # Print colored shield logo with gradient (green to cyan) and medical cross
        # Matches the SVG design: rgb(0,255,136) → rgb(0,255,255)
        print("\033[1;38;2;0;255;136m        ▄▀▀▀▄\033[0m")
        print("\033[1;38;2;0;255;150m       █  │  █\033[0m")
        print("\033[1;38;2;0;255;170m      █ ──┼── █\033[0m      \033[1;97mCY\033[1;38;2;0;255;255mBUDDY\033[0m")
        print("\033[1;38;2;0;255;190m      █   │   █\033[0m")
        print("\033[1;38;2;0;255;210m       █     █\033[0m       \033[2mYour Security Learning Companion\033[0m")
        print("\033[1;38;2;0;255;230m        █   █\033[0m")
        print("\033[1;38;2;0;255;245m         █ █\033[0m")
        print("\033[1;38;2;0;255;255m          ▀\033[0m\n")

        self.console.print("[cyan]Available commands:[/cyan]")
        for cmd, desc in self.COMMANDS.items():
            self.console.print(f"  [yellow]{cmd:8s}[/yellow] → {desc}")

        self.console.print()
        self.console.print("[dim]Examples:[/dim]")
        self.console.print("  [dim]explain 'nmap -sV target.local'[/dim]")
        self.console.print("  [dim]tip 'SQL injection basics'[/dim]")
        self.console.print("  [dim]help 'connection refused'[/dim]")
        self.console.print()
        self.console.print("[green]💡 Natural Language Support:[/green]")
        self.console.print("  [dim]how do I scan ports?[/dim]")
        self.console.print("  [dim]what is nmap?[/dim]")
        self.console.print("  [dim]tips on sql injection[/dim]")
        self.console.print("  [dim]I'm stuck on this nmap thing[/dim]")
        self.console.print()

    def _process_command(self, text: str) -> None:
        """Process user command with progressive loading feedback."""
        import shlex
        from ..nl_parser import is_natural_language, parse_natural_query

        # Show processing feedback for natural language queries
        if is_natural_language(text):
            # Show processing indicator
            with self.console.status("[bold green]Processing natural language query...", spinner="dots"):
                cmd, parsed_query = parse_natural_query(text)
            
            # Process as the parsed command
            if cmd == "clarify":
                self.console.print(f"[yellow]❓ {parsed_query}[/yellow]")
                return
            
            # Set up for normal command processing
            parts = [cmd, parsed_query]
        else:
            # Parse command using shlex for proper shell-like parsing
            try:
                parts = shlex.split(text)
            except ValueError:
                # Fallback for unclosed quotes
                parts = text.split()

        if not parts:
            return

        cmd = parts[0].lower()
        # Join all remaining parts as the argument
        # This preserves the original behavior but handles quotes properly
        arg = " ".join(parts[1:]) if len(parts) > 1 else ""

        # Route to handler with processing feedback
        self.console.print()
        
        # Show processing feedback for complex operations
        if cmd in ["explain", "tip", "help", "assist", "report", "quiz", "plan"]:
            with self.console.status(f"[bold green]Processing {cmd} request...", spinner="dots"):
                self._execute_command(cmd, arg)
        else:
            self._execute_command(cmd, arg)

        # Log to history
        history_append(
            {"type": "tui", "data": {"cmd": cmd, "arg": arg}},
            session=self.session_name
        )

    def _execute_command(self, cmd: str, arg: str) -> None:
        """Execute a command with the given argument."""
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

        elif cmd in {"help", "assist"}:
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

        elif cmd == "history":
            self._handle_history_command(arg)

        elif cmd == "clear":
            self._handle_clear_command()

        else:
            self.console.print(f"[red]⚠[/red] Unknown command: {cmd}")
            self.console.print("[dim]Available: " + ", ".join(self.COMMANDS.keys()) + "[/dim]")

        self.console.print()

    def _print_response(self, title: str, content: str) -> None:
        """Print formatted response with README-style borders and syntax highlighting."""
        from ..formatters import create_syntax_highlight, is_likely_code

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

    def _handle_history_command(self, arg: str) -> None:
        """Handle history command with smart suggestions."""
        from ..history import get_history
        
        history = get_history()
        
        if not arg:
            # Show recent history with smart suggestions
            entries = history.get_history()
            if not entries:
                self.console.print("[yellow]📚 No command history yet.[/yellow]")
                self.console.print("\n[cyan]💡 Try these commands to get started:[/cyan]")
                self.console.print("  [dim]explain 'nmap -sV'[/dim]")
                self.console.print("  [dim]tip 'sql injection'[/dim]")
                self.console.print("  [dim]help 'connection refused'[/dim]")
                return
            
            self.console.print("[cyan]📚 Recent Commands:[/cyan]")
            recent_entries = entries[-20:]  # Show last 20
            for i, cmd in enumerate(recent_entries, 1):
                self.console.print(f"  [dim]{i:3d}.[/dim] {cmd}")
            
            # Show smart suggestions
            suggestions = history.get_smart_suggestions(limit=3)
            if suggestions:
                self.console.print("\n[green]💡 Smart Suggestions:[/green]")
                for i, suggestion in enumerate(suggestions, 1):
                    self.console.print(f"  [dim]{i}.[/dim] {suggestion}")
            return
        
        # Parse history arguments
        args = arg.split()
        
        if args[0] == "--clear":
            history.clear()
            self.console.print("[green]🗑️  Command history cleared.[/green]")
            return
        
        if args[0] == "--search" and len(args) > 1:
            query = " ".join(args[1:])
            results = history.search(query)
            if not results:
                self.console.print(f"[red]❌ No commands found matching '{query}'.[/red]")
                
                # Provide smart suggestions based on query
                suggestions = history.get_smart_suggestions(query, limit=3)
                if suggestions:
                    self.console.print("\n[green]💡 Did you mean one of these?[/green]")
                    for i, suggestion in enumerate(suggestions, 1):
                        self.console.print(f"  [dim]{i}.[/dim] {suggestion}")
                return
            
            self.console.print(f"[cyan]🔍 Commands matching '{query}':[/cyan]")
            for i, cmd in enumerate(results, 1):
                self.console.print(f"  [dim]{i:3d}.[/dim] {cmd}")
            return
        
        if args[0] == "--stats":
            # Show analytics and statistics
            if not history.get_history():
                self.console.print("[yellow]No command history yet.[/yellow]")
                return
            
            self.console.print("[cyan]📊 Command History Analytics:[/cyan]")
            self.console.print("=" * 40)
            
            # Category statistics
            category_stats = history.get_category_stats()
            if category_stats:
                self.console.print("\n[green]📈 Commands by Category:[/green]")
                for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
                    self.console.print(f"  [yellow]{category:12}[/yellow]: [cyan]{count:3d}[/cyan]")
            
            # Most used tools
            tools = history.get_most_used_tools(limit=5)
            if tools:
                self.console.print("\n[green]🛠️  Most Used Tools/Techniques:[/green]")
                for tool, count in tools:
                    self.console.print(f"  [yellow]{tool:20}[/yellow]: [cyan]{count:3d}[/cyan]")
            
            # Recent patterns
            patterns = history.get_recent_patterns(days=7)
            if patterns:
                self.console.print("\n[green]🔥 Recent Patterns (7 days):[/green]")
                for pattern in patterns[:5]:
                    self.console.print(f"  [dim]•[/dim] {pattern}")
            return
        
        if args[0] == "--suggest" and len(args) > 1:
            # Get smart suggestions for specific input
            query = " ".join(args[1:])
            suggestions = history.get_smart_suggestions(query, limit=5)
            
            if not suggestions:
                self.console.print(f"[red]❌ No suggestions found for '{query}'.[/red]")
                return
            
            self.console.print(f"[green]💡 Smart Suggestions for '{query}':[/green]")
            for i, suggestion in enumerate(suggestions, 1):
                self.console.print(f"  [dim]{i:2d}.[/dim] {suggestion}")
            return
        
        # Invalid arguments
        self.console.print("[red]⚠[/red] Invalid history arguments")
        self.console.print("[dim]Usage: history [--clear|--search <query>|--stats|--suggest <input>][/dim]")

    def _handle_clear_command(self) -> None:
        """Handle clear command to clear the terminal screen."""
        import os
        os.system('clear' if os.name == 'posix' else 'cls')


__all__ = ["SimpleTUI"]