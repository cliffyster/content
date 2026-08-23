# Two-week study plan

Assumes ~1 hour on weekdays and a longer session at the weekend. The pattern is
the same every day: **read one note, drill its domain, build something small.**
Reading without drilling feels productive and isn't.

## Week 1 — Claude Code

| Day | Read | Drill | Build |
|---|---|---|---|
| 1 | [01 CLI & config](notes/01-cli-and-config.md) | `--domain settings` | Write a `.claude/settings.json` for a real project of yours |
| 2 | [02 Permissions](notes/02-permissions.md) | `--domain permissions` | Write allow rules for your test suite; try to break them with a compound command |
| 3 | [03 Skills](notes/03-skills-and-commands.md) | `--domain skills` | [Lab 02](labs/lab-02-skill/) |
| 4 | [04 Hooks](notes/04-hooks.md) | `--domain hooks` | [Lab 01](labs/lab-01-hooks/) |
| 5 | [05 Subagents](notes/05-subagents.md) | `--domain subagents` | [Lab 03](labs/lab-03-subagent/) |
| 6 | [06 MCP](notes/06-mcp.md) | `--domain mcp` | [Lab 04](labs/lab-04-mcp-server/) |
| 7 | — | `python3 -m quiz drill` (whatever is due) | Review `stats`; re-read the note for your worst domain |

Day 2 is the heaviest. Permissions is the densest examinable area and the one
where intuition is most often wrong — budget extra time rather than rushing it.

## Week 2 — API, agents, and consolidation

| Day | Read | Drill | Build |
|---|---|---|---|
| 8 | [08 Claude API](notes/08-claude-api.md) | `--domain claude-api` | [`sandbox/01_first_call.py`](sandbox/01_first_call.py) |
| 9 | [09 Cost & context](notes/09-cost-context-security.md) | `--domain prompt-caching` | [`sandbox/02_prompt_caching.py`](sandbox/02_prompt_caching.py) — watch the cache break |
| 10 | [07 Agents & SDKs](notes/07-agents-and-sdks.md) | `--domain agent-sdk` | [Lab 05](labs/lab-05-agent-sdk/) |
| 11 | 09, security half | `--domain security` | Audit a repo you didn't write: what does its `.claude/` and `.mcp.json` grant? |
| 12 | — | `--domain models-and-cost` | [`sandbox/04_grade_free_response.py`](sandbox/04_grade_free_response.py) on three questions |
| 13 | — | **`python3 -m quiz exam`** — full 53/120 mock | Re-read notes for every domain you missed |
| 14 | — | `drill` on everything still due | Second mock with a different `--seed` |

## How to use the schedule

The spacing does the work. Drill **every day**, even a five-minute session —
`drill` with no arguments shows only what is actually due, so a maintenance day
is short by design. Skipping days and then cramming defeats the algorithm
entirely.

## Signals you're ready

- Two mock exams above 80% with different seeds.
- `stats` shows no domain below 75%.
- You can explain, without looking: why `Bash(ls *)` doesn't match `lsof`; why a
  hook's `"allow"` loses to a deny rule but exit 2 doesn't; why `.mcp.json`
  prompts interactively but not under `claude -p`; and the difference between
  the Tool Runner, the Claude Agent SDK, and Managed Agents.

If you can't do the last one out loud, you'll recognise the right answer on the
page and still lose the marks that need you to distinguish them.
