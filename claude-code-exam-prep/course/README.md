# The course

A taught sequence: 24 lessons in 5 modules, from never having used Claude Code
to Claude Certified Developer exam depth. Published as an interactive artifact
with progress tracking and gated checks.

## Why this exists alongside `notes/`

They are different things and both are useful.

| | For |
|---|---|
| `course/` | **Learning it the first time.** Ordered, one idea per lesson, each building on the last. You cannot skip ahead. |
| `notes/` | **Looking something up.** Organised by topic, dense, assumes you already know the shape. |
| `quiz/` | **Retention.** Spaced repetition over 188 items, once you have learned the material. |

Learn from the course, drill with the quiz, look things up in the notes.

## Structure

| Module | Lessons | Covers |
|---|---|---|
| 01 How Claude Code works | 4 | the agent loop, context, permission prompts, CLAUDE.md |
| 02 Controlling what Claude can do | 5 | deny→ask→allow, Bash and file rule syntax, modes, settings precedence |
| 03 Extending Claude Code | 6 | choosing a mechanism, skills, hooks, hook-vs-rule precedence, subagents, MCP |
| 04 Running it without you | 3 | headless mode, why CI needs `--bare`, context at scale |
| 05 The API and the SDKs | 6 | Messages API, tool use, caching, the four agent approaches, SDK permissions, sandboxing |

Every lesson has an objective, taught prose, a worked example, a one-line
takeaway, and one to three checks that must be answered correctly before the
next lesson unlocks.

## Editing

Lesson content is authored in Python, not raw JSON, so the prose is readable
and diffable:

- `build_part1.py` — modules 1–2
- `build_part2.py` — module 3
- `build_part3.py` — modules 4–5

The page shell is `shell-head.html` (styles), `shell-body.html` (markup) and
`shell-script.html` (the course engine).

```bash
./assemble.sh              # regenerate course.json and course.html
node test-layout.mjs       # check every lesson at 320/390/430/1440px
```

## Layout rules that are easy to break

`test-layout.mjs` exists because both of these shipped once:

- **Use `minmax(0, 1fr)`, never a bare `1fr`,** for the content column. A bare
  `1fr` is `minmax(auto, 1fr)`, and that `auto` minimum will not shrink below
  the content's min-content width — so a single long inline `<code>` widens the
  whole page on a phone.
- **Never write a bare `code { white-space: normal }`.** It hits `<code>` inside
  `<pre>` and silently collapses every code block onto one line. Scope inline
  wrapping to `.teach p code` and friends, and restate `pre code { white-space: pre }`.

The published page also carries its own `<meta name="viewport">` plus a runtime
injection into `<head>`, because the artifact harness owns `<head>` and without
the meta iOS Safari lays out at 980px and scales down — which stops every
`max-width` media query from ever matching.

Then republish `course.html` as the artifact.

## Lesson schema

```python
{
 "id": "l7", "title": "File rules — the silent no-op",
 "objective": "One sentence: what the learner can do afterwards.",
 "teach": "<p>HTML. Use <b>, <code>, .tbl tables, p.callout, ol.steps.</p>",
 "example": {"label": "…", "lang": "json", "code": "…"},
 "takeaway": "One line they should remember a week later.",
 "checks": [{"q": "…", "choices": [...], "answer": [1], "why": "…"}],
}
```

`answer` is a list of 0-based indices; more than one makes it multi-select.
`why` should explain the distinction that makes the distractors wrong, not just
restate the right answer — that is where the teaching happens.
