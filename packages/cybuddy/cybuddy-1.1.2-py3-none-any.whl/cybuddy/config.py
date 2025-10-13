"""Configuration management for Cybuddy with sensible defaults."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

# Default configuration - works for 99% of users
DEFAULT_CONFIG = {
    'tui': {
        'theme': 'default',
        'show_tips': True,
        'history_file': '~/.local/share/cybuddy/history.jsonl'
    },
    'cli': {
        'color': True,
        'verbose': False
    },
    'data': {
        'mock_mode': True,  # v1.0 is always mock
        'api_url': None
    },
    'history': {
        'enabled': True,
        'path': '~/.local/share/cybuddy/history.jsonl',
        'verbatim': False
    },
    'output': {
        'truncate_lines': 60
    },
    'approvals': {
        'require_exec': True
    }
}


def _config_path() -> Path:
    """Get the standard config file path."""
    return Path.home() / '.config' / 'cybuddy' / 'config.yaml'


def _old_config_path() -> Path:
    """Get the old config file path for migration."""
    return Path.home() / '.cybuddy' / 'config.toml'


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> None:
    """Deep merge override dict into base dict."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def migrate_old_config() -> bool:
    """
    Migrate config from old location if exists.
    
    Returns:
        True if migration was performed, False otherwise.
    """
    old_path = _old_config_path()
    new_path = _config_path()
    
    if old_path.exists() and not new_path.exists():
        try:
            # Create new config directory
            new_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Parse old TOML config and convert to YAML
            old_config = {}
            with open(old_path, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" not in line:
                        continue
                    k, v = [p.strip() for p in line.split("=", 1)]
                    v = v.strip()
                    if v.lower() in {"true", "false"}:
                        old_config[k] = v.lower() == "true"
                    elif v.startswith('"') and v.endswith('"'):
                        old_config[k] = v.strip('"')
                    else:
                        try:
                            old_config[k] = int(v)
                        except ValueError:
                            old_config[k] = v
            
            # Convert to new YAML format
            new_config = DEFAULT_CONFIG.copy()
            
            # Map old keys to new structure
            if old_config.get("output.truncate_lines"):
                new_config["output"]["truncate_lines"] = old_config["output.truncate_lines"]
            
            # Save as YAML
            with open(new_path, 'w', encoding='utf-8') as f:
                yaml.dump(new_config, f, default_flow_style=False, sort_keys=True)
            
            print(f"Migrated config from {old_path} to {new_path}")
            return True
        except Exception as e:
            print(f"Warning: Could not migrate config: {e}")
            return False
    
    return False


def load_config() -> dict[str, Any]:
    """
    Load configuration with fallback to defaults.

    Returns:
        Configuration dictionary with user settings merged over defaults.
    """
    # Start with defaults
    config = DEFAULT_CONFIG.copy()

    # Try to migrate old config first
    migrate_old_config()

    # Load user config if it exists
    config_path = _config_path()
    if config_path.exists():
        try:
            with open(config_path, encoding='utf-8') as f:
                user_config = yaml.safe_load(f) or {}
                # Merge user config with defaults
                _deep_merge(config, user_config)
        except Exception as e:
            print(f"Warning: Could not load config file {config_path}: {e}")


    return config


def save_config(config: dict[str, Any]) -> bool:
    """
    Save configuration to file.
    
    Args:
        config: Configuration dictionary to save.
        
    Returns:
        True if saved successfully, False otherwise.
    """
    try:
        config_path = _config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=True)
        
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def get_config_value(key_path: str, default: Any = None) -> Any:
    """
    Get a configuration value using dot notation.
    
    Args:
        key_path: Dot-separated path to the config value (e.g., 'tui.theme').
        default: Default value if key is not found.
        
    Returns:
        Configuration value or default.
    """
    config = load_config()
    keys = key_path.split('.')
    
    current = config
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current
