from ProjectInfo.ProjectInfo import ProjectInfoInstance

import requests
from Models.WorkerModels import WorkerModel


class CliTranslator:
    _args: list[str]

    def __init__(self):
        pass

    def parse_args(self, args: list[str]):
        try:
            self._parse_args_internal(args)
        except Exception as e:
            print(f"[ ERROR ] During argument parsing error occurred:\n\t{e}")

        return self

    def parse_stdin(self):
        return self

    def _parse_args_internal(self, args: list[str]) -> None:
        index = 1
        self._args = args

        while index < len(args):
            index = self._execute_command(index)

    def _execute_command(self, index: int) -> int:
        command = self._args[index].strip()

        if not command.startswith("--"):
            raise Exception(f"Expected command starting with: \"--\", received \"{command}\"")
        command = command[2:].strip()

        if command not in self.COMMANDS:
            raise Exception(f"Command \"{command}\" not supported")

        cli_cmd = self.COMMANDS[command]

        try:
            return cli_cmd(self, index + 1)
        except Exception as e:
            self._display_help(command)
            raise Exception(f"Command execution: \"{command}\", failed by reason:\n\t\t{e}")

    def _display_help(self, command: str) -> None:
        if command in self.COMMAND_HELP:
            print("Providing command description:")
            self.COMMAND_HELP[command]()

    @staticmethod
    def _is_command(arg: str) -> bool:
        return arg.strip().startswith("--")

    def _parse_options(self, index: int) -> [int, dict[str, str]]:
        rv = dict[str, str]()

        while index < len(self._args) and not CliTranslator._is_command(self._args[index]):
            arg = self._args[index].strip()
            split = arg.split("=", 1)

            if len(split) == 1:
                raise Exception(f"Expected key-value pair written as \"key\"=\"value\", received {arg} ")

            rv[split[0]] = split[1]
            index += 1

        return [index, rv]

    @staticmethod
    def _extract_option_guarded(options: dict[str, str], option: str) -> str:
        if option not in options:
            raise Exception(f"Option \"{option}\" is expected to be provided")
        return options[option]

    @staticmethod
    def _extract_option_not_guarded(options: dict[str, str], option: str) -> str:
        if option not in options:
            return ""
        return options[option]

    def _help(self, index: int) -> int:
        print("HELP COMMAND")
        return index

    def _version(self, index: int) -> int:
        ProjectInfoInstance.display_info("Worker")
        return index

    def _connect(self, index: int) -> int:
        [index, options] = self._parse_options(index)

        host = CliTranslator._extract_option_guarded(options, "host")
        name = CliTranslator._extract_option_guarded(options, "name")

        try:
            opt = CliTranslator._extract_option_not_guarded(options, "cpus")
            cpus = int(opt) if opt != "" else 1
            opt = CliTranslator._extract_option_not_guarded(options, "memoryMB")
            memory_mb = int(opt) if opt != "" else 128
        except Exception as e:
            raise Exception(f"Unable to parse option \"{e}\"")

        version = ProjectInfoInstance.get_current_version()

        model = WorkerModel(name=name, cpus=cpus, memoryMB=memory_mb, version=version)
        url = f"{host}/worker/register"
        headers = {
            "Content-Type": "application/json",
        }

        response = requests.post(url, json=model.model_dump(), headers=headers)

        print(response.json())

        return index

    @staticmethod
    def _connect_help() -> None:
        help_str = ("command syntax: --connect \"key1=value1\" \"key2=value2\" ...\n"
                    "Mandatory options:\n"
                    "\thost - defines url to the Manager endpoint\n"
                    "\tname - definition of name for the worker instance\n"
                    "Not mandatory options:\n"
                    "\tcpus - number of CPU cores to use - default = 1\n"
                    "\tmemoryMB - amount of memory to use - default = 128")
        print(help_str)

    def _log_level(self, index: int) -> int:
        pass

    COMMANDS = {
        "help": _help,
        "version": _version,
        "connect": _connect,
    }

    COMMAND_HELP = {
        "connect": _connect_help
    }
