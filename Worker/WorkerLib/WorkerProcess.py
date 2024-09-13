import json
import socket
import time
from threading import Thread, Semaphore
from typing import Callable

from Utils.Logger import Logger, LogLevel
from Utils.SettingsLoader import SettingsLoader
from .CliTranslator import CliTranslator
from .LockFile import LockFile, LOCK_FILE_PATH
from .WorkerComponents import StopType
from Utils.Helpers import get_pretty_time_spent_string_from_seconds, convert_ns_to_s


class WorkerProcess:
    # ------------------------------
    # Class fields
    # ------------------------------

    _stop_type: StopType

    _creation_time: int

    _should_threads_work: bool
    _stop_sem: Semaphore

    _lock_file: LockFile

    _cli_thread: Thread
    _cli_socket: socket.socket

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self):
        self._lock_file = LockFile(LOCK_FILE_PATH)
        self._creation_time = time.perf_counter_ns()
        self._stop_type = StopType.gentle_stop

        if not self._lock_file.lock_file_safe():
            raise Exception(f"[ ERROR ] Failed to lock file at {LOCK_FILE_PATH}. Aborting...")

        self._should_threads_work = False

        Logger().log_info("Created Worker Process instance", LogLevel.LOW_FREQ)

    def destroy(self):
        self._should_threads_work = False

        # Cleanup CLI connection thread
        self._cli_socket.close()
        self._cli_thread.join()

        self._lock_file.unlock_file()
        Logger().log_info("Correctly destroyed Worker Process instance", LogLevel.LOW_FREQ)

    # ------------------------------
    # Class interaction
    # ------------------------------

    def get_uptime_str(self) -> str:
        uptime_ns = time.perf_counter_ns() - self._creation_time
        uptime_s = convert_ns_to_s(uptime_ns)

        return get_pretty_time_spent_string_from_seconds(uptime_s)

    def start_processing(self) -> None:
        self._should_threads_work = True

        self._stop_sem = Semaphore(0)

        # Start CLI thread
        self._cli_thread = Thread(target=self._worker_cli_thread_guarded)
        self._cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._cli_thread.start()

    def set_stop_type(self, stop_type: StopType) -> None:
        self._stop_type = stop_type

    def wait_for_stop(self) -> None:
        self._stop_sem.acquire()

    def stop_processing(self) -> None:
        self._stop_sem.release()\

    def get_stop_type(self) -> StopType:
        return self._stop_type

    # ------------------------------
    # Private methods
    # ------------------------------

    @staticmethod
    def _thread_guard(func: Callable):
        tries = SettingsLoader().get_settings().thread_retries

        while tries > 0:
            try:
                func()
                break
            except Exception as e:
                tries -= 1

                react_str = f"Trying to restart the function. Remaining retries: {tries}" if tries > 0 \
                    else "All retries have been used. Aborting execution..."
                Logger().log_error(f"Thread func: {func.__name__} failed: {e}. {react_str}", LogLevel.LOW_FREQ)
                time.sleep(0.1)

        Logger().log_info("Thread stopped...", LogLevel.LOW_FREQ)

    def _worker_cli_try_catch_guard(self, call: Callable) -> any:
        try:
            return call()
        except Exception as e:
            if self._should_threads_work:
                Logger().log_error(f"Failed to process socket operation {call} because of error: {e}", LogLevel.LOW_FREQ)
            return None

    def _worker_cli_thread(self) -> None:
        self._cli_socket.bind(("localhost", SettingsLoader().get_settings().process_port))
        self._cli_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._cli_socket.listen()
        self._cli_socket.settimeout(5)

        while self._should_threads_work:
            result = self._worker_cli_try_catch_guard(self._cli_socket.accept)
            if result is None:
                continue

            conn, addr = result

            Logger().log_info(f"Received connection from: {addr}", LogLevel.MEDIUM_FREQ)
            data = self._worker_cli_try_catch_guard(conn.recv(1024).decode)
            if data is None:
                continue

            Logger().log_info(f"Received command payload: {data}", LogLevel.MEDIUM_FREQ)
            try:
                cli_translator = CliTranslator()
                cli_translator.parse_args(json.loads(data)["args"])
                response = f"SUCCESS: {cli_translator.get_response()}"
            except Exception as e:
                msg = f"Failed to parse or process command : {e}"
                Logger().log_error(msg, LogLevel.LOW_FREQ)
                response = msg

            try:
                conn.sendall(response.encode())
                conn.close()
            except Exception as e:
                Logger().log_error(f"Failed to send response to client: {e}", LogLevel.LOW_FREQ)

    def _worker_cli_thread_guarded(self):
        WorkerProcess._thread_guard(self._worker_cli_thread)
