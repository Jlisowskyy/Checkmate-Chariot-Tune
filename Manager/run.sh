#!/bin/bash

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
cd "${SCRIPT_DIR}" || exit 1

source ../.venv/bin/activate

cd ..
PROJECT_PATH=$(pwd)
export PYTHONPATH=$PROJECT_PATH
cd "${SCRIPT_DIR}" || exit 1

fastapi dev ./manager_main.py --app Manager