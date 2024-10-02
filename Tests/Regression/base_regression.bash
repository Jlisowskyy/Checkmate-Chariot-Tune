#!/bin/bash

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
cd "$SCRIPT_DIR" || exit 1

source ./helpers.bash

base_regression_main() {
  pretty_sleep 5
}
