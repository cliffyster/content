#!/usr/bin/env bash
# Lift this project out into its own standalone git repository.
#
# It currently lives as a subdirectory. This copies it somewhere else, starts a
# fresh history, and (optionally) points it at a remote you have already created
# on GitHub.
#
#   ./scripts/extract-to-new-repo.sh ~/code/claude-code-exam-prep
#   ./scripts/extract-to-new-repo.sh ~/code/exam-prep git@github.com:you/exam-prep.git
set -euo pipefail

target="${1:-}"
remote="${2:-}"

if [ -z "$target" ]; then
  echo "usage: $0 <target-directory> [git-remote-url]" >&2
  exit 1
fi

source_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ -e "$target" ]; then
  echo "refusing to overwrite existing path: $target" >&2
  exit 1
fi

mkdir -p "$target"
# Copy everything including dotfiles, but never the learner's progress.
tar -cf - -C "$source_dir" \
    --exclude='./.git' \
    --exclude='.quiz-progress.json' \
    --exclude='__pycache__' \
    --exclude='.venv' \
    . | tar -xf - -C "$target"

cd "$target"
# Pin the branch name so the push instructions below are always right;
# -b needs git 2.28+, so fall back for older versions.
git init -q -b main 2>/dev/null || { git init -q && git symbolic-ref HEAD refs/heads/main; }
git add -A
git commit -qm "Initial commit: Claude Certified Developer exam prep

Study notes, a stdlib-only spaced-repetition drill engine over a sourced
question bank, five hands-on labs, a working .claude/ configuration, and
runnable Anthropic SDK experiments."

if [ -n "$remote" ]; then
  git remote add origin "$remote"
  echo "Remote set. Push with:  git -C $target push -u origin main"
else
  echo "No remote given. Create an empty repo on GitHub, then:"
  echo "  git -C $target remote add origin <url>"
  echo "  git -C $target push -u origin main"
fi

echo
echo "Extracted to $target"
python3 -m unittest discover -s tests -q 2>&1 | tail -3
