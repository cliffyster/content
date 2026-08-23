# Lab 04 — answers

**1. The `--` separates Claude's flags from the server's command line.**
For stdio servers, everything after `--` is passed to the server untouched. So
`claude mcp add --env K=v --transport stdio bank -- python3 server.py --port 80`
runs `python3 server.py --port 80` with `K=v` set, instead of Claude Code trying
to parse `--port` as one of its own options.

**2. Interactive sessions prompt; non-interactive ones cannot.**
Claude Code asks for approval before using project-scoped `.mcp.json` servers —
but `claude -p` runs, Agent SDK sessions and cloud sessions have no way to show
that prompt, so they load them **without asking**. That is the security shape
worth remembering: the place with no human watching is the place with no prompt.

What to do about it: if a server must not load in CI, put it in
`disabledMcpjsonServers`, which blocks it in every mode. To exclude project
settings wholesale, use `--setting-sources` (or the SDK's `settingSources`).
`claude mcp reset-project-choices` clears approvals you have already given.

**3. The allow rule:**

```json
{"permissions": {"allow": [
  "mcp__bank__list_domains",
  "mcp__bank__get_question",
  "mcp__bank__search_bank"
]}}
```

or, since all three are read-only, `mcp__bank__*`.

`mcp__*` does not work because allow rules accept tool-name globs **only after a
literal `mcp__<server>__` prefix**, and the server segment must be glob-free —
the rule has to name a specific server you configured. An unanchored allow glob
like `"*"`, `"B*"` or `"mcp__*"` is skipped with a warning and auto-approves
nothing. (Deny rules are not so constrained, which is the right asymmetry:
broad restrictions are safe, broad grants are not.)
