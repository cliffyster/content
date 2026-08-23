# Lab 07 — answers

## What was wrong with the original

| Problem | Fix |
|---|---|
| Repo `.claude/settings.json` hooks and `.mcp.json` servers execute untrusted | `--bare` |
| `--allowedTools "Bash"` is unbounded shell access | Drop Bash; pipe the diff in |
| Manual mode means unmatched calls prompt — and in CI nobody answers | `--permission-mode dontAsk` |
| No cap on turns or spend | `--max-turns`, `--max-budget-usd` |
| A failed plugin or MCP server is invisible | Gate on `plugin_errors` / `mcp_server_errors` |

## The questions

**1. Trust verification.**
First-time codebase runs and new MCP servers normally require trust
verification — and it is **disabled when running non-interactively with `-p`**,
because there is no way to show the dialog. That single fact is why `--bare` is
the correct default for CI rather than a nicety.

**2. Piping removes the need for Bash.**
If Claude has to run `git diff` itself, the run needs Bash permission, and a
Bash grant is hard to scope tightly (compound commands, environment runners like
`npx` and `docker exec` that are not stripped before matching). Piping the diff
in means the content arrives as stdin and the run can hold `Read` only. The docs
make the same point for the `package.json` linter example.

**3. Exit code 143.**
SIGTERM exits with 143. Claude Code terminates the process tree of any running
Bash command, runs `SessionEnd` hooks, and records **no result** for the
in-flight turn — which continues when you resume the session. To end the turn
cleanly instead, send SIGINT, or call the Agent SDK's `interrupt()` before
stopping the process.

## Why `dontAsk` and not `bypassPermissions`

`dontAsk` converts any prompt into a **denial**: tools pre-approved by
`--allowedTools` or by allow rules run, everything else is denied outright. That
is a fixed, explicit tool surface. `bypassPermissions` is the opposite — and
note the trap from the Agent SDK docs, which applies to the same permission
engine: **`allowed_tools` does not constrain `bypassPermissions`**. Unlisted
tools are simply unmatched by an allow rule and fall through to the mode, which
approves them. `--allowedTools "Read"` with bypass would still permit `Bash`,
`Write` and `Edit`.

## One more thing worth doing

Add `--settings '{"disableAllHooks": true}'` if you want belt and braces.
Setting `disableAllHooks` in *user* settings alone is not enough, because a
repository's project settings take precedence and can set it back to `false`.
