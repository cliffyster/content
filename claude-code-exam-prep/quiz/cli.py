"""Command line interface for the drill engine.

    python -m quiz drill --domain hooks
    python -m quiz exam --count 53 --minutes 120
    python -m quiz stats
"""

from __future__ import annotations

import argparse
import datetime as _dt
import random
import sys
import textwrap
import time
from typing import Sequence

from . import scheduler, store
from .models import Card, Question

LETTERS = "abcdefghijklmnopqrstuvwxyz"
WRAP = textwrap.TextWrapper(width=88, subsequent_indent="   ")

# The real exam is 53 items in 120 minutes; mirror it by default so practice
# runs feel like the thing you are practising for.
EXAM_ITEMS = 53
EXAM_MINUTES = 120
PASS_PERCENT = 72.0  # 720 on the exam's scaled 100-1000 range


# --------------------------------------------------------------------------- ui


def _rule(char: str = "-") -> str:
    return char * 72


def _render(question: Question, number: int, total: int) -> str:
    lines = [
        "",
        _rule("="),
        f"[{number}/{total}]  {question.domain}",
        _rule("="),
        "",
        WRAP.fill(question.question),
        "",
    ]
    for i, choice in enumerate(question.choices):
        lines.append(WRAP.fill(f"{LETTERS[i]}) {choice}"))
    if question.is_multi:
        lines.append("")
        lines.append(f"(select {len(question.answer)} -- e.g. 'ac')")
    return "\n".join(lines)


def _parse_selection(raw: str, num_choices: int) -> list[int] | None:
    """Turn 'a c' or 'ac' or '1,3' into zero-based indices, or None if unparseable."""
    picks: set[int] = set()
    for token in raw.replace(",", " ").replace(".", " ").split() or [raw]:
        for char in token.strip():
            if char in LETTERS:
                index = LETTERS.index(char)
            elif char.isdigit():
                index = int(char) - 1
            else:
                return None
            if not 0 <= index < num_choices:
                return None
            picks.add(index)
    return sorted(picks) or None


def _ask(question: Question, number: int, total: int) -> tuple[list[int] | None, float]:
    """Prompt until a valid selection arrives. Returns (selection, seconds)."""
    print(_render(question, number, total))
    started = time.monotonic()
    while True:
        try:
            raw = input("\nyour answer ('s' skip, 'q' quit) > ").strip().lower()
        except EOFError:
            return None, time.monotonic() - started
        if raw in {"q", "quit"}:
            raise KeyboardInterrupt
        if raw in {"s", "skip", ""}:
            return None, time.monotonic() - started
        selection = _parse_selection(raw, len(question.choices))
        if selection is not None:
            return selection, time.monotonic() - started
        print("  ! didn't understand that -- use letters like 'a' or 'ac'")


def _feedback(question: Question, selection: list[int] | None, correct: bool) -> None:
    if selection is None:
        verdict = "SKIPPED"
    else:
        verdict = "CORRECT" if correct else "WRONG"
    expected = ", ".join(LETTERS[i] for i in question.answer)
    print(f"\n  {verdict}   answer: {expected}")
    print(WRAP.fill(f"   {question.explanation}"))
    if question.source:
        print(f"   source: {question.source}")


# ---------------------------------------------------------------------- selection


def due_questions(
    questions: Sequence[Question],
    cards: dict[str, Card],
    today: _dt.date,
    *,
    include_all: bool = False,
) -> list[Question]:
    """Questions to review now: unseen first, then most overdue."""
    if include_all:
        selected = list(questions)
    else:
        selected = [q for q in questions if store.card_for(cards, q).is_due(today)]

    def sort_key(q: Question) -> tuple[int, str]:
        card = cards[q.id]
        # Unseen cards lead; after that, oldest due date first.
        return (1 if card.times_seen else 0, card.due or "")

    return sorted(selected, key=sort_key)


# ----------------------------------------------------------------------- commands


def cmd_drill(args: argparse.Namespace) -> int:
    questions = store.load_questions()
    cards = store.load_cards()
    today = _dt.date.today()

    if args.domain:
        questions = [q for q in questions if q.domain == args.domain]
        if not questions:
            print(f"no questions in domain {args.domain!r}", file=sys.stderr)
            print(f"known domains: {', '.join(store.domains(store.load_questions()))}")
            return 1

    queue = due_questions(questions, cards, today, include_all=args.all)
    if not queue:
        print("Nothing due today. Use --all to drill the whole bank anyway.")
        return 0
    queue = queue[: args.limit]

    correct_count = 0
    answered = 0
    try:
        for i, question in enumerate(queue, start=1):
            selection, elapsed = _ask(question, i, len(queue))
            correct = selection is not None and question.is_correct(selection)
            _feedback(question, selection, correct)
            if selection is None:
                continue
            answered += 1
            correct_count += correct
            scheduler.review(cards[question.id], scheduler.grade(correct, elapsed), today)
    except KeyboardInterrupt:
        print("\n\nstopping early -- progress saved")
    finally:
        store.save_cards(cards)

    if answered:
        print(f"\n{_rule()}\n{correct_count}/{answered} correct "
              f"({100 * correct_count / answered:.0f}%)")
    return 0


