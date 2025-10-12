#!/usr/bin/env python3
"""
aibot: tiny, extensible AI CLI for terminal workflows.

Features:
- Providers: OpenAI, Anthropic, Ollama (local)
- Streaming output (--stream)
- Sessions with persistent history (--session / -s)
- System prompt support (--system)
- JSON export of responses (--json)
- Reads from STDIN if no -q provided and stdin is piped
"""

import argparse
import json
import pathlib
import sys
import time
from typing import Dict, List, Optional

if __package__ in {None, ""}:
    sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))

from core.io_utils import read_stdin_if_piped
from core.messages import build_messages
from core.providers import PROVIDER_DEFAULTS, PROVIDERS
from core.sessions import append_message, load_session, save_session

Messages = List[Dict[str, str]]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aibot", description="A tiny AI CLI you can grow.")
    parser.add_argument("-q", "--query", help="Your question/prompt. If omitted, reads from STDIN when piped.")
    parser.add_argument("-s", "--session", default=None, help="Session name to persist conversation (e.g., 'devops').")
    parser.add_argument("-p", "--provider", choices=sorted(PROVIDERS.keys()), default="openai", help="Which backend to use.")
    parser.add_argument("-m", "--model", default=None, help="Model name (defaults depend on provider).")
    parser.add_argument("--system", default=None, help="System prompt to set behavior.")
    parser.add_argument("--stream", action="store_true", help="Stream tokens as they arrive.")
    parser.add_argument("--json", action="store_true", help="Print raw JSON envelope of the final assistant message.")
    parser.add_argument("--show", action="store_true", help="Show last conversation turns of the session and exit.")
    parser.add_argument("--limit", type=int, default=6, help="When --show, how many recent messages to display.")
    return parser


def resolve_user_query(args: argparse.Namespace) -> Optional[str]:
    return args.query or read_stdin_if_piped()


def show_session_history(session: str, limit: int) -> int:
    history = load_session(session)
    if not history:
        print("(empty session)")
        return 0
    for message in history[-limit:]:
        print(f"[{message['role']}] {message['content']}\n")
    return 0


def determine_model(provider: str, explicit: Optional[str]) -> str:
    if explicit:
        return explicit
    try:
        return PROVIDER_DEFAULTS[provider]
    except KeyError as exc:
        raise ValueError(f"Unknown provider '{provider}'.") from exc


def invoke_provider(provider: str, messages: Messages, model: str, stream: bool) -> str:
    try:
        handler = PROVIDERS[provider]
    except KeyError as exc:
        raise ValueError(f"Unsupported provider '{provider}'.") from exc
    return handler(messages, model, stream)


def persist_session(session: Optional[str], history: Messages, user_query: str, answer: str) -> None:
    if not session:
        return
    if not history or history[-1].get("role") != "user" or history[-1].get("content") != user_query:
        append_message(history, "user", user_query)
    append_message(history, "assistant", answer)
    save_session(session, history)


def emit_output(answer: str, args: argparse.Namespace, provider: str, model: str, messages: Messages) -> None:
    if args.json:
        envelope = {
            "provider": provider,
            "model": model,
            "session": args.session,
            "timestamp": int(time.time()),
            "messages": messages,
            "answer": answer,
        }
        print(json.dumps(envelope, ensure_ascii=False, indent=2))
    elif not args.stream:
        print(answer)


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.show:
        if not args.session:
            print("--show requires --session", file=sys.stderr)
            return 1
        return show_session_history(args.session, args.limit)

    user_query = resolve_user_query(args)
    if not user_query:
        parser.print_help()
        return 1

    history: Messages = load_session(args.session) if args.session else []
    model = determine_model(args.provider, args.model)
    messages = build_messages(args.system, history, user_query)

    try:
        answer = invoke_provider(args.provider, messages, model, args.stream)
    except Exception as exc:
        print(f"[aibot error] {exc}", file=sys.stderr)
        return 2

    persist_session(args.session, history, user_query, answer)
    emit_output(answer, args, args.provider, model, messages)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
