# 16 — The context window

> Source: [Explore the context window](https://code.claude.com/docs/en/context-window) ·
> [How Claude Code uses prompt caching](https://code.claude.com/docs/en/prompt-caching)

## What loads before you type anything

System prompt (~4k tokens), auto memory (`MEMORY.md`, first 200 lines / 25KB),
environment info (cwd, platform, shell, git status as a separate block at the
end of the system prompt), MCP tool names, CLAUDE.md files and unscoped rules,
and tool definitions.

MCP tool **schemas** are deferred by default — only names load, and Claude pulls
specific schemas on demand via tool search. `ENABLE_TOOL_SEARCH=auto` loads
schemas upfront when they fit within 10% of the window; `=false` loads
everything. With many servers connected this is the difference between a usable
session and one that starts half-full.

## What survives compaction

The single most testable table on the page:

| Mechanism | After compaction |
|---|---|
| System prompt and output style | Unchanged — not part of message history |
| Project-root CLAUDE.md and unscoped rules | **Re-injected from disk** |
| Auto memory | **Re-injected from disk** |
| Rules with `paths:` frontmatter | **Lost** until a matching file is read again |
| Nested CLAUDE.md in subdirectories | **Lost** until a file there is read again |
| Invoked skill bodies | Re-injected — capped at 5,000 tokens per skill and 25,000 total, oldest dropped first |
| Hooks | N/A — hooks are code, not context |

Two consequences worth internalising:

1. **If a rule must persist across compaction, drop its `paths:` frontmatter**
   or move it into the project-root CLAUDE.md. Path-scoped rules enter message
   history when their trigger file is read, so compaction summarizes them away
   like anything else.
2. **Skill truncation keeps the start of the file** — so put the most important
   instructions near the top of `SKILL.md`, not in a closing section.

Since v2.1.198 the summarization request inherits the session's extended
thinking configuration.

## Managing it

- `/context` — visualize what is actually in the window right now. This is the
  diagnostic; use it before guessing.
- `/compact` — summarize and continue. `/autocompact` sets the window.
- `/clear` — start fresh. Use it when the *task* changed; `/compact` when the
  task continues but the history got long.
- **Subagents** — a search that reads 40 files returns one paragraph to the
  parent. The single biggest structural lever.
- **Skills** — bodies load only when invoked, so long reference material costs
  nothing until needed. This is the argument for moving a procedure out of
  CLAUDE.md and into a skill.
- `/btw` — ask a side question without adding it to the conversation.

## Claude Code and prompt caching

Claude Code caches the stable prefix of your session automatically. The practical
consequence is the same as note 09: anything that changes near the front of the
context invalidates everything after it. A CLAUDE.md that embeds a timestamp, or
a tool list that varies between turns, quietly costs you the cache for the whole
session.
