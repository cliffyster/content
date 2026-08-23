# Lab 06 — answers

**1. No prompt, and that surprises people.**
Auto-allow works independently of your permission mode (plan mode excepted). A
sandboxable Bash command that writes a file inside the sandbox boundary runs
without prompting **even in Manual mode**, where the Edit and Write tools would
have prompted. The reasoning is that the OS boundary, not the prompt, is now
what protects you — which is exactly why the filesystem policy has to be right
before you turn auto-allow on.

**2. The content-scoped ask rule fires; a bare one does not.**
`Bash(git push *)` is content-scoped and still forces a prompt even for
sandboxed commands. A **bare** `Bash` ask rule (or the equivalent `Bash(*)`) is
*skipped* for commands that run sandboxed — it still applies to commands that
fall back to the regular permission flow. The exception is plan mode, where the
bare rule is not skipped and prompts even for read-only commands.

That is why the solution adds `Bash(dangerouslyDisableSandbox:true)` as an ask
rule: it uses the `Tool(param:value)` syntax to catch every unsandboxed retry,
including in auto mode where you would otherwise not be asked.

**3. Less than it looks.**
By default the built-in proxy does **not terminate or inspect TLS**. It makes
its allow decision from the client-supplied hostname, so code running inside the
sandbox can use domain fronting or similar techniques to reach hosts outside the
allowlist. Allowing a broad domain like `github.com` therefore creates a
plausible data-exfiltration path.

What you *have* guaranteed is that a well-behaved process cannot casually reach
an unlisted host. If your threat model needs more, configure a custom proxy that
terminates TLS and inspects traffic, and install its CA certificate inside the
sandbox.

**4. `Read` is not sandboxed at all.**
The sandbox isolates Bash subprocesses and their children. `Read`, `Edit` and
`Write` go through the permission system directly. The two layers are
complementary, and paths from `sandbox.filesystem` and from `Read`/`Edit`
permission rules are merged into the final sandbox configuration — but the
enforcement mechanisms stay distinct: permission rules are evaluated *before* a
call from the command string, the sandbox is enforced by the OS on the *running
process*.

**Why `allowUnsandboxedCommands: false`.**
This is Strict sandbox mode: the `dangerouslyDisableSandbox` parameter is
ignored entirely, so commands must run sandboxed or appear in
`excludedCommands`. It removes the escape hatch. Use it when the policy is the
security boundary rather than a convenience.

**For an organization**: deploy this in managed settings. Once managed settings
configure `sandbox.filesystem` at all — or list any `credentials.files` entry
with `"mode": "deny"` — only managed settings can set that key, so a developer
cannot quietly relax it.
