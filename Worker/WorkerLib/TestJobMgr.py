import time

from Utils.GlobalObj import GlobalObj
from Utils.Logger import Logger, LogLevel
from Utils.SettingsLoader import SettingsLoader
from .TestJob import TestJob

from threading import Thread
import websockets
import json


class TestJobMgr(metaclass=GlobalObj):
    # ------------------------------
    # Class fields
    # ------------------------------

    _connection_thread: Thread | None
    _should_conn_thread_work: bool

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        self._connection_thread = None
        self._should_conn_thread_work = False

    def destroy(self) -> None:
        self.process_abort()

    # ------------------------------
    # Class interaction
    # ------------------------------

    def abort_connection(self) -> None:
        self._should_conn_thread_work = False
        self._connection_thread.join()
        self._connection_thread = None

    def is_connected(self) -> bool:
        return self._connection_thread is not None

    def bond_connection(self, host: str) -> None:
        if self.is_connected():
            Logger().log_warning(f"New \"bond_connection\" was done, when there was already connection working",
                                 LogLevel.LOW_FREQ)
            self.abort_connection()

        self._should_conn_thread_work = True
        self._connection_thread = Thread(target=self._connection_thread, args=host)
        self._connection_thread.start()

    def abort_jobs(self) -> None:
        pass

    def process_abort(self) -> None:
        self.abort_jobs()
        self.abort_connection()

    # ------------------------------
    # Private methods
    # ------------------------------

    def _process_msg(self, msg: str) -> str:
        parsed = json.loads(msg)

        proc = parsed['method']
        kwargs = parsed['kwargs']

        result = getattr(self, proc)(**kwargs)

        return result

    def _conn_msg_life_cycle(self, sc, attempt: int) -> int:
        while self._should_conn_thread_work:
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

    # ------------------------------
    # RPC procedures
    # ------------------------------

    def _init_test_setup(self):
        pass
