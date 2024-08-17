#!/bin/bash

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
cd "$SCRIPT_DIR" || exit 1

python -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt