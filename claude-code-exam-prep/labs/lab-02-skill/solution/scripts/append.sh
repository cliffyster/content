#!/usr/bin/env bash
# Append a timestamped line to the study journal.
set -euo pipefail

journal="${CLAUDE_PROJECT_DIR:-.}/notes/journal.md"
text="${1:-}"

if [ -z "$text" ]; then
  echo "nothing to record" >&2
  exit 1
fi

mkdir -p "$(dirname "$journal")"
[ -f "$journal" ] || printf '# Study journal\n\n' > "$journal"
printf -- '- **%s** — %s\n' "$(date -u +%Y-%m-%dT%H:%MZ)" "$text" >> "$journal"
echo "recorded: $text"
