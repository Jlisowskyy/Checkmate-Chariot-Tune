#!/bin/bash

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
cd "${SCRIPT_DIR}" || exit 1
cd ..

source ./.venv/bin/activate

PROJECT_PATH=$(pwd)
export PYTHONPATH=$PROJECT_PATH


fastapi dev ./Manager/manager_main.py --app Manager