"""Helpers for I/O interactions with the terminal."""

import sys
from typing import Optional


def read_stdin_if_piped() -> Optional[str]:
    if not sys.stdin.isatty():
        data = sys.stdin.read().strip()
        return data if data else None
    return None


def print_stream_chunk(chunk: str) -> None:
    sys.stdout.write(chunk)
    sys.stdout.flush()
