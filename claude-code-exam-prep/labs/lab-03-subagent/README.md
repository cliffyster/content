# Lab 03 — A subagent that cannot write

**Goal:** build `notes-auditor`, a subagent that reads every file in `notes/`,
finds claims that contradict the question bank, and reports them — and that is
**structurally incapable** of editing anything.

## Why this shape

The point of a subagent is not that you asked it nicely. It is that
`tools: Read, Grep, Glob` removes the write tools from its pool entirely, so a
confused agent, a bad prompt, or injected text in a file it reads cannot make
it write. Constraint by construction, not by instruction.

## Build it

Create `.claude/agents/notes-auditor.md`:

```markdown
---
name: notes-auditor
description: ...when should Claude delegate to this?
tools: Read, Grep, Glob
model: inherit
---

<system prompt>
```

Requirements:

1. Read-only tools only.
2. The description must be specific enough that Claude delegates on the right
   task and not on everything.
3. The system prompt must tell it to **report**, not fix — and to output a
   structured list your main session can act on.

## Run it

```
@notes-auditor check notes/02-permissions.md against the permissions questions
```

The `@` form guarantees this agent runs. Without it, Claude decides based on the
description — useful, but not a guarantee.

## Questions

1. Your subagent needs to ask the learner which of two readings they meant.
   How does it do that?
2. It has no idea what you and Claude discussed three turns ago. Why not, and
   what would give it that context?
3. You set `model: haiku`. What did you trade away, and when is that right?
