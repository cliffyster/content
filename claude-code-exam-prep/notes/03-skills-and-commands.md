# 03 — Skills and slash commands

> Source: [Extend Claude with skills](https://code.claude.com/docs/en/skills)

## Commands are skills now

`.claude/commands/deploy.md` and `.claude/skills/deploy/SKILL.md` both create
`/deploy` and behave the same way. Existing `commands/` files keep working. The
skill form adds three things: a directory for supporting files, frontmatter that
controls who can invoke it, and automatic loading by Claude when relevant.

## Frontmatter

```yaml
---
name: commit
description: Stage and commit the current changes with a conventional message.
argument-hint: "[scope]"
disable-model-invocation: true
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *)
disallowed-tools: AskUserQuestion
---
```

| Field | Notes |
|---|---|
| `name`, `description` | Required |
| `argument-hint` | Autocomplete hint. **Rejected** by claude.ai skill uploads and the Skills API — those accept only `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` |
| `disable-model-invocation` | `true` = only you can invoke it. Also blocks preloading into subagents |
| `allowed-tools` | Pre-approves tools **for the invoking turn only** |
| `disallowed-tools` | Removes tools from the pool while the skill is active |
| `context: fork` | Runs the skill in its own subagent context |

## Two lifetimes, and they differ

This is the trap:

- **Content** enters the conversation as one message and **stays for the whole
  session**. Claude Code never re-reads `SKILL.md` on later turns.
- **Permissions** (`allowed-tools` / `disallowed-tools`) last **one turn** and
  clear when you send your next message.

Consequence: write standing instructions, not one-time steps. "First do X, then
Y" reads badly on turn nine; "Always prefer X over Y" reads correctly forever.

## Arguments

| Placeholder | Expands to |
|---|---|
| `$ARGUMENTS` | The full argument string as typed |
| `$ARGUMENTS[N]` | Argument N, **0-based** |
| `$N` | Shorthand for `$ARGUMENTS[N]` — so `$0` is first, `$1` is second |

`/migrate-component SearchBar React Vue` → `$0`=SearchBar, `$1`=React, `$2`=Vue.
Multi-word values need shell-style quoting. Escape a literal with a backslash:
`\$1.00`.

If the body has no `$ARGUMENTS` at all, Claude Code appends
`ARGUMENTS: <your input>` to the end so nothing is lost.

You can stack skills: `/write-tests /fix-issue 123` loads both and passes `123`
to each.

## `${CLAUDE_SKILL_DIR}` and the no-prompt pattern

Claude Code substitutes `${CLAUDE_SKILL_DIR}` in exactly two places: the
markdown body, and the Bash rules inside `allowed-tools`. Using it in both makes
the allow rule match the command the body tells Claude to run:

```yaml
---
name: render-chart
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/render.sh *)
---
Run `${CLAUDE_SKILL_DIR}/scripts/render.sh $ARGUMENTS` to produce the chart.
```

## The security note

**Workspace trust does not gate `allowed-tools`.** A project skill's grant
applies whenever the skill is invoked — including a `-p` run in a folder you
have never trusted. A skill checked into a repository can therefore grant itself
broad tool access. Review the `allowed-tools` of repository skills before
running Claude Code there.
