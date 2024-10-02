#!/bin/bash

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
cd "$SCRIPT_DIR" || exit 1

source Regression/helpers.bash
source Regression/base_regression.bash

init_env
run_test "base_regression_main"
cleanup