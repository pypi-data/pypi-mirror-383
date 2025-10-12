"""Message construction utilities."""

from typing import Dict, List, Optional

Message = Dict[str, str]


def build_messages(system_text: Optional[str], history: List[Message], user_query: str) -> List[Message]:
    messages: List[Message] = []
    if system_text:
        messages.append({"role": "system", "content": system_text})
    messages.extend(history)
    messages.append({"role": "user", "content": user_query})
    return messages
