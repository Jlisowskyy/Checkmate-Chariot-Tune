#!/bin/bash

declare RUNNER_SCRIPT_DIR
declare RUNNER_VENV_DIR

RUNNER_SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

# SCRIPT PARENT DIR
RUNNER_VENV_DIR="$(dirname "${RUNNER_SCRIPT_DIR}")/.venv/bin/activate"

source "${RUNNER_SCRIPT_DIR}/Regression/helpers.bash"
source "${RUNNER_SCRIPT_DIR}/Regression/base_regression.bash"

# run unit tests
helpers_pretty_chapter "Unit Test (PyTest) - Manager"

source "${RUNNER_VENV_DIR}"
"${RUNNER_SCRIPT_DIR}/pytest_runner.bash"

# run regression

helpers_pretty_chapter "Regression tests"

helpers_init_env
helpers_run_test "base_regression_main"
helpers_cleanup
