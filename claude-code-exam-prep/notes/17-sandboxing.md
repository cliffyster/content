# 17 — The sandboxed Bash tool

> Source: [Configure the sandboxed Bash tool](https://code.claude.com/docs/en/sandboxing) ·
> [Sandbox environments](https://code.claude.com/docs/en/sandbox-environments)

The sandbox lets Claude run most shell commands **without asking**, because the
operating system — not the permission system — enforces what those commands can
touch.

## Sandboxing is not a permission mode

This distinction is the heart of the topic:

| | Controls | Enforced |
|---|---|---|
| **Permission rules / modes** | *whether a tool call runs*, and whether you're asked | Before the command runs, from the command string (plus a classifier in auto mode) |
| **Sandbox** | *what a Bash command can access* once it runs | By the OS, on the running process |

So the sandbox holds **regardless of what the model chose to run, and even if an
allowed command does more than its name suggests.** Permission rules apply to
every tool; the sandbox applies only to Bash and its child processes. Read, Edit
and Write use the permission system directly and never go through the sandbox.

Paths from `sandbox.filesystem` settings and from `Read`/`Edit` permission rules
are **merged** into the final sandbox configuration.

## Platforms

macOS uses the built-in **Seatbelt** framework — nothing to install. Linux and
WSL2 use **bubblewrap**. WSL1 and native Windows are not supported. Configure
interactively with `/sandbox`.

## Two modes

**Auto-allow** — a sandboxable command runs sandboxed and is auto-approved.
Commands that can't be sandboxed fall back to the normal permission flow.

Even in auto-allow, these still apply:
- explicit **deny** rules
- `rm`/`rmdir` targeting a **critical path**
- content-scoped **ask** rules like `Bash(git push *)`
- a bare `Bash` ask rule is *skipped* for sandboxed commands — but **not in plan
  mode**, where it prompts even for read-only ones

Auto-allow works independently of your permission mode, **with plan mode as the
exception**. The consequence to remember: with auto-allow on, Bash commands that
modify files inside the sandbox boundary run without prompting **even in Manual
mode**, where the file-edit tools would have prompted.

**Regular permissions** — every Bash command goes through the normal flow even
when sandboxed. More control, more approvals.

## The unsandboxed retry escape hatch

When a command fails because the sandbox blocked it, Claude Code appends the
violation details to the output so Claude can see which path or host was
blocked, and Claude may retry with `dangerouslyDisableSandbox`. That retry runs
outside the sandbox and therefore goes through the normal permission flow.

- To be prompted on every retry even in auto mode, add an ask rule for
  `Bash(dangerouslyDisableSandbox:true)` — a nice example of the
  `Tool(param:value)` syntax from note 02.
- To remove the hatch entirely, set `"allowUnsandboxedCommands": false`
  (**Strict sandbox mode**); commands must then run sandboxed or be listed in
  `excludedCommands`.

## Configuration

```json
{
  "sandbox": {
    "enabled": true,
    "filesystem": {
      "denyRead": ["~/"],
      "allowRead": ["~/projects"],
      "allowWrite": ["/tmp/build"],
      "denyWrite": ["~/.ssh"]
    },
    "network": { "allowedDomains": ["*.github.com", "registry.npmjs.org"] },
    "credentials": {
      "files": [{ "path": "~/.aws/credentials", "mode": "deny" }],
      "env":   [{ "name": "GITHUB_TOKEN", "mode": "deny" }]
    }
  }
}
```

**Allow/deny interaction** — worth memorizing, because it is the opposite of the
permission-rule answer:

| Combination | Result |
|---|---|
| `denyRead: ["~/"]` + `allowRead: ["~/projects"]` | The narrower allow **re-opens** that part of the denied region |
| `allowRead: ["~/"]` + `denyRead: ["~/.env"]` | The deny **holds inside** the wider allow |
| `allowRead: ["~/"]` + `denyRead: ["~/**/.env"]` | A wildcard deny holds the same way |

So a broad allow can't silently re-expose a secret, and a narrow allow can
re-open a denied region. The session temp directory is writable by default, and
`$TMPDIR` points there for sandboxed commands.

## Known limitations — the security-aware answers

- **No TLS inspection by default.** The proxy decides from the client-supplied
  hostname, so code inside the sandbox can potentially use domain fronting to
  reach hosts outside the allowlist. Allowing a broad domain like `github.com`
  creates an exfiltration path. For stronger guarantees, run a custom
  TLS-terminating proxy and install its CA inside the sandbox.
- **Unix sockets escalate.** Allowing `/var/run/docker.sock` effectively grants
  the host.
- **Filesystem escalation.** Write access to `$PATH` directories, system config,
  or `.bashrc`/`.zshrc` becomes code execution in another security context.
- **`enableWeakerNestedSandbox`** lets Linux isolation work inside Docker
  without privileged namespaces, and considerably weakens it.
- **`allowAppleEvents`** (macOS) removes code-execution isolation — sandboxed
  commands can launch other apps unsandboxed. Honored only from user, managed
  or CLI settings; **project settings cannot enable it.**

## For organizations

Enforce with managed settings. When managed settings configure
`sandbox.filesystem` at all — or list any `credentials.files` entry with
`"mode": "deny"` — **only managed settings can set that key**, so a developer
can't relax the deployment locally.
