"""Model provider adapters."""

from typing import Dict, List

from ..config import get_api_key
from ..io_utils import print_stream_chunk


Message = Dict[str, str]


def call_openai(messages: List[Message], model: str, stream: bool) -> str:
    """Call OpenAI chat completions using either the modern or legacy SDK."""
    api_key = get_api_key("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in environment or .env file.")

    try:
        from openai import OpenAI  # type: ignore[import-not-found]

        client = OpenAI(api_key=api_key)
        if stream:
            resp = client.chat.completions.create(model=model, messages=messages, stream=True)
            final_text = []
            for chunk in resp:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    print_stream_chunk(delta)
                    final_text.append(delta)
            print()
            return "".join(final_text)
        resp = client.chat.completions.create(model=model, messages=messages)
        return resp.choices[0].message.content or ""
    except ImportError:
        import openai  # type: ignore[import-not-found]

        openai.api_key = api_key
        if stream:
            completion = openai.ChatCompletion.create(model=model, messages=messages, stream=True)
            final_text = []
            for chunk in completion:
                delta = chunk["choices"][0]["delta"].get("content", "")
                if delta:
                    print_stream_chunk(delta)
                    final_text.append(delta)
            print()
            return "".join(final_text)
        completion = openai.ChatCompletion.create(model=model, messages=messages)
        return completion.choices[0].message["content"]


def call_anthropic(messages: List[Message], model: str, stream: bool) -> str:
    """Call Anthropic messages API."""
    api_key = get_api_key("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set in environment or .env file.")

    import anthropic  # type: ignore[import-not-found]

    client = anthropic.Client(api_key=api_key)

    sys_prompt = None
    conv: List[Message] = []
    for entry in messages:
        if entry["role"] == "system":
            sys_prompt = entry["content"]
        elif entry["role"] in ("user", "assistant"):
            conv.append({"role": entry["role"], "content": entry["content"]})

    if stream:
        final_text = []
        with client.messages.stream(model=model, system=sys_prompt, max_tokens=1024, messages=conv) as stream_resp:
            for event in stream_resp:
                if event.type == "content_block_delta":
                    delta = event.delta.get("text", "")
                    if delta:
                        print_stream_chunk(delta)
                        final_text.append(delta)
        print()
        return "".join(final_text)

    resp = client.messages.create(model=model, system=sys_prompt, max_tokens=1024, messages=conv)
    out = []
    for block in resp.content:
        if block.type == "text":
            out.append(block.text)
    return "".join(out)


def call_ollama(messages: List[Message], model: str, stream: bool) -> str:
    """Call a local Ollama HTTP endpoint."""
    import json

    import requests  # type: ignore[import-not-found]

    host = get_api_key("OLLAMA_HOST") or "http://localhost:11434"
    url = f"{host}/api/chat"
    payload = {"model": model, "messages": messages, "stream": stream}

    if stream:
        response = requests.post(url, json=payload, stream=True, timeout=600)
        response.raise_for_status()
        final_text = []
        for line in response.iter_lines():
            if not line:
                continue
            try:
                data = json.loads(line.decode("utf-8"))
            except Exception:
                continue
            delta = data.get("message", {}).get("content", "")
            if delta:
                print_stream_chunk(delta)
                final_text.append(delta)
        print()
        return "".join(final_text)

    response = requests.post(url, json=payload, timeout=600)
    response.raise_for_status()
    data = response.json()
    return data.get("message", {}).get("content", "")


PROVIDER_DEFAULTS = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-sonnet-latest",
    "ollama": "llama3",
}

PROVIDERS = {
    "openai": call_openai,
    "anthropic": call_anthropic,
    "ollama": call_ollama,
}
