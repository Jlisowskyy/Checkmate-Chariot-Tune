from abc import ABC, abstractmethod
from Utils.Logger import Logger, LogLevel
from enum import IntEnum
from typing import Callable


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
    command_func: Callable[[int], int]
    command_help: Callable[[], str]

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self,
                 command_type: CommandType,
                 command: str,
                 command_func: Callable[[int], int],
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

    registered_commands: {str, CommandCli}
    _args: list[str]

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        self._args = []

    # ------------------------------
    # Abstract/Virtual methods
    # ------------------------------

    def notify_parse_fail(self, arg: any) -> None:
        pass

    @abstractmethod
    def execute_command(self, index: int) -> int:
        pass

    # ------------------------------
    # Class interaction
    # ------------------------------

    def parse_args(self, args: list[str]):
        try:
            self._parse_args_internal(args)
        except Exception as e:
            self.notify_parse_fail(e)
            Logger().log_error(f"During argument parsing, error occurred: {e}", LogLevel.LOW_FREQ)

        return self

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
        index = 1
        self._args = args

        while index < len(args):
            index = self.execute_command(index)

        Logger().log_info("Finished parsing arguments", LogLevel.LOW_FREQ)

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


BaseCli.add_command(CommandCli(CommandType.UNIVERSAL, "help", BaseCli._help, BaseCli._help_help))
