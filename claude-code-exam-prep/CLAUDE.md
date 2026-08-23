# claude-code-exam-prep

Study project for the Claude Certified Developer exam. Stdlib-only drill
engine, sourced notes, hands-on labs, and a working `.claude/` config that
doubles as reference material.

## Commands

```bash
python3 -m quiz drill --domain hooks     # drill one domain
python3 -m quiz stats                    # progress by domain
python3 -m unittest discover -s tests    # the full suite (fast, no deps)
```

## Layout

- `quiz/` — drill engine. `models.py` (Question/Card), `scheduler.py` (SM-2),
  `store.py` (bank loading + progress persistence), `cli.py` (subcommands).
- `quiz/questions/*.json` — the question bank. Ids must be globally unique
  across all files; `answer` is a list of 0-based choice indices.
- `notes/` — study notes, one per domain.
- `labs/` — exercises, each with a `solution/`.
- `sandbox/` — Anthropic SDK scripts. The only code here that needs
  `pip install anthropic`.
- `.claude/` — hooks, skills and a subagent. These are **content**, not just
  config: they are cited in the README as worked examples.

## Rules for changing this repo

**Everything factual must be sourced.** Every question carries a `source` URL
and the test suite enforces it. Do not add a question, or a claim in a note,
from memory — fetch the doc page first. A wrong item in a spaced-repetition
system teaches the error on a schedule, which is worse than omitting it.

**Where the notes and the official docs disagree, the docs are right.** Claude
Code ships continuously. Fix the note *and* the question that teaches it.

**Keep `quiz/` dependency-free.** The drill engine must run on a clean Python
3.11+ with no `pip install`. New dependencies belong in `sandbox/` only.

**Don't edit `.quiz-progress.json`** — it is the learner's data, and a deny rule
in `.claude/settings.json` blocks it.

## Style

Match what's there: `from __future__ import annotations`, type hints on public
functions, docstrings that say *why* rather than restating the signature.
Comments are for non-obvious decisions only — the write-then-rename in
`store.save_cards`, not the `for` loop above it.
