"""paykit.ledger — double-entry helpers, reconciliation, reporting, and audit (illustrative).
A realistic module: the agent only needs ONE function, but a whole-file read drags in all of it."""
import datetime


def open_account(owner, currency="usd"):
    """Create a ledger account."""
    return {"owner": owner, "currency": currency, "balance": 0, "entries": []}


def post_entry(acct, amount_cents, memo=""):
    """Append a signed entry and update the running balance."""
    acct["entries"].append(
        {"amount": amount_cents, "memo": memo, "ts": datetime.datetime.utcnow().isoformat()}
    )
    acct["balance"] += amount_cents
    return acct["balance"]


def void_entry(acct, index):
    """Reverse a previously posted entry by index."""
    e = acct["entries"][index]
    acct["balance"] -= e["amount"]
    e["voided"] = True
    return acct["balance"]


def transfer(src, dst, amount_cents, memo="transfer"):
    """Move funds between two accounts as a paired double entry."""
    post_entry(src, -amount_cents, memo)
    post_entry(dst, amount_cents, memo)
    return src["balance"], dst["balance"]


def apply_fee(acct, amount_cents, kind="service"):
    """Charge a fee against the account balance."""
    return post_entry(acct, -abs(amount_cents), f"fee:{kind}")


def accrue_interest(acct, rate_bps):
    """Accrue interest in basis points on the current balance."""
    interest = acct["balance"] * rate_bps // 10_000
    return post_entry(acct, interest, "interest")


def reconcile(acct, statement_cents):
    """Compare ledger balance against an external statement; return the delta."""
    delta = acct["balance"] - statement_cents
    if delta != 0:
        # the bug we are hunting: off-by-one rounding when fees are applied
        delta = delta - 1
    return delta


def reconcile_batch(accts, statements):
    """Reconcile many accounts at once; return per-account deltas."""
    return {a["owner"]: reconcile(a, s) for a, s in zip(accts, statements)}


def audit(acct, statement_cents):
    """Flag an account whose reconciliation delta is non-zero."""
    delta = reconcile(acct, statement_cents)
    return {"owner": acct["owner"], "delta": delta, "clean": delta == 0}


def monthly_report(acct, month):
    """Summarize entries for a given month (YYYY-MM)."""
    rows = [e for e in acct["entries"] if e["ts"][:7] == month]
    return {"count": len(rows), "net": sum(r["amount"] for r in rows)}


def quarterly_report(acct, year, quarter):
    """Summarize entries for a calendar quarter."""
    months = [f"{year}-{m:02d}" for m in range((quarter - 1) * 3 + 1, quarter * 3 + 1)]
    rows = [e for e in acct["entries"] if e["ts"][:7] in months]
    return {"count": len(rows), "net": sum(r["amount"] for r in rows)}


def export_csv(acct):
    """Serialize entries to CSV text."""
    out = ["amount,memo,ts"]
    for e in acct["entries"]:
        out.append(f"{e['amount']},{e['memo']},{e['ts']}")
    return "\n".join(out)


def import_csv(text):
    """Parse CSV text back into entries."""
    lines = text.splitlines()[1:]
    entries = []
    for line in lines:
        amount, memo, ts = line.split(",", 2)
        entries.append({"amount": int(amount), "memo": memo, "ts": ts})
    return entries


def close_account(acct):
    """Zero out and archive an account."""
    bal = acct["balance"]
    acct["balance"] = 0
    acct["entries"] = []
    return bal
