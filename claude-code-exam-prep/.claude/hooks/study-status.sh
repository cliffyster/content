#!/usr/bin/env bash
# SessionStart hook -- inject the learner's current study state into context.
#
# Demonstrates: a hook that ADDS context rather than blocking anything, using
# the universal `additionalContext` field. Exits 0 with JSON on stdout.
set -euo pipefail

cd "${CLAUDE_PROJECT_DIR:-.}"

# Never let a broken hook break the session: any failure below degrades to a
# silent no-op, because a non-zero exit that isn't 2 is a non-blocking error
# but still prints noise.
status=$(python3 -m quiz stats 2>/dev/null) || exit 0

python3 - "$status" <<'PY'
import json
import sys

status = sys.argv[1]
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": (
            "Current exam-prep progress for this learner:\n\n"
            + status
            + "\n\nWhen they ask what to study, ground your answer in these "
              "numbers rather than guessing."
        ),
    }
}))
PY
