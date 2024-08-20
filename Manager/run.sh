#!/bin/bash

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
cd "$SCRIPT_DIR" || exit 1

source ../.venv/bin/activate
PATH=${PATH}:$(dirname "$(pwd)")/Models
echo "$PATH"
fastapi dev main.py --app Manager