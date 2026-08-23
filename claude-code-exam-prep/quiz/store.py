"""Loading question banks and persisting review progress."""

from __future__ import annotations

import json
import os
import pathlib
from typing import Iterable

from .models import Card, Question

PACKAGE_DIR = pathlib.Path(__file__).resolve().parent
BANK_DIR = PACKAGE_DIR / "questions"

# Progress is per-user state, not repo content, so it stays out of git.
DEFAULT_PROGRESS_PATH = PACKAGE_DIR.parent / ".quiz-progress.json"


def progress_path() -> pathlib.Path:
    """Where review state lives. Override with QUIZ_PROGRESS_FILE for tests."""
    override = os.environ.get("QUIZ_PROGRESS_FILE")
    return pathlib.Path(override) if override else DEFAULT_PROGRESS_PATH


def load_questions(bank_dir: pathlib.Path | None = None) -> list[Question]:
    """Load every *.json bank, failing loudly on a malformed or duplicated item."""
    bank_dir = bank_dir or BANK_DIR
    questions: list[Question] = []
    seen: dict[str, str] = {}

    for path in sorted(bank_dir.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        for item in raw:
            question = Question.from_dict(item, origin=path.name)
            if question.id in seen:
                raise ValueError(
                    f"duplicate question id {question.id!r} in {path.name} "
                    f"(first seen in {seen[question.id]})"
                )
            seen[question.id] = path.name
            questions.append(question)

    if not questions:
        raise ValueError(f"no questions found in {bank_dir}")
    return questions


def load_cards(path: pathlib.Path | None = None) -> dict[str, Card]:
    path = path or progress_path()
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {qid: Card.from_dict(card) for qid, card in raw.get("cards", {}).items()}


def save_cards(cards: dict[str, Card], path: pathlib.Path | None = None) -> None:
    path = path or progress_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"version": 1, "cards": {qid: c.to_dict() for qid, c in cards.items()}}
    # Write-then-rename so an interrupted run can't truncate existing progress.
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def card_for(cards: dict[str, Card], question: Question) -> Card:
    """Get the card for a question, creating a fresh one on first sight."""
    return cards.setdefault(question.id, Card(question_id=question.id))


def domains(questions: Iterable[Question]) -> list[str]:
    return sorted({q.domain for q in questions})
