#!/usr/bin/env python3
"""Tiny token-attribution inspector for a Claude Code-style JSONL transcript.
Usage: python3 inspect_session.py sample_session.jsonl
The real tools (Tokview / claude-devtools) do this on your live session logs."""
import json, sys
from collections import defaultdict

by_tool = defaultdict(int)        # tokens returned INTO context, per tool
by_file = defaultdict(int)        # tokens returned, per file read
turn_in = turn_out = 0
for line in open(sys.argv[1]):
    r = json.loads(line)
    if r.get("type") != "assistant": continue
    turn_in  += r["usage"]["input_tokens"]
    turn_out += r["usage"]["output_tokens"]
    for tc in r.get("tool_calls", []):
        rt = tc.get("result_tokens", 0)
        by_tool[tc["name"]] += rt
        f = tc.get("input", {}).get("file")
        if f: by_file[f] += rt

tool_total = sum(by_tool.values())
print("=== where context came from (tool output) ===")
for name, tok in sorted(by_tool.items(), key=lambda x:-x[1]):
    print(f"  {name:6} {tok:>12,}  {100*tok/tool_total:5.1f}%")
print(f"  {'TOTAL':6} {tool_total:>12,}")
print("\n=== top files pulled into context ===")
for f, tok in sorted(by_file.items(), key=lambda x:-x[1])[:5]:
    print(f"  {tok:>12,}  {f}")
print(f"\nprompt input tokens (billed): {turn_in:,}   output: {turn_out:,}")
hot_f, hot_t = max(by_file.items(), key=lambda x:x[1])
print(f"HOTSPOT: one Read of '{hot_f}' = {hot_t:,} tokens ({100*hot_t/tool_total:.1f}% of all tool output)")
