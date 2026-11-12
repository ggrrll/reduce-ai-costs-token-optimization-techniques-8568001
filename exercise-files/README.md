# Stop Burning Tokens — demo pack

Self-contained. Every chapter folder has the files it needs (including its own `make_log.py`,
so `app.log` is always one command away). Every demo requires `ANTHROPIC_API_KEY`
and the `anthropic` package.

**One-time setup** — install [uv](https://docs.astral.sh/uv/), then from the
`exercise-files` folder run:

```bash
uv sync
source .venv/bin/activate
export ANTHROPIC_API_KEY=sk-ant-...
```

---

## Ch1 — Tokens & the Real Cost

### 01_03 token bill
```bash
cd ch1
python3 make_log.py                 # writes app.log (~14 MB)
python3 token_bill.py app.log       # real count_tokens (whole log counted directly)
```
Expect (real count_tokens):
```
method: API count_tokens (claude-opus-4-8) — log: app.log
  lean prompt only      :           39 tokens
  prompt + whole log     :    8,120,782 tokens
  cost of pasting the log:    8,120,743 tokens  (208224x the prompt)
```

---

## Ch2 — See Where Your Tokens Go

### 02_04 session inspector
```bash
cd ch2
python3 make_session.py
python3 inspect_session.py sample_session.jsonl
```
Expect (key lines):
```
  Read      8,121,451  100.0%
     8,120,743  app.log
HOTSPOT: one Read of 'app.log' = 8,120,743 tokens (100.0% of all tool output)
```

### 02_01 + 02_02 /context  `[CC]`  (your real numbers)
```bash
cd ch2/sample-repo
python3 ../../ch4/make_log.py        # drop an app.log here to read
claude
```
Then inside Claude Code:
```
/context        # point at Memory files row -> this repo's CLAUDE.md (~261 tok)
/mcp            # lists different mcp servers and tools
/context        # Messages row balloons
/usage
/stats
```

### 02_03 Codex /status  `[CODEX]`
```bash
cd ch2/sample-repo
codex
```
Then: `/status`, `/statusline`, open `AGENTS.md` (~94 tok).

---

## Ch3 — Where the Bloat Comes From

### 03_01 needle in the haystack
```bash
cd ch3
python3 make_log.py
python3 compare.py
grep -n -B3 -A3 ERROR app.log
```
Expect: `Read whole file 8,120,743` vs `grep+context 325` -> `99.9960%`; `40.6x too big`.


### 03_03 memory hygiene
```bash
cd ch3
python3 ../tok.py CLAUDE_before.md    # 763 tokens (real count_tokens)
python3 ../tok.py CLAUDE_after.md     # 172 tokens
```
763 -> 172 (≈77% smaller), paid every message.

### 03_04 the re-send problem
```bash
cd ch3
python3 sim_resend.py
```
Expect (real counts): `630,515` vs `255,422` -> saves `375,093 (59%)`; ~40k read x15 = `609,465`.

---

## Ch4 — Tools That Cut at the Source

### 04_02 rtk: filter tool output before it reaches the model
```bash
cd ch4
./rtk_demo.sh
```
Runs the test suite raw vs. `rtk`-filtered. Expect: raw = ~300 lines / thousands of tokens;
rtk = only the failure line. Requires `pytest` and `rtk` on PATH (both in the venv).

### 04_03 ast-grep: map and retrieve symbols from bigmod.py
```bash
cd ch4
./symbol_demo.sh
```
Uses `ast-grep` to list all function names and retrieve only `reconcile()` from `bigmod.py`.
Requires `ast-grep` (`brew install ast-grep` or `cargo install ast-grep`).

---

## Ch5 — Beyond Coding Agents

### 05_01 build it
```bash
cd ch5
python3 make_log.py
python3 harness.py naive
```
Expect: `naive  total input ~8,121,410 tokens` (won't fit a 200k window).

### 05_02 measure and cut
```bash
cd ch5
python3 harness.py compare
```
Expect:
```
  naive  total input ~8,121,410 tokens
  lean   total input ~538 tokens
  reduction: 8,121,410 -> 538 tokens  (99.99% smaller)
  fits a 200k window? naive: NO   lean: yes
```

---
