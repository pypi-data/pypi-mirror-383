from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import NamedTuple


class CommandEntry(NamedTuple):
    """Enhanced command entry with metadata."""
    command: str
    timestamp: str
    frequency: int = 1
    category: str = ""


class SmartHistory:
    """Enhanced command history with smart suggestions and analytics."""
    
    def __init__(self, max_size: int = 1000):
        self.history_file = Path.home() / '.local' / 'share' / 'cybuddy' / 'history.json'
        self.max_size = max_size
        self.history = self.load()
        self._command_patterns = self._build_command_patterns()
    
    def _build_command_patterns(self) -> dict[str, list[str]]:
        """Build patterns for smart command categorization."""
        return {
            "explain": ["explain", "what is", "how does", "tell me about"],
            "tip": ["tip", "tips", "guide", "best practice", "technique"],
            "help": ["help", "troubleshoot", "fix", "error", "problem"],
            "report": ["report", "document", "write", "create report"],
            "quiz": ["quiz", "test", "practice", "question"],
            "plan": ["plan", "next step", "what should", "strategy"],
            "history": ["history", "previous", "last", "recent"]
        }
    
    def _categorize_command(self, command: str) -> str:
        """Categorize command based on patterns."""
        cmd_lower = command.lower()
        
        for category, patterns in self._command_patterns.items():
            if any(pattern in cmd_lower for pattern in patterns):
                return category
        
        # Default categorization based on first word
        first_word = command.split()[0] if command.split() else "unknown"
        return first_word if first_word in self._command_patterns else "other"
    
    def _extract_tools_and_techniques(self, command: str) -> list[str]:
        """Extract security tools and techniques from command."""
        tools = [
            'nmap', 'masscan', 'wireshark', 'tcpdump', 'burp', 'sqlmap', 
            'metasploit', 'hydra', 'john', 'hashcat', 'gobuster', 'ffuf',
            'nikto', 'dirb', 'wfuzz', 'netcat', 'nc', 'ssh', 'enum4linux',
            'smbclient', 'impacket', 'crackmapexec', 'responder'
        ]
        
        techniques = [
            'xss', 'sqli', 'sql injection', 'csrf', 'ssrf', 'xxe', 'rce',
            'lfi', 'rfi', 'ssti', 'deserialization', 'privilege escalation',
            'privesc', 'buffer overflow', 'format string', 'race condition'
        ]
        
        found_items = []
        cmd_lower = command.lower()
        
        for tool in tools:
            if tool in cmd_lower:
                found_items.append(tool)
        
        for technique in techniques:
            if technique in cmd_lower:
                found_items.append(technique)
        
        return found_items
    
    def load(self) -> list[CommandEntry]:
        """Load history from file with enhanced metadata."""
        if not self.history_file.exists():
            return []
        
        try:
            with open(self.history_file) as f:
                data = json.load(f)
                commands = data.get('commands', [])
                
                # Convert old format to new format
                if commands and isinstance(commands[0], str):
                    # Migrate from old format
                    return [CommandEntry(cmd, datetime.now().isoformat()) for cmd in commands]
                
                # Load new format
                return [CommandEntry(**cmd) for cmd in commands]
        except (json.JSONDecodeError, FileNotFoundError, TypeError):
            return []
    
    def save(self) -> None:
        """Save history to file with enhanced metadata."""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.history_file, 'w') as f:
            json.dump({
                'commands': [cmd._asdict() for cmd in self.history[-self.max_size:]],
                'last_updated': datetime.now().isoformat(),
                'version': '2.0'
            }, f, indent=2)
    
    def add(self, command: str) -> None:
        """Add command to history with smart deduplication and categorization."""
        if not command.strip():
            return
        
        # Check for exact duplicate
        if self.history and self.history[-1].command == command:
            # Update frequency instead of adding duplicate
            entry = self.history[-1]
            self.history[-1] = entry._replace(frequency=entry.frequency + 1)
            self.save()
            return
        
        # Create new entry with metadata
        category = self._categorize_command(command)
        entry = CommandEntry(
            command=command,
            timestamp=datetime.now().isoformat(),
            frequency=1,
            category=category
        )
        
        self.history.append(entry)
        self.save()
    
    def clear(self) -> None:
        """Clear history."""
        self.history = []
        if self.history_file.exists():
            self.history_file.unlink()
    
    def get_history(self) -> list[str]:
        """Get all history entries as strings."""
        return [entry.command for entry in self.history]
    
    def get_enhanced_history(self) -> list[CommandEntry]:
        """Get all history entries with metadata."""
        return self.history.copy()
    
    def search(self, query: str) -> list[str]:
        """Search history for commands containing query."""
        return [entry.command for entry in self.history if query.lower() in entry.command.lower()]
    
    def get_smart_suggestions(self, current_input: str = "", limit: int = 5) -> list[str]:
        """Generate smart suggestions based on current input and history patterns."""
        if not current_input.strip():
            # Return most frequent recent commands
            recent_entries = self.history[-20:] if len(self.history) > 20 else self.history
            frequency_map = Counter(entry.command for entry in recent_entries)
            return [cmd for cmd, _ in frequency_map.most_common(limit)]
        
        # Find similar commands
        suggestions = []
        input_lower = current_input.lower()
        
        # Exact matches first
        for entry in reversed(self.history):
            if input_lower in entry.command.lower():
                suggestions.append(entry.command)
                if len(suggestions) >= limit:
                    break
        
        # If not enough exact matches, find similar patterns
        if len(suggestions) < limit:
            # Extract tools/techniques from current input
            current_tools = self._extract_tools_and_techniques(current_input)
            
            for entry in reversed(self.history):
                entry_tools = self._extract_tools_and_techniques(entry.command)
                
                # If they share tools/techniques, it's a good suggestion
                if current_tools and any(tool in entry_tools for tool in current_tools):
                    if entry.command not in suggestions:
                        suggestions.append(entry.command)
                        if len(suggestions) >= limit:
                            break
        
        return suggestions[:limit]
    
    def get_category_stats(self) -> dict[str, int]:
        """Get statistics by command category."""
        category_counts = Counter(entry.category for entry in self.history)
        return dict(category_counts)
    
    def get_most_used_tools(self, limit: int = 10) -> list[tuple[str, int]]:
        """Get most frequently used tools/techniques."""
        all_tools = []
        for entry in self.history:
            tools = self._extract_tools_and_techniques(entry.command)
            all_tools.extend(tools)
        
        tool_counts = Counter(all_tools)
        return tool_counts.most_common(limit)
    
    def get_recent_patterns(self, days: int = 7) -> list[str]:
        """Get command patterns from recent days."""
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        recent_entries = []
        
        for entry in self.history:
            try:
                entry_time = datetime.fromisoformat(entry.timestamp).timestamp()
                if entry_time >= cutoff_date:
                    recent_entries.append(entry)
            except ValueError:
                continue
        
        # Find common patterns
        patterns = []
        for entry in recent_entries:
            tools = self._extract_tools_and_techniques(entry.command)
            patterns.extend(tools)
        
        pattern_counts = Counter(patterns)
        return [pattern for pattern, _ in pattern_counts.most_common(10)]


# Legacy compatibility - maintain old interface
class CommandHistory:
    """Legacy wrapper for backward compatibility."""
    
    def __init__(self, max_size: int = 1000):
        self._smart_history = SmartHistory(max_size)
    
    def load(self) -> list[str]:
        return self._smart_history.get_history()
    
    def save(self) -> None:
        self._smart_history.save()
    
    def add(self, command: str) -> None:
        self._smart_history.add(command)
    
    def clear(self) -> None:
        self._smart_history.clear()
    
    def get_history(self) -> list[str]:
        return self._smart_history.get_history()
    
    def search(self, query: str) -> list[str]:
        return self._smart_history.search(query)


# Global history instance
_history_instance: SmartHistory | None = None


def get_history() -> SmartHistory:
    """Get the global history instance with smart features."""
    global _history_instance
    if _history_instance is None:
        _history_instance = SmartHistory()
    return _history_instance


def add_command(command: str) -> None:
    """Add a command to history."""
    get_history().add(command)


def clear_history() -> None:
    """Clear command history."""
    get_history().clear()


def get_history_entries() -> list[str]:
    """Get all history entries."""
    return get_history().get_history()


def search_history(query: str) -> list[str]:
    """Search history for commands containing query."""
    return get_history().search(query)
