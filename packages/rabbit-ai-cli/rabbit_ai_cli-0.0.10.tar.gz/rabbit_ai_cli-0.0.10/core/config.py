"""Runtime configuration paths and environment loading for the rabbit CLI."""

import os
import pathlib
from typing import Optional


CONFIG_DIR = pathlib.Path(os.environ.get("XDG_CONFIG_HOME", pathlib.Path.home() / ".config")) / "aibot"
SESSIONS_DIR = CONFIG_DIR / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


def load_env_file(env_file_path: Optional[str] = None) -> dict:
    """
    Load environment variables from a .env file.
    
    Args:
        env_file_path: Path to the .env file. If None, looks for .env in current directory.
        
    Returns:
        Dictionary of environment variables from the file.
    """
    if env_file_path is None:
        env_file_path = ".env"
    
    env_vars = {}
    env_path = pathlib.Path(env_file_path)
    
    if not env_path.exists():
        return env_vars
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse KEY=VALUE format
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    env_vars[key] = value
    except Exception as e:
        # Silently continue if there's an error reading the file
        pass
    
    return env_vars


def get_api_key(key_name: str, env_file_path: Optional[str] = None) -> Optional[str]:
    """
    Get an API key, first trying from .env file, then from environment variables.
    
    Args:
        key_name: Name of the environment variable (e.g., 'OPENAI_API_KEY')
        env_file_path: Path to the .env file. If None, looks for .env in current directory.
        
    Returns:
        The API key value or None if not found.
    """
    # First try to load from .env file
    env_vars = load_env_file(env_file_path)
    if key_name in env_vars:
        return env_vars[key_name]
    
    # Fall back to environment variables
    return os.environ.get(key_name)
