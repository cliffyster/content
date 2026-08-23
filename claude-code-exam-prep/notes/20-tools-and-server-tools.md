# 20 — Tool design, server tools, and scaling

> Source: [Tool use](https://platform.claude.com/docs/en/build-with-claude/tool-use) ·
> Agent design guidance

## Tool definition

```json
{
  "name": "get_weather",
  "description": "Get current weather for a location",
  "input_schema": {
    "type": "object",
    "properties": {
      "location": {"type": "string", "description": "City and state, e.g. San Francisco, CA"},
      "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
    },
    "required": ["location"]
  }
}
```

The description is the highest-leverage field. **Be prescriptive about *when* to
call it, not just what it does** — "Call this when the user asks about current
prices or recent events". Recent Opus models reach for tools more
conservatively, so trigger conditions in the description measurably raise the
should-call rate. Use `enum` for fixed value sets, and mark only genuinely
required parameters as required.

## `tool_choice`

| Value | Behavior |
|---|---|
| `{"type": "auto"}` | Claude decides (default) |
| `{"type": "any"}` | Must use at least one tool |
| `{"type": "tool", "name": "…"}` | Must use that tool |
| `{"type": "none"}` | Cannot use tools |

Any value can add `"disable_parallel_tool_use": true` to cap it at one tool per
response. By default Claude may request several.

## Bash vs. dedicated tools — the design question

Claude emits tool calls; **your harness handles them**. The shape of the call
determines what the harness can do.

A bash tool gives broad leverage but hands the harness an **opaque command
string** — the same shape for every action. A dedicated tool gives an
action-specific hook with typed arguments the harness can intercept, gate,
render, or audit.

Promote an action to a dedicated tool when you need:

- **A security boundary.** Reversibility is the useful criterion: hard-to-reverse
  actions (external API calls, sending messages, deleting data) should be
  gateable. A `send_email` tool is easy to gate; `bash -c "curl -X POST …"` is
  not.
- **Staleness checks.** A dedicated `edit` tool can reject a write if the file
  changed since Claude last read it. Bash cannot enforce that invariant.
- **Rendering.** Claude Code promotes question-asking to a tool so it can render
  as a modal and block the loop until answered.
- **Scheduling.** Read-only tools can be marked parallel-safe. Through bash the
  harness can't tell a parallel-safe `grep` from a parallel-unsafe `git push`,
  so it must serialize everything.

**Rule of thumb: start with bash for breadth; promote when you need to gate,
render, audit, or parallelize.**

## Client-side vs. server-side tools

| Tool | Side | Notes |
|---|---|---|
| Bash | Client | Anthropic defines it, your harness executes |
| Text editor | Client | Same |
| Memory | Client | Claude reads/writes `/memories`; you implement storage |
| Computer use | Either | Self-hosted or Anthropic-hosted |
| Code execution | Server | Anthropic-hosted container |
| Web search / fetch | Server | Anthropic executes; results carry citations |

**Client-side Anthropic tools are schema-less** — declare
`{"type": "bash_20250124", "name": "bash"}` with no `input_schema`. A custom
tool with your own schema named `"bash"` is a *different tool*.

## Code execution

- Isolated container: 1 CPU, 5 GiB RAM, 5 GiB disk. **No internet access.**
- Python 3.11 with pandas, numpy, scipy, scikit-learn, statsmodels, matplotlib,
  seaborn, openpyxl, pillow, pypdf, python-docx, python-pptx, sympy.
- Containers persist 30 days and can be reused across requests.
- Free alongside web search/fetch; otherwise billed hourly after a large monthly
  free allowance.
- Declaring it grants Claude `bash_code_execution` and
  `text_editor_code_execution` automatically.

Practical consequence: for a "produce a report/chart/spreadsheet" request, code
execution plus the Files API beats returning text.

## Programmatic tool calling

Standard tool use is a round trip per call: call → result into context → reason
→ next call. Three sequential lookups means three round trips, and most
intermediate data is never needed again.

PTC lets Claude **compose those calls into a script** that runs in the code
execution container. When the script calls a tool, the container pauses, the
call executes, and the result returns **to the running code — not to Claude's
context**. Only the script's final output comes back.

Token cost then scales with the *final output*, not the intermediate results.
Use it for many sequential calls or large intermediate results you want filtered
before they hit the window.

## Scaling the tool set

| Feature | Use when | Effect |
|---|---|---|
| **Tool search** | Many tools, few relevant per request | Claude searches and loads only relevant schemas. **Schemas are appended, not swapped — so the cache prefix survives.** |
| **Skills** | Task-specific instructions | Description sits in context; the full file loads only when needed |

Both keep the fixed context small and load detail on demand. Note the tool
search caveat from the API side: the search tool itself must not be deferred,
and at least one tool must be non-deferred, or you get a 400.

## Three ways to manage a long-running agent's context

| Pattern | Does | Scope |
|---|---|---|
| **Context editing** | *Clears* stale tool results and thinking blocks | Within a session |
| **Compaction** | *Summarizes* earlier context server-side | Within a session |
| **Memory** | Persists state to files | **Across** sessions |

They are not alternatives — many long-running agents use all three. The critical
implementation detail for compaction: append `response.content`, not just the
extracted text, or you silently lose the compaction blocks the API needs.

## Caching workarounds for agents

| Constraint | Workaround |
|---|---|
| Editing the system prompt mid-session invalidates the cache | Append a `{"role": "system", …}` message to `messages[]` instead |
| Switching models mid-session invalidates the cache | Spawn a **subagent** on the cheaper model; keep the main loop on one model |
| Adding/removing tools mid-session invalidates the cache | Use **tool search** — it appends rather than swaps |
