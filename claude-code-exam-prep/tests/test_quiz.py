"""Tests for the drill engine. Run with `python -m unittest discover tests`."""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from quiz import scheduler, store  # noqa: E402
from quiz.cli import _parse_selection, due_questions  # noqa: E402
from quiz.models import Card, Question  # noqa: E402


def make_question(**overrides) -> Question:
    base = {
        "id": "q1",
        "domain": "hooks",
        "question": "?",
        "choices": ["a", "b"],
        "answer": [0],
        "explanation": "because",
    }
    base.update(overrides)
    return Question.from_dict(base, origin="test")


class TestQuestion(unittest.TestCase):
    def test_rejects_missing_keys(self):
        with self.assertRaises(ValueError):
            Question.from_dict({"id": "x"}, origin="test")

    def test_rejects_out_of_range_answer(self):
        with self.assertRaisesRegex(ValueError, "out of range"):
            make_question(answer=[7])

    def test_rejects_empty_answer(self):
        with self.assertRaisesRegex(ValueError, "no answer"):
            make_question(answer=[])

    def test_multi_select_grading_ignores_order(self):
        question = make_question(choices=["a", "b", "c"], answer=[2, 0])
        self.assertTrue(question.is_multi)
        self.assertTrue(question.is_correct([0, 2]))
        self.assertTrue(question.is_correct([2, 0]))
        self.assertFalse(question.is_correct([0]))
        self.assertFalse(question.is_correct([0, 1, 2]))


class TestScheduler(unittest.TestCase):
    def setUp(self):
        self.today = dt.date(2026, 1, 1)

    def test_first_correct_review_schedules_one_day(self):
        card = scheduler.review(Card("q1"), scheduler.QUALITY_CORRECT, self.today)
        self.assertEqual(card.interval_days, 1)
        self.assertEqual(card.repetitions, 1)
        self.assertEqual(card.due, "2026-01-02")

    def test_second_correct_review_schedules_six_days(self):
        card = Card("q1")
        scheduler.review(card, scheduler.QUALITY_CORRECT, self.today)
        scheduler.review(card, scheduler.QUALITY_CORRECT, self.today)
        self.assertEqual(card.interval_days, 6)

    def test_intervals_grow_by_ease_after_the_second_review(self):
        card = Card("q1")
        for _ in range(3):
            scheduler.review(card, scheduler.QUALITY_PERFECT, self.today)
        self.assertGreater(card.interval_days, 6)

    def test_wrong_answer_resets_interval_and_lowers_ease(self):
        card = Card("q1")
        for _ in range(3):
            scheduler.review(card, scheduler.QUALITY_PERFECT, self.today)
        ease_before = card.ease
        scheduler.review(card, scheduler.QUALITY_WRONG, self.today)
        self.assertEqual(card.interval_days, 1)
        self.assertEqual(card.repetitions, 0)
        self.assertLess(card.ease, ease_before)

    def test_ease_never_falls_below_the_floor(self):
        card = Card("q1")
        for _ in range(50):
            scheduler.review(card, scheduler.QUALITY_WRONG, self.today)
        self.assertGreaterEqual(card.ease, scheduler.MIN_EASE)

    def test_accuracy_counts_only_passing_grades(self):
        card = Card("q1")
        scheduler.review(card, scheduler.QUALITY_PERFECT, self.today)
        scheduler.review(card, scheduler.QUALITY_WRONG, self.today)
        self.assertEqual(card.times_seen, 2)
        self.assertEqual(card.times_correct, 1)
        self.assertAlmostEqual(card.accuracy, 0.5)

    def test_grade_maps_speed_and_correctness(self):
        self.assertEqual(scheduler.grade(True, 2.0), scheduler.QUALITY_PERFECT)
        self.assertEqual(scheduler.grade(True, 30.0), scheduler.QUALITY_CORRECT)
        self.assertEqual(scheduler.grade(True, 90.0), scheduler.QUALITY_SLOW)
        self.assertEqual(scheduler.grade(False, 1.0), scheduler.QUALITY_WRONG)

    def test_rejects_out_of_range_quality(self):
        with self.assertRaises(ValueError):
            scheduler.review(Card("q1"), 9, self.today)


