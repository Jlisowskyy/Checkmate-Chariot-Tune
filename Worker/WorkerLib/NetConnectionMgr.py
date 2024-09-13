import json
import time
from threading import Thread
from time import sleep

import requests
import websockets
from pydantic import BaseModel

from Models.GlobalModels import CommandResult
from Models.WorkerModels import WorkerRegistration, WorkerUnregister, WorkerModel, WorkerAuth
from Utils.Logger import Logger, LogLevel
from Utils.SettingsLoader import SettingsLoader
from Worker.WorkerLib.WorkerComponents import WorkerComponents, StopType


class NetConnectionMgr:
    # ------------------------------
    # Class fields
    # ------------------------------

    _session_token: int | None
    _session_model: WorkerModel | None
    _session_host: str | None

    _socket_mgr: websockets.WebSocketClientProtocol | None
    _connection_thread: Thread | None
    _should_conn_thread_work: bool
    _is_connected_and_authenticated: bool

    _ka_thread: Thread | None
    _should_ka_thread_work: bool

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        self._session_token = None
        self._session_host = None
        self._session_model = None

        # Prepare conn thread
        self._connection_thread = None
        self._socket_mgr = None
        self._should_conn_thread_work = False
        self._is_connected_and_authenticated = False

        # Prepare KA thread
        self._should_ka_thread_work = True
        self._ka_thread = Thread(target=self._ka_thread_func)
        self._ka_thread.start()

    def destroy(self) -> None:
        # Abort ka thread
        self._should_ka_thread_work = False
        self._ka_thread.join()
        self._ka_thread = None

        if WorkerComponents().get_worker_process().get_stop_type() == StopType.abort_stop or not WorkerComponents().get_conn_mgr().is_registered():
            self.abort_connection_sync()
            return

        self._should_conn_thread_work = False
        self._is_connected_and_authenticated = False
        try:
            WorkerComponents().get_conn_mgr().unregister()
            self._connection_thread.join(SettingsLoader().get_settings().gentle_stop_timeout)

        except Exception as e:
            Logger().log_error(f"Failed to gently close connection with manager: {e}. Aborting...", LogLevel.LOW_FREQ)
            self.abort_connection_sync()

    # ------------------------------
    # Class interaction
    # ------------------------------

    def get_max_mem_str(self) -> str:
        return str(self._session_model.memoryMB) if self._session_model is not None else "UNSPECIFIED"

    def get_max_mem_mb(self) -> int:
        return self._session_model.memoryMB if self._session_model is not None else 0

    def get_max_cpus(self) -> int:
        return self._session_model.cpus if self._session_model is not None else 0

    def get_max_cpus_str(self) -> str:
        return str(self._session_model.cpus) if self._session_model is not None else "UNSPECIFIED"

    def get_registered_name(self) -> str:
        return self._session_model.name if self._session_model is not None else "UNREGISTERED"

    def get_registered_token(self) -> str:
        return str(hex(self._session_token)) if self._session_token is not None else "UNREGISTERED"

    def get_registered_str(self) -> str:
        return "REGISTERED" if self.is_registered() else "NOT REGISTERED"

    def get_connection_str(self) -> str:
        return "CONNECTED" if self.is_connected() else "NOT CONNECTED"

    def get_mem_usage(self) -> int:
        raise NotImplementedError("Method not implemented")

    def gem_cpu_usage(self) -> int:
        raise NotImplementedError("Method not implemented")

    def get_cpu_usage_str(self) -> str:
        raise NotImplementedError("Method not implemented")

    def get_mem_usage_str(self) -> str:
        raise NotImplementedError("Method not implemented")

    def abort_connection_sync(self) -> None:
        Logger().log_info("Started connection with Manager abort", LogLevel.LOW_FREQ)

        self._should_conn_thread_work = False

        if self._socket_mgr is not None:
            self._socket_mgr.close()
            self._socket_mgr = None

        self._connection_thread.join()
        self._connection_thread = None

        Logger().log_info("Connection with Manager aborted correctly", LogLevel.LOW_FREQ)

    def bond_connection_async(self, host: str) -> None:
        if self.is_connected():
            Logger().log_warning(f"New \"bond_connection\" was done, when there was already connection working",
                                 LogLevel.LOW_FREQ)
            self.abort_connection_sync()

        self._should_conn_thread_work = True
        # self._are_new_jobs_globally_blocked = False TODO
        self._connection_thread = Thread(target=self._connection_thread, args=host)

        Logger().log_info("Starting connection with manager", LogLevel.LOW_FREQ)
        self._connection_thread.start()

    def is_connected(self) -> bool:
        return self._is_connected_and_authenticated

    def is_registered(self) -> bool:
        return self._session_token is not None and self._session_model is not None

    def register(self, host: str, register_request: WorkerModel) -> None:
        url = f"{host}/worker/register"
        response = NetConnectionMgr.send_request(requests.post, url, register_request)

        model_response = WorkerRegistration.model_validate(response.json())
        NetConnectionMgr.validate_response(model_response.result)

        self._session_token = model_response.session_token
        self._session_host = host
        self._session_model = register_request

        self._register_internal()

    def get_connected_host(self) -> str:
        if not self.is_connected():
            raise Exception("Worker is not connected to any host at the moment")
        return self._session_host

    def unregister(self) -> None:
        retries = 0

        request = self.prepare_unregister_request()
        host = self.get_connected_host()
        url = f"{host}/worker/unregister"
        response = None

        self._session_token = None
        self._session_host = None
        self._session_model = None

        while retries < SettingsLoader().get_settings().unregister_retries:
            try:
                response = NetConnectionMgr.send_request(requests.delete, url, request)
                break
            except Exception as e:
                Logger().log_info(
                    f"Unregister request failed, trying again with retry num: {retries + 1}, error trace: {e}",
                    LogLevel.MEDIUM_FREQ)

            time.sleep(SettingsLoader().get_settings().retry_timestep)
            retries += 1

        if response is not None:
            NetConnectionMgr.validate_response(CommandResult.model_validate(response.json()))

    def prepare_unregister_request(self) -> WorkerUnregister:
        if not self.is_registered():
            raise Exception("Worker is not registered!")

        return WorkerUnregister(name=self._session_model.name, session_token=self._session_token)

    @staticmethod
    def validate_response(result: CommandResult) -> None:
        if result.result != "SUCCESS":
            raise Exception(f"Failed on Manager end-point with error: {result.result}")

    def prepare_worker_auth(self) -> BaseModel:
        if not self.is_registered():
            raise Exception("Worker is not registered!")

        return WorkerAuth(session_token=self._session_token, name=self._session_model.name)

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

    def _ka_thread_func(self) -> None:
        execution_time = 0

        while self._should_ka_thread_work:
            ka_interval = SettingsLoader().get_settings().ka_interval
            sleep(max(0, ka_interval - execution_time))
            prev_run_execution_time = execution_time
            execution_time = max(0, execution_time - ka_interval)

            if not self.is_connected():
                continue

            timestamp_before = time.perf_counter_ns()
            auth = self.prepare_worker_auth()

            try:
                Logger().log_info(
                    f"Sending KA to currently connected host,"
                    f" after previous KA which processing took {prev_run_execution_time}...",
                    LogLevel.MEDIUM_FREQ)

                url = f"{self.get_connected_host()}/worker/bump_ka"
                response = self.send_request(requests.post, url, auth)
                NetConnectionMgr.validate_response(response.json())

                Logger().log_info("KA correctly sent to current host!", LogLevel.MEDIUM_FREQ)
            except Exception as e:
                Logger().log_error(f"Failed to send KA to the manager: {e}", LogLevel.MEDIUM_FREQ)

            timestamp_after = time.perf_counter_ns()

            execution_time += timestamp_after - timestamp_before

    # TODO:
    def _register_internal(self) -> None:
        pass

    def _process_msg(self, msg: str) -> str:
        parsed = json.loads(msg)

        proc = parsed['method']
        kwargs = parsed['kwargs']

        result = getattr(self, proc)(**kwargs)

        return result

    def _conn_msg_life_cycle(self, attempt: int) -> int:
        try:
            self._authenticate()
        except Exception as e:
            Logger().log_error(f"Failed to authenticate with Manager: {e}", LogLevel.LOW_FREQ)
            return attempt + 1

        # save connected state
        self._is_connected_and_authenticated = True

        while self._should_conn_thread_work:
            try:
                msg = self._socket_mgr.recv()
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
                self._socket_mgr.send(response)
                Logger().log_info("Response to Manager correctly send", LogLevel.HIGH_FREQ)
            except Exception as e:
                Logger().log_error(f"Failed to send response to Manager: {e}", LogLevel.LOW_FREQ)
                break

        return attempt + 1

    def _authenticate(self) -> None:
        auth = WorkerComponents().get_conn_mgr().prepare_worker_auth().model_dump_json()

        Logger().log_info(f"Sending auth msg to manager: {auth}", LogLevel.MEDIUM_FREQ)
        self._socket_mgr.send(auth)

        rsp = self._socket_mgr.recv()
        Logger().log_info(f"Received auth response from manager: {rsp}", LogLevel.MEDIUM_FREQ)

        result = CommandResult.model_validate(rsp)

        if result.result != "SUCCESS":
            raise Exception(f"Auth process failed: {result.result}")

    async def _conn_thread(self, host: str):
        attempt = 0

        while self._should_conn_thread_work and attempt < SettingsLoader().get_settings().connection_retries:

            if attempt != 0:
                Logger().log_info(
                    f"Performing another attempt to work with test websocket after 1 second."
                    f" Current attempt: {attempt + 1}",
                    LogLevel.MEDIUM_FREQ)
                time.sleep(1)

            try:
                self._socket_mgr = await websockets.connect(f"{host}/perform-test")
                Logger().log_info(f"Connected with host: {host}", LogLevel.MEDIUM_FREQ)
                attempt = self._conn_msg_life_cycle(attempt)
                self._socket_mgr = None
            except Exception as e:
                Logger().log_error(f"Failed to connect with host {host}: {e}", LogLevel.MEDIUM_FREQ)
                attempt += 1

    @staticmethod
    def prepare_success_response() -> str:
        return json.dumps({"status": "SUCCESS"})
