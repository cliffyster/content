"""A stdio MCP server over the exam question bank.

    pip install "mcp[cli]"
    claude mcp add --transport stdio bank -- python3 /abs/path/bank_server.py
"""

from __future__ import annotations

import pathlib
import sys

from mcp.server.fastmcp import FastMCP

# The server runs from wherever Claude Code launches it, so resolve the repo
# relative to this file rather than the working directory.
REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from quiz import store  # noqa: E402

mcp = FastMCP("bank")


@mcp.tool()
def list_domains() -> dict[str, int]:
    """List every exam domain in the question bank with its question count.

    Call this first to find out what domains exist before searching one.
    """
    counts: dict[str, int] = {}
    for question in store.load_questions():
        counts[question.domain] = counts.get(question.domain, 0) + 1
    return counts


@mcp.tool()
def get_question(question_id: str) -> dict:
    """Fetch one question by its id, with the correct answer and explanation.

    Args:
        question_id: An id such as "perm-001" or "hook-004".
    """
    for question in store.load_questions():
        if question.id == question_id:
            return {
                "id": question.id,
                "domain": question.domain,
                "question": question.question,
                "choices": question.choices,
                "correct": [question.choices[i] for i in question.answer],
                "explanation": question.explanation,
                "source": question.source,
            }
    raise ValueError(f"no question with id {question_id!r}")


@mcp.tool()
def search_bank(text: str, limit: int = 5) -> list[dict]:
    """Find questions whose text or explanation mentions a phrase.

    Args:
        text: Case-insensitive phrase, e.g. "prompt caching" or "exit code".
        limit: Maximum number of matches to return.
    """
    needle = text.lower()
    hits = [
        {"id": q.id, "domain": q.domain, "question": q.question}
        for q in store.load_questions()
        if needle in q.question.lower() or needle in q.explanation.lower()
    ]
    return hits[:limit]


if __name__ == "__main__":
    mcp.run()
