# Study notes

Twenty-one notes, grouped by exam domain. Read a note, then drill its domain.

## Claude Code — core

| Note | Drill |
|---|---|
| [01 — CLI and configuration](01-cli-and-config.md) | `--domain settings` |
| [02 — Permissions](02-permissions.md) | `--domain permissions` |
| [03 — Skills and slash commands](03-skills-and-commands.md) | `--domain skills` |
| [04 — Hooks](04-hooks.md) | `--domain hooks` |
| [05 — Subagents](05-subagents.md) | `--domain subagents` |
| [06 — MCP](06-mcp.md) | `--domain mcp` |

## Claude Code — reference and operations

| Note | Drill |
|---|---|
| [10 — CLI reference and built-in commands](10-cli-and-commands.md) | `--domain cli` |
| [11 — Memory: CLAUDE.md, rules, auto memory](11-memory-and-instructions.md) | `--domain memory` |
| [12 — Tools reference](12-tools-reference.md) | `--domain tools` |
| [13 — Plugins and marketplaces](13-plugins.md) | `--domain plugins` |
| [14 — Headless mode and CI](14-headless-and-ci.md) | `--domain cli` |
| [16 — The context window](16-context-window.md) | `--domain context` |

## Agents and SDKs

| Note | Drill |
|---|---|
| [07 — Agents and the SDKs](07-agents-and-sdks.md) | `--domain agent-sdk` |
| [15 — The Claude Agent SDK in depth](15-agent-sdk-deep.md) | `--domain agent-sdk` |

## Claude API

| Note | Drill |
|---|---|
| [08 — Claude API mechanics](08-claude-api.md) | `--domain claude-api` |
| [19 — Prompt and context engineering](19-prompt-engineering.md) | `--domain prompt-engineering` |
| [20 — Tool design, server tools, and scaling](20-tools-and-server-tools.md) | `--domain tool-design` |
| [21 — Model selection and platform availability](21-models-and-platforms.md) | `--domain models-and-cost` |

## Security and cost

| Note | Drill |
|---|---|
| [09 — Cost, context and security](09-cost-context-security.md) | `--domain prompt-caching` |
| [17 — The sandboxed Bash tool](17-sandboxing.md) | `--domain sandboxing` |
| [18 — Claude Code's security model](18-security-model.md) | `--domain security` |

---

**Every factual claim here is sourced.** Where a note states a rule, the linked
doc page is the authority — if the two disagree, the doc is right and the note
is stale. Claude Code ships continuously; re-check anything load-bearing before
you sit the exam.

## The rules that catch people out

A short list of the highest-value facts across all 21 notes. If you can produce
these cold, you are in good shape:

1. Permission rules evaluate **deny → ask → allow**; specificity is irrelevant.
2. A hook's `"allow"` loses to a deny rule, but **exit 2 beats an allow rule**.
3. `Bash(ls *)` matches `ls -la` but **not** `lsof`; `Bash(ls*)` matches both.
4. Only **`Read(path)` and `Edit(path)`** are consulted by file permission checks.
5. Settings precedence: managed → `--settings` → local → project → user; **lists merge**.
6. `deny`/`ask` apply before workspace trust; **`allow` waits for it**.
7. A skill's **content persists all session**; its `allowed-tools` grant lasts **one turn**.
8. `$0` is the **first** argument (`$N` is 0-based).
9. Subagents can't `AskUserQuestion` — design the prompt so they never need to.
10. `.mcp.json` prompts interactively but loads **silently under `-p`, the SDK, and cloud**.
11. Without `--bare`, a `-p` run executes the repo's hooks and MCP servers **untrusted**.
12. After compaction, **path-scoped rules are lost**; project-root CLAUDE.md is re-injected.
13. Skill bodies re-inject **truncated from the top** — put what matters first.
14. In the SDK, **auto-approved tools never reach `can_use_tool`**.
15. `allowed_tools` does **not** constrain `bypassPermissions`.
16. Sandbox: a **deny holds inside a wider allow**; a narrow allow re-opens a denied region.
17. Long documents go at the **top**, above the question — up to 30% better.
18. **Prefill is removed** (400); use structured outputs.
19. `effort` lives inside **`output_config`**, not at the top level.
20. Batch results arrive in **any order** — key by `custom_id`.
