#!/usr/bin/env bash
# Serena's idea, with a REAL non-MCP CLI tool: ast-grep (`sg`). Instead of reading a
# whole module to touch one function, the agent retrieves at the SYMBOL level — and can
# map symbols / find callers without ever slurping the file. Cuts reads to what matters.
#
# ast-grep is AST-level (LSP-grade structure); Serena does this repo-wide over MCP.
# Setup: source ~/.venvs/headroom/bin/activate  (ast-grep + anthropic installed there)
# Run:   ./symbol_demo.sh          (from demos/ch4)
set -euo pipefail
cd "$(dirname "$0")"

FILE=bigmod.py
SYM=reconcile

SYMSRC=$(mktemp); trap 'rm -f "$SYMSRC"' EXIT
# find_symbol: pull ONLY the requested function, by structure not line guessing.
ast-grep run --lang python --pattern "def ${SYM}(\$\$\$):
    \$\$\$" "$FILE" > "$SYMSRC"

echo "=== the symbol map (no file body read — like find_symbol) ==="
ast-grep run --lang python --pattern 'def $NAME($$$): $$$' "$FILE" --json=compact \
  | python3 -c "import sys,json;print(', '.join(m['metaVariables']['single']['NAME']['text'] for m in json.load(sys.stdin)))"

echo
echo "=== who calls ${SYM}()? (like find_referencing_symbols) ==="
ast-grep run --lang python --pattern "${SYM}(\$\$\$)" "$FILE" | grep -E ':[0-9]+:' || true

echo
report() {  # "<label>" <file>
  if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    printf '%-26s: %5s tokens\n' "$1" "$(python3 ../tok.py "$2")"
  else
    printf '%-26s: %4s lines\n' "$1" "$(wc -l < "$2" | tr -d ' ')"
  fi
}
report "whole file '$FILE'"   "$FILE"
report "just symbol '${SYM}()'" "$SYMSRC"
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  w=$(python3 ../tok.py "$FILE"); s=$(python3 ../tok.py "$SYMSRC")
  printf '%-26s: %d%%   (real count_tokens via API)\n' "reduction" "$(( 100 * (w - s) / w ))"
fi

echo
echo "--- what the agent loads (the one function it asked for) ---"
cat "$SYMSRC"
