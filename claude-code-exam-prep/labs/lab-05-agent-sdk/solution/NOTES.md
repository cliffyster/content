# Lab 05 — answers

**1. All three `tool_result` blocks go back in a SINGLE user message.**
Splitting them across several messages silently trains Claude to stop making
parallel tool calls — it does not error, it just quietly gets slower and more
sequential over the conversation. A tool that failed still gets a
`tool_result`, with `is_error: true`; dropping it leaves an unanswered
`tool_use` and the API rejects the next request.

**2. `end_turn` should end it.**
The one that looks like an ending but is not is **`pause_turn`** — a server-side
tool hit an iteration limit and the turn can be resumed by sending the paused
assistant content back. Treating `pause_turn` as terminal gives you a silently
truncated answer with no error and no warning. (The Python Tool Runner does not
auto-resume `pause_turn`; it exits when no client tool ran, so handle it by
mirroring the history and restarting the runner, or use a manual loop.)

Also worth knowing: `refusal` arrives as **HTTP 200**, not an exception, and is
the only `stop_reason` for which `stop_details` is populated.

**3. No — approval does not require a manual loop.**
Gate *inside the tool function* and return "user declined" as the tool result.
That keeps the model in the loop: it sees the refusal as data and can propose an
alternative, which a raised exception would not let it do. You can also inspect
pending `tool_use` blocks inside the `for message in runner:` body.

Reach for a manual loop only when you need something the runner does not expose:
a custom transport, request shapes the SDK cannot build, or avoiding the beta
dependency.

**On the deliberate break.**
An uncaught exception in a tool aborts the run — the model never learns the tool
failed, so it cannot adapt. Returning `"error: no progress recorded yet, tell
the user to run a drill first"` turns a crash into a conversation. This is the
single highest-leverage habit in agent tool design.
