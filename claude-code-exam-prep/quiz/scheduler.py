"""SM-2 spaced repetition.

The classic SuperMemo-2 algorithm, which is the smallest scheduler that still
behaves sensibly: items you keep getting right stretch out geometrically,
items you miss collapse back to a one-day interval.
"""

from __future__ import annotations

import datetime as _dt

from .models import ISO_DAY, Card

MIN_EASE = 1.3

# Response quality on SM-2's 0-5 scale, derived from the answer rather than
# asked of the user -- self-rating is the step people skip.
QUALITY_PERFECT = 5   # correct, answered quickly
QUALITY_CORRECT = 4   # correct
QUALITY_SLOW = 3      # correct, but took a long time
QUALITY_WRONG = 1     # incorrect

FAST_SECONDS = 15.0
SLOW_SECONDS = 60.0


def grade(correct: bool, elapsed_seconds: float) -> int:
    """Map an answer into an SM-2 quality score."""
    if not correct:
        return QUALITY_WRONG
    if elapsed_seconds <= FAST_SECONDS:
        return QUALITY_PERFECT
    if elapsed_seconds >= SLOW_SECONDS:
        return QUALITY_SLOW
    return QUALITY_CORRECT


def review(card: Card, quality: int, today: _dt.date | None = None) -> Card:
    """Apply one review to `card`, returning it with updated scheduling."""
    if not 0 <= quality <= 5:
        raise ValueError(f"quality must be 0-5, got {quality}")
    today = today or _dt.date.today()

    if quality < 3:
        # Lapse: relearn from scratch, but keep the ease penalty.
        card.repetitions = 0
        card.interval_days = 1
    else:
        if card.repetitions == 0:
            card.interval_days = 1
        elif card.repetitions == 1:
            card.interval_days = 6
        else:
            card.interval_days = max(1, round(card.interval_days * card.ease))
        card.repetitions += 1

    delta = 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
    card.ease = max(MIN_EASE, card.ease + delta)

    card.due = (today + _dt.timedelta(days=card.interval_days)).strftime(ISO_DAY)
    card.last_seen = today.strftime(ISO_DAY)
    card.times_seen += 1
    card.times_correct += 1 if quality >= 3 else 0
    return card
