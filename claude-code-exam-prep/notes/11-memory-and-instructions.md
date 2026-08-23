# 11 — Memory: CLAUDE.md, rules, and auto memory

> Source: [How Claude remembers your project](https://code.claude.com/docs/en/memory)

Every session starts with a fresh context window. Two mechanisms carry knowledge
across sessions, and they differ in **who writes them**:

| | CLAUDE.md | Auto memory |
|---|---|---|
| Written by | You | Claude |
| Contains | Instructions and rules | Learnings and corrections |
| Scope | Project, user, or org | Per repository, shared across worktrees |
| Loaded | Every session | Every session (first 200 lines / 25KB of `MEMORY.md`) |

Both are **context, not enforced configuration**. To block an action regardless
of what Claude decides, you need a `PreToolUse` hook — this is the single most
important distinction on the page.

## Where CLAUDE.md lives

Load order, broadest to most specific:

| Scope | Location |
|---|---|
| Managed policy | `/Library/Application Support/ClaudeCode/CLAUDE.md` (macOS), `/etc/claude-code/CLAUDE.md` (Linux/WSL), `C:\Program Files\ClaudeCode\CLAUDE.md` (Windows) |
| User | `~/.claude/CLAUDE.md` |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` |
| Local | `./CLAUDE.local.md` (gitignore it) |

Files are **concatenated, not overridden**. Across the tree, content is ordered
from filesystem root down to your working directory, so instructions closer to
where you launched are read last. Within a directory, `CLAUDE.local.md` comes
after `CLAUDE.md`.

Files in subdirectories below the working directory load **on demand**, when
Claude reads files there.

Managed policy CLAUDE.md **cannot be excluded** by individual settings. The
`claudeMd` key puts managed CLAUDE.md content directly in
`managed-settings.json`; it is honored only in managed/policy settings.

## Imports

`@path/to/file` expands at launch. Relative paths resolve against the file
containing the import, not the working directory. **Maximum depth is four hops.**

Import parsing skips code spans and fenced blocks — write `` `@README` `` to
mention a path without importing it.

**External imports get an approval dialog.** An import in a *project* memory
file whose path resolves outside the working directory prompts once, listing the
files; decline and they stay disabled. User-scope memory files are trusted
without the dialog, because you wrote them.

Note the sizing trap: imports help **organization**, not context cost. Imported
files still load in full at launch.

## AGENTS.md

Claude Code reads `CLAUDE.md`, not `AGENTS.md`. Bridge them with an import:

```markdown
@AGENTS.md

## Claude Code
Use plan mode for changes under `src/billing/`.
```

A symlink works too, but needs Administrator or Developer Mode on Windows.

## `.claude/rules/`

Modular instruction files, discovered recursively. Rules **without** a `paths`
frontmatter field load at launch with the same priority as `.claude/CLAUDE.md`.
Rules **with** `paths` load only when Claude touches a matching file:

```markdown
---
paths:
  - "src/api/**/*.ts"
  - "tests/**/*.test.ts"
---
```

Brace expansion is budgeted: one rule's whole `paths` list shares 1,000 expanded
patterns and 4 MiB. `~/.claude/rules/` are user-level and load *before* project
rules, giving project rules higher priority. Symlinks are supported and
circular ones are handled.

## Sizing rules

- Target **under 200 lines** per CLAUDE.md. Longer files reduce adherence.
- Claude Code loads a CLAUDE.md up to **4 MiB** in full and **skips a larger
  one**.
- `MEMORY.md` loads only its first **200 lines or 25KB**, whichever comes first.
  Over the limit, the write succeeds but everything past it is dropped on the
  next load.
- Block-level HTML comments (`<!-- … -->`) are stripped before injection — free
  maintainer notes.

## Auto memory

On by default. Claude records four types in frontmatter: `user`, `feedback`,
`project`, `reference`. It skips anything derivable from the codebase and
anything CLAUDE.md already says.

Storage: `~/.claude/projects/<project>/memory/`, with a `MEMORY.md` index plus
topic files. Machine-local; shared across worktrees of the same repo. Excluded
from the `cleanupPeriodDays` retention sweep.

Disable with `autoMemoryEnabled: false` or `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`.
Relocate with `autoMemoryDirectory`.

Auto memory from the main conversation is **not** loaded into subagents — except
a fork, which inherits the parent conversation. A subagent's own `memory:` field
creates a separate directory.

## Debugging adherence

`/context` shows what actually loaded under **Memory files**. `/memory` lists
and opens them. The `InstructionsLoaded` hook logs exactly which files load,
when, and why.

CLAUDE.md is delivered as a **user message after the system prompt**, not as
part of it — which is why adherence is best-effort. For system-prompt-level
instructions use `--append-system-prompt`; for guarantees use a hook.

Project-root CLAUDE.md **survives `/compact`** — Claude re-reads and re-injects
it. Nested CLAUDE.md and path-scoped rules reload as their files are touched.
Instructions given only in conversation do not survive.

## Monorepos

`claudeMdExcludes` skips ancestor files by glob. Arrays merge across settings
layers. Managed policy files cannot be excluded.
