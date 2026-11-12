#!/usr/bin/env bash
# 05_01: rtk on the CLI — the REAL tool, not a Python reimplementation.
# A genuine pytest run (311 pass / 1 fail). Raw output is a wall of PASSED lines;
# prepend `rtk test` and only the failure survives. Token counts via Anthropic
# count_tokens (claude-opus-4-8) when ANTHROPIC_API_KEY is set; else line counts.
#
# Setup: source ../.venv/bin/activate  (needs pytest + anthropic + rtk on PATH)
# Run:   ./rtk_demo.sh          (from demos/ch4)
set -euo pipefail
cd "$(dirname "$0")"

RAW=$(mktemp); RTK=$(mktemp)
trap 'rm -f "$RAW" "$RTK"' EXIT

# pytest exits non-zero on failure; that's expected, so don't let set -e abort.
pytest -v          > "$RAW" 2>&1 || true   # what the model would normally swallow
rtk test pytest -v > "$RTK" 2>&1 || true   # same run, rtk-filtered to failures

lines() { wc -l < "$1" | tr -d ' '; }
report() {  # "<label>" <file>
  if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    printf '%-20s: %4s lines  %5s tokens\n' "$1" "$(lines "$2")" "$(python3 ../tok.py "$2")"
  else
    printf '%-20s: %4s lines\n' "$1" "$(lines "$2")"
  fi
}

report "raw  pytest -v"     "$RAW"
report "rtk test pytest -v" "$RTK"
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  r=$(python3 ../tok.py "$RAW"); k=$(python3 ../tok.py "$RTK")
  printf '%-20s: %d%%   (real count_tokens via API)\n' "reduction" "$(( 100 * (r - k) / r ))"
fi

echo
echo "--- what rtk actually hands the model ---"
cat "$RTK"
