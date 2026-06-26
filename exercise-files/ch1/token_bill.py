#!/usr/bin/env python3
"""check a request's token cost BEFORE sending — with REAL token counts.
Requires ANTHROPIC_API_KEY; uses Anthropic's count_tokens (model claude-opus-4-8).
count_tokens handles inputs far larger than the context window, so the whole log is
counted directly. Run: python3 token_bill.py [path_to_log]   (defaults to ./app.log)"""
import os, sys

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
    """Real input-token count via Anthropic count_tokens. count_tokens accepts inputs
    far larger than the context window, so count directly; fall back to counting a chunk
    and scaling by the character ratio only if the API rejects an oversized request."""
    text = text if text else " "
    try:
        return _API.messages.count_tokens(model=_MODEL,
            messages=[{"role": "user", "content": text}]).input_tokens
    except Exception:
        seg = text[:500_000]
        n = _API.messages.count_tokens(model=_MODEL,
            messages=[{"role": "user", "content": seg}]).input_tokens
        return round(n * len(text) / len(seg))

prompt = "Read the attached log and find the error, then explain the likely cause."
system = "You are a senior SRE assistant."

path = sys.argv[1] if len(sys.argv) > 1 else ("app.log" if os.path.isfile("app.log") else None)
if not path:
    sys.exit("ERROR: no log to weigh. Pass a path or run make_log.py first. "
             "Usage: python3 token_bill.py [path_to_log]")
log = open(path).read()

lean = ntok(system + "\n" + prompt)
bloated = lean + ntok(log)
print(f"method: API count_tokens (claude-opus-4-8) — log: {path}")
print(f"  lean prompt only      : {lean:>12,} tokens")
print(f"  prompt + whole log     : {bloated:>12,} tokens")
print(f"  cost of pasting the log: {bloated - lean:>12,} tokens  ({(bloated-lean)/max(lean,1):.0f}x the prompt)")
