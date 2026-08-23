# Claude Code exam prep

A study project for the **Claude Certified Developer** exam, and a working
sandbox for the things it tests. The repo is deliberately self-referential: the
`.claude/` directory is a live example of every extensibility feature on the
syllabus, so studying hooks means reading a hook that is actually running.

```bash
git clone <this repo> && cd claude-code-exam-prep
python3 -m quiz domains        # what's in the bank
python3 -m quiz drill          # start drilling (no dependencies)
python3 -m unittest discover -s tests
```

The drill engine is **stdlib only**. Only the `sandbox/` scripts need
`pip install anthropic`.

## What's here

| | |
|---|---|
| [`notes/`](notes/) | Nine sourced study notes — CLI, permissions, skills, hooks, subagents, MCP, agents, API, cost/security |
| [`quiz/`](quiz/) | A spaced-repetition drill CLI (SM-2) over 68 questions, each with an explanation and a doc link |
| [`labs/`](labs/) | Five build-it-yourself exercises with solutions |
| [`.claude/`](.claude/) | A working config: 3 hooks, 2 skills, 1 subagent — read them as reference implementations |
| [`sandbox/`](sandbox/) | Runnable Anthropic SDK experiments: caching, tool runner, LLM-as-judge |

## The drill engine

```bash
python3 -m quiz drill                      # review what's due today
python3 -m quiz drill --domain hooks       # one domain
python3 -m quiz drill --all --limit 30     # ignore the schedule
python3 -m quiz exam                       # timed mock: 53 items, 120 minutes
python3 -m quiz exam --count 15 --minutes 20 --seed 7
python3 -m quiz stats                      # accuracy and due counts by domain
python3 -m quiz reset
```

Answer with letters — `a`, or `ac` for multi-select. Scheduling is SM-2:
questions you get right stretch out geometrically (1 day → 6 days → 6×ease…),
questions you miss collapse back to one day and lose ease. Grading is automatic
from correctness and speed, so there is no self-rating step to skip.

Progress is saved to `.quiz-progress.json` (gitignored). Override the location
with `QUIZ_PROGRESS_FILE`.

## The `.claude/` directory is study material

| File | Demonstrates |
|---|---|
| [`hooks/study-status.sh`](.claude/hooks/study-status.sh) | `SessionStart` hook that **injects context** via `additionalContext` |
| [`hooks/validate-bank.sh`](.claude/hooks/validate-bank.sh) | `PostToolUse` hook that **blocks with exit 2** when an edit breaks the bank |
| [`hooks/block-destructive.sh`](.claude/hooks/block-destructive.sh) | `PreToolUse` hook using a structured `permissionDecision` |
| [`skills/drill/SKILL.md`](.claude/skills/drill/SKILL.md) | `disable-model-invocation` + a scoped `allowed-tools` grant |
| [`skills/exam-coach/SKILL.md`](.claude/skills/exam-coach/SKILL.md) | A model-invocable skill with read-only tools |
| [`agents/question-writer.md`](.claude/agents/question-writer.md) | A subagent with a tool allowlist and a hard grounding rule |
| [`settings.json`](.claude/settings.json) | `allow` / `ask` / `deny` rules and all three hook registrations |

Each hook works. Try one:

```bash
CLAUDE_PROJECT_DIR=$PWD sh -c \
  'echo "{\"tool_input\":{\"command\":\"rm -rf build\"}}" | .claude/hooks/block-destructive.sh'
```

## The exam

The Claude Certification program (Practitioner, Architect, Developer) is
delivered through Pearson VUE. Reported format for the Developer exam: **53
items, 120 minutes, 8 domains, scaled 100–1000 with 720 to pass**, $99–$175 per
attempt, with registration through Anthropic's Partner Academy.

> ⚠️ **Verify this before you book.** `anthropic.com` was unreachable from the
> environment this repo was built in, so the logistics above come from
> secondary sources, not the official page. Treat them as approximate and
> confirm at [anthropic.com/certification](https://www.anthropic.com/certification)
> and [pearsonvue.com/anthropic](https://www.pearsonvue.com/us/en/anthropic.html).
> The *technical* content in `notes/` is sourced from the official docs and is
> linked line by line.

Reported content areas: Claude API mechanics, agents and workflows with the
Agent SDK, Claude Code, model selection and cost management, prompt and context
engineering, security, and tools and MCP servers. The notes and the question
bank are organised to match.

See [STUDY-PLAN.md](STUDY-PLAN.md) for a two-week schedule.

## Accuracy

Every question carries a `source` URL, and the test suite enforces it. The notes
were written against the official docs, but Claude Code ships continuously —
**where a note and the docs disagree, the docs are right.** If you find a stale
claim, fix the note *and* the question that teaches it, then run the tests.

## Adding questions

Append to a file in [`quiz/questions/`](quiz/questions/):

```json
{
  "id": "hook-013",
  "domain": "hooks",
  "difficulty": 2,
  "question": "...",
  "choices": ["...", "...", "...", "..."],
  "answer": [0],
  "explanation": "...",
  "source": "https://code.claude.com/docs/en/hooks"
}
```

`answer` holds 0-based indices; more than one makes it multi-select, and the
question text must then say how many to pick. Ids must be globally unique. The
`PostToolUse` hook validates the bank the moment you save, and
`python3 -m unittest discover -s tests` checks structure and sourcing.

Or delegate it: `@question-writer add five questions about MCP scopes`.

## License

MIT — see [LICENSE](LICENSE).
