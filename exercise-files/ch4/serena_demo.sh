#!/usr/bin/env bash
# Serena's idea on the CLI: retrieve ONE symbol by name instead of reading the whole file.
# Uses Python's built-in `ast` module on a real well-known file (requests/sessions.py).
# Serena does this repo-wide over MCP/LSP; this shows the principle and the token numbers.
#
# Setup: source ~/.venvs/headroom/bin/activate
# Run:   ./serena_demo.sh          (from demos/ch4)
set -euo pipefail
cd "$(dirname "$0")"

SESSIONS=$(python3 -c "import requests; import os; print(os.path.dirname(requests.__file__))")/sessions.py
SYM_FILE=$(mktemp); trap 'rm -f "$SYM_FILE"' EXIT

# find_symbol: pull ONLY Session.send — no whole-file read
python3 - <<'EOF' "$SESSIONS" "$SYM_FILE"
import ast, sys
src = open(sys.argv[1]).read()
tree = ast.parse(src)
for cls in ast.walk(tree):
    if isinstance(cls, ast.ClassDef) and cls.name == "Session":
        for node in cls.body:
            if isinstance(node, ast.FunctionDef) and node.name == "send":
                open(sys.argv[2], "w").write(ast.get_source_segment(src, node))
                sys.exit(0)
sys.exit(1)
EOF

report() {  # "<label>" <file>
  if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    printf '%-30s: %4s lines  %6s tokens\n' "$1" "$(wc -l < "$2" | tr -d ' ')" "$(python3 ../tok.py "$2")"
  else
    printf '%-30s: %4s lines\n' "$1" "$(wc -l < "$2" | tr -d ' ')"
  fi
}

echo "=== symbol map of sessions.py (no body loaded) ==="
python3 - "$SESSIONS" <<'EOF'
import ast, sys
src = open(sys.argv[1]).read()
tree = ast.parse(src)
for cls in ast.walk(tree):
    if isinstance(cls, ast.ClassDef) and cls.name == "Session":
        names = [n.name for n in cls.body if isinstance(n, ast.FunctionDef)]
        print(", ".join(names))
EOF

echo
report "whole file  sessions.py" "$SESSIONS"
report "just symbol Session.send" "$SYM_FILE"
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  w=$(python3 ../tok.py "$SESSIONS"); s=$(python3 ../tok.py "$SYM_FILE")
  printf '%-30s: %d%%   (real count_tokens via API)\n' "reduction" "$(( 100 * (w - s) / w ))"
fi

echo
echo "--- what the agent loads (the one method it asked for) ---"
cat "$SYM_FILE"
