# 13 — Plugins and marketplaces

> Source: [Plugins reference](https://code.claude.com/docs/en/plugins-reference) ·
> [Create plugins](https://code.claude.com/docs/en/plugins)

A plugin is the distribution unit for everything else in this syllabus: it can
bundle skills, commands, subagents, hooks, MCP servers and more into one
installable package.

## Structure

```
plugin-root/
├── .claude-plugin/plugin.json    # manifest (optional)
├── skills/<name>/SKILL.md
├── commands/*.md
├── agents/*.md
├── workflows/
├── output-styles/
├── themes/
├── hooks/hooks.json
├── .mcp.json
├── .lsp.json
└── bin/                          # added to PATH
```

## Manifest

Only `name` is required (kebab-case, unique).

- **Metadata**: `displayName`, `version`, `description`, `author`, `homepage`,
  `repository`, `license`, `keywords`, `defaultEnabled`
- **Components**: `skills`, `commands`, `agents`, `workflows`, `hooks`,
  `mcpServers`, `lspServers`, `outputStyles`, plus
  `experimental.themes` / `experimental.monitors`
- **Configuration**: `userConfig` (prompts the user at enable time),
  `channels`, `dependencies`

## Path variables

`${CLAUDE_PLUGIN_ROOT}` — install directory.
`${CLAUDE_PLUGIN_DATA}` — persistent data that **survives plugin updates**.
`${CLAUDE_PROJECT_DIR}` — the project root, as everywhere else.

## CLI

```bash
claude plugin init <name>          # scaffold
claude plugin install <plugin>     # from a marketplace
claude plugin enable|disable <p>
claude plugin update <plugin>
claude plugin list
claude plugin details <plugin>     # components AND token cost
claude plugin validate <path>
claude plugin tag <path>           # create a release git tag
```

`--scope user|project|local`, defaulting to `user`.

`claude plugin details` reporting **token cost** is the detail worth
remembering — every plugin you enable spends context, and this is how you see
how much.

## Skills-directory plugins

A directory of skills under `~/.claude/skills/` or `.claude/skills/` is loaded
with no marketplace and no install step. The simplest possible distribution.

## Where plugin content sits in precedence

Plugins are the **lowest** precedence source for subagents (managed → `--agents`
→ project → user → plugin) and their hooks are one of the seven places hooks can
be declared. A plugin can therefore add capability without ever overriding what
a project or user has set.

## The security shape

Installing a plugin executes its hooks, starts its MCP servers, and puts its
`bin/` on your PATH. `claude plugin validate` checks the manifest, not the
intent. Treat a plugin the way you would treat any dependency you run with your
own credentials.
