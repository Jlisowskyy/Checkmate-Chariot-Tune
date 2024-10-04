#!/bin/bash
OPTS="--help --version --connect --unregister --set_log_level --stop_worker --abort_worker --switch_jobs_block --query_worker_state --deploy"

_worker_cli_completion() {
    local cur
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"

    if [[ ${cur} == -* ]]; then
        COMPREPLY=( $(compgen -W "${OPTS}" -- "${cur}") )
    fi
    return 0
}

complete -F _worker_cli_completion wcli
