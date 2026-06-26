import random
random.seed(7)
lines, N = [], 200_000
svcs = ["auth","cache","db","api","worker","scheduler","payment"]
needle_at = random.randint(90_000, 120_000)
for i in range(N):
    ts = f"2026-06-20T10:{(i//1000)%60:02d}:{(i//17)%60:02d}.{i%1000:03d}Z"
    if i == needle_at:
        lines.append(f"{ts} ERROR [payment] tx_id=8842 charge failed: upstream timeout after 30000ms (retries=3)")
    else:
        lvl = random.choices(["INFO","DEBUG"],[0.7,0.3])[0]
        s = random.choice(svcs)
        lines.append(f"{ts} {lvl} [{s}] req_id={random.randint(1000000,9000000)} latency={random.randint(2,250)}ms ok")
open("app.log","w").write("\n".join(lines)+"\n")
print(f"wrote app.log: {N:,} lines, needle (ERROR) at line {needle_at:,}")
