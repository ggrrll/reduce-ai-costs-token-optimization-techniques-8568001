#!/usr/bin/env bash
# One-time setup for "Reduce AI Costs: Token Optimization Techniques"
# Creates a virtual environment at ~/.venv/token-opt and installs all
# course dependencies. Run once, then activate before any demo.
set -euo pipefail

VENV="$HOME/.venv/token-opt"
PYTHON="${1:-python3}"   # override: ./install.sh python3.11

echo "==> Creating virtual environment at $VENV"
"$PYTHON" -m venv "$VENV"
"$VENV/bin/pip" install --upgrade pip --quiet

echo "==> Installing course packages"
"$VENV/bin/pip" install \
    anthropic \
    "headroom-ai[all]" \
    rtk \
    serena \
    ponytail

echo
echo "All done."
echo
echo "Activate the environment before running any demo:"
echo "  source $VENV/bin/activate"
echo
echo "Set your Anthropic API key (required for token-counting demos):"
echo "  export ANTHROPIC_API_KEY=sk-ant-..."
