#!/bin/bash

PYTEST_RUNNER_SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
cd "${PYTEST_RUNNER_SCRIPT_DIR}" || exit 1

source ../.venv/bin/activate

pytest ./ManagerPyTest/test_getters.py
pytest ./ManagerPyTest/test_pytest.py
pytest ./ManagerPyTest/test_tasks.py
pytest ./ManagerPyTest/test_checkmate_chariot_task.py