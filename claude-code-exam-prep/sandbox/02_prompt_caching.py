"""Sandbox 2 -- watch prompt caching hit, then watch it silently break.

Caching is a PREFIX match: any byte change anywhere in the cached prefix
invalidates everything after it. The render order is tools -> system ->
messages, so stable content goes first and volatile content goes last.

This script sends the same large system prompt three times:

    1. cold   -- writes the cache (cache_creation_input_tokens > 0)
    2. warm   -- reads it        (cache_read_input_tokens > 0)
    3. broken -- prepends a timestamp, so nothing is reused

Run it and compare the three usage lines. The third is what a stray
datetime.now() in a system prompt does to your bill.

    python sandbox/02_prompt_caching.py
"""

from __future__ import annotations

import datetime
import pathlib

import anthropic

MODEL = "claude-opus-5"
REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


def build_context() -> str:
    """Concatenate the study notes into a prompt big enough to be cacheable.

    The minimum cacheable prefix is around 1024 tokens -- shorter prefixes
    silently do not cache, which is the other common surprise.
    """
    notes = sorted((REPO_ROOT / "notes").glob("*.md"))
    if not notes:
        raise SystemExit("no notes found -- run this from a full checkout")
    return "\n\n".join(path.read_text(encoding="utf-8") for path in notes)


def ask(client: anthropic.Anthropic, system: str, question: str, label: str) -> None:
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
        output_config={"effort": "low"},
        messages=[{"role": "user", "content": question}],
    )
    usage = response.usage
    print(
        f"{label:<8} write={usage.cache_creation_input_tokens:>7} "
        f"read={usage.cache_read_input_tokens:>7} "
        f"uncached={usage.input_tokens:>6}"
    )


def main() -> int:
    client = anthropic.Anthropic()
    context = build_context()
    question = "In one sentence: what order are permission rules evaluated in?"

    print(f"context: ~{len(context) // 4} tokens (rough estimate)\n")
    print(f"{'run':<8} {'write':>13} {'read':>12} {'uncached':>15}")

    ask(client, context, question, "cold")
    ask(client, context, question, "warm")

    # The silent invalidator: a value that changes every call, at the FRONT of
    # the prefix. Everything after it is now a cache miss.
    stamped = f"Generated at {datetime.datetime.now().isoformat()}\n\n{context}"
    ask(client, stamped, question, "broken")

    print(
        "\nIf 'warm' shows read>0 and 'broken' shows read=0, you have just "
        "reproduced the single most common caching bug."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
