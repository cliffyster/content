"""Core data types for the drill engine."""

from __future__ import annotations

import dataclasses
import datetime as _dt
from typing import Any


ISO_DAY = "%Y-%m-%d"


@dataclasses.dataclass(frozen=True)
class Question:
    """One exam-style item loaded from a bank file."""

    id: str
    domain: str
    question: str
    choices: list[str]
    answer: list[int]
    explanation: str
    source: str = ""
    difficulty: int = 2

    @property
    def is_multi(self) -> bool:
        return len(self.answer) > 1

    def is_correct(self, selected: list[int]) -> bool:
        return sorted(selected) == sorted(self.answer)

    @classmethod
    def from_dict(cls, raw: dict[str, Any], *, origin: str) -> "Question":
        missing = {"id", "domain", "question", "choices", "answer", "explanation"} - raw.keys()
        if missing:
            raise ValueError(f"{origin}: question missing keys {sorted(missing)}")

        choices = list(raw["choices"])
        answer = sorted(int(i) for i in raw["answer"])
        if not answer:
            raise ValueError(f"{origin}: question {raw['id']!r} has no answer")
        for index in answer:
            if not 0 <= index < len(choices):
                raise ValueError(
                    f"{origin}: question {raw['id']!r} answer index {index} "
                    f"out of range for {len(choices)} choices"
                )

        return cls(
            id=str(raw["id"]),
            domain=str(raw["domain"]),
            question=str(raw["question"]),
            choices=choices,
            answer=answer,
            explanation=str(raw["explanation"]),
            source=str(raw.get("source", "")),
            difficulty=int(raw.get("difficulty", 2)),
        )


@dataclasses.dataclass
class Card:
    """Spaced-repetition state for a single question."""

    question_id: str
    repetitions: int = 0
    interval_days: int = 0
    ease: float = 2.5
    due: str = ""          # ISO date; empty means "never seen, due now"
    last_seen: str = ""
    times_seen: int = 0
    times_correct: int = 0

    @property
    def accuracy(self) -> float:
        return self.times_correct / self.times_seen if self.times_seen else 0.0

    def is_due(self, today: _dt.date) -> bool:
        if not self.due:
            return True
        return _dt.datetime.strptime(self.due, ISO_DAY).date() <= today

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Card":
        fields = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in raw.items() if k in fields})
