#!/bin/bash

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
cd "$SCRIPT_DIR" || exit 1

cp -r ../ProjectInfo .
cp -r ../Utils .
cp -r ../Models .

# prepare env
python -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt