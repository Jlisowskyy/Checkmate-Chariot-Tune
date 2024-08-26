from ProjectInfo.ProjectInfo import ProjectInfoInstance
from Models.WorkerModels import WorkerModel, WorkerRegistration
from Models.GlobalModels import CommandResult
from Utils.Logger import Logger, LogLevel
from .WorkerCLI import WorkerCLI
from Utils.SettingsLoader import SettingsLoader
from BaseCli import BaseCli, CommandCli, CommandType

import requests
import time
import subprocess
import os


class CliTranslator(BaseCli):
    # ------------------------------
    # Class fields
    # ------------------------------

    _worker: WorkerCLI

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, worker: WorkerCLI):
        super().__init__()
        self._worker = worker

    # ------------------------------
    # Class interaction
    # ------------------------------

    # ---------------------------------------------
    # Abstract/Virtual methods implementation
    # ---------------------------------------------

    def execute_command(self, index: int) -> int:
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

    # ------------------------------
    # Private methods
    # ------------------------------

    # ------------------------------
    # Available Commands
    # ------------------------------

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
    def _connect_help() -> str:
        help_str = ("command syntax: --connect \"key1=value1\" \"key2=value2\" ...\n"
                    "Mandatory options:\n"
                    "\thost - defines url to the Manager endpoint\n"
                    "\tname - definition of name for the worker instance\n"
                    "Not mandatory options:\n"
                    "\tcpus - number of CPU cores to use - default = 1\n"
                    "\tmemoryMB - amount of memory to use - default = 128")
        return help_str

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
    def _unregister_help() -> str:
        return "syntax: --unregister\n\tCommand unregisters worker from the Manager node, stopping all ongoing jobs"

    def _set_log_level(self, index: int) -> int:
        if index >= len(self._args):
            raise Exception("LEVEL should bo provided")

        level = self._args[index]

        try:
            level = LogLevel[level]
        except Exception as e:
            raise Exception(f"Provided wrong log level: {e}")

        Logger().set_log_level(level)

        return index + 1

    @staticmethod
    def _set_log_level_help() -> str:
        help_str = ("syntax: --set_log_level LEVEL\n\t"
                    "Changes log level of logger\n\t"
                    "Available log levels:\n\t"
                    "LOW\n\t"
                    "MEDIUM\n\t"
                    "HIGH")

        return help_str


BaseCli.add_command(
    CommandCli(CommandType.BACKEND, "connect", CliTranslator._connect, CliTranslator._connect_help))
BaseCli.add_command(
    CommandCli(CommandType.BACKEND, "unregister", CliTranslator._unregister, CliTranslator._unregister_help))
BaseCli.add_command(
    CommandCli(CommandType.BACKEND, "set_log_level", CliTranslator._set_log_level, CliTranslator._set_log_level_help))
