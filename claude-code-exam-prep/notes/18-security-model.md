# 18 — Claude Code's security model

> Source: [Security](https://code.claude.com/docs/en/security) ·
> [Permissions](https://code.claude.com/docs/en/permissions)

## The architecture

In Manual mode Claude Code starts **read-only** and asks before editing files or
running commands that modify the system. A built-in set of read-only commands
(`ls`, `cat`, `git status`) runs without asking. In auto mode a separate
classifier model reviews actions instead of you — but **your explicit ask and
deny rules still apply**, and an organization can turn auto mode off entirely.

## Built-in protections

- **Working directory boundary.** In Manual mode Claude Code writes only to the
  folder it started in and below. It also asks before *reading* outside that
  boundary with Read, Grep and Glob. **In auto mode it reads them without
  asking.** Widen deliberately with `additionalDirectories`.
- **Sandboxed Bash** — OS-level filesystem and network isolation (note 17).
- **Accept Edits** auto-approves edits plus `mkdir`, `touch`, `rm`, `mv`, `cp`,
  `sed` inside the working directory. Other commands and out-of-scope paths
  still prompt.
- **Prompt fatigue mitigation** — allowlisting per user, codebase or org.

## Prompt injection: the safeguards

- **Permission system** — sensitive operations need approval in Manual mode.
- **Context-aware analysis** — harmful instructions detected across the full
  request.
- **Input sanitization** against command injection.
- **Network command approval** — `curl` and `wget` are **not** auto-approved by
  default. Block them entirely with `permissions.deny`.
- **Isolated context windows** — WebFetch runs in a *separate* context window
  specifically so fetched content can't inject into the main conversation.
- **Trust verification** — first run in a codebase and each new MCP server
  require it. **Disabled when running non-interactively with `-p`.**
- **Command injection detection** — suspicious Bash requires manual approval
  even if previously allowlisted.
- **Fail-closed matching** — an unmatched command requires approval.
- **Natural language descriptions** for complex Bash commands.
- **Secure credential storage** — macOS Keychain where available; file
  permissions on Windows and Linux.

Two footnotes that make good exam questions: trust verification is off under
`-p`, and starting Claude Code **directly in your home directory** holds trust
for the session only, never writes it to disk, and re-prompts every launch —
with no setting to persist it. Start from a project subdirectory instead.

## Working with untrusted content

1. Review suggested commands before approving.
2. **Don't pipe untrusted content directly to Claude.**
3. Verify proposed changes to critical files.
4. Use VMs for scripts that touch external web services.
5. Report suspicious behavior with `/feedback`.

The honest framing from the docs: these protections *significantly reduce* risk;
no system is immune.

## MCP security

The allowed-server list is checked into source control as part of settings.
Anthropic reviews connectors against listing criteria before adding them to the
Directory but **does not security-audit or manage any MCP server**. Write your
own or use servers from providers you trust.

## Cloud execution

Anthropic-hosted cloud sessions: isolated per-session VMs, network access
limited by default and configurable, credentials handled through a secure proxy
using a scoped credential that is translated to your real GitHub token, **git
push restricted to the current working branch**, audit logging, and automatic VM
reclamation.

Self-hosted environments run on your infrastructure — isolation, egress and git
credentials become your responsibility.

**Remote Control is different**: the web interface connects to Claude Code
running on *your local machine*. All execution and file access stays local; the
transcript is stored on Anthropic servers while connected in order to sync
across devices. No cloud VM, no sandboxing. It uses multiple short-lived,
narrowly scoped credentials so one compromise has a small blast radius.

## Team practices

- Managed settings to enforce standards (and note from 17: some sandbox keys
  become managed-only once managed settings touch them).
- Share approved permission configurations through version control.
- Monitor with OpenTelemetry metrics.
- **Audit or block settings changes mid-session with `ConfigChange` hooks.**
- Audit periodically with `/permissions`.
- `/security-review` for an on-demand pass over the current branch.

## Reporting

Don't disclose publicly; report through Anthropic's HackerOne program with
reproduction steps.
