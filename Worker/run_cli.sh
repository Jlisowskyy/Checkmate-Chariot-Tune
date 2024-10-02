#!/bin/bash

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
cd "$SCRIPT_DIR" || exit 1
cd ..

source .venv/bin/activate
python worker_cli.py "$@"
exit_code=$?

exit $exit_code