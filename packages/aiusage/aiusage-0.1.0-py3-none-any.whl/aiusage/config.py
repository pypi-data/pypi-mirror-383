"""
Configuration management for aiusage.
Handles loading and saving user preferences like renewal day.
"""

import json
from pathlib import Path
from typing import Optional

from platformdirs import user_config_dir


def get_config_file() -> Path:
    """
    Get the path to the config file.

    Returns:
        Path to the aiusage config file in the user's config directory
    """
    config_dir = Path(user_config_dir('aiusage', appauthor='aiusage'))
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / 'config.json'


def load_renewal_day() -> Optional[int]:
    """
    Load the saved renewal day from config file.

    Returns:
        The saved renewal day (1-31) or None if not saved
    """
    config_file = get_config_file()
    if not config_file.exists():
        return None

    try:
        with config_file.open('r') as f:
            config = json.load(f)
            renewal_day = config.get('renewal_day')
            if isinstance(renewal_day, int):
                return renewal_day
            return None
    except (json.JSONDecodeError, OSError):
        return None


def save_renewal_day(day: int) -> None:
    """
    Save the renewal day to config file.

    Args:
        day: The renewal day (1-31) to save
    """
    config_file = get_config_file()

    # Load existing config if it exists
    config = {}
    if config_file.exists():
        try:
            with config_file.open('r') as f:
                config = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    # Update with new renewal day
    config['renewal_day'] = day

    # Save config
    try:
        with config_file.open('w') as f:
            json.dump(config, f, indent=2)
    except OSError as e:
        print(f'Warning: Could not save config: {e}')
