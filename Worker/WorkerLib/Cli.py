import subprocess

from .CliTranslator import *
from Utils.Logger import Logger, LogLevel
from .BaseCli import BaseCli, CommandType


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

    # ------------------------------
    # Available Commands
    # ------------------------------

    def _deploy(self, index: int) -> int:
        # process = subprocess.Popen(['python', ''])

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
