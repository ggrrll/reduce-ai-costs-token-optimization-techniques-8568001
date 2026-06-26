#!/usr/bin/env python3
"""05_02: what Serena does — pull ONE symbol by name instead of the whole file.
REAL token counts via Anthropic's count_tokens (claude-opus-4-8); requires
ANTHROPIC_API_KEY. Serena does this across a repo via the Language Server Protocol;
this is the IDEA on one file. Run: python3 symbol_extract.py"""
import os, sys, ast

_MODEL = "claude-opus-4-8"
if not os.environ.get("ANTHROPIC_API_KEY"):
    sys.exit("ERROR: this demo requires a real API key. "
             "Activate the venv and `export ANTHROPIC_API_KEY=sk-...`, then rerun.")
try:
    import anthropic
except ImportError:
    sys.exit("ERROR: `anthropic` not installed. Activate the venv that has it "
             "(e.g. `source ~/.venvs/headroom/bin/activate`).")
_API = anthropic.Anthropic()

def ntok(text):
    return _API.messages.count_tokens(model=_MODEL,
        messages=[{"role": "user", "content": text or " "}]).input_tokens

path, sym = "bigmod.py", "reconcile"
src = open(path).read()
tree = ast.parse(src)
node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == sym)
symbol_src = ast.get_source_segment(src, node)
whole_tok, sym_tok = ntok(src), ntok(symbol_src)
print(f"whole file '{path}'        : {whole_tok:>4} tokens")
print(f"just symbol '{sym}()'      : {sym_tok:>4} tokens")
print(f"reduction                  : {100*(whole_tok-sym_tok)/whole_tok:.0f}%   (real count_tokens via API)")
print(f"\n--- what the agent loads (the one function it asked for) ---\n{symbol_src}")
