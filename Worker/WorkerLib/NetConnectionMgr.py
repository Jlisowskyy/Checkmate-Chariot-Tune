import json
import time
from threading import Thread

import requests
import websockets
from pydantic import BaseModel

from Models.GlobalModels import CommandResult
from Models.WorkerModels import WorkerRegistration, WorkerUnregister, WorkerModel, WorkerAuth
from Utils.Logger import Logger, LogLevel
from Utils.SettingsLoader import SettingsLoader
from Worker.WorkerLib.WorkerComponents import WorkerComponents


class NetConnectionMgr:
    # ------------------------------
    # Class fields
    # ------------------------------

    _session_token: int | None
    _session_model: WorkerModel | None
    _session_host: str | None

    _connection_thread: Thread | None
    _should_conn_thread_work: bool

    # TODO: KA thread

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self):
        self._session_token = None
        self._session_host = None
        self._session_model = None
        self._connection_thread = None
        self._should_conn_thread_work = False

    # ------------------------------
    # Class interaction
    # ------------------------------

    def abort_connection_sync(self) -> None:
        Logger().log_info("Started connection with Manager abort", LogLevel.LOW_FREQ)

        self._should_conn_thread_work = False
        self._connection_thread.join()
        self._connection_thread = None

        Logger().log_info("Connection with Manager aborted correctly", LogLevel.LOW_FREQ)

    def bond_connection_async(self, host: str) -> None:
        if self.is_connected():
            Logger().log_warning(f"New \"bond_connection\" was done, when there was already connection working",
                                 LogLevel.LOW_FREQ)
            self.abort_connection_sync()

        self._should_conn_thread_work = True
        self._are_new_jobs_globally_blocked = False
        self._connection_thread = Thread(target=self._connection_thread, args=host)

        Logger().log_info("Starting connection with manager", LogLevel.LOW_FREQ)
        self._connection_thread.start()

    def is_connected(self) -> bool:
        return self._session_host is not None

    def is_registered(self) -> bool:
        return self._session_token is not None and self._session_model is not None

    def register(self, host: str, register_request: WorkerModel, register_response: WorkerRegistration) -> None:
        NetConnectionMgr.validate_response(register_response.result)

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

    def prepare_worker_auth(self) -> str:
        if not self.is_registered():
            raise Exception("Worker is not registered!")

        return WorkerAuth(session_token=self._session_token, name=self._session_model.name).model_dump_json()

    @staticmethod
    def send_request(command_type, url: str, model: BaseModel) -> requests.Response:
        headers = {
            "Content-Type": "application/json",
        }

        Logger().log_info(f"Sending request to {url} with payload: {model.model_dump_json()}",
                          LogLevel.MEDIUM_FREQ)
        result = command_type(url, json=model.model_dump(), headers=headers)

        Logger().log_info(f"Received response: {result.json()}", LogLevel.MEDIUM_FREQ)

        return result

    # ------------------------------
    # Private methods
    # ------------------------------

    def _register_internal(self) -> None:
        pass

    def _process_msg(self, msg: str) -> str:
        parsed = json.loads(msg)

        proc = parsed['method']
        kwargs = parsed['kwargs']

        result = getattr(self, proc)(**kwargs)

        return result

    def _conn_msg_life_cycle(self, sc, attempt: int) -> int:
        while self._should_conn_thread_work:
            try:
                self._authenticate(sc)
            except Exception as e:
                Logger().log_error(f"Failed to authenticate with Manager: {e}", LogLevel.LOW_FREQ)
                break

            try:
                msg = sc.recv()
                Logger().log_info(f"Received message from test socket: {msg}", LogLevel.HIGH_FREQ)
                attempt = 0
            except Exception as e:
                Logger().log_error(f"Exception occurred during test websocket was receiving msg: {e}",
                                   LogLevel.LOW_FREQ)
                break

            try:
                response = self._process_msg(msg)
                Logger().log_info(f"Prepared response for last msg: {response}", LogLevel.HIGH_FREQ)
            except Exception as e:
                Logger().log_error(f"Failed to process msg received from Manager: {e}", LogLevel.LOW_FREQ)
                break

            try:
                sc.send(response)
                Logger().log_info("Response to Manager correctly send", LogLevel.HIGH_FREQ)
            except Exception as e:
                Logger().log_error(f"Failed to send response to Manager: {e}", LogLevel.LOW_FREQ)
                break

        return attempt + 1

    def _authenticate(self, sc) -> None:
        auth = WorkerComponents().get_worker_cli().prepare_worker_auth()

        Logger().log_info(f"Sending auth msg to manager: {auth}", LogLevel.MEDIUM_FREQ)
        sc.send(auth)

        rsp = sc.recv()
        Logger().log_info(f"Received auth response from manager: {rsp}", LogLevel.MEDIUM_FREQ)

        result = CommandResult.model_validate(rsp)

        if result.result != "SUCCESS":
            raise Exception(f"Auth process failed: {result.result}")

    def _conn_thread(self, host: str):
        attempt = 0

        while self._should_conn_thread_work and attempt < SettingsLoader().get_settings().connection_retries:

            if attempt != 0:
                Logger().log_info(
                    f"Performing another attempt to work with test websocket after 1 second."
                    f" Current attempt: {attempt + 1}",
                    LogLevel.MEDIUM_FREQ)
                time.sleep(1)

            try:
                with websockets.connect(f"{host}/perform-test") as websocket:
                    Logger().log_info(f"Connected with host: {host}", LogLevel.MEDIUM_FREQ)
                    attempt = self._conn_msg_life_cycle(websocket, attempt)
            except Exception as e:
                Logger().log_error(f"Failed to connect with host {host}: {e}", LogLevel.MEDIUM_FREQ)
                attempt += 1

    @staticmethod
    def _prepare_success_response() -> str:
        return json.dumps({"status": "SUCCESS"})
