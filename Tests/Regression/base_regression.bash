#!/bin/bash

declare BASE_REGRESSION_SCRIPT_DIR
declare BASE_REGRESSION_PREV_DIR

BASE_REGRESSION_PREV_DIR=$(pwd)
BASE_REGRESSION_SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
cd "$BASE_REGRESSION_SCRIPT_DIR" || exit 1

source ./helpers.bash

base_regression_main() {
  pretty_sleep 5
}

cd "${BASE_REGRESSION_PREV_DIR}" || exit 1
