# 02 — Permissions

> Source: [Configure permissions](https://code.claude.com/docs/en/permissions) ·
> [Permission modes](https://code.claude.com/docs/en/permission-modes)

The single most testable area, because the rules are precise and the intuitive
answer is often wrong.

## Evaluation order

**deny → ask → allow. First match wins. Specificity is irrelevant.**

`Bash(aws *)` in deny blocks `aws s3 ls` even if `Bash(aws s3 ls)` is in allow.
A deny rule cannot carry allowlist exceptions. Same between ask and allow: a
matching ask rule prompts even when a narrower allow also matches.

## Bare name vs. scoped rule

| Rule | Effect |
|---|---|
| `deny: Bash` | Removes the tool from Claude's context entirely — it never sees it |
| `deny: Bash(rm *)` | Tool stays available; matching calls are blocked |
| `Bash(*)` | Equivalent to `Bash` |

The one tool that cannot be removed by a bare deny is `EndConversation`, while
any other tool remains.

## Bash pattern matching

Wildcards are not shell globs:

| Pattern | Matches |
|---|---|
| `Bash(npm run build)` | exactly that command |
| `Bash(npm *)` | anything starting `npm ` |
| `Bash(* install)` | anything ending ` install` |
| `Bash(git * main)` | `git checkout main`, `git push origin main` |
| `Bash(ls *)` | `ls -la` — **not** `lsof` (space before `*` = word boundary) |
| `Bash(ls*)` | `ls -la` **and** `lsof` |
| `Bash(ls:*)` | same as `Bash(ls *)`; `:*` is only recognized at the end |

**Shell operators split the command.** Separators are `&&`, `||`, `;`, `|`,
`|&`, `&` and newlines, and every subcommand must match a rule independently.
`Bash(safe-cmd *)` does not approve `safe-cmd && rm -rf /`.

**Wrappers that get stripped** before matching: `timeout`, `time`, `nice`,
`nohup`, `stdbuf`, the builtins `command` and `builtin`, zsh's `noglob`, and
bare `xargs`. So `Bash(npm test *)` covers `timeout 30 npm test`. A leading
assignment of a known-safe env var is also stripped for allow rules, so it
covers `NODE_ENV=test npm test`.

**Wrappers that are NOT stripped** — and this is the security point — environment
runners like `npx`, `docker exec`, `devbox run`, `direnv exec`, `mise exec`.
`Bash(devbox run *)` matches `devbox run rm -rf .`. Write
`Bash(devbox run npm test)`, one rule per inner command.

Exec wrappers (`watch`, `setsid`, `ionice`, `flock`) and `find` with `-exec` or
`-delete` can never be prefix-approved — they always prompt in Manual mode.

## File rules

Only **`Read(path)`** and **`Edit(path)`** are consulted by file permission
checks. A path rule written for `Write`, `NotebookEdit`, `Glob` or `MultiEdit`
is accepted, never consulted, and warned about at startup.

```jsonc
// wrong — silently does nothing
"deny": ["Write(./secrets/**)"]
// right
"deny": ["Edit(./secrets/**)", "Read(./secrets/**)"]
```

Path syntax: `./x` is relative to the settings file, `//x` is absolute from the
filesystem root, `~/x` is home. Output redirection targets (`>`, `>>`, `2>`) are
checked as file writes; `/dev/null` is exempt; a `~` or glob target always
prompts.

## Parameter rules

`Tool(param:value)` matches a top-level scalar parameter — **deny and ask only**.
It cannot match a tool's primary content field (`command`, `file_path`, `path`,
`notebook_path`, `url`); `Bash(command:rm *)` is ignored with a startup warning
because a compound command would bypass it.

## MCP rules

`mcp__<server>__<tool>`. Allow globs need a literal, glob-free server segment:

- `mcp__puppeteer__*` ✅  `mcp__github__get_*` ✅
- `mcp__*` ❌ `"*"` ❌ — skipped with a warning, approve nothing

## Modes

| Mode | Behavior |
|---|---|
| `default` | Prompts on first use of each tool |
| `plan` | Reads and read-only shell only; no source edits |
| `acceptEdits` | Auto-accepts edits **and** `mkdir`, `touch`, `mv`, `cp` in working dirs |
| `auto` | A classifier approves actions instead of you |
| `dontAsk` | Auto-**denies** anything not pre-approved |
| `bypassPermissions` | Skips prompts, including writes to `.git` and `.claude` |

Set the starting mode with `defaultMode`. Lock the dangerous ones with
`permissions.disableBypassPermissionsMode` / `disableAutoMode` set to
`"disable"` — most useful in managed settings.

## Hooks vs. rules

Two directions, both worth knowing:

- A `PreToolUse` hook returning `"allow"` does **not** override a deny or ask
  rule — deny-first precedence is preserved.
- A hook exiting **2** blocks the call *before* rules are evaluated, so it
  overrides an allow rule.

That asymmetry gives you the "allow everything except these" pattern: put
`"Bash"` in allow, and block the specific cases from a `PreToolUse` hook.
