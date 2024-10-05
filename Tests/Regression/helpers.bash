#!/bin/bash

declare HELPERS_MANAGER_PID
declare HELPERS_SCRIPT_DIR
declare HELPERS_PROJECT_DIR
declare HELPERS_WORKER_PID
declare HELPERS_LOG_DIR
declare HELPERS_LOG_FILE
declare HELPERS_WORKER_LOCK_PATH
declare HELPERS_PREV_DIR

HELPERS_PREV_DIR=$(pwd)
HELPERS_SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
cd "$HELPERS_SCRIPT_DIR" || exit 1

cd ../.. || exit 1
HELPERS_PROJECT_DIR=$(pwd)
cd "$HELPERS_SCRIPT_DIR" || exit 1

HELPERS_LOG_DIR="${HELPERS_PROJECT_DIR}/Tests/Regression/logs"
mkdir "${HELPERS_LOG_DIR}" 2>/dev/null

HELPERS_LOG_FILE="${HELPERS_LOG_DIR}/runner_$(date +"%Y-%m-%d_%H-%M-%S").log"

HELPERS_WORKER_LOCK_PATH="/tmp/Checkmate-Chariot-Worker.lock"

helpers_log_message() {
  echo "$1" >> "${HELPERS_LOG_FILE}"
}

helpers_pretty_message() {
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    BLUE='\033[0;34m'
    YELLOW='\033[0;33m'
    PURPLE='\033[0;35m'
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
        "purple")
            echo -e "${PURPLE}${pretty_message}${NC}"
            ;;
        *)
            echo -e "${pretty_message}"
            ;;
    esac

    helpers_log_message "${pretty_message}"
}

helpers_pretty_info () {
    helpers_pretty_message "$1" "blue"
}

helpers_pretty_error () {
    helpers_pretty_message "$1" "red"
}

helpers_pretty_success () {
    helpers_pretty_message "$1" "green"
}

helpers_pretty_warning () {
    helpers_pretty_message "$1" "yellow"
}

helpers_pretty_chapter() {
  helpers_pretty_message "------------------------------------------------" "purple"
  helpers_pretty_message "$1" "purple"
  helpers_pretty_message "------------------------------------------------" "purple"
}

helpers_pretty_sleep() {
  duration=$1
  while [ "${duration}" -gt 0 ]; do
    echo -ne "Sleeping for $duration seconds\033[0K\r"
    sleep 1
    duration=$((duration - 1))
  done
}

helpers_run_cli () {
  helpers_pretty_info "Running CLI command: $*"

  cd "${HELPERS_PROJECT_DIR}" || exit 1
  ./Worker/run_cli.sh "$@"
}

helpers_wait_for_process_death() {
  pid=$1
  max_duration=${2:-60}

  helpers_pretty_info "Waiting for process: ${pid} to die"
  duration=0
  while [ "${duration}" -lt "${max_duration}" ]; do
    if pgrep -P "${pid}" > /dev/null; then
      helpers_pretty_sleep 5
      duration=$((duration + 5))
    else
      break
    fi
  done

  if [ "${duration}" -ge "${max_duration}" ]; then
    helpers_pretty_warning "Process: ${pid} did not die in ${max_duration} seconds"
    pkill -SIGKILL -g "${pid}"
  fi

  helpers_pretty_success "Process: ${pid} died"
}

helpers_cleanup() {
  helpers_pretty_info "Cleaning up the environment"

  if [ -n "${HELPERS_WORKER_PID}" ]; then
    helpers_pretty_info "Stopping worker"

    helpers_run_cli --stop_worker
    helpers_wait_for_process_death "${HELPERS_WORKER_PID}" 100

    rm -f "${HELPERS_WORKER_LOCK_PATH}"
  fi

  if [ -n "${HELPERS_MANAGER_PID}" ]; then
    helpers_pretty_info "Stopping manager"

    kill -s SIGINT -"${HELPERS_MANAGER_PID}"
    helpers_wait_for_process_death "${HELPERS_MANAGER_PID}" 100
  fi

  helpers_pretty_info "Killing any remaining processes"
  pkill -P $$

  helpers_pretty_success "Environment cleaned up successfully"
}

helpers_validate_state() {
  result=$?
  local worker_pid

  if ! pgrep -P "${HELPERS_MANAGER_PID}" > /dev/null; then
    helpers_pretty_error "Manager died"
    exit 1
  fi

  if [ $result -ne 0 ]; then
    helpers_pretty_error "Failed with exit code $result"
    exit $result
  fi

  if [ ! -e "${HELPERS_WORKER_LOCK_PATH}" ]; then
    helpers_pretty_error "Worker did not start"
    exit 1
  fi

  worker_pid=$(cat "${HELPERS_WORKER_LOCK_PATH}")
  helpers_pretty_info "Validating worker state with PID: ${worker_pid}"

  if ! pgrep -P "${worker_pid}" > /dev/null; then
    helpers_pretty_error "Worker died, but lock file still exists"
    exit 1
  fi

  helpers_pretty_success "State validated successfully"
}

helpers_run_test() {
  test=$1

  helpers_pretty_info "Running test: ${test}"
  eval "${test}"

  helpers_validate_state
  helpers_pretty_success "Test: ${test} passed"
}

helpers_init_env() {
  helpers_pretty_info "Initializing the environment"

  trap helpers_cleanup EXIT

  cd "${HELPERS_PROJECT_DIR}" || exit 1
  source ".venv/bin/activate"

  # Start Manager
  helpers_pretty_info "Starting Manager"
  setsid ./Manager/run.sh &
  HELPERS_MANAGER_PID=$!

  helpers_pretty_info "Started Manager with PID: ${HELPERS_MANAGER_PID}"
  helpers_pretty_sleep 5

  # Start Worker
  helpers_pretty_info "Starting Worker"
  helpers_run_cli --deploy
  helpers_pretty_sleep 5

  HELPERS_WORKER_PID=$(cat "${HELPERS_WORKER_LOCK_PATH}")
  helpers_pretty_info "Started Worker with PID: ${HELPERS_WORKER_PID}"

  helpers_validate_state

  helpers_pretty_success "Environment initialized successfully"
}

cd "${HELPERS_PREV_DIR}" || exit 1
