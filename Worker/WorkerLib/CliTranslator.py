import time

import requests

from Models.GlobalModels import CommandResult
from Models.WorkerModels import WorkerModel, WorkerRegistration
from ProjectInfo.ProjectInfo import ProjectInfoInstance
from Utils.Logger import Logger, LogLevel
from Utils.SettingsLoader import SettingsLoader
from .BaseCli import BaseCli, CommandCli, CommandType
from .NetConnectionMgr import NetConnectionMgr
from .WorkerComponents import WorkerComponents, BlockType


class CliTranslator(BaseCli):
    # ------------------------------
    # Class fields
    # ------------------------------

    _response: str

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self):
        super().__init__()
        self._response = "FAILED"

    # ------------------------------
    # Class interaction
    # ------------------------------

    def get_response(self) -> str:
        return self._response

    # ---------------------------------------------
    # Abstract/Virtual methods implementation
    # ---------------------------------------------

    def parse_single_command(self, index: int) -> int:
        cli_cmd = self._extract_command(index)

        if cli_cmd.command_type == CommandType.FRONTEND:
            raise Exception(f"Received command intended for frontend CLI only")

        return self._execute_command(cli_cmd, index)

    # ------------------------------
    # Private methods
    # ------------------------------

    # ------------------------------
    # Available Commands
    # ------------------------------

    def _connect_command(self, index: int) -> int:
        [index, options] = self.parse_options(index)

        if WorkerComponents().get_conn_mgr().is_registered():
            raise Exception("Worker is already registered to manager")

        host = CliTranslator.extract_option_guarded(options, "host")
        name = CliTranslator.extract_option_guarded(options, "name")

        try:
            opt = CliTranslator.extract_option_not_guarded(options, "cpus")
            cpus = int(opt) if opt != "" else 1
            opt = CliTranslator.extract_option_not_guarded(options, "memoryMB")
            memory_mb = int(opt) if opt != "" else 128
        except Exception as e:
            raise Exception(f"Unable to parse options \"{e}\"")

        version = ProjectInfoInstance.get_current_version()

        model = WorkerModel(name=name, cpus=cpus, memoryMB=memory_mb, version=version)
        WorkerComponents().get_conn_mgr().register(host, model)

        Logger().log_info(f"Correctly registered worker", LogLevel.LOW_FREQ)
        self._response = "Correctly registered worker"

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

    def _unregister_command(self, index: int) -> int:
        if not WorkerComponents().get_conn_mgr().is_registered():
            raise Exception("Worker is not registered to any manager")

        WorkerComponents().get_conn_mgr().unregister()

        self._response = "Correctly unregistered worker"
        return index

    @staticmethod
    def _unregister_help() -> str:
        return "syntax: --unregister\n\tCommand unregisters worker from the Manager node, stopping all ongoing jobs"

    def _set_log_level_command(self, index: int) -> int:
        if index >= len(self._args):
            raise Exception("LEVEL should bo provided")

        level = self._args[index]

        try:
            level = LogLevel[level]
        except Exception as e:
            raise Exception(f"Provided wrong log level: {e}")

        Logger().set_log_level(level)
        self._response = "Correctly changed log level"

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

    def _stop_command(self, index: int) -> int:
        WorkerComponents().get_worker_process().stop_processing()
        self._response = "Initialized worker stop process"
        return index

    @staticmethod
    def _stop_help() -> str:
        return ("syntax: --stop_worker\n\t"
                "Gently shutdowns background worker process")

    def _abort_command(self, index: int) -> int:
        WorkerComponents().get_worker_process().stop_processing()
        self._response = "Initialized worker abort process"
        return index

    @staticmethod
    def _abort_help() -> str:
        return ("syntax: --abort_worker\n\t"
                "Brutally shutdowns background worker process with guaranteed state hardened")

    def _abort_jobs_command(self, index: int) -> int:
        task_name = self._args[index] if index < len(self._args) else ""
        WorkerComponents().get_test_job_mgr().abort_jobs(task_name)

        self._response = "Jobs abort process started"
        return index + 1 if index < len(self._args) else index

    @staticmethod
    def _abort_jobs_help() -> str:
        return ("syntax: --abort_jobs TASK_NAME\n\t"
                "Command immediately stops all ongoing TestJobs,"
                "where TASK_NAME if provided links to specific TestTask jobs")

    def _switch_jobs_block(self, index: int) -> int:
        [index, options] = self.parse_options(index)

        block_type = CliTranslator.extract_option_guarded(options, "type")
        task_name = CliTranslator.extract_option_not_guarded(options, "host_name")

        try:
            converted = BlockType[block_type]
        except Exception as e:
            raise Exception(f"Unable to parse block type \"{e}\"")

        WorkerComponents().get_test_job_mgr().block_new_jobs(converted, task_name)

        self._response = f"Correctly stopped new jobs for {"every task" if task_name == "" else task_name}"
        return index

    @staticmethod
    def _switch_jobs_block_help() -> str:
        return ("command syntax: --switch_jobs_block \"key1=value1\" \"key2=value2\" ...\n"
                "Mandatory options:\n"
                "\ttype - defines whether block should be enable or disabled provide \"enable\" or \"disable\"\n"
                "Not mandatory options:\n"
                "\thost_name - if empty all jobs are blocked if not only mentioned TestTask jobs are blocked\n")

    def _query_worker_state(self, index: int) -> int:
        worker_process_status = ("Worker state: Healthy\n"
                                 f"RAM assigned in MB: {WorkerComponents().get_conn_mgr().get_max_mem_str()}\n"
                                 f"RAM usage: NOT IMPLEMENTED\n"
                                 f"CPUs assigned: {WorkerComponents().get_conn_mgr().get_max_cpus_str()}\n"
                                 f"CPUs utilized: NOT IMPLEMENTED\n"
                                 "Worker last harden: NOT IMPLEMENTED\n"
                                 "Worker repo size: NOT IMPLEMENTED\n"
                                 f"Worker uptime: {WorkerComponents().get_worker_process().get_uptime_str()}\n"
                                 f"Settings loaded: {SettingsLoader().get_settings().model_dump_json(indent=2)}\n")

        test_jobs_mgr_status = ("Contained tasks: NOT IMPLEMENTED\n"
                                "Ongoing jobs count: NOT IMPLEMENTED\n"
                                "Completed jobs count: NOT IMPLEMENTED\n"
                                "Synced jobs count: NOT IMPLEMENTED\n"
                                "Blocked tasks: NOT IMPLEMENTED\n"
                                "Average job time: NOT IMPLEMENTED\n")

        connectivity_mgr_status = (f"Registration status: {WorkerComponents().get_conn_mgr().get_registered_str()}\n"
                                   f"Registered name: {WorkerComponents().get_conn_mgr().get_registered_name()}\n"
                                   f"Session token: {WorkerComponents().get_conn_mgr().get_registered_token()}\n"
                                   "Connection status: NOT IMPLEMENTED\n")

        self._response = f"\n{worker_process_status}\n{test_jobs_mgr_status}\n{connectivity_mgr_status}"

        return index

    @staticmethod
    def _query_worker_state_help() -> str:
        return ("command syntax: --query_worker_state\n\t"
                "Command simply displays all parameters of deployed worker")

    # ------------------------------
    # Commands registration
    # ------------------------------

    BaseCli.add_command(
        CommandCli(CommandType.BACKEND, "connect", _connect_command, _connect_help))
    BaseCli.add_command(
        CommandCli(CommandType.BACKEND, "unregister", _unregister_command, _unregister_help))
    BaseCli.add_command(
        CommandCli(CommandType.BACKEND, "set_log_level", _set_log_level_command, _set_log_level_help))
    BaseCli.add_command(
        CommandCli(CommandType.BACKEND, "stop_worker", _stop_command, _stop_help))
    BaseCli.add_command(
        CommandCli(CommandType.BACKEND, "abort_worker", _abort_command, _abort_help))
    BaseCli.add_command(
        CommandCli(CommandType.BACKEND, "switch_jobs_block", _switch_jobs_block, _switch_jobs_block_help))
    BaseCli.add_command(
        CommandCli(CommandType.BACKEND, "query_worker_state", _query_worker_state, _query_worker_state_help))
