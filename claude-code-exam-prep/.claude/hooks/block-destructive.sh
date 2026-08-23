#!/usr/bin/env bash
# PreToolUse hook -- refuse recursive deletes.
#
# Demonstrates the structured deny: exit 0 with a permissionDecision, which
# gives Claude a reason it can act on. (Exiting 2 would also block, but with a
# bare error instead of an explanation.)
#
# Note the ordering rule this relies on: a hook decision never overrides a deny
# or ask RULE -- but a hook CAN block something an allow rule would have let
# through, which is what makes "allow Bash, block these" possible.
set -uo pipefail

command=$(jq -r '.tool_input.command // ""' 2>/dev/null) || command=""

if printf '%s' "$command" | grep -Eq '(^|[;&|[:space:]])rm[[:space:]]+(-[[:alnum:]]*[rR][[:alnum:]]*[[:space:]]+)'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Recursive delete blocked by .claude/hooks/block-destructive.sh. Delete specific paths instead, or remove the hook if you really mean it."
    }
  }'
  exit 0
fi

exit 0   # no decision -- the normal permission flow applies
