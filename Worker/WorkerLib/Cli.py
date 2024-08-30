import socket
import json
import os
from pathlib import Path

from .CliTranslator import *
from Utils.Logger import Logger, LogLevel
from .BaseCli import BaseCli, CommandType
from Utils.SettingsLoader import SettingsLoader
from .LockFile import LockFile, LOCK_FILE_PATH


class Cli(BaseCli):
    # ------------------------------
    # Class fields
    # ------------------------------

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self):
        super().__init__()

    # ------------------------------
    # Class interaction
    # ------------------------------

    # ---------------------------------------------
    # Abstract/Virtual methods implementation
    # ---------------------------------------------

    def parse_single_command(self, index: int) -> int:
        cli_cmd = self._extract_command(index)

        return self._execute_command(cli_cmd, index) \
            if cli_cmd.command_type == CommandType.FRONTEND \
            else self._forward_backend_command_prepare(cli_cmd, index + 1)

    # ------------------------------
    # Private methods
    # ------------------------------

    def _forward_backend_command_prepare(self, command: CommandCli, index: int) -> int:
        args_to_send = list[str]()

        args_to_send.append(f"--{command.command}")
        while index < len(self._args) and not BaseCli.is_command(self._args[index]):
            args_to_send.append(self._args[index])
            index += 1

        self._forward_backend_command_send(args_to_send)
        return index

    def _forward_backend_command_send(self, command_parts: list[str]) -> None:
        full_command = ' '.join(command_parts)
        Logger().log_info(f"Sending command '{full_command}' to the backend process", LogLevel.MEDIUM_FREQ)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)

        try:
            client_socket.connect(('localhost', SettingsLoader().get_settings().process_port))
            client_socket.sendall(json.dumps({"args": command_parts}).encode())
            client_socket.close()
        except Exception as e:
            raise Exception(f"Failed to send command: {full_command} to backend process: {e}")

    @staticmethod
    def _format_error_status(status) -> str:
        if os.WIFEXITED(status):
            exit_code = os.WEXITSTATUS(status)
            return f"Process exited with code {exit_code}"
        elif os.WIFSIGNALED(status):
            signal_number = os.WTERMSIG(status)
            return f"Process terminated by signal {signal_number}"
        else:
            return "Unknown exit status"

    # ------------------------------
    # Available Commands
    # ----------`--------------------

    def _deploy(self, index: int) -> int:
        script_path = os.path.dirname(os.path.abspath(__file__))
        worker_process_path = Path(script_path).parent / "run_worker_process_test.sh"

        lockfile = LockFile(LOCK_FILE_PATH)
        if lockfile.is_locked_process_existing():
            Logger().log_warning(f"Worker process already exists with PID: {lockfile.get_locked_process_pid()}",
                                 LogLevel.LOW_FREQ)
            return index

        Logger().log_info(f"Starting worker process from path: {worker_process_path}", LogLevel.LOW_FREQ)

        pid = os.spawnl(os.P_NOWAIT, str(worker_process_path), worker_process_path)

        if pid <= 0:
            raise Exception(f"Failed to start worker process: {Cli._format_error_status(pid)}")

        time.sleep(5)
        Logger().log_info("Worker process correctly deployed", LogLevel.LOW_FREQ)

        return index

    @staticmethod
    def _deploy_help() -> str:
        rv = ("syntax: --deploy\n\t"
              "Command will try to create a background process that will be responsible\n"
              "for all job processing"
              )
        return rv

    BaseCli.add_command(CommandCli(CommandType.FRONTEND, "deploy", _deploy, _deploy_help))
