# Lab 02 — A skill with arguments and a scoped grant

**Goal:** build `/note`, a skill that appends a timestamped study note to
`notes/journal.md` — without triggering a permission prompt, and without
granting Claude blanket Bash access.

## Build it

Create `.claude/skills/note/SKILL.md`.

Requirements:

1. **You** invoke it, never Claude — it has a side effect.
2. It takes free text: `/note deny beats allow, always`.
3. It runs a bundled script at `.claude/skills/note/scripts/append.sh` with no
   permission prompt.
4. The grant must cover **only** that script — not `Bash(*)`.

The mechanism for (3) and (4) is `${CLAUDE_SKILL_DIR}`, which Claude Code
substitutes in exactly two places: the markdown body, and the Bash rules in
`allowed-tools`. Use it in both so the rule matches the command the body tells
Claude to run.

## Check yourself

- Invoke `/note something` and confirm no prompt appears.
- Send another message, then check: is the grant still active? (It should not
  be — `allowed-tools` clears at your next message, even though the skill's
  *content* stays in context all session.)
- Ask Claude to write a study note without using `/note`. It should not be able
  to invoke the skill itself.

## Questions

1. You invoke `/note` with arguments but forget `$ARGUMENTS` in the body. Where
   does your text go?
2. `$0` and `$1` — which is the first argument?
3. Your skill says "first, read the journal". On turn 9 Claude reads the journal
   again unprompted. Why?
