# 14 — Headless mode and CI

> Source: [Run Claude Code programmatically](https://code.claude.com/docs/en/headless) ·
> [GitHub Actions](https://code.claude.com/docs/en/github-actions)

## The basic form

```bash
claude -p "Find and fix the bug in auth.py" --allowedTools "Read,Edit,Bash"
```

Exit code 0 on success, non-zero on failure. An invalid flag reports to stderr
before the run; a failure inside the run prints as the result on stdout.
SIGTERM exits with **143**, leaves the turn unfinished, kills running Bash
process trees, runs `SessionEnd` hooks, and resumes that turn if you later
resume the session.

## Output formats

| `--output-format` | Shape |
|---|---|
| `text` (default) | plain text |
| `json` | `result`, `session_id`, usage, `total_cost_usd` and a per-model cost breakdown |
| `stream-json` | newline-delimited events; last line is the `result` message |

`--json-schema` with `--output-format json` constrains the answer and puts it in
`structured_output`. An invalid schema now errors rather than silently returning
unstructured text. `format` keywords are accepted as annotations but **not
enforced**.

Stream with `--output-format stream-json --verbose --include-partial-messages`.

```bash
claude -p "Summarize this project" --output-format json | jq -r '.result'
```

## Reading the stream

- `system/init` — first event; model, tools, MCP servers, plugins, and a
  `capabilities` array for feature detection instead of version comparison.
- `plugins` / `plugin_errors` and `mcp_servers` / `mcp_server_errors` — the CI
  gate. A plugin or MCP server that fails to load does **not** fail the run, so
  check for a non-empty errors array yourself.
- `system/api_retry` — `attempt`, `max_retries`, `retry_delay_ms`,
  `error_status`, and an `error` category (`rate_limit`, `overloaded`,
  `authentication_failed`, `billing_error`, …).
- Subagent messages carry `parent_tool_use_id`; main-conversation messages carry
  `null`. Add `--forward-subagent-text` to get subagent text and thinking too.

## Permission posture for CI

`-p` starts in **Manual mode on every plan**, so pass what you want:

- `--permission-mode dontAsk` — denies anything not in `permissions.allow` or
  the read-only command set. The locked-down choice.
- `--permission-mode acceptEdits` — writes files plus `mkdir`/`touch`/`mv`/`cp`;
  other shell commands still need a rule.
- `--permission-mode auto` — a classifier reviews instead of you.

## The CI security checklist

1. **Use `--bare`.** Without it a `-p` run executes the repo's
   `.claude/settings.json` hooks and connects its `.mcp.json` servers, in a
   folder nobody trusted, with no prompt.
2. Set `ANTHROPIC_API_KEY` — bare mode never reads OAuth credentials or the
   keychain. `claude setup-token` generates a long-lived OAuth token where you
   need one.
3. Pin the permission mode explicitly rather than relying on a default.
4. Gate on `plugin_errors` / `mcp_server_errors`.
5. Cap the blast radius with `--max-turns` and `--max-budget-usd`.

## Sessions across invocations

```bash
session_id=$(claude -p "Start a review" --output-format json | jq -r '.session_id')
claude -p "Continue that review" --resume "$session_id"
```

`--continue` picks the most recent conversation and skips background sessions.
Sessions are now found by ID from any directory on the machine.

## Background tasks at exit

A background Bash shell is terminated ~5s after the final result. Background
**subagents and workflows** are exempt — `claude -p` waits for them, capped at
ten minutes by default (`CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS`, `0` for no cap).

## Piping

stdin is capped at **10MB**; past that, write a file and reference its path.

```bash
git diff main | claude -p "report typos as filename:line" --bare
```

Piping the diff means Claude never needs Bash permission to read it — the
cheapest way to narrow what a CI run can touch.
