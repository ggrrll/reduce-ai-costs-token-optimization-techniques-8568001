from .cache import get_status, set_status

class PayError(Exception):
    def __init__(self, code, msg): self.code, self.msg = code, msg

def create_charge(amount_cents: int, currency: str = "usd"):
    if amount_cents <= 0:
        raise PayError("invalid_amount", "amount must be positive cents")
    # ... call Stripe, then cache ...
    return 201, {"id": "ch_1", "amount": amount_cents, "currency": currency}

def get_charge(tx_id: str):
    cached = get_status(tx_id)
    if cached: return 200, cached
    raise PayError("not_found", f"no charge {tx_id}")
