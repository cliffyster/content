#!/usr/bin/env bash
# PostToolUse hook -- validate the question bank the moment it is edited.
#
# Demonstrates: catching a mistake at the point of the edit rather than at the
# next test run. Exit 2 is a blocking error, which surfaces the message to
# Claude so it can fix its own broken JSON immediately.
set -uo pipefail

cd "${CLAUDE_PROJECT_DIR:-.}"

# Only care about edits that touched the bank.
file_path=$(jq -r '.tool_input.file_path // ""' 2>/dev/null) || file_path=""
case "$file_path" in
  *quiz/questions/*.json) ;;
  *) exit 0 ;;
esac

if errors=$(python3 -c 'from quiz import store; store.load_questions()' 2>&1); then
  exit 0
fi

echo "Question bank is invalid after that edit:" >&2
echo "$errors" >&2
exit 2
