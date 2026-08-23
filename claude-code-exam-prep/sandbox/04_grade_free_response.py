"""Sandbox 4 -- LLM-as-judge, with a validated schema.

Multiple choice is easy to grade and easy to game. This grades a FREE-TEXT
answer against the bank's reference explanation, which is where the exam's
harder domains actually live.

The interesting mechanic is structured outputs: client.messages.parse() with a
Pydantic model constrains the response and hands back a validated object, so
there is no brittle JSON-scraping step between the model and your code.

    pip install anthropic pydantic
    python sandbox/04_grade_free_response.py perm-001
"""

from __future__ import annotations

import pathlib
import sys

import anthropic
from pydantic import BaseModel, Field

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from quiz import store  # noqa: E402

MODEL = "claude-opus-5"


class Grade(BaseModel):
    """The shape the grader must return."""

    score: int = Field(description="0-5, where 5 fully matches the reference answer")
    correct: bool = Field(description="True if the answer would earn credit on an exam")
    missing: list[str] = Field(description="Key points the answer left out")
    wrong: list[str] = Field(description="Statements in the answer that are incorrect")
    feedback: str = Field(description="Two sentences of coaching, addressed to the learner")


RUBRIC = """You are grading a free-response answer for the Claude Certified
Developer exam. Grade only against the reference material given -- do not add
requirements from your own knowledge, and do not penalise an answer for being
brief if it contains the load-bearing facts. Be strict about factual errors and
lenient about phrasing."""


def main(question_id: str) -> int:
    questions = {q.id: q for q in store.load_questions()}
    question = questions.get(question_id)
    if question is None:
        print(f"unknown question id {question_id!r}", file=sys.stderr)
        print(f"try one of: {', '.join(sorted(questions)[:8])} ...")
        return 1

    print(f"\n{question.question}\n")
    print("Answer in your own words. Blank line to finish.\n")
    lines: list[str] = []
    while True:
        try:
            line = input("> ")
        except EOFError:
            break
        if not line.strip():
            break
        lines.append(line)

    answer = "\n".join(lines).strip()
    if not answer:
        print("nothing to grade")
        return 0

    reference = "\n".join(
        [question.explanation]
        + [f"Correct option: {question.choices[i]}" for i in question.answer]
    )

    client = anthropic.Anthropic()
    response = client.messages.parse(
        model=MODEL,
        max_tokens=16000,
        system=RUBRIC,
        output_config={"effort": "medium"},
        messages=[{
            "role": "user",
            "content": (
                f"QUESTION\n{question.question}\n\n"
                f"REFERENCE ANSWER\n{reference}\n\n"
                f"LEARNER'S ANSWER\n{answer}"
            ),
        }],
        output_format=Grade,
    )

    grade = response.parsed_output
    print(f"\n{'PASS' if grade.correct else 'NOT YET'}  --  {grade.score}/5")
    if grade.missing:
        print("\nmissed:")
        for point in grade.missing:
            print(f"  - {point}")
    if grade.wrong:
        print("\nincorrect:")
        for point in grade.wrong:
            print(f"  - {point}")
    print(f"\n{grade.feedback}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "perm-001"))
