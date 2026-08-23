# 06 — MCP

> Source: [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp)

MCP is an open standard for AI–tool integrations. Connect a server when you
find yourself copying data into chat from another system.

## Four ways to add a server

```bash
# remote HTTP
claude mcp add --transport http notion https://mcp.notion.com/mcp

# remote SSE (legacy endpoints)
claude mcp add --transport sse asana https://mcp.asana.com/sse

# local stdio — note the `--`
claude mcp add --env API_KEY=xxx --transport stdio airtable -- npx -y airtable-mcp

# WebSocket — .mcp.json or add-json only; --transport does NOT accept ws
claude mcp add-json events '{"type":"ws","url":"wss://example.com/mcp"}'
```

The bare `--` separates Claude's own flags from the server's command line.
Everything after it is passed to the server untouched.

## Config shape

```json
{
  "mcpServers": {
    "shared-server": { "type": "http", "url": "https://example.com/mcp" }
  }
}
```

`type` accepts **`streamable-http`** as an alias for `http`, because that is
what the MCP spec calls the transport — so a config copied from a server's own
docs works unedited.

For `claude mcp add-json`, pass the object *inside* `mcpServers`, not the
wrapper.

## Scopes

| Scope | Stored in | Shared? |
|---|---|---|
| `local` (default) | your user config, per project | no |
| `project` | `.mcp.json` at the project root | yes — commit it |
| `user` | your user config, all projects | no |

## The approval asymmetry

Project-scoped servers from `.mcp.json` prompt for approval in **interactive**
sessions. `claude -p`, Agent SDK sessions and cloud sessions cannot show that
prompt, so they load them **without asking**.

If you need a server excluded regardless of mode, that is
`disabledMcpjsonServers` — or drop project settings entirely with
`--setting-sources` (SDK: `settingSources`). Clear past approvals with
`claude mcp reset-project-choices`.

This is a real supply-chain consideration: a `.mcp.json` in a repo you clone is
a request to run someone else's code, and CI is exactly where nobody sees the
prompt.

## Naming

`mcp__<server>__<tool>` — e.g. `mcp__github__get_issue`. Permission rules and
hook matchers both use this form.

## Managing

```bash
claude mcp list            # what is configured
claude mcp get notion      # status of one server, incl. connection state
claude mcp remove notion
```

MCP servers can also expose **resources** (referenced with `@`) and **prompts**
(surfaced as `/mcp__server__prompt` commands), not just tools. With many
servers connected, tool search / `defer_loading` keeps the tool list from
crowding out the context window.
