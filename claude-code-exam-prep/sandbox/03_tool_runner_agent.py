"""Sandbox 3 -- an agent over the question bank, using the SDK tool runner.

The tool runner (client.beta.messages.tool_runner) drives the
request -> execute -> feed-result-back loop for tools you define. You write the
tool functions; the SDK writes the loop. It is a helper on the regular Messages
API -- NOT the Claude Agent SDK, which is a separate package that ships the
whole Claude Code harness with built-in file and bash tools.

Ask it something like:

    python sandbox/03_tool_runner_agent.py "quiz me on the hooks I keep missing"

    pip install anthropic
"""

from __future__ import annotations

import json
import sys
import pathlib

import anthropic
from anthropic import beta_tool

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from quiz import store  # noqa: E402  (path shim above must run first)

MODEL = "claude-opus-5"


@beta_tool
def list_domains() -> str:
    """List every exam domain in the question bank, with how many items each has."""
    counts: dict[str, int] = {}
    for question in store.load_questions():
        counts[question.domain] = counts.get(question.domain, 0) + 1
    return json.dumps(counts)


@beta_tool
def get_questions(domain: str, limit: int = 3) -> str:
    """Fetch questions from one domain of the bank.

    Args:
        domain: Domain name, e.g. "hooks" or "permissions". Use list_domains first.
        limit: How many questions to return. Keep it small.
    """
    matches = [q for q in store.load_questions() if q.domain == domain][:limit]
    if not matches:
        return f"no questions in domain {domain!r}"
    return json.dumps([
        {
            "id": q.id,
            "question": q.question,
            "choices": q.choices,
            "answer": q.answer,
            "explanation": q.explanation,
        }
        for q in matches
    ])


@beta_tool
def weakest_domains(limit: int = 3) -> str:
    """Report the domains with the worst accuracy in the learner's saved progress.

    Args:
        limit: How many domains to return, worst first.
    """
    cards = store.load_cards()
    if not cards:
        return "no progress recorded yet -- run `python -m quiz drill` first"

    by_domain: dict[str, list[int]] = {}
    for question in store.load_questions():
        card = cards.get(question.id)
        if card and card.times_seen:
            seen, hit = by_domain.setdefault(question.domain, [0, 0])
            by_domain[question.domain] = [seen + card.times_seen, hit + card.times_correct]

    ranked = sorted(by_domain.items(), key=lambda kv: kv[1][1] / kv[1][0])
    return json.dumps([
        {"domain": d, "accuracy": round(hit / seen, 2), "attempts": seen}
        for d, (seen, hit) in ranked[:limit]
    ])


SYSTEM = """You are a study coach for the Claude Certified Developer exam.

Use the tools to ground everything you say in the learner's actual question bank
and their actual progress -- never invent exam content. When they ask to be
quizzed, ask one question at a time and wait for an answer before revealing it.
Keep explanations short and mechanical: what the rule is, and the case where
getting it wrong bites."""


def main(prompt: str) -> int:
    client = anthropic.Anthropic()

    runner = client.beta.messages.tool_runner(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM,
        output_config={"effort": "medium"},
        tools=[list_domains, get_questions, weakest_domains],
        messages=[{"role": "user", "content": prompt}],
    )

    # Each iteration is one assistant turn; the runner executes any tool calls
    # and loops until Claude stops asking for tools.
    for message in runner:
        for block in message.content:
            if block.type == "text" and block.text.strip():
                print(block.text)
            elif block.type == "tool_use":
                print(f"  [calling {block.name}({json.dumps(block.input)})]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(" ".join(sys.argv[1:]) or "What should I study first?"))
