# paykit — agent instructions (Codex reads this file)

Same project as CLAUDE.md. Python 3.12 payments service over Stripe + Redis.

- Money is integer cents, never floats.
- Handlers return (status_code, dict). Errors raise PayError(code, msg).
- Lint with ruff, test with pytest -q.
- Prefer small diffs and editing existing functions.
- Don't add dependencies without asking.
