"""Session history persistence and helpers."""

import json
from typing import Dict, List

from .config import SESSIONS_DIR


def session_path(name: str):
    safe = "".join(c for c in name if c.isalnum() or c in ("-", "_", "."))
    return SESSIONS_DIR / f"{safe}.json"


def load_session(name: str) -> List[Dict[str, str]]:
    path = session_path(name)
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return []
    return []


def save_session(name: str, messages: List[Dict[str, str]]) -> None:
    path = session_path(name)
    path.write_text(json.dumps(messages, ensure_ascii=False, indent=2))


def append_message(messages: List[Dict[str, str]], role: str, content: str) -> None:
    messages.append({"role": role, "content": content})
