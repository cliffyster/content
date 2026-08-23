# Lab 05 — An agent loop with the Tool Runner

**Goal:** build a study agent that reads the learner's progress, picks the
weakest domain, and drills them on it — using `client.beta.messages.tool_runner`
rather than a hand-written loop.

```bash
pip install anthropic
```

## First, the disambiguation the exam tests

| | Tool Runner | Claude Agent SDK |
|---|---|---|
| Package | `anthropic` (the API SDK) | `claude-agent-sdk` |
| Reached via | `client.beta.messages.tool_runner` | `query(prompt, options)` |
| Built-in tools | **none** — you define every tool | Read/Write/Edit/Bash/Glob/Grep/… |
| Sandbox | none | none (you host) |

Both supply a harness and leave deployment to you. Only **Managed Agents**
supplies both a harness and hosted infrastructure. Getting these three straight
is worth more marks than any amount of syntax.

## Build it

1. Define tools with `@beta_tool`. The **docstring becomes the tool
   description** and the `Args:` block becomes the parameter schema — so write
   them for a reader who cannot see your code.

   ```python
   @beta_tool
   def weakest_domain() -> str:
       """Return the exam domain with the worst accuracy in saved progress."""
   ```

2. Pass them to the runner and iterate:

   ```python
   runner = client.beta.messages.tool_runner(
       model="claude-opus-5", max_tokens=16000,
       tools=[...], messages=[{"role": "user", "content": prompt}],
   )
   for message in runner:
       ...
   ```

3. Give it a system prompt that forbids inventing exam content. An agent with a
   `get_questions` tool that answers from memory instead is worse than no agent.

A working version is in [`sandbox/03_tool_runner_agent.py`](../../sandbox/03_tool_runner_agent.py).

## Then break it deliberately

Make one tool raise an exception. Watch what reaches the model. Then change it
to return an error *string* instead. The model can recover from a tool result;
it cannot recover from a traceback that never reaches it.

## Questions

1. Claude returns three `tool_use` blocks in one message. How many user messages
   do the results go back in, and what breaks if you get it wrong?
2. Your loop never terminates. Which `stop_reason` should have ended it, and
   which one looks like an ending but is not?
3. You want a human to approve one tool before it runs. Do you need to abandon
   the runner and write a manual loop?
