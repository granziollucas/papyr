#!/usr/bin/env sh
set -e
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
VENV_PATH="$SCRIPT_DIR/.venv"
PYTHON="python3"

if [ ! -x "$VENV_PATH/bin/python" ]; then
  "$PYTHON" -m venv "$VENV_PATH"
fi

"$VENV_PATH/bin/python" -m pip install -r "$SCRIPT_DIR/requirements.txt"
