# Project: paykit

## Overview
paykit is our internal payments service. It exposes a small API for creating
charges, refunds, and reading transaction status. It talks to Stripe upstream
and caches transaction status in Redis. This file is loaded on every message.

## Architecture
- `src/payments.py` — charge/refund/status handlers
- `src/cache.py` — thin Redis wrapper with TTL helpers
- Upstream: Stripe (charges), Redis (status cache, 60s TTL)

## Conventions
- Python 3.12, type hints required, ruff for lint, pytest for tests.
- All money is integer cents. Never floats.
- Every handler returns (status_code, dict).
- Log with the `log` helper; never print.
- Errors: raise PayError(code, msg); the API layer maps it to a response.

## Setup
- `pip install -r requirements.txt`
- `export STRIPE_KEY=...` and `export REDIS_URL=...`
- `pytest -q` to run tests.

## Notes for the assistant
- Prefer editing existing functions over adding new files.
- Keep diffs small. Match the existing style exactly.
- Don't add dependencies without asking.
