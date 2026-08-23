# 04 — Hooks

> Source: [Hooks reference](https://code.claude.com/docs/en/hooks)

A hook is deterministic code the *harness* runs at a lifecycle point. That is
the whole reason they exist: "please always run the linter" is a request Claude
can forget; a `PostToolUse` hook cannot.

## Shape

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(rm *)",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.sh",
            "args": [],
            "timeout": 600
          }
        ]
      }
    ]
  }
}
```

Three nested levels: **event** → **matcher group** → **handler**.

## Events worth knowing

| Group | Events |
|---|---|
| Session | `SessionStart`, `SessionEnd`, `Setup` |
| Turn | `UserPromptSubmit`, `UserPromptExpansion`, `Stop`, `StopFailure` |
| Tools | `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `PermissionRequest`, `PermissionDenied` |
| Subagents | `SubagentStart`, `SubagentStop` |
| Context | `PreCompact`, `PostCompact` |
| Files/env | `FileChanged`, `CwdChanged`, `InstructionsLoaded`, `ConfigChange` |

Note `PostToolUse` fires after **success**; failures get `PostToolUseFailure`.

## Matchers

| Matcher | Read as |
|---|---|
| `"*"`, `""`, omitted | match everything |
| Letters, digits, `_`, `-`, space, `,`, `\|` | exact string or list — `Edit\|Write` |
| Anything else | **unanchored JavaScript regex** — `^Notebook.*`, `mcp__memory__.*` |

What the matcher filters depends on the event: tool name for tool events,
`startup`/`resume`/`clear` for `SessionStart`, notification type for
`Notification`, agent type for `SubagentStart`, error type for `StopFailure`.

## Handler types

`command`, `http`, `mcp_tool`, `prompt`, `agent`. Default timeout is 600s for
the first three, 30s for `prompt`, 60s for `agent`.

For `command`: supplying `args` switches to **exec form** — no shell, special
characters verbatim. Omitting `args` uses **shell form**, where pipes and `&&`
are interpreted.

## Exit codes and JSON

| Exit | Meaning |
|---|---|
| 0 | Success — stdout is parsed as JSON for structured control |
| 2 | **Blocking** error |
| other | Non-blocking error; the action proceeds |

Universal JSON fields: `continue` (false stops all processing), `systemMessage`,
`additionalContext`, `hookSpecificOutput`.

Per-event decisions:

```jsonc
// PreToolUse — block, allow, or rewrite the call
{"hookSpecificOutput": {"hookEventName": "PreToolUse",
  "permissionDecision": "deny", "permissionDecisionReason": "…",
  "updatedInput": {"command": "echo safe"}}}

// UserPromptSubmit — block or rewrite the prompt
{"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
  "decision": "deny", "reason": "…", "updatedPrompt": "…"}}

// PermissionRequest — grant or deny
{"decision": "deny", "reason": "…"}
```

## Where hooks can be declared

User settings, project settings, project local settings, managed policy, a
plugin's `hooks/hooks.json`, **skill frontmatter** (rest of session) and
**subagent frontmatter** (while it runs).

## Precedence, again

- Hook says `"allow"`, a deny rule matches → **denied**.
- Hook exits 2, an allow rule matches → **blocked**.

Restrictions win in both directions.