def cmd_exam(args: argparse.Namespace) -> int:
    """A timed mock: fixed item count, a clock, and a pass/fail verdict."""
    questions = store.load_questions()
    if len(questions) < args.count:
        print(f"note: bank has {len(questions)} questions, running all of them")
    rng = random.Random(args.seed)
    paper = rng.sample(questions, min(args.count, len(questions)))

    deadline = time.monotonic() + args.minutes * 60
    print(f"\nMock exam: {len(paper)} items, {args.minutes} minutes. "
          f"Pass mark {PASS_PERCENT:.0f}%.\n")

    correct_count = 0
    answered = 0
    try:
        for i, question in enumerate(paper, start=1):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                print("\n*** time is up ***")
                break
            print(f"\n(time left: {int(remaining // 60)}m {int(remaining % 60)}s)")
            selection, _ = _ask(question, i, len(paper))
            if selection is None:
                continue
            answered += 1
            correct_count += question.is_correct(selection)
    except KeyboardInterrupt:
        print("\n\nexam ended early")

    # Unanswered items score zero, exactly as they would on the real exam.
    percent = 100 * correct_count / len(paper) if paper else 0.0
    verdict = "PASS" if percent >= PASS_PERCENT else "FAIL"
    print(f"\n{_rule('=')}")
    print(f"{verdict}  --  {correct_count}/{len(paper)} correct ({percent:.0f}%), "
          f"{answered} attempted")
    print(_rule("="))
    if args.review and correct_count < len(paper):
        print("\nRun `python -m quiz drill --all` to work through the bank with "
              "explanations.")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    questions = store.load_questions()
    cards = store.load_cards()
    today = _dt.date.today()

    by_domain: dict[str, list[Question]] = {}
    for question in questions:
        by_domain.setdefault(question.domain, []).append(question)

    print(f"\n{'domain':<28} {'seen':>6} {'acc':>6} {'due':>6} {'total':>6}")
    print(_rule())
    total_seen = total_correct = 0
    for domain in sorted(by_domain):
        items = by_domain[domain]
        seen = [cards[q.id] for q in items if q.id in cards and cards[q.id].times_seen]
        due = sum(1 for q in items if store.card_for(cards, q).is_due(today))
        attempts = sum(c.times_seen for c in seen)
        hits = sum(c.times_correct for c in seen)
        total_seen += attempts
        total_correct += hits
        accuracy = f"{100 * hits / attempts:.0f}%" if attempts else "-"
        print(f"{domain:<28} {len(seen):>6} {accuracy:>6} {due:>6} {len(items):>6}")
    print(_rule())
    overall = f"{100 * total_correct / total_seen:.0f}%" if total_seen else "-"
    print(f"{'overall':<28} {'':>6} {overall:>6} {'':>6} {len(questions):>6}")
    print(f"\nprogress file: {store.progress_path()}")
    return 0


def cmd_reset(args: argparse.Namespace) -> int:
    path = store.progress_path()
    if not path.exists():
        print("no progress to reset")
        return 0
    if not args.yes:
        confirm = input(f"delete {path}? [y/N] ").strip().lower()
        if confirm != "y":
            print("kept")
            return 0
    path.unlink()
    print(f"deleted {path}")
    return 0


def cmd_domains(args: argparse.Namespace) -> int:
    questions = store.load_questions()
    counts: dict[str, int] = {}
    for question in questions:
        counts[question.domain] = counts.get(question.domain, 0) + 1
    for domain in sorted(counts):
        print(f"{counts[domain]:>4}  {domain}")
    print(f"{len(questions):>4}  TOTAL")
    return 0


# --------------------------------------------------------------------------- main


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="quiz",
        description="Spaced-repetition drills for the Claude Certified Developer exam.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    drill = sub.add_parser("drill", help="review the questions that are due")
    drill.add_argument("--domain", help="restrict to one domain (see `domains`)")
    drill.add_argument("--limit", type=int, default=20, help="max items (default 20)")
    drill.add_argument("--all", action="store_true",
                       help="ignore the schedule and drill everything")
    drill.set_defaults(func=cmd_drill)

    exam = sub.add_parser("exam", help="timed mock exam")
    exam.add_argument("--count", type=int, default=EXAM_ITEMS)
    exam.add_argument("--minutes", type=int, default=EXAM_MINUTES)
    exam.add_argument("--seed", type=int, default=None, help="reproducible paper")
    exam.add_argument("--no-review", dest="review", action="store_false", default=True)
    exam.set_defaults(func=cmd_exam)

    stats = sub.add_parser("stats", help="accuracy and due counts by domain")
    stats.set_defaults(func=cmd_stats)

    domains = sub.add_parser("domains", help="list domains and question counts")
    domains.set_defaults(func=cmd_domains)

    reset = sub.add_parser("reset", help="delete saved progress")
    reset.add_argument("--yes", action="store_true")
    reset.set_defaults(func=cmd_reset)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except ValueError as exc:          # malformed bank file
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
