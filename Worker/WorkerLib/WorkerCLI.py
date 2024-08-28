from Models.WorkerModels import WorkerRegistration, WorkerUnregister, WorkerModel
from Models.GlobalModels import CommandResult
from pydantic import BaseModel
from Utils.Logger import Logger, LogLevel
from .LockFile import LOCK_FILE_PATH, LockFile

import requests


class WorkerCLI:
    # ------------------------------
    # Class fields
    # ------------------------------

    _session_token: int | None
    _session_model: WorkerModel | None
    _session_host: str | None
    _lock_file: LockFile

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self):
        self._session_token = None
        self._session_host = None
        self._session_model = None
        self._lock_file = LockFile(LOCK_FILE_PATH)

    # ------------------------------
    # Class interaction
    # ------------------------------

    def is_deployed(self) -> bool:
        return self._lock_file.is_locked_process_existing()

    def is_connected(self) -> bool:
        return self._session_host is not None

    def is_registered(self) -> bool:
        return self._session_token is not None

    def register(self, host: str, register_request: WorkerModel, register_response: WorkerRegistration) -> None:
        WorkerCLI.validate_response(register_response.result)

        self._session_token = register_response.session_token
        self._session_host = host
        self._session_model = register_request

        self._register_internal()

    def get_connected_host(self) -> str:
        if not self.is_connected():
            raise Exception("Worker is not connected to any host at the moment")
        return self._session_host

    def unregister(self) -> None:
        self._session_token = None
        self._session_host = None
        self._session_model = None

    def prepare_unregister_request(self) -> WorkerUnregister:
        if not self.is_registered():
            raise Exception("Worker is not registered!")

        return WorkerUnregister(name=self._session_model.name, session_token=self._session_token)

    @staticmethod
    def validate_response(result: CommandResult) -> None:
        if result.result != "SUCCESS":
            raise Exception(f"Failed on Manager end-point with error: {result.result}")

    @staticmethod
    def send_request(command_type, url: str, model: BaseModel) -> requests.Response:
        headers = {
            "Content-Type": "application/json",
        }

        Logger().log_info(f"Sending request to {url} with payload: {model.model_dump_json()}",
                          LogLevel.LOW_FREQ)
        result = command_type(url, json=model.model_dump(), headers=headers)

        Logger().log_info(f"Received response: {result.json()}", LogLevel.LOW_FREQ)

        return result

    # ------------------------------
    # Private methods
    # ------------------------------

    def _register_internal(self) -> None:
        pass
