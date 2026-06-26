#!/usr/bin/env python3
"""04_01: needle in the haystack — REAL token counts (requires ANTHROPIC_API_KEY).
Whole-file vs grep vs grep+context, counted with Anthropic's count_tokens
(claude-opus-4-8). count_tokens accepts inputs larger than the context window, so the
whole file is counted directly. Run: python3 compare.py"""
import os, sys, subprocess

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

whole = open("app.log").read()
naive_tok = ntok(whole)

grep = subprocess.run(["grep","-n","ERROR","app.log"], capture_output=True, text=True).stdout
grep_tok = ntok(grep)

ctx = subprocess.run(["grep","-n","-B3","-A3","ERROR","app.log"], capture_output=True, text=True).stdout
ctx_tok = ntok(ctx)

print(f"{'approach':38} {'lines':>9} {'chars':>12} {'tokens':>12}")
print("-"*73)
print(f"{'Read whole file (naive)':38} {whole.count(chr(10)):>9,} {len(whole):>12,} {naive_tok:>12,}")
print(f"{'grep ERROR (scoped)':38} {grep.count(chr(10)):>9,} {len(grep):>12,} {grep_tok:>12,}")
print(f"{'grep -B3 -A3 ERROR (scoped+context)':38} {ctx.count(chr(10)):>9,} {len(ctx):>12,} {ctx_tok:>12,}")
print("-"*73)
print(f"reduction (whole -> grep+context): {100*(naive_tok-ctx_tok)/naive_tok:.4f}%")
print(f"a 200k context window holds ~200,000 tokens; naive read needs ~{naive_tok:,} -> {naive_tok/200000:.1f}x too big")
print("(tokens: real count_tokens via API, claude-opus-4-8)")
print("\n--- what the model actually needs (the grep+context output) ---")
print(ctx.strip())
