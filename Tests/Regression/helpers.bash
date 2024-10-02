#!/bin/bash

declare MANAGER_PID
declare SCRIPT_DIR
declare PROJECT_DIR
declare WORKER_PID
declare LOG_DIR
declare LOG_FILE

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
cd "$SCRIPT_DIR" || exit 1

cd ../.. || exit 1
PROJECT_DIR=$(pwd)
cd "$SCRIPT_DIR" || exit 1

LOG_DIR="${PROJECT_DIR}/Tests/Regression/logs"
mkdir "${LOG_DIR}" 2>/dev/null

LOG_FILE="${LOG_DIR}/runner_$(date +"%Y-%m-%d_%H-%M-%S").log"

log_message() {
  echo "$1" >> "${LOG_FILE}"
}

pretty_message() {
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    BLUE='\033[0;34m'
    YELLOW='\033[0;33m'
    NC='\033[0m'

    local message="$1"
    local color="$2"

    local current_time=$(date +"%Y-%m-%d %H:%M:%S")
    local calling_file="${BASH_SOURCE[2]}"
    local calling_function="${FUNCNAME[2]}"

    local pretty_message="${current_time} [${calling_file}:${calling_function}] ${message}"

    case "$color" in
        "red")
            echo -e "${RED}${pretty_message}${NC}"
            ;;
        "green")
            echo -e "${GREEN}${pretty_message}${NC}"
            ;;
        "blue")
            echo -e "${BLUE}${pretty_message}${NC}"
            ;;
        "yellow")
            echo -e "${YELLOW}${pretty_message}${NC}"
            ;;
        *)
            echo -e "${pretty_message}"
            ;;
    esac

    log_message "${pretty_message}"
}

pretty_info () {
    pretty_message "$1" "blue"
}

pretty_error () {
    pretty_message "$1" "red"
}

pretty_success () {
    pretty_message "$1" "green"
}

pretty_warning () {
    pretty_message "$1" "yellow"
}

pretty_sleep() {
  duration=$1
  while [ "${duration}" -gt 0 ]; do
    echo -ne "Sleeping for $duration seconds\033[0K\r"
    sleep 1
    duration=$((duration - 1))
  done
}

run_cli () {
  pretty_info "Running CLI command: $*"

  cd "${PROJECT_DIR}" || exit 1
  ./Worker/run_cli.sh "$@"
}

wait_for_process_death() {
  pid=$1
  max_duration=${2:-60}

  duration=0
  while [ "${duration}" -lt "${max_duration}" ]; do
    if pgrep -P "${pid}" > /dev/null; then
      pretty_sleep 5
      duration=$((duration + 5))
    else
      break
    fi
  done

  if [ "${duration}" -ge "${max_duration}" ]; then
    pretty_warning "Process did not die in ${max_duration} seconds"
    kill -9 "${pid}"
  fi

  pretty_success "Process died"
}

cleanup() {
  pretty_info "Cleaning up the environment"

  pkill -P $$

  if [ -e "/tmp/Checkmate-Chariot-Worker.lock" ]; then
    pretty_info "Stopping worker"

    pid=$(cat /tmp/Checkmate-Chariot-Worker.lock)

    run_cli --stop_worker
    wait_for_process_death "${pid}" 100

    rm -f /tmp/Checkmate-Chariot-Worker.lock
  fi

  if [ -n "${MANAGER_PID}" ]; then
    pretty_info "Stopping manager"

    kill -s SIGINT "${MANAGER_PID}"
    wait_for_process_death "${MANAGER_PID}"
  fi

  pretty_success "Environment cleaned up successfully"
}

validate_state() {
  result=$?
  local worker_pid

  if ! pgrep -P "${MANAGER_PID}" > /dev/null; then
    pretty_error "Manager died"
    exit 1
  fi

  if [ $result -ne 0 ]; then
    pretty_error "Failed with exit code $result"
    exit $result
  fi

  if [ ! -e "/tmp/Checkmate-Chariot-Worker.lock" ]; then
    pretty_error "Worker did not start"
    exit 1
  fi

  worker_pid=$(cat /tmp/Checkmate-Chariot-Worker.lock)

  if ! pgrep -P "${worker_pid}" > /dev/null; then
    pretty_error "Worker died, but lock file still exists"
    rm -f /tmp/Checkmate-Chariot-Worker.lock
    exit 1
  fi

  pretty_success "State validated successfully"
}

run_test() {
  test=$1

  pretty_info "Running test: ${test}"
  eval "${test}"

  validate_state
  pretty_success "Test: ${test} passed"
}

init_env() {
  pretty_info "Initializing the environment"

  trap cleanup EXIT
  trap cleanup SIGINT
  trap cleanup SIGTERM
  trap cleanup SIGQUIT

  cd "${PROJECT_DIR}" || exit 1
  source ".venv/bin/activate"

  # Start Manager
  pretty_info "Starting Manager"
  ./Manager/run.sh &
  MANAGER_PID=$!
  pretty_sleep 5

  # Start Worker
  pretty_info "Starting Worker"
  run_cli --deploy
  pretty_sleep 5

  validate_state
  WORKER_PID=$(cat /tmp/Checkmate-Chariot-Worker.lock)

  pretty_success "Environment initialized successfully"
}

