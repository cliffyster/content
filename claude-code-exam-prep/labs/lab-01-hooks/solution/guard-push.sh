#!/usr/bin/env bash
# PreToolUse hook: refuse `git push` when the branch has no upstream.
set -uo pipefail

command=$(jq -r '.tool_input.command // ""' 2>/dev/null) || exit 0

case "$command" in
  *"git push"*) ;;
  *) exit 0 ;;   # not our business -- no decision
esac

# An explicit remote+branch is fine; it does not depend on an upstream.
if printf '%s' "$command" | grep -Eq 'git push[[:space:]]+[^[:space:]-]+[[:space:]]+[^[:space:]-]+'; then
  exit 0
fi

if git rev-parse --abbrev-ref --symbolic-full-name '@{u}' >/dev/null 2>&1; then
  exit 0   # upstream exists -- let the normal permission flow decide
fi

branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "HEAD")
jq -n --arg branch "$branch" '{
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    permissionDecision: "deny",
    permissionDecisionReason: ("Branch \($branch) has no upstream. Push with an explicit target: git push -u origin \($branch)")
  }
}'
exit 0
