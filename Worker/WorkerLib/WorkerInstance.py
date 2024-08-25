from Utils.GlobalObj import GlobalObj
from Models.WorkerModels import WorkerRegistration, WorkerUnregister, WorkerModel
from Models.GlobalModels import CommandResult
from pydantic import BaseModel
from Utils.Logger import Logger, LogLevel

import requests


class WorkerInstance(metaclass=GlobalObj):
    # ------------------------------
    # Class fields
    # ------------------------------

    _session_token: int | None
    _session_model: WorkerModel | None
    _session_host: str | None

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self):
        self._session_token = None
        self._session_host = None
        self._session_model = None

    # ------------------------------
    # Class interaction
    # ------------------------------

    def is_connected(self) -> bool:
        return self._session_host is not None

    def is_registered(self) -> bool:
        return self._session_token is not None

    def register(self, host: str, register_request: WorkerModel, register_response: WorkerRegistration) -> None:
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

        return WorkerUnregister(name=self._session_model.name, token=self._session_token)

    def validate_unregister_response(self, result: CommandResult) -> None:
        pass

    @staticmethod
    def send_request(url: str, model: BaseModel) -> requests.Response:
        headers = {
            "Content-Type": "application/json",
        }

        Logger().log_info(f"Sending register request to {url} with payload: {model.model_dump_json()}",
                          LogLevel.LOW_FREQ)
        return requests.post(url, json=model.model_dump(), headers=headers)

    # ------------------------------
    # Private methods
    # ------------------------------

    def _register_internal(self) -> None:
        pass
