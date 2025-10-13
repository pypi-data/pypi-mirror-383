"""
Fuzzy matching and suggestion system for Cybuddy.

Provides intelligent suggestions for typos and similar commands/tools.
"""

from difflib import get_close_matches


def get_tool_suggestions(
    tool_name: str,
    available_tools: list[str],
    max_suggestions: int = 5,
    cutoff: float = 0.4
) -> list[str]:
    """
    Get suggestions for a tool name using fuzzy matching.

    Args:
        tool_name: The tool name to match
        available_tools: List of available tool names
        max_suggestions: Maximum number of suggestions to return
        cutoff: Similarity threshold (0.0 to 1.0)

    Returns:
        List of suggested tool names

    Examples:
        >>> tools = ["nmap", "netcat", "nikto"]
        >>> get_tool_suggestions("nmpa", tools)
        ['nmap']
        >>> get_tool_suggestions("netct", tools)
        ['netcat']
    """
    # Normalize for better matching
    tool_name_lower = tool_name.lower().strip()
    available_tools_lower = [tool.lower() for tool in available_tools]

    # Get close matches
    matches = get_close_matches(
        tool_name_lower,
        available_tools_lower,
        n=max_suggestions,
        cutoff=cutoff
    )

    # Return original case versions
    suggestions = []
    for match in matches:
        # Find original case version
        for original in available_tools:
            if original.lower() == match:
                suggestions.append(original)
                break

    return suggestions


def get_command_suggestions(
    command: str,
    valid_commands: list[str],
    max_suggestions: int = 3,
    cutoff: float = 0.5
) -> list[str]:
    """
    Get suggestions for a command using fuzzy matching.

    Args:
        command: The command to match
        valid_commands: List of valid commands
        max_suggestions: Maximum number of suggestions to return
        cutoff: Similarity threshold (0.0 to 1.0)

    Returns:
        List of suggested commands

    Examples:
        >>> commands = ["explain", "tip", "plan", "assist"]
        >>> get_command_suggestions("explian", commands)
        ['explain']
        >>> get_command_suggestions("tipp", commands)
        ['tip']
    """
    # Normalize for better matching
    command_lower = command.lower().strip()

    # Get close matches
    matches = get_close_matches(
        command_lower,
        valid_commands,
        n=max_suggestions,
        cutoff=cutoff
    )

    # Format as command examples
    suggestions = [f'cybuddy {cmd} "topic"' for cmd in matches]

    return suggestions


def get_category_suggestions(
    query: str,
    categories: list[str],
    max_suggestions: int = 3,
    cutoff: float = 0.4
) -> list[str]:
    """
    Get suggestions for categories using fuzzy matching.

    Args:
        query: The query to match against categories
        categories: List of available categories
        max_suggestions: Maximum number of suggestions to return
        cutoff: Similarity threshold (0.0 to 1.0)

    Returns:
        List of suggested categories

    Examples:
        >>> categories = ["web_attack", "network_scan", "forensics"]
        >>> get_category_suggestions("web", categories)
        ['web_attack']
        >>> get_category_suggestions("net", categories)
        ['network_scan']
    """
    # Normalize for better matching
    query_lower = query.lower().strip()
    categories_lower = [cat.lower() for cat in categories]

    # Get close matches
    matches = get_close_matches(
        query_lower,
        categories_lower,
        n=max_suggestions,
        cutoff=cutoff
    )

    # Return original case versions
    suggestions = []
    for match in matches:
        for original in categories:
            if original.lower() == match:
                suggestions.append(original)
                break

    return suggestions


def get_technique_suggestions(
    query: str,
    techniques: list[str],
    max_suggestions: int = 5,
    cutoff: float = 0.3
) -> list[str]:
    """
    Get suggestions for techniques using fuzzy matching.

    Args:
        query: The query to match against techniques
        techniques: List of available techniques
        max_suggestions: Maximum number of suggestions to return
        cutoff: Similarity threshold (0.0 to 1.0)

    Returns:
        List of suggested techniques

    Examples:
        >>> techniques = ["SQL Injection", "XSS", "CSRF"]
        >>> get_technique_suggestions("sql", techniques)
        ['SQL Injection']
        >>> get_technique_suggestions("cross site", techniques)
        ['XSS', 'CSRF']
    """
    # Normalize for better matching
    query_lower = query.lower().strip()
    techniques_lower = [tech.lower() for tech in techniques]

    # Get close matches
    matches = get_close_matches(
        query_lower,
        techniques_lower,
        n=max_suggestions,
        cutoff=cutoff
    )

    # Return original case versions
    suggestions = []
    for match in matches:
        for original in techniques:
            if original.lower() == match:
                suggestions.append(original)
                break

    return suggestions


def find_partial_matches(
    query: str,
    items: list[str],
    max_results: int = 5
) -> list[str]:
    """
    Find items that contain the query as a substring.

    Args:
        query: The search query
        items: List of items to search
        max_results: Maximum number of results to return

    Returns:
        List of matching items

    Examples:
        >>> items = ["nmap", "nmap scripts", "zenmap"]
        >>> find_partial_matches("nmap", items)
        ['nmap', 'nmap scripts', 'zenmap']
        >>> find_partial_matches("script", items)
        ['nmap scripts']
    """
    query_lower = query.lower().strip()
    matches = []

    for item in items:
        if query_lower in item.lower():
            matches.append(item)
            if len(matches) >= max_results:
                break

    return matches


def rank_suggestions_by_popularity(
    suggestions: list[str],
    popularity_scores: dict
) -> list[str]:
    """
    Rank suggestions by popularity/usage frequency.

    Args:
        suggestions: List of suggestions to rank
        popularity_scores: Dictionary mapping items to popularity scores

    Returns:
        Ranked list of suggestions

    Examples:
        >>> suggestions = ["metasploit", "nmap", "burp"]
        >>> scores = {"nmap": 100, "burp": 80, "metasploit": 90}
        >>> rank_suggestions_by_popularity(suggestions, scores)
        ['nmap', 'metasploit', 'burp']
    """
    # Sort by popularity score (higher is better)
    ranked = sorted(
        suggestions,
        key=lambda x: popularity_scores.get(x, 0),
        reverse=True
    )

    return ranked


def get_smart_suggestions(
    query: str,
    tools: list[str],
    techniques: list[str],
    categories: list[str]
) -> dict:
    """
    Get comprehensive suggestions across all types.

    Args:
        query: The search query
        tools: List of available tools
        techniques: List of available techniques
        categories: List of available categories

    Returns:
        Dictionary with suggestions by type
    """
    return {
        'tools': get_tool_suggestions(query, tools, max_suggestions=3),
        'techniques': get_technique_suggestions(query, techniques, max_suggestions=3),
        'categories': get_category_suggestions(query, categories, max_suggestions=2)
    }
