#!/usr/bin/env python3
"""06: a minimal bug-investigation harness that calls the model DIRECTLY (no coding agent).
Shows that token discipline isn't a coding-tool trick — it's how you build any LLM app.
Modes: naive (slurp everything) | lean (scope + symbol) | compare.
REAL token counts via Anthropic's count_tokens (claude-opus-4-8); requires
ANTHROPIC_API_KEY. count_tokens accepts inputs larger than the context window, so the
naive whole-file payload is counted directly. Usage: python3 harness.py compare"""
import os, sys, subprocess, ast

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

SYSTEM = ("You are a senior SRE assistant. Investigate the reported bug and cite file:line. "
          "Money is integer cents. Handlers return (status_code, dict). Be concise.")  # static => cacheable
BUG = "Charges intermittently fail; reconcile() seems to report a wrong delta. Find the cause."

def whole_log():  return open("app.log").read()
def scoped_log(): return subprocess.run(["grep","-n","-B3","-A3","ERROR","app.log"],
                                        capture_output=True, text=True).stdout
def whole_code(): return open("bigmod.py").read()
def symbol_code(sym="reconcile"):
    src = open("bigmod.py").read(); t = ast.parse(src)
    n = next(x for x in t.body if isinstance(x, ast.FunctionDef) and x.name == sym)
    return ast.get_source_segment(src, n)

def count(system, user):
    return ntok(system + "\n" + user)

def build(mode):
    if mode == "naive":
        return f"{BUG}\n\nLOG:\n{whole_log()}\n\nCODE:\n{whole_code()}"
    return f"{BUG}\n\nLOG (scoped):\n{scoped_log()}\nCODE (symbol):\n{symbol_code()}"

def report(mode):
    user = build(mode); tot = count(SYSTEM, user)
    print(f"  {mode:6} total input ~{tot:,} tokens  (system ~{ntok(SYSTEM)} of that is static => cacheable)")
    return tot

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "compare"
    if mode == "compare":
        print("bug-investigation harness — same task, two ways (real count_tokens via API):")
        n = report("naive"); l = report("lean")
        print("-"*64)
        print(f"  reduction: {n:,} -> {l:,} tokens  ({100*(n-l)/n:.2f}% smaller)")
        print(f"  fits a 200k window? naive: {'NO' if n>200000 else 'yes'}   lean: {'yes' if l<200000 else 'NO'}")
    else:
        report(mode)
