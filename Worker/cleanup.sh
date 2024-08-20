#!/bin/bash

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
cd "$SCRIPT_DIR" || exit 1

rm -rf ./ProjectInfo
rm -rf ./Utils
rm -rf ./Models