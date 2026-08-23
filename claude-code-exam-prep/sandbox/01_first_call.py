"""Sandbox 1 -- the shape of a Messages API call.

Everything in the Claude API goes through POST /v1/messages. Tools, thinking,
caching and structured outputs are all features of this one endpoint, not
separate APIs. This script is the smallest complete call plus the two things
people most often get wrong: reading content blocks, and error handling.

    pip install anthropic
    python sandbox/01_first_call.py "why is my prompt cache missing?"
"""

from __future__ import annotations

import sys

import anthropic

MODEL = "claude-opus-5"


def main(question: str) -> int:
    client = anthropic.Anthropic()  # resolves ANTHROPIC_API_KEY or an `ant auth login` profile

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=16000,
            system="You are a concise tutor for the Claude Certified Developer exam.",
            # Adaptive thinking: Claude decides how much to think. On Opus 5 it is
            # on by default; the fixed `budget_tokens` knob is gone (400 if sent).
            thinking={"type": "adaptive", "display": "summarized"},
            # Effort lives inside output_config, not at the top level.
            output_config={"effort": "medium"},
            messages=[{"role": "user", "content": question}],
        )
    except anthropic.AuthenticationError:
        print("No valid credentials. Run `ant auth login` or export ANTHROPIC_API_KEY.")
        return 1
    except anthropic.RateLimitError as exc:
        retry_after = exc.response.headers.get("retry-after", "60")
        print(f"Rate limited; retry after {retry_after}s")
        return 1
    except anthropic.APIConnectionError:
        print("Network error reaching the API.")
        return 1

    # A refusal is a 200 with stop_reason "refusal" -- check before reading content.
    if response.stop_reason == "refusal":
        detail = response.stop_details
        print(f"Refused ({detail.category if detail else 'unknown'})")
        return 1

    # response.content is a LIST of blocks (thinking, text, tool_use, ...).
    # Reading response.content[0].text blindly is the classic first bug.
    for block in response.content:
        if block.type == "thinking" and block.thinking:
            print(f"--- thinking ---\n{block.thinking}\n")
        elif block.type == "text":
            print(block.text)

    usage = response.usage
    print(
        f"\n[in {usage.input_tokens} / out {usage.output_tokens} tokens, "
        f"stop_reason={response.stop_reason}]"
    )
    return 0


if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) or "Explain MCP transports in three sentences."
    raise SystemExit(main(prompt))
