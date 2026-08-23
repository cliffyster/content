# 15 — The Claude Agent SDK in depth

> Source: [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview) ·
> [Python reference](https://code.claude.com/docs/en/agent-sdk/python) ·
> [SDK permissions](https://code.claude.com/docs/en/agent-sdk/permissions)

```bash
pip install claude-agent-sdk          # npm i @anthropic-ai/claude-agent-sdk
```

Python and TypeScript only. To drive the same loop from another language, run
the CLI as a subprocess with `-p --output-format json`.

## Which surface to use

| If you're… | Use |
|---|---|
| Building an agent without writing the tool loop | **Agent SDK** |
| Working interactively in a terminal | Claude Code CLI |
| Calling the API and writing the loop yourself | Client SDK (`anthropic`) |
| Running long agents without managing a sandbox | Managed Agents (hosted REST) |

## `query()` vs `ClaudeSDKClient`

| | `query()` | `ClaudeSDKClient` |
|---|---|---|
| For | one-off tasks | continuous conversation |
| Session | new each time (or `continue_conversation=True`) | reuses one session |
| Interrupts | no | yes |

```python
async for message in query(prompt="Fix the bug in auth.py", options=options):
    ...

async with ClaudeSDKClient(options=options) as client:
    await client.query("What's the capital of France?")
    async for msg in client.receive_response():
        ...
    await client.query("Population of that city?")   # same session
```

## `ClaudeAgentOptions`

```python
options = ClaudeAgentOptions(
    system_prompt="You are an expert…",     # or a preset / file
    model="claude-opus-5",
    allowed_tools=["Read", "Write", "Bash"],
    disallowed_tools=["Bash(rm *)"],
    permission_mode="acceptEdits",          # default|plan|acceptEdits|auto|dontAsk|bypassPermissions
    mcp_servers={"calc": server},
    strict_mcp_config=False,                # True ignores .mcp.json
    agents={"reviewer": AgentDefinition(description=…, prompt=…, tools=["Read", "Grep"])},
    hooks={"PreToolUse": [matcher_config]},
    can_use_tool=my_permission_callback,
    setting_sources=["project"],            # which settings layers to load
    continue_conversation=False,
    resume="session-id-uuid",
    max_turns=10,
    cwd="/path/to/project",
    add_dirs=["/extra/path"],
    env={"API_TIMEOUT_MS": "120000"},
)
```

`setting_sources` is the one to watch: **default `query()` options enable
`project`**, so `.claude/settings.json` rules apply. If you set the field
explicitly you must include `"project"` yourself or those rules silently stop
applying.

## Custom tools

```python
from claude_agent_sdk import tool, create_sdk_mcp_server, ToolAnnotations

@tool("add", "Add two numbers", {"a": float, "b": float})
async def add(args):
    return {"content": [{"type": "text", "text": str(args["a"] + args["b"])}]}

server = create_sdk_mcp_server(name="math", tools=[add])

options = ClaudeAgentOptions(
    mcp_servers={"math": server},
    allowed_tools=["mcp__math__add"],       # note the MCP naming
)
```

SDK custom tools are exposed as an **in-process MCP server**, so they are named
`mcp__<server>__<tool>` like any other MCP tool — including in permission rules.
`ToolAnnotations(readOnlyHint=True, openWorldHint=True)` describes side effects.

## The six-step permission flow — memorize this

This is the SDK's evaluation order, and it is *richer* than the CLI's
deny→ask→allow:

1. **Hooks** — run first. A hook can deny outright. A hook returning `allow`
   does **not** skip the deny and ask rules below.
2. **Deny rules** — block even in `bypassPermissions`. A bare-name deny
   (`Bash`) removes the tool before this step; only scoped rules are checked
   here.
3. **Ask rules** — fall through to `can_use_tool`, even in `bypassPermissions`.
4. **Permission mode** — `bypassPermissions` approves; `acceptEdits` approves
   file ops; `plan` routes edits to the callback regardless of allow rules;
   others fall through.
5. **Allow rules** — approve if matched.
6. **`can_use_tool` callback** — only if nothing above resolved it. **Skipped
   entirely in `dontAsk`**, which denies instead.

### The trap this creates

> **Auto-approved tools never reach `can_use_tool`.**

A check you put in the callback is silently bypassed for anything an allow rule,
`acceptEdits`, or `bypassPermissions` already approved. A bare entry like
`allowed_tools=["Read"]` auto-approves *every* `Read`; a scoped entry like
`Bash(ls *)` only auto-approves matching calls. **For a check that must run on
every call, use a `PreToolUse` hook** — hooks run before every other step, and a
hook deny applies even in `bypassPermissions`.

The TypeScript SDK emits a one-time process warning,
`CLAUDE_SDK_CAN_USE_TOOL_SHADOWED`, when you pass a callback in a configuration
that would shadow it.

### And the other trap

> **`allowed_tools` does not constrain `bypassPermissions`.**

Unlisted tools aren't matched by an allow rule, so they fall through to the mode
— which approves them. `allowed_tools=["Read"]` with
`permission_mode="bypassPermissions"` still approves `Bash`, `Write` and `Edit`.
To block specific tools under bypass, use `disallowed_tools`.

For a genuinely locked-down agent, pair them the other way:

```python
ClaudeAgentOptions(allowed_tools=["Read", "Glob", "Grep"], permission_mode="dontAsk")
```

## `can_use_tool`

```python
async def custom_permission(tool_name, input_data, context):
    if tool_name == "Write" and input_data.get("file_path", "").startswith("/system/"):
        return PermissionResultDeny(message="System writes blocked", interrupt=True)
    return PermissionResultAllow(updated_input=input_data)   # can rewrite the call
```

`PermissionResultAllow(updated_input=…)` rewrites the tool call — the same
capability `PreToolUse`'s `updatedInput` gives a hook.

## Subagent inheritance

Subagents **inherit the parent's permission mode**. An `AgentDefinition`'s
`permissionMode` can override it — *except* when the parent is
`bypassPermissions`, `acceptEdits` or `auto`, which apply to every subagent and
cannot be overridden per subagent. Inheriting `bypassPermissions` gives a
subagent with a different system prompt full autonomous system access.

## Message types

`AssistantMessage` (with `TextBlock` / `ToolUseBlock` / `ThinkingBlock`
content), `ToolResultMessage`, `ResultMessage` (carries `result` and
`terminal_reason`), and `StreamEvent` when `include_partial_messages=True`.

## Branding, if it comes up

Partners may use "Claude Agent", or "\{YourName} Powered by Claude". Not
permitted: "Claude Code", "Claude Code Agent", or Claude Code ASCII art.
Third-party developers may not offer claude.ai login or rate limits for products
built on the SDK — use API key authentication.
