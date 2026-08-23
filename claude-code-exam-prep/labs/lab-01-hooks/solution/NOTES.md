# Lab 01 — answers

**1. Deny rule vs. hook `"allow"` — the deny rule wins.**
Hook decisions do not bypass permission rules. Claude Code evaluates deny and
ask rules regardless of what a `PreToolUse` hook returns, preserving deny-first
precedence — including deny rules from managed settings.

**2. Exit 2 vs. a deny decision.**
Both block. Exit 2 is a blocking *error*: it stops the call before permission
rules are evaluated at all, which is what lets a hook override an `allow` rule.
A `deny` decision goes through the structured path and carries a
`permissionDecisionReason` that Claude can read and act on. Prefer the
structured form when you want Claude to adapt; use exit 2 for hard stops.

**3. Exit 1 — the tool call still runs.**
Only 0 (success) and 2 (blocking error) are special. Every other exit code is a
*non-blocking* error: it is reported, and the action proceeds. This is the
failure mode to watch for — a hook with a typo silently stops protecting you.

**Why the solution checks for an explicit remote and branch first:** `git push
origin my-branch` does not need an upstream, so denying it would be wrong. A
guard that fires on cases it shouldn't gets disabled, and then guards nothing.
