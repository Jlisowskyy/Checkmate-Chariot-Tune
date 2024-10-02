from abc import ABC, abstractmethod
from enum import IntEnum
from typing import Callable

from Utils.Logger import Logger, LogLevel


class CommandType(IntEnum):
    FRONTEND = 0
    BACKEND = 1
    UNIVERSAL = 2


class CommandCli:
    # ------------------------------
    # Class fields
    # ------------------------------

    command_type: CommandType
    command: str
    command_func: Callable[['BaseCli', int], int]
    command_help: Callable[[], str]

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self,
                 command_type: CommandType,
                 command: str,
                 command_func: Callable[['BaseCli', int], int],
                 command_help: Callable[[], str]
                 ) -> None:
        self.command_type = command_type
        self.command = command
        self.command_func = command_func
        self.command_help = command_help

    # ------------------------------
    # Class interaction
    # ------------------------------

    def get_short_description(self) -> str:
        return f"Command: {self.command}, command type: {self.command_type.name.lower()}"

    def get_help_str(self) -> str:
        return f"{self.get_short_description()}\n{self.command_help()}"


class BaseCli(ABC):
    # ------------------------------
    # Class fields
    # ------------------------------

    registered_commands = dict[str, CommandCli]()
    _args: list[str]

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        self._args = []

    # ------------------------------
    # Abstract/Virtual methods
    # ------------------------------

    def _notify_parse_fail(self, arg: any) -> None:
        pass

    @abstractmethod
    def parse_single_command(self, index: int) -> int:
        pass

    # ------------------------------
    # Class interaction
    # ------------------------------

    def parse_args(self, args: list[str]) -> int:
        rv = 0

        try:
            self._parse_args_internal(args)
        except Exception as e:
            self._notify_parse_fail(e)
            Logger().log_error(f"During argument parsing, error occurred: {e}", LogLevel.LOW_FREQ)
            rv = 1

        return rv

    @staticmethod
    def is_command(arg: str) -> bool:
        return arg.strip().startswith("--")

    def parse_options(self, index: int) -> [int, dict[str, str]]:
        rv = dict[str, str]()

        while index < len(self._args) and not BaseCli.is_command(self._args[index]):
            arg = self._args[index].strip()
            split = arg.split("=", 1)

            if len(split) == 1:
                raise Exception(f"Expected key-value pair written as \"key\"=\"value\", received {arg} ")

            rv[split[0]] = split[1]
            index += 1

        return [index, rv]

    @staticmethod
    def extract_option_guarded(options: dict[str, str], option: str) -> str:
        if option not in options:
            raise Exception(f"Option \"{option}\" is expected to be provided")
        return options[option]

    @staticmethod
    def extract_option_not_guarded(options: dict[str, str], option: str) -> str:
        if option not in options:
            return ""
        return options[option]

    @staticmethod
    def add_command(command: CommandCli) -> None:
        if command.command in BaseCli.registered_commands:
            raise Exception(f"Command \"{command.command}\" is already registered")
        BaseCli.registered_commands[command.command] = command

    @staticmethod
    def display_help(command: str) -> None:
        if command in BaseCli.registered_commands:
            print(BaseCli.registered_commands[command].get_help_str())

    # ------------------------------
    # Private methods
    # ------------------------------

    def _parse_args_internal(self, args: list[str]) -> None:
        index = 0
        self._args = args

        while index < len(args):
            index = self.parse_single_command(index)

        Logger().log_info("Finished parsing arguments", LogLevel.MEDIUM_FREQ)

    def _extract_command(self, index) -> CommandCli:
        command = self._args[index].strip()

        if not command.startswith("--"):
            raise Exception(f"Expected command starting with: \"--\", received \"{command}\"")
        command = command[2:].strip()

        if command not in BaseCli.registered_commands:
            raise Exception(f"Command \"{command}\" not supported")

        return BaseCli.registered_commands[command]

    def _execute_command(self, command: CommandCli, index: int) -> int:
        try:
            rv = command.command_func(self, index + 1)
            Logger().log_info(f"Correctly finished execution of \"{command.command}\" command", LogLevel.MEDIUM_FREQ)
            return rv
        except Exception as e:
            BaseCli.display_help(command.command)
            raise Exception(f"Command execution: \"{command.command}\", failed by reason: {e}")

    # ------------------------------
    # Available Commands
    # ------------------------------

    def _help(self, index: int) -> int:
        if index < len(self._args) and not BaseCli.is_command(self._args[index]):
            command = self._args[index].strip()
            if command not in BaseCli.registered_commands:
                raise Exception(f"Help for command \"{command}\" not supported")
            BaseCli.display_help(command)
            return index + 1
        else:
            print("Available commands:")
            for command in BaseCli.registered_commands.values():
                print(f"\t{command.get_short_description()}")
            print("Type \"--help COMMAND_NAME\" to get more details on the command")
            return index

    @staticmethod
    def _help_help() -> str:
        return ("syntax: --help COMMAND_NAME\n\tDisplay detailed help for the given command "
                "--help\n\t to display list of available commands")

    registered_commands["help"] = CommandCli(CommandType.UNIVERSAL, "help", _help, _help_help)
