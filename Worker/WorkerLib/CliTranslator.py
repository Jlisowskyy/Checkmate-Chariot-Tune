from ProjectInfo.ProjectInfo import ProjectInfoInstance
from Models.WorkerModels import WorkerModel, WorkerRegistration
from Models.GlobalModels import CommandResult
from Utils.Logger import Logger, LogLevel
from .WorkerCLI import WorkerCLI
from Utils.SettingsLoader import SettingsLoader

import requests
import time
import subprocess
import os


class CliTranslator:
    # ------------------------------
    # Class fields
    # ------------------------------

    _args: list[str]
    _worker: WorkerCLI

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, worker: WorkerCLI):
        self._worker = worker

    # ------------------------------
    # Class interaction
    # ------------------------------

    def parse_args(self, args: list[str]):
        try:
            self._parse_args_internal(args)
        except Exception as e:
            print(f"[ ERROR ] During argument parsing error occurred:\n\t{e}")

        return self

    def parse_stdin(self):
        return self

    # ------------------------------
    # Private methods
    # ------------------------------

    def _set_log_level(self, index: int) -> int:
        if index >= len(self._args):
            raise Exception("LEVEL should bo provided")

        level = self._args[index]

        try:
            level = LogLevel[level]
        except Exception as e:
            raise Exception("Provided wrong log level")

        Logger().set_log_level(level)

        return index + 1

    @staticmethod
    def _set_log_level_help():
        print("syntax: --set_log_level LEVEL\n\t"
              "Changes log level of logger\n\t"
              "Available log levels:\n\t"
              "LOW\n\t"
              "MEDIUM\n\t"
              "HIGH")

    def _parse_args_internal(self, args: list[str]) -> None:
        index = 1
        self._args = args

        while index < len(args):
            index = self._execute_command(index)

        Logger().log_info("Finished parsing arguments", LogLevel.LOW_FREQ)

    def _execute_command(self, index: int) -> int:
        command = self._args[index].strip()

        if not command.startswith("--"):
            raise Exception(f"Expected command starting with: \"--\", received \"{command}\"")
        command = command[2:].strip()

        if command not in self.COMMANDS:
            raise Exception(f"Command \"{command}\" not supported")

        cli_cmd = self.COMMANDS[command]

        try:
            Logger().log_info(f"Finished parsing command: {command} as argument", LogLevel.MEDIUM_FREQ)
            return cli_cmd(self, index + 1)
        except Exception as e:
            self._display_help(command)
            msg = f"Command execution: \"{command}\", failed by reason: {e}"

            Logger().log_error(msg, LogLevel.LOW_FREQ)
            raise Exception(msg)

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
        if index < len(self._args) and not CliTranslator._is_command(self._args[index]):
            command = self._args[index].strip()
            if command not in self.COMMAND_HELP:
                raise Exception(f"Help for command \"{command}\" not supported")
            self.COMMAND_HELP[command]()
            return index + 1
        else:
            print("Available commands:")
            for command in self.COMMANDS.keys():
                print(f"\t{command}")
            print("Type \"--help COMMAND_NAME\" to get more details on the command")
            return index

    @staticmethod
    def _help_help() -> None:
        print("syntax: --help COMMAND_NAME\n\tDisplay detailed help for the given command"
              "--help\n\t to display list of available commands")

    def _version(self, index: int) -> int:
        ProjectInfoInstance.display_info("Worker")
        return index

    @staticmethod
    def _version_help() -> None:
        print("syntax: --version\n\tDisplay the version of the Worker")

    def _connect(self, index: int) -> int:
        [index, options] = self._parse_options(index)

        if self._worker.is_registered():
            raise Exception("Worker is already registered to manager")

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
        response = WorkerCLI.send_request(requests.post, url, model)

        self._worker.register(host, model, WorkerRegistration.model_validate(response.json()))

        Logger().log_info(f"Correctly registered worker", LogLevel.LOW_FREQ)

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

    def _unregister(self, index: int) -> int:
        retries = 0

        if not self._worker.is_registered():
            raise Exception("Worker is not registered to any manager")

        request = self._worker.prepare_unregister_request()
        host = self._worker.get_connected_host()
        url = f"{host}/worker/unregister"
        self._worker.unregister()
        response = None

        while retries < SettingsLoader().get_settings().unregister_retries:
            try:
                response = WorkerCLI.send_request(requests.delete, url, request)
                break
            except Exception as e:
                Logger().log_info(
                    f"Unregister request failed, trying again with retry num: {retries + 1}, error trace: {e}",
                    LogLevel.MEDIUM_FREQ)

            time.sleep(SettingsLoader().get_settings().retry_timestep)
            retries += 1

        if response is not None:
            WorkerCLI.validate_response(CommandResult.model_validate(response.json()))
        return index

    @staticmethod
    def _unregister_help() -> None:
        print("syntax: --unregister\n\tCommand unregisters worker from the Manager node, stopping all ongoing jobs")

    def _deploy(self, index: int) -> int:
        process = subprocess.Popen(['python', ''])

        Logger().log_info("Worker process correctly deployed", LogLevel.LOW_FREQ)

        return index

    @staticmethod
    def _deploy_help() -> None:
        print(
            "syntax: --deploy\n\t"
            "Command will try to create a background process that will be responsible\n"
            "for all job processing"
        )

    COMMANDS = {
        "help": _help,
        "version": _version,
        "connect": _connect,
        "unregister": _unregister,
        "set_log_level": _set_log_level,
        "deploy": _deploy,
    }

    COMMAND_HELP = {
        "connect": _connect_help,
        "version": _version_help,
        "help": _help_help,
        "unregister": _unregister_help,
        "set_log_level": _set_log_level_help,
        "deploy": _deploy_help,
    }
