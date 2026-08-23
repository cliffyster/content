#!/usr/bin/env bash
# A headless review that is safe to run on an untrusted pull request.
set -euo pipefail

: "${ANTHROPIC_API_KEY:?set ANTHROPIC_API_KEY -- bare mode does not read OAuth or the keychain}"

base="${1:-main}"
out=$(mktemp)
trap 'rm -f "$out"' EXIT

# Pipe the diff in rather than letting Claude run git itself: the run then needs
# no Bash permission at all to see the change.
git diff "$base" | claude \
  --bare \
  -p "You are a code reviewer. Report correctness bugs in this diff. For each, give file:line and a one-sentence description. Report nothing else." \
  --permission-mode dontAsk \
  --allowedTools "Read" \
  --max-turns 12 \
  --max-budget-usd 2 \
  --output-format json > "$out"

# A plugin or MCP server that fails to load does NOT fail the run, so gate on it.
if jq -e '.mcp_server_errors // empty | length > 0' "$out" >/dev/null 2>&1; then
  echo "MCP server(s) failed to load:" >&2
  jq -r '.mcp_server_errors[] | "  \(.name): \(.message)"' "$out" >&2
  exit 1
fi
if jq -e '.plugin_errors // empty | length > 0' "$out" >/dev/null 2>&1; then
  echo "Plugin(s) failed to load:" >&2
  jq -r '.plugin_errors[] | "  \(.plugin): \(.message)"' "$out" >&2
  exit 1
fi

jq -r '.result' "$out"
printf '\ncost: $%s\n' "$(jq -r '.total_cost_usd // "unknown"' "$out")" >&2
