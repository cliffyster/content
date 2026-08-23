# 10 — CLI reference and built-in commands

> Source: [CLI reference](https://code.claude.com/docs/en/cli-reference) ·
> [Commands](https://code.claude.com/docs/en/commands)

## Invocation forms

| Command | Does |
|---|---|
| `claude` | Interactive session |
| `claude "query"` | Interactive, with an opening prompt |
| `claude -p "query"` | Non-interactive; print and exit |
| `cat f \| claude -p "…"` | Process piped stdin (capped at 10MB) |
| `claude -c` | Continue the most recent conversation |
| `claude -r "<session>" "query"` | Resume by session ID or name |

## Subcommands worth knowing

`claude update`, `claude install [version]`, `claude doctor`,
`claude auth login|logout|status`, `claude mcp …`, `claude plugin …`,
`claude setup-token` (long-lived OAuth token for CI), `claude agents`
(monitor background sessions), `claude attach|logs|stop|rm|respawn <id>`,
`claude import [codex|gemini]`, `claude project purge`,
`claude gateway`, `claude self-hosted-runner`, `claude ultrareview`.

## Flags grouped by what they do

**Model and effort**
`--model`, `--fallback-model`, `--effort <low|medium|high|xhigh|max|ultracode>`,
`--advisor <model>`, `--betas`, `--max-budget-usd`

**Permissions and tools**
`--permission-mode`, `--allowedTools` / `--allowed-tools`,
`--disallowedTools`, `--tools` (restrict built-ins),
`--dangerously-skip-permissions`, `--permission-prompt-tool`,
`--add-dir`

**Context and configuration**
`--settings <file|json>`, `--setting-sources`, `--mcp-config`,
`--strict-mcp-config`, `--agents <json>`, `--agent <name>`,
`--plugin-dir`, `--plugin-url`, `--bare`, `--safe-mode`,
`--system-prompt`, `--system-prompt-file`, `--append-system-prompt`,
`--append-system-prompt-file`, `--append-subagent-system-prompt`

**Programmatic I/O**
`-p` / `--print`, `--output-format <text|json|stream-json>`,
`--input-format <text|stream-json>`, `--json-schema`, `--max-turns`,
`--include-partial-messages`, `--include-hook-events`,
`--forward-subagent-text`, `--replay-user-messages`, `--verbose`

**Sessions and parallelism**
`--session-id <uuid>`, `--fork-session`, `--continue`, `--resume`,
`--name` / `-n`, `--bg` / `--background`, `--worktree` / `-w`, `--tmux`,
`--cloud`, `--environment`, `--teleport`, `--remote-control` / `--rc`

**Session lifecycle hooks**
`--init` (run `Setup` hooks with the init matcher), `--init-only`
(run Setup/SessionStart hooks then exit), `--maintenance`

## `--bare` is the one to remember

`--bare` skips auto-discovery of hooks, skills, commands, subagents, plugins,
MCP servers, auto memory and CLAUDE.md. It is **recommended for scripted and
SDK calls** and is slated to become the default for `-p`.

The reason it matters is a security one. **Without `--bare`, a `-p` session runs
the hooks in a project's `.claude/settings.json` and connects the servers in its
`.mcp.json` — even in a folder you have never trusted — with no workspace-trust
dialog and no per-server approval prompt.** That is the exact combination CI
runs in.

In bare mode Claude Code never reads OAuth credentials or the system keychain,
so set `ANTHROPIC_API_KEY` (Bedrock / Google Cloud / Foundry still read their
own provider credentials).

## Built-in slash commands

**Session**: `/help` `/clear` `/compact` `/autocompact` `/context` `/resume`
`/rewind` `/export` `/copy` `/exit` `/status` `/usage` (`/cost` is an alias)

**Configuration**: `/config` `/model` `/effort` `/fast` `/permissions` `/hooks`
`/agents` `/mcp` `/skills` `/plugin` `/memory` `/output-style` `/statusline`
`/theme` `/color` `/keybindings` `/terminal-setup` `/add-dir` `/cd`

**Work**: `/init` `/plan` `/code-review` (alias `/review`) `/security-review`
`/diff` `/goal` `/loop` (alias `/proactive`) `/deep-research` `/insights`
`/advisor` `/artifacts`

**Parallelism**: `/branch` `/fork` `/background` (`/bg`) `/tasks` `/subtask`
`/batch` `/list-agents` (alias `/peers`)

**Diagnostics**: `/doctor` `/debug` `/bug` `/release-notes` `/login` `/logout`

`/btw` asks a side question without adding it to the conversation — a context
tool, not a convenience.

## Commands under `-p`

User-invoked skills and custom commands **do** work in `-p`: put `/skill-name`
in the prompt string and Claude Code expands it. Terminal-only commands like
`/login` do not. `/model`, `/effort`, `/fast`, `/color` and `/rename` take the
value as an argument (`/model sonnet`), and `/config key=value` changes a
setting from a `-p` run.
