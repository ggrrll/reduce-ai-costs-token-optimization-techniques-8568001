"""Tiny payments module under test — the suite in test_pay.py exercises it.
create_charge returns (status, body) for valid amounts and raises PayError otherwise."""


class PayError(Exception):
    pass


def create_charge(amount_cents):
    if amount_cents <= 0:
        raise PayError("invalid_amount: amount must be positive cents")
    return (201, {"id": "ch_live", "amount": amount_cents})
