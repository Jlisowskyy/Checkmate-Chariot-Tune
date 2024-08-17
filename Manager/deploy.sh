#!/bin/bash

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
cd "$SCRIPT_DIR" || exit 1

# copy project info
cp -r ../ProjectInfo .

# prepare env
python -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt