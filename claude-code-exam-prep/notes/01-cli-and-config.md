# 01 — CLI and configuration

> Source: [Settings](https://code.claude.com/docs/en/settings) ·
> [CLI reference](https://code.claude.com/docs/en/cli-reference)

## Where settings live, and who wins

Five sources, highest precedence first:

| # | Source | Set by |
|---|---|---|
| 1 | Managed settings (`managed-settings.json`, MDM, claude.ai console) | Your organization |
| 2 | `claude --settings` | You, this session |
| 3 | `.claude/settings.local.json` | You, this project |
| 4 | `.claude/settings.json` | Everyone in the project |
| 5 | `~/.claude/settings.json` | You, every project |

Nothing overrides managed settings — not even a `--settings` flag. A managed
`model` only sets the *starting* model; the key that actually constrains
`/model` and `--model` is `availableModels`.

**Lists merge, scalars override.** Set `permissions.allow` in three files and
you get the union of all three. This is why "I removed that allow rule and it
still applies" usually means another scope still declares it.

## The trust gate

A repository can ship `.claude/settings.json`, and cloning it must not silently
widen your access. So:

- `deny` and `ask` rules apply **immediately**.
- `permissions.allow`, `permissions.additionalDirectories`,
  `extraKnownMarketplaces` and most `env` values apply **only after you trust
  the folder**.

Restrictions bind at once; grants wait for a human. Learn this asymmetry — it is
the answer to a whole family of exam questions.

## Strict JSON

Settings files are strict JSON. A `//` comment or a trailing comma is a syntax
error and produces a Settings Error at the next start. There is no JSON5 mode.

```json
{
  "permissions": {
    "allow": ["Bash(npm run test:*)", "Bash(npm run lint)"],
    "deny": ["Read(./.env)", "Read(./secrets/**)"]
  },
  "env": { "NODE_ENV": "test" },
  "model": "claude-opus-5"
}
```

## Instruction files

`CLAUDE.md` is loaded into context at session start — it is for **facts**:
project layout, conventions, commands that work. When a section of it grows
into a *procedure*, move it to a skill. A skill's body loads only when used, so
long reference material costs nothing until it is needed; a CLAUDE.md section
costs its tokens on every single turn.

## Things worth memorizing

- `.claude/settings.local.json` is where "Yes, and don't ask again" writes its
  allow rule. It is gitignored by convention and is read from the **repository
  root** even if you started Claude in a subdirectory or worktree.
- `disableAllHooks` set in *project* settings outranks your user settings, so
  turning hooks off for one run means `claude --settings '{"disableAllHooks": true}'`.
- `~/.claude.json` is separate from settings. If it corrupts, Claude Code backs
  it up to `~/.claude/backups/` and offers to reset.
