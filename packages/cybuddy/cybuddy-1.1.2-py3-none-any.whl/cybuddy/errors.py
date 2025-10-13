"""
Smart error handling system for Cybuddy.

Provides clear, actionable error messages with:
- Description of what went wrong
- Why it happened
- How to fix it
- Similar commands/tools suggestions
"""


from rich.console import Console

console = Console()


class SmartError:
    """Smart error class with actionable feedback."""

    def __init__(
        self,
        message: str,
        reason: str | None = None,
        fix: str | None = None,
        suggestions: list[str] | None = None,
        browse_hint: str | None = None
    ):
        """
        Initialize a smart error.

        Args:
            message: What went wrong
            reason: Why it happened
            fix: How to fix it
            suggestions: Similar commands/tools
            browse_hint: Additional help hint
        """
        self.message = message
        self.reason = reason
        self.fix = fix
        self.suggestions = suggestions or []
        self.browse_hint = browse_hint

    def display(self) -> None:
        """Display the error message with formatting."""
        # Main error message
        console.print(f"[red]✗ Error:[/red] {self.message}")

        # Reason (why it happened)
        if self.reason:
            console.print(f"\n[dim]{self.reason}[/dim]")

        # How to fix
        if self.fix:
            console.print(f"\n[cyan]💭 Tip:[/cyan] {self.fix}")

        # Suggestions
        if self.suggestions:
            console.print("\n[yellow]💡 Did you mean:[/yellow]")
            for suggestion in self.suggestions:
                console.print(f"  • [bold]{suggestion}[/bold]")

        # Browse hint
        if self.browse_hint:
            console.print(f"\n[cyan]💭 {self.browse_hint}[/cyan]")

        # Help reference
        console.print("\n[dim]📚 See all commands: [bold]cybuddy help[/bold][/dim]")


def handle_unknown_tool(tool_name: str, available_tools: list[str]) -> SmartError:
    """
    Handle unknown tool name error.

    Args:
        tool_name: The unknown tool name
        available_tools: List of available tool names

    Returns:
        SmartError with suggestions
    """
    from .suggestions import get_tool_suggestions

    suggestions = get_tool_suggestions(tool_name, available_tools)

    return SmartError(
        message=f'Unknown tool: "{tool_name}"',
        reason=f'The tool "{tool_name}" is not in the security tools database.',
        fix='Check the spelling or browse available tools.',
        suggestions=suggestions,
        browse_hint="Browse categories: Web, Network, Forensics, Cryptography, etc."
    )


def handle_unknown_command(command: str) -> SmartError:
    """
    Handle unknown command error.

    Args:
        command: The unknown command

    Returns:
        SmartError with command suggestions
    """
    from .suggestions import get_command_suggestions

    valid_commands = [
        "explain", "tip", "plan", "assist", "report", "quiz", "help"
    ]

    suggestions = get_command_suggestions(command, valid_commands)

    return SmartError(
        message=f'Unknown command: "{command}"',
        reason=f'"{command}" is not a valid Cybuddy command.',
        fix='Use one of the available commands listed below.',
        suggestions=suggestions
    )


def handle_missing_argument(command: str, argument_name: str = "topic") -> SmartError:
    """
    Handle missing required argument error.

    Args:
        command: The command that's missing an argument
        argument_name: Name of the missing argument

    Returns:
        SmartError with usage example
    """
    examples = {
        "explain": 'cybuddy explain "nmap"',
        "tip": 'cybuddy tip "sql injection"',
        "plan": 'cybuddy plan "web app pentest"',
        "assist": 'cybuddy assist "found open port 22"',
        "report": 'cybuddy report "XSS vulnerability"',
        "quiz": 'cybuddy quiz "web security"'
    }

    example = examples.get(command, f'cybuddy {command} "topic"')

    return SmartError(
        message=f'Missing required argument: {argument_name}',
        reason=f'The "{command}" command requires a {argument_name} to be specified.',
        fix=f'Provide a {argument_name} as an argument.',
        suggestions=[f'Example: {example}']
    )


def handle_empty_query() -> SmartError:
    """
    Handle empty query error.

    Returns:
        SmartError with usage examples
    """
    return SmartError(
        message='Empty query provided',
        reason='You need to specify what you want to learn about.',
        fix='Provide a security topic, tool, or question.',
        suggestions=[
            'cybuddy explain "nmap"',
            'cybuddy tip "sql injection"',
            'cybuddy "how do I scan for vulnerabilities?"'
        ]
    )


def handle_invalid_characters(query: str, invalid_chars: str) -> SmartError:
    """
    Handle invalid characters in query.

    Args:
        query: The query with invalid characters
        invalid_chars: String of invalid characters found

    Returns:
        SmartError with guidance
    """
    cleaned_query = ''.join(
        c for c in query if c not in invalid_chars
    ).strip()

    suggestions = []
    if cleaned_query:
        suggestions.append(f'Try: cybuddy "{cleaned_query}"')

    return SmartError(
        message='Invalid characters in query',
        reason=f'The query contains special characters that may cause issues: {invalid_chars}',
        fix='Use alphanumeric characters, spaces, and basic punctuation.',
        suggestions=suggestions
    )


def handle_no_results(query: str) -> SmartError:
    """
    Handle no results found error.

    Args:
        query: The search query that returned no results

    Returns:
        SmartError with search tips
    """
    return SmartError(
        message=f'No results found for: "{query}"',
        reason='The search didn\'t match any tools, techniques, or scenarios.',
        fix='Try using different keywords or browse by category.',
        suggestions=[
            'Use simpler keywords (e.g., "web" instead of "web application")',
            'Try tool names (e.g., "nmap", "burp", "metasploit")',
            'Browse categories with: cybuddy help'
        ],
        browse_hint='Browse categories: Web, Network, Forensics, Cryptography, etc.'
    )






def handle_network_error() -> SmartError:
    """
    Handle network connectivity error.

    Returns:
        SmartError with troubleshooting steps
    """
    return SmartError(
        message='Network connection failed',
        reason='Unable to connect to the AI service.',
        fix='Check your internet connection and try again.',
        suggestions=[
            'Verify your internet is working',
            'Check if the AI service is accessible',
            'Try again in a few moments',
            'Use offline mode without --send flag'
        ]
    )
