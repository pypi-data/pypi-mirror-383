"""Syntax highlighting and formatting utilities for Cybuddy output."""
from __future__ import annotations

from rich.console import Console
from rich.syntax import Syntax


def detect_language(text: str) -> str:
    """
    Detect programming/scripting language from text content.

    Args:
        text: Code or command text to analyze

    Returns:
        Language identifier for syntax highlighting (bash, python, etc.)
    """
    # Check shebang first
    if text.strip().startswith('#!'):
        shebang = text.split('\n')[0].lower()
        if 'python' in shebang:
            return 'python'
        if any(x in shebang for x in ['bash', 'sh', 'zsh']):
            return 'bash'

    # Common security tools are typically bash commands
    first_token = text.strip().split()[0] if text.strip() else ''
    common_tools = {
        'nmap', 'sqlmap', 'gobuster', 'ffuf', 'nikto', 'hydra',
        'john', 'hashcat', 'metasploit', 'msfconsole', 'msfvenom',
        'burpsuite', 'zaproxy', 'wireshark', 'tcpdump', 'netcat',
        'nc', 'ssh', 'telnet', 'ftp', 'curl', 'wget', 'dig',
        'nslookup', 'whois', 'ping', 'traceroute', 'netstat',
        'iptables', 'aircrack', 'airmon', 'reaver', 'wifite',
        'enum4linux', 'smbclient', 'crackmapexec', 'bloodhound',
        'mimikatz', 'responder', 'impacket', 'searchsploit',
        'exploit', 'payload', 'auxiliary', 'post'
    }

    if first_token.lower() in common_tools:
        return 'bash'

    # Check for Python indicators
    python_indicators = ['import ', 'from ', 'def ', 'class ', 'print(']
    if any(indicator in text for indicator in python_indicators):
        return 'python'

    # Check for SQL
    sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP']
    if any(keyword in text.upper() for keyword in sql_keywords):
        return 'sql'

    # Default to bash for most command-line content
    return 'bash'


def create_syntax_highlight(
    code: str,
    language: str | None = None,
    theme: str = "monokai",
    line_numbers: bool = False,
    word_wrap: bool = True
) -> Syntax:
    """
    Create a Rich Syntax object with syntax highlighting.

    Args:
        code: Code/command text to highlight
        language: Language for highlighting (auto-detected if None)
        theme: Color theme (monokai, dracula, github-dark, nord)
        line_numbers: Show line numbers on the left
        word_wrap: Enable word wrapping for long lines

    Returns:
        Rich Syntax object ready for rendering
    """
    if language is None:
        language = detect_language(code)

    return Syntax(
        code,
        language,
        theme=theme,
        line_numbers=line_numbers,
        word_wrap=word_wrap,
        background_color="default"
    )


def highlight_command(command: str, console: Console | None = None) -> None:
    """
    Print command with syntax highlighting to console.

    Args:
        command: Command text to highlight
        console: Rich Console instance (creates new one if None)
    """
    if console is None:
        console = Console()

    syntax = create_syntax_highlight(command, language="bash")
    console.print(syntax)


def highlight_code_block(
    code: str,
    language: str | None = None,
    console: Console | None = None
) -> None:
    """
    Print code block with syntax highlighting to console.

    Args:
        code: Code text to highlight
        language: Language for highlighting (auto-detected if None)
        console: Rich Console instance (creates new one if None)
    """
    if console is None:
        console = Console()

    syntax = create_syntax_highlight(code, language=language)
    console.print(syntax)


def is_likely_code(text: str) -> bool:
    """
    Determine if text is likely code/command that should be highlighted.

    Args:
        text: Text to analyze

    Returns:
        True if text appears to be code/commands
    """
    # Empty or very short text is probably not code
    if not text or len(text.strip()) < 3:
        return False

    # Check for common code indicators
    code_indicators = [
        '#!',  # Shebang
        'import ', 'from ',  # Python
        'def ', 'class ',  # Python
        'function ', 'const ', 'let ', 'var ',  # JavaScript
        'nmap ', 'sqlmap ', 'curl ',  # Common tools
        '#!/',  # Script
        '-', '--',  # Command flags (multiple)
    ]

    text_lower = text.lower()

    # Multiple flags indicate a command
    if text.count('-') >= 2 or text.count('--') >= 1:
        return True

    # Check for indicators
    if any(indicator in text_lower for indicator in code_indicators):
        return True

    # Check if it starts with a known command
    first_word = text.strip().split()[0] if text.strip() else ''
    common_commands = {
        'ls', 'cd', 'pwd', 'cat', 'grep', 'find', 'chmod',
        'chown', 'ps', 'kill', 'top', 'df', 'du', 'mount',
        'sudo', 'su', 'apt', 'yum', 'dnf', 'pacman',
        'git', 'docker', 'kubectl', 'npm', 'pip', 'python'
    }

    if first_word.lower() in common_commands:
        return True

    return False


__all__ = [
    'detect_language',
    'create_syntax_highlight',
    'highlight_command',
    'highlight_code_block',
    'is_likely_code',
]
