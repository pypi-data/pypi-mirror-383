from __future__ import annotations

from ..history import clear_history, get_history, search_history


def cmd_history(args: list[str]) -> int:
    """Handle the history command with smart suggestions and analytics."""
    if not args:
        # Show recent history with smart suggestions
        history = get_history()
        if not history:
            print("No command history yet.")
            print("\n💡 Try these commands to get started:")
            print("  cybuddy explain 'nmap -sV'")
            print("  cybuddy tip 'sql injection'")
            print("  cybuddy help 'connection refused'")
            return 0
        
        print("📚 Recent Commands:")
        recent_entries = history.get_history()[-20:]  # Show last 20
        for i, cmd in enumerate(recent_entries, 1):
            print(f"{i:3d}. {cmd}")
        
        # Show smart suggestions
        suggestions = history.get_smart_suggestions(limit=3)
        if suggestions:
            print("\n💡 Smart Suggestions:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
        
        return 0
    
    if args[0] == "--clear":
        clear_history()
        print("🗑️  Command history cleared.")
        return 0
    
    if args[0] == "--search" and len(args) > 1:
        query = " ".join(args[1:])
        results = search_history(query)
        if not results:
            print(f"❌ No commands found matching '{query}'.")
            
            # Provide smart suggestions based on query
            history = get_history()
            suggestions = history.get_smart_suggestions(query, limit=3)
            if suggestions:
                print("\n💡 Did you mean one of these?")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"  {i}. {suggestion}")
            return 0
        
        print(f"🔍 Commands matching '{query}':")
        for i, cmd in enumerate(results, 1):
            print(f"{i:3d}. {cmd}")
        return 0
    
    if args[0] == "--stats":
        # Show analytics and statistics
        history = get_history()
        if not history:
            print("No command history yet.")
            return 0
        
        print("📊 Command History Analytics:")
        print("=" * 40)
        
        # Category statistics
        category_stats = history.get_category_stats()
        if category_stats:
            print("\n📈 Commands by Category:")
            for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
                print(f"  {category:12}: {count:3d}")
        
        # Most used tools
        tools = history.get_most_used_tools(limit=5)
        if tools:
            print("\n🛠️  Most Used Tools/Techniques:")
            for tool, count in tools:
                print(f"  {tool:20}: {count:3d}")
        
        # Recent patterns
        patterns = history.get_recent_patterns(days=7)
        if patterns:
            print("\n🔥 Recent Patterns (7 days):")
            for pattern in patterns[:5]:
                print(f"  • {pattern}")
        
        return 0
    
    if args[0] == "--suggest" and len(args) > 1:
        # Get smart suggestions for specific input
        query = " ".join(args[1:])
        history = get_history()
        suggestions = history.get_smart_suggestions(query, limit=5)
        
        if not suggestions:
            print(f"❌ No suggestions found for '{query}'.")
            return 0
        
        print(f"💡 Smart Suggestions for '{query}':")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i:2d}. {suggestion}")
        return 0
    
    print("Usage: cybuddy history [--clear|--search <query>|--stats|--suggest <input>]")
    print("\nOptions:")
    print("  --clear              Clear command history")
    print("  --search <query>     Search history for commands")
    print("  --stats              Show analytics and statistics")
    print("  --suggest <input>    Get smart suggestions for input")
    return 1
