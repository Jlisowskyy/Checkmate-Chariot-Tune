#!/bin/bash

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
cd "$SCRIPT_DIR" || exit 1

# prepare env
python -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt

cp autocomplete.bash /etc/bash_completion.d/wcli
chmod +x /etc/bash_completion.d/wcli

echo "alias wcli='${SCRIPT_DIR}/run_cli.sh'" >> ~/.bashrc