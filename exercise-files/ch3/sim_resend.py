#!/usr/bin/env python3
"""04_04: why conversation history is expensive — with REAL token counts (requires
ANTHROPIC_API_KEY). Most tools re-send the WHOLE conversation each turn; the killer is
a big tool output (a file read) that lands in history and is re-sent every later turn.
The per-turn pieces and the big read are measured with Anthropic's count_tokens
(claude-opus-4-8) on real strings; the re-send math is then exact. Run: python3 sim_resend.py"""
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

# Representative real payloads — counted via the API so every number is measured.
SYSTEM = ("You are a senior SRE coding assistant. Money is integer cents. Handlers return "
          "(status_code, dict). Cite file:line. Be concise. Available tools: read, grep, "
          "edit, bash, web_search, web_fetch (schemas loaded on demand via tool search).")
USER_MSG = "Why are some payments failing? Check the logs and the payment handler, then propose a fix."
ASST_MSG = ("Looking at the failing charges, reconcile() applies a fee adjustment that subtracts an "
            "extra cent, so the delta is off by one. I'll trace the call sites and confirm before editing.")
SUMMARY  = ("Summary so far: investigating intermittent payment failures; reconcile() in payments.py "
            "appears to mis-apply a rounding step; next step is to confirm and patch the off-by-one.")

OVERHEAD = ntok(SYSTEM)        # fixed system + tool-registry overhead, re-sent every turn
USER     = ntok(USER_MSG)
ASST     = ntok(ASST_MSG)
SUMM     = ntok(SUMMARY)
# A real big file read: count an actual slice of the log (~40k tokens at this log's density).
BIG_READ = ntok(open("app.log").read()[:70_000])

BIG_READ_TURN, TURNS = 5, 20

def run(compact_at=None):
    history, billed = 0, 0
    for t in range(1, TURNS+1):
        if compact_at and t == compact_at:
            history = SUMM                       # /compact collapses history to a summary
        billed += OVERHEAD + history             # this turn re-sends everything so far
        history += USER + ASST
        if t == BIG_READ_TURN:
            history += BIG_READ                  # the big file read joins history...
    return billed

base = run()
comp = run(compact_at=12)                        # compact a couple turns after the big read
print("measured pieces (real count_tokens, claude-opus-4-8):")
print(f"  system/overhead {OVERHEAD:,} | user {USER:,} | assistant {ASST:,} | big read ~{BIG_READ:,} | summary {SUMM:,}")
print(f"\n{'scenario':34} {'billed input tokens':>20}")
print("-"*56)
print(f"{'20 turns, big read stays in history':34} {base:>20,}")
print(f"{'20 turns, /compact at turn 12':34} {comp:>20,}")
print("-"*56)
print(f"savings from one /compact after a big read: {base-comp:,} tokens ({100*(base-comp)/base:.0f}%)")
print(f"\nThat big read alone is re-sent on turns {BIG_READ_TURN+1}-{TURNS} "
      f"= {TURNS-BIG_READ_TURN}x = {(TURNS-BIG_READ_TURN)*BIG_READ:,} tokens you pay again.")