class TestDueSelection(unittest.TestCase):
    def test_unseen_cards_come_first(self):
        today = dt.date(2026, 1, 10)
        seen = make_question(id="seen")
        unseen = make_question(id="unseen")
        cards = {"seen": Card("seen", times_seen=3, due="2026-01-01")}

        order = due_questions([seen, unseen], cards, today)
        self.assertEqual([q.id for q in order], ["unseen", "seen"])

    def test_cards_not_yet_due_are_excluded_unless_all(self):
        today = dt.date(2026, 1, 10)
        question = make_question(id="future")
        cards = {"future": Card("future", times_seen=1, due="2026-02-01")}

        self.assertEqual(due_questions([question], cards, today), [])
        self.assertEqual(len(due_questions([question], cards, today, include_all=True)), 1)


class TestSelectionParsing(unittest.TestCase):
    def test_accepts_letters_digits_and_separators(self):
        self.assertEqual(_parse_selection("a", 4), [0])
        self.assertEqual(_parse_selection("ac", 4), [0, 2])
        self.assertEqual(_parse_selection("a c", 4), [0, 2])
        self.assertEqual(_parse_selection("1,3", 4), [0, 2])
        self.assertEqual(_parse_selection("ca", 4), [0, 2])

    def test_rejects_garbage_and_out_of_range(self):
        self.assertIsNone(_parse_selection("?", 4))
        self.assertIsNone(_parse_selection("z", 4))
        self.assertIsNone(_parse_selection("9", 4))


class TestStore(unittest.TestCase):
    def test_rejects_duplicate_ids_across_bank_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            bank = pathlib.Path(tmp)
            item = [{"id": "dup", "domain": "d", "question": "?",
                     "choices": ["a"], "answer": [0], "explanation": "e"}]
            (bank / "a.json").write_text(json.dumps(item))
            (bank / "b.json").write_text(json.dumps(item))
            with self.assertRaisesRegex(ValueError, "duplicate question id"):
                store.load_questions(bank)

    def test_round_trips_progress(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "progress.json"
            cards = {"q1": Card("q1", repetitions=2, interval_days=6, ease=2.6)}
            store.save_cards(cards, path)
            loaded = store.load_cards(path)
            self.assertEqual(loaded["q1"].interval_days, 6)
            self.assertAlmostEqual(loaded["q1"].ease, 2.6)

    def test_missing_progress_file_is_an_empty_dict(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(store.load_cards(pathlib.Path(tmp) / "nope.json"), {})


class TestShippedBank(unittest.TestCase):
    """The bank itself is content, so guard it like content."""

    def setUp(self):
        self.questions = store.load_questions()

    def test_bank_loads_and_is_not_trivially_small(self):
        self.assertGreaterEqual(len(self.questions), 150)

    def test_every_domain_has_enough_questions_to_drill(self):
        counts: dict[str, int] = {}
        for question in self.questions:
            counts[question.domain] = counts.get(question.domain, 0) + 1
        for domain, count in sorted(counts.items()):
            with self.subTest(domain):
                # A domain with one question can't produce a meaningful drill.
                self.assertGreaterEqual(count, 2)

    def test_difficulty_is_in_range(self):
        for question in self.questions:
            with self.subTest(question.id):
                self.assertIn(question.difficulty, (1, 2, 3))

    def test_ids_are_prefixed_consistently(self):
        for question in self.questions:
            with self.subTest(question.id):
                self.assertRegex(question.id, r"^[a-z]+-\d{3}$")

    def test_every_question_has_an_explanation_and_source(self):
        for question in self.questions:
            with self.subTest(question.id):
                self.assertGreater(len(question.explanation), 40)
                self.assertTrue(question.source.startswith("http"))

    def test_every_question_has_at_least_three_choices(self):
        for question in self.questions:
            with self.subTest(question.id):
                self.assertGreaterEqual(len(question.choices), 3)

    def test_multi_select_questions_say_how_many_to_pick(self):
        for question in self.questions:
            if question.is_multi:
                with self.subTest(question.id):
                    self.assertIn("select", question.question.lower())


if __name__ == "__main__":
    unittest.main()
