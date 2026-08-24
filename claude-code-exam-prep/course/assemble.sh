#!/usr/bin/env bash
# Rebuild the published course page from its sources.
#
#   ./assemble.sh && open course.html
#
# Lesson content lives in build_part*.py as readable Python; those emit
# course.json, which this inlines into the shell.
set -euo pipefail
cd "$(dirname "$0")"

python3 build_part1.py
python3 build_part2.py
python3 build_part3.py
python3 - <<'PY'
import json, pathlib
mods = []
for f in ("part1.json", "part2.json", "part3.json"):
    mods.extend(json.loads(pathlib.Path(f).read_text()))
pathlib.Path("course.json").write_text(json.dumps(mods, separators=(",", ":")))
lessons = sum(len(m["lessons"]) for m in mods)
checks = sum(len(l["checks"]) for m in mods for l in m["lessons"])
print(f"{len(mods)} modules, {lessons} lessons, {checks} checks")
PY

{
  cat shell-viewport.html
  cat shell-head.html
  cat shell-body.html
  printf '<script>\nconst COURSE = '
  cat course.json
  printf ';\n</script>\n'
  cat shell-script.html
} > course.html

rm -f part1.json part2.json part3.json
echo "wrote course.html ($(wc -c < course.html) bytes)"
