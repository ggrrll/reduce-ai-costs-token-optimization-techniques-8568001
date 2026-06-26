#!/usr/bin/env python3
"""Print the REAL input-token count of a file via Anthropic count_tokens (claude-opus-4-8).
Requires ANTHROPIC_API_KEY. Used by the memory-hygiene demo (04_03). Usage: python3 tok.py <file>"""
import os, sys

if not os.environ.get("ANTHROPIC_API_KEY"):
    sys.exit("ERROR: this demo requires a real API key. "
             "Activate the venv and `export ANTHROPIC_API_KEY=sk-...`, then rerun.")
try:
    import anthropic
except ImportError:
    sys.exit("ERROR: `anthropic` not installed. Activate the venv that has it "
             "(e.g. `source ~/.venvs/headroom/bin/activate`).")

text = open(sys.argv[1]).read() or " "
n = anthropic.Anthropic().messages.count_tokens(
    model="claude-opus-4-8", messages=[{"role": "user", "content": text}]).input_tokens
print(n)
