# Lab 01 — A hook that blocks

**Goal:** stop Claude from running `git push` without a matching upstream check,
using a `PreToolUse` hook.

## Why a hook and not a rule

A permission rule matches a *pattern*. A hook runs *code*, so it can inspect
the whole command, read the repo state, and give a reason. This is the
difference the exam probes: rules are declarative and cheap; hooks are
imperative and can decide.

## Build it

1. Create `.claude/hooks/guard-push.sh`. It receives the hook payload as JSON
   on **stdin**. Pull the command out:

   ```bash
   command=$(jq -r '.tool_input.command // ""')
   ```

2. If the command is a `git push` and the current branch has no upstream
   (`git rev-parse --abbrev-ref --symbolic-full-name @{u}` fails), emit a deny
   decision on **stdout** and exit **0**:

   ```json
   {"hookSpecificOutput": {"hookEventName": "PreToolUse",
     "permissionDecision": "deny", "permissionDecisionReason": "..."}}
   ```

3. Otherwise exit 0 with no output — that means "no decision", and the normal
   permission flow applies. Do **not** emit `"allow"` unless you mean to
   pre-approve it.

4. Register it in `.claude/settings.json` under `PreToolUse` with
   `"matcher": "Bash"` and `"if": "Bash(git push *)"`.

5. `chmod +x` the script.

## Check yourself

```bash
echo '{"tool_input":{"command":"git push"}}' | .claude/hooks/guard-push.sh
echo '{"tool_input":{"command":"git status"}}' | .claude/hooks/guard-push.sh
```

The first should print a deny decision; the second should print nothing.

## Questions to answer before moving on

1. You emit `"permissionDecision": "allow"`, but `.claude/settings.json` has a
   `deny` rule matching the same command. Which wins, and why?
2. What is the difference between exiting 2 and emitting a `deny` decision?
3. Your script has a typo and exits 1. Does the tool call still run?

Answers are in [notes/04-hooks.md](../../notes/04-hooks.md) — and questions 1
and 3 are in the bank: `python -m quiz drill --domain hooks`.
