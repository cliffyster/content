# 07 — Agents and the SDKs

> Source: [Agent SDK](https://code.claude.com/docs/en/agent-sdk) ·
> [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)

## Should this even be an agent?

Check four things before choosing the agent tier:

1. **Complexity** — multi-step and hard to fully specify up front?
2. **Value** — does the outcome justify higher cost and latency?
3. **Viability** — is Claude actually good at this task type?
4. **Cost of error** — can mistakes be caught and recovered (tests, review, rollback)?

Any "no" → drop to a workflow (you own the control flow) or a single call.
Most production LLM work is a single call.

## Four ways to build one

Two independent questions: who supplies the **harness** (loop + context
management), and who supplies the **deployment** (infra it runs on).

| Approach | You write | Harness / deployment | Tools |
|---|---|---|---|
| Manual loop | the `while stop_reason == "tool_use"` loop | you build, you host | yours only |
| **Tool Runner** (`client.beta.messages.tool_runner`) | tool functions | SDK harness, you host | yours only |
| **Managed Agents** | agent config | Anthropic harness **and** hosted sandbox | hosted bash/files/code + Skills/MCP + yours |
| **Claude Agent SDK** | a prompt + options | Claude Code harness, you host | built-in Read/Write/Edit/Bash/Glob/Grep + MCP + subagents |

**Tool Runner ≠ Claude Agent SDK.** They sound alike and are different packages:

- *Tool Runner* lives in the regular Anthropic API SDK (`anthropic` /
  `@anthropic-ai/sdk`). It is a thin helper over `POST /v1/messages` that loops
  over tools **you** define. No built-in tools, no filesystem, no sandbox.
- *Claude Agent SDK* (`claude-agent-sdk` / `@anthropic-ai/claude-agent-sdk`) is
  Claude Code packaged as a library — built-in tools, context management, hooks,
  subagents, permissions, sessions. You call `query(prompt, options)`.

Both are harness-only: **you host and deploy them**. Only Managed Agents adds
managed deployment.

## Tool Runner, concretely (Python)

```python
from anthropic import Anthropic, beta_tool

@beta_tool
def get_weather(location: str, unit: str = "celsius") -> str:
    """Get current weather for a location.

    Args:
        location: City and state, e.g. San Francisco, CA.
        unit: Either "celsius" or "fahrenheit".
    """
    return f"18°C and raining in {location}"

runner = Anthropic().beta.messages.tool_runner(
    model="claude-opus-5",
    max_tokens=16000,
    tools=[get_weather],
    messages=[{"role": "user", "content": "Weather in Paris?"}],
)
for message in runner:
    print(message)
```

The docstring **is** the tool description and the `Args:` block **is** the
parameter schema. Vague descriptions are the most common cause of an agent
calling the wrong tool.

## Designing the tool surface

- Few, well-described tools beat many overlapping ones.
- Return errors *as tool results* with `is_error: true`, not as exceptions —
  the model can recover from a result, not from a stack trace.
- Return all parallel `tool_result` blocks in **one** user message; splitting
  them trains Claude to stop making parallel calls.
- Human approval does not require a manual loop — gate inside the tool function
  and return "user declined" as the result.

See [`sandbox/03_tool_runner_agent.py`](../sandbox/03_tool_runner_agent.py) for
a runnable version of all of this.
