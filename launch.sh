#!/bin/bash
# Launch Hermes Desktop Pet (小黑猫)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HERMES_VENV="$HOME/.hermes/hermes-agent/venv"

if [ -d "$HERMES_VENV" ]; then
    PY="$HERMES_VENV/bin/python3"
else
    PY="python3"
fi

exec "$PY" "$SCRIPT_DIR/pet.py" "$@"
