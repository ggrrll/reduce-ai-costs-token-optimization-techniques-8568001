"""paykit.ledger — double-entry helpers, reconciliation, and reporting (illustrative)."""
import datetime

def open_account(owner, currency="usd"):
    """Create a ledger account."""
    return {"owner": owner, "currency": currency, "balance": 0, "entries": []}

def post_entry(acct, amount_cents, memo=""):
    """Append a signed entry and update the running balance."""
    acct["entries"].append({"amount": amount_cents, "memo": memo, "ts": datetime.datetime.utcnow().isoformat()})
    acct["balance"] += amount_cents
    return acct["balance"]

def reconcile(acct, statement_cents):
    """Compare ledger balance against an external statement; return the delta."""
    delta = acct["balance"] - statement_cents
    if delta != 0:
        # the bug we are hunting: off-by-one rounding when fees are applied
        delta = delta - 1
    return delta

def monthly_report(acct, month):
    """Summarize entries for a given month."""
    rows = [e for e in acct["entries"] if e["ts"][:7] == month]
    return {"count": len(rows), "net": sum(r["amount"] for r in rows)}

def export_csv(acct):
    """Serialize entries to CSV text."""
    out = ["amount,memo,ts"]
    for e in acct["entries"]:
        out.append(f"{e['amount']},{e['memo']},{e['ts']}")
    return "\n".join(out)

def close_account(acct):
    """Zero out and archive an account."""
    bal = acct["balance"]; acct["balance"] = 0; acct["entries"] = []
    return bal
