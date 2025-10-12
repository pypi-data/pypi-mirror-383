"""
Rabbit - A tiny, extensible AI CLI for terminal workflows.
"""

__version__ = "0.0.12"  # This will be updated by the release workflow

from .rabbit import main

__all__ = ["main", "__version__"]