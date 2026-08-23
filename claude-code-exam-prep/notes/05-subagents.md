# 05 — Subagents

> Source: [Subagents](https://code.claude.com/docs/en/sub-agents)

A subagent is a specialized assistant with its **own context window**. You reach
for one when a task produces a lot of output you do not want in the main
conversation, or when you want to hard-limit what a piece of work can touch.

## Definition

```markdown
---
name: code-reviewer
description: Expert code reviewer. Use proactively after code changes.
tools: Read, Grep, Glob
model: sonnet
---

You are a senior code reviewer. Focus on correctness, security, and clarity.
```

`name` and `description` are the only required fields. Optional:
`tools`, `disallowedTools`, `model`, `permissionMode`, `skills`, `mcpServers`,
`hooks`, `memory`, `maxTurns`, `background`, `isolation`, `effort`, `color`.

`model` defaults to **`inherit`** — accepted values are `sonnet`, `opus`,
`haiku`, `fable`, a full model ID, or `inherit`.

## Precedence

Managed settings → `--agents` CLI flag → `.claude/agents/` → `~/.claude/agents/`
→ plugin `agents/`.

## Invocation

| Way | Guarantee |
|---|---|
| Description matches the task | Claude decides — not guaranteed |
| `@code-reviewer …` | **Guaranteed** |
| `claude --agent code-reviewer` | Makes it the main agent for the session |
| `claude --agents '{"name": {…}}'` | Defines one inline, session only |

## What crosses the boundary

A non-fork subagent **receives**: its own system prompt, the task message Claude
writes, `CLAUDE.md` (except for Explore and Plan), a git status snapshot,
skills named in `skills:`, and the sibling agent roster.

It does **not** receive: the main conversation history, output style
preferences, auto memory, or skills invoked earlier in the main session.

A **fork** is the opposite: full conversation history, same system prompt, tools
and model, and a shared prompt cache with the parent.

## Always-removed tools

`Agent` (at the depth limit), `AskUserQuestion`, `EndConversation`,
`EnterPlanMode`/`ExitPlanMode`, `ScheduleWakeup`, `Workflow`. A subagent cannot
ask the user a question — design its prompt so it never needs to.

## Built-ins

| Agent | Purpose |
|---|---|
| `Explore` | Read-only codebase exploration (model inherited, capped at Opus) |
| `Plan` | Research for plan mode |
| `general-purpose` | Complex multi-step tasks |

## When they earn their keep

- **Context preservation** — a search that reads 40 files returns one paragraph.
- **Enforced constraints** — `tools: Read, Grep, Glob` cannot write, whatever
  the prompt says.
- **Cost** — route mechanical, verbose work to a faster model.

And when they do not: a subagent starting from a blank context has to rediscover
everything you already know. For a small edit in a file you are looking at, the
handoff costs more than it saves.
