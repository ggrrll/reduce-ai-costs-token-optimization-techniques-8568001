# paykit

Python 3.12 payments service. Stripe upstream, Redis status cache (60s TTL).
- `src/payments.py` — charge/refund/status handlers
- `src/cache.py` — Redis wrapper

## Rules
- Money = integer cents, never floats.
- Handlers return `(status_code, dict)`; errors `raise PayError(code, msg)`.
- Lint `ruff`, test `pytest -q`. Small diffs, match style, no new deps without asking.
