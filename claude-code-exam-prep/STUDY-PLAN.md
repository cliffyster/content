# Three-week study plan

Assumes ~1 hour on weekdays and a longer session at the weekend. The pattern is
the same every day: **read one note, drill its domain, build something small.**
Reading without drilling feels productive and isn't.

If you only have two weeks, drop days 15–18 and fold their drills into the
consolidation days — but don't drop day 13 (security) or day 20 (the first
mock).

## Week 1 — Claude Code, the examinable core

| Day | Read | Drill | Build |
|---|---|---|---|
| 1 | [01 CLI & config](notes/01-cli-and-config.md) | `--domain settings` | Write a `.claude/settings.json` for a real project of yours |
| 2 | [02 Permissions](notes/02-permissions.md) | `--domain permissions` | Write allow rules for your test suite; try to break them with a compound command |
| 3 | [03 Skills](notes/03-skills-and-commands.md) | `--domain skills` | [Lab 02](labs/lab-02-skill/) |
| 4 | [04 Hooks](notes/04-hooks.md) | `--domain hooks` | [Lab 01](labs/lab-01-hooks/) |
| 5 | [05 Subagents](notes/05-subagents.md) | `--domain subagents` | [Lab 03](labs/lab-03-subagent/) |
| 6 | [06 MCP](notes/06-mcp.md) | `--domain mcp` | [Lab 04](labs/lab-04-mcp-server/) |
| 7 | — | `drill` (whatever is due) | Review `stats`; re-read the note for your worst domain |

Day 2 is the heaviest. Permissions is the densest examinable area and the one
where intuition is most often wrong — budget extra time rather than rushing it.

## Week 2 — The rest of the Claude Code surface

| Day | Read | Drill | Build |
|---|---|---|---|
| 8 | [10 CLI & commands](notes/10-cli-and-commands.md) | `--domain cli` | Run `claude -p` three ways: text, `json`, and `--json-schema` |
| 9 | [11 Memory](notes/11-memory-and-instructions.md) | `--domain memory` | Add a path-scoped rule to a project; confirm with `/context` that it loads only when expected |
| 10 | [16 Context window](notes/16-context-window.md) | `--domain context` | Run `/context` mid-task; force a `/compact` and see what survives |
| 11 | [12 Tools](notes/12-tools-reference.md) + [13 Plugins](notes/13-plugins.md) | `--domain tools`, `--domain plugins` | `claude plugin details` on something installed — look at its token cost |
| 12 | [14 Headless & CI](notes/14-headless-and-ci.md) | `--domain cli` | [Lab 07](labs/lab-07-ci-hardening/) |
| 13 | [17 Sandboxing](notes/17-sandboxing.md) + [18 Security](notes/18-security-model.md) | `--domain sandboxing`, `--domain security` | [Lab 06](labs/lab-06-sandbox-policy/) |
| 14 | — | `drill` | Audit a repo you didn't write: what do its `.claude/` and `.mcp.json` grant? |

Day 13 is the other heavy one. Sandboxing and the security model together are a
large share of the security domain, and the answers are counter-intuitive in
both directions — a deny holds inside a wider allow, but auto-allow runs
file-modifying commands without a prompt even in Manual mode.

## Week 3 — API, agents, consolidation

| Day | Read | Drill | Build |
|---|---|---|---|
| 15 | [08 Claude API](notes/08-claude-api.md) | `--domain claude-api` | [`sandbox/01_first_call.py`](sandbox/01_first_call.py) |
| 16 | [09 Cost & context](notes/09-cost-context-security.md) | `--domain prompt-caching` | [`sandbox/02_prompt_caching.py`](sandbox/02_prompt_caching.py) — watch the cache break |
| 17 | [19 Prompt engineering](notes/19-prompt-engineering.md) | `--domain prompt-engineering` | Rewrite one of your own prompts: long data at the top, XML tags, 3–5 examples |
| 18 | [20 Tool design](notes/20-tools-and-server-tools.md) | `--domain tool-design` | Take one bash-shaped action in your own agent and promote it to a dedicated tool |
| 19 | [07](notes/07-agents-and-sdks.md) + [15 Agent SDK](notes/15-agent-sdk-deep.md) | `--domain agent-sdk` | [Lab 05](labs/lab-05-agent-sdk/) |
| 20 | [21 Models & platforms](notes/21-models-and-platforms.md) | `--domain models-and-cost` | **`python3 -m quiz exam`** — full 53/120 mock |
| 21 | — | `drill` on everything still due | Second mock with a different `--seed`; `sandbox/04_grade_free_response.py` on your three weakest questions |

## How to use the schedule

The spacing does the work. Drill **every day**, even a five-minute session —
`drill` with no arguments shows only what is actually due, so a maintenance day
is short by design. Skipping days and then cramming defeats the algorithm
entirely.

With 188 questions across 19 domains, a single pass takes about three sittings.
The point of the schedule is the *second* and *third* exposure, which is where
retention actually happens.

## Signals you're ready

- Two mock exams above 80% with different seeds.
- `stats` shows no domain below 75%.
- You can produce the twenty rules at the bottom of the
  [notes index](notes/README.md) cold, out loud, without looking.

That last one is the real test. You will recognise the right answer on the page
long before you can generate it — and the exam has questions that need you to
distinguish between two things you only half-remember.
