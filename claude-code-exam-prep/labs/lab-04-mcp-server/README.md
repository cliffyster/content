# Lab 04 — A stdio MCP server

**Goal:** expose this repo's question bank to Claude Code as an MCP server, so
Claude can query it through tools instead of reading JSON files.

```bash
pip install "mcp[cli]"
```

## Build it

Create `bank_server.py` exposing three tools:

| Tool | Returns |
|---|---|
| `list_domains()` | every domain and its question count |
| `get_question(question_id)` | one question, with its explanation and source |
| `search_bank(text, limit)` | questions whose text or explanation matches |

Use the `mcp` Python SDK's `FastMCP`, which turns type-annotated functions into
tools — the docstring becomes the description and the annotations become the
schema, so a vague docstring is a vague tool.

## Wire it up

```bash
claude mcp add --transport stdio bank -- python3 /abs/path/to/bank_server.py
claude mcp get bank      # check it actually connected
```

Then ask Claude: *"use the bank server to find every question about caching"*.
The tools appear as `mcp__bank__list_domains`, `mcp__bank__get_question`,
`mcp__bank__search_bank`.

## Then change the scope

Re-add it with `--scope project` and look at the `.mcp.json` it writes. Commit
that file and you have shared the server with everyone on the project —
including CI.

## Questions

1. Why did the `--` matter in the `claude mcp add` command above?
2. You commit `.mcp.json`. A teammate opens the repo interactively and gets an
   approval prompt. Your CI runs `claude -p` and gets none. Why the difference,
   and what would you do about it?
3. Write an allow rule that auto-approves only the read-only tools from this
   server. Why doesn't `mcp__*` work?
