import json
import os
import socket
from pathlib import Path
from time import sleep

from .CliTranslator import *
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
            if cli_cmd.command_type != CommandType.BACKEND \
            else self._forward_backend_command_prepare(cli_cmd, index + 1)

    def _notify_parse_fail(self, arg: any) -> None:
        print(f"Command failed: {arg}")

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

    def _cli_connection_life_cycle(self, client_socket, command_parts: list[str]) -> None:
        full_command = ' '.join(command_parts)

        Logger().log_info(f"Sending command '{full_command}' to the backend process", LogLevel.MEDIUM_FREQ)

        try:
            client_socket.connect(('localhost', SettingsLoader().get_settings().process_port))
        except Exception as e:
            raise Exception(f"Failed to connect with backend process: {e}")

        try:
            client_socket.sendall(json.dumps({"args": command_parts}).encode())
        except Exception as e:
            raise Exception(f"Failed to send command: {full_command}, error info: {e}")

        try:
            response = client_socket.recv(512 * 1024).decode()
            client_socket.close()
        except Exception as e:
            raise Exception(f"Failed to receive response: {e}")

        print(
            f"Command: {full_command}, received response:\n\n{response}"
            f"\n----------------------------------------------------------------------------------")

    def _forward_backend_command_send(self, command_parts: list[str]) -> None:
        retries = 3

        if not Cli._is_worker_deployed():
            raise Exception("Worker is not deployed!")

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)

        while retries > 0:
            retries -= 1

            try:
                self._cli_connection_life_cycle(client_socket, command_parts)
            except Exception as e:
                msg = f"Failed sending msg to worker process: {e}"

                if retries == 0:
                    raise Exception(msg)
                else:
                    Logger().log_warning(msg, LogLevel.MEDIUM_FREQ)
                    time.sleep(1)

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

    @staticmethod
    def _is_worker_deployed() -> bool:
        lockfile = LockFile(LOCK_FILE_PATH)
        return lockfile.is_locked_process_existing()

    @staticmethod
    def _get_deployed_worker_pid() -> int:
        lockfile = LockFile(LOCK_FILE_PATH)
        return lockfile.get_locked_process_pid()

    @staticmethod
    def _await_worker_with_pid(pid: int, timeout_s: int) -> None:
        lockfile = LockFile(LOCK_FILE_PATH)
        lockfile.await_creation(pid, timeout_s * 1000)

    # ------------------------------
    # Available Commands
    # ----------`--------------------

    def _deploy(self, index: int) -> int:
        script_path = os.path.dirname(os.path.abspath(__file__))
        worker_process_path = Path(script_path).parent / "run_worker_process_test.sh"

        if Cli._is_worker_deployed():
            Logger().log_warning(f"Worker process already exists with PID: {Cli._get_deployed_worker_pid()}",
                                 LogLevel.LOW_FREQ)
            return index

        Logger().log_info(f"Starting worker process from path: {worker_process_path}", LogLevel.LOW_FREQ)

        pid = os.spawnl(os.P_NOWAIT, str(worker_process_path), worker_process_path)

        if pid <= 0:
            raise Exception(f"Failed to start worker process: {Cli._format_error_status(pid)}")

        Cli._await_worker_with_pid(pid, 5)
        sleep(1)

        Logger().log_info("Worker process correctly deployed", LogLevel.LOW_FREQ)
        print("Worker deployment status: Worker process correctly deployed")

        return index

    @staticmethod
    def _deploy_help() -> str:
        rv = ("syntax: --deploy\n\t"
              "Command will try to create a background process that will be responsible\n"
              "for all job processing"
              )
        return rv

    BaseCli.add_command(CommandCli(CommandType.FRONTEND, "deploy", _deploy, _deploy_help))
