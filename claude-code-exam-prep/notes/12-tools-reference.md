# 12 — Tools reference

> Source: [Tools reference](https://code.claude.com/docs/en/tools-reference)

## Which tools need permission

**No prompt (read-only or metadata):** `Read`, `Grep`, `Glob`, `LSP`,
`Agent`, `AskUserQuestion`, `TodoWrite`, the `Task*` and `Cron*` families,
`ListAgents`, `SendMessage`, `ToolSearch`, `ScheduleWakeup`,
`ListMcpResourcesTool`, `ReadMcpResourceTool`, `ExitWorktree`, `EnterPlanMode`.

**Prompt required:** `Bash`, `PowerShell`, `Edit`, `Write`, `NotebookEdit`,
`WebFetch`, `WebSearch`, `Skill`, `Workflow`, `Monitor`, `EnterWorktree`,
`ExitPlanMode`, `Artifact`.

## Rule syntax per tool

```
Read(~/secrets/**)              # path patterns: Read, Edit, Write, Glob, Grep, LSP
Bash(npm run *)                 # command patterns: Bash, Monitor, PowerShell
WebFetch(domain:example.com)    # domain matching
Agent(Explore)                  # subagent type
Skill(deploy *)                 # skill name
WebSearch                       # no specifier
```

Remember from note 02: **only `Read(path)` and `Edit(path)` are actually
consulted** by file permission checks, even though several tools accept path
rules.

## Behaviors worth memorizing

**Bash**
- Read-only commands (`grep`, `find`, `git diff`) run without a prompt.
- `run_in_background: true` for long tasks; auto-backgrounds on timeout except
  for `sleep`, `git`, and compound commands.
- Output ~30KB inline, else a file path; failures return a 10KB excerpt.

**Edit / Write**
- `Edit` requires a prior read, and grants read access to the same path.
- `old_string` must match **exactly once**, or use `replace_all: true`.
- `Write` grants implicit read access to the path it writes.

**Read**
- Read-only. Handles images, PDFs and notebooks. Paginated for large files.

**Grep vs. Glob**
- `Grep` (ripgrep) **respects** `.gitignore`; `Glob` **ignores** it by default.
  That asymmetry catches people out.

**WebFetch**
- Lossy by design: it runs an extraction prompt, not raw retrieval.
- Auto-upgrades HTTP → HTTPS; caches 15 minutes.
- Needs domain permission on first fetch.

**EndConversation** — the special case
- **Cannot be blocked by a deny rule.** The exemption is deliberate: a deny rule
  can't remove it while any other tool remains, and an ask rule never prompts
  for it.
- Locks the session afterward; only `/clear`, `/resume`, `/help`, `/exit` and
  `/feedback` still work.
- For sustained abuse only. Unavailable in `-p`, the Agent SDK, the VS Code
  panel, GitHub Actions, claude.ai web, and the cloud providers.

**Task tools and TodoWrite**
- Hidden by default on the newest models to preserve context. Opt in with
  `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` or `--allowedTools TaskCreate`.

**Monitor**
- Watches processes, logs and WebSockets; `ws://`/`wss://` only, and denies
  private and metadata IPs. Binary frames ignored; >1MB ends the watch.

## Removed from subagents

`EndConversation` is never available. `Agent` is removed at the depth limit, so
subagents can't spawn subagents by default. `AskUserQuestion`,
`EnterPlanMode`/`ExitPlanMode`, `ScheduleWakeup` and `Workflow` are also
removed — see note 05.

## Availability constraints

Several tools are unavailable on Bedrock, Google Cloud and Foundry:
`RemoteTrigger`, `ScheduleWakeup`, `Monitor`, `EndConversation`, and
`SendUserFile`. `Artifact` requires Pro or above.
