#!/usr/bin/env sh
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
export PYTHONPATH="$SCRIPT_DIR/src:${PYTHONPATH}"
PYTHON="${SCRIPT_DIR}/.venv/bin/python"
if [ ! -x "$PYTHON" ]; then
  PYTHON="python3"
fi

if [ $# -gt 0 ]; then
  "$PYTHON" -m papyr "$@"
  exit $?
fi

if ! "$PYTHON" -m papyr bootstrap; then
  exit 1
fi
printf '%s\n' 'Papyr shell. Type "help" for commands, "exit" to quit.'
while true; do
  printf '%s' 'papyr> '
  if ! IFS= read -r line; then
    break
  fi
  case "$line" in
    "" ) continue ;;
    exit|quit ) break ;;
    help )
      printf '%s\n' 'Examples: init | new | resume <path> | config show | doctor'
      continue
      ;;
  esac
  "$PYTHON" -m papyr $line
done
