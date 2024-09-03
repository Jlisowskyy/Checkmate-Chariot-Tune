import errno
import json
import socket
import time
from threading import Thread, Semaphore
from typing import Callable

from Utils.Logger import Logger, LogLevel
from Utils.SettingsLoader import SettingsLoader
from .CliTranslator import CliTranslator
from .LockFile import LockFile, LOCK_FILE_PATH
from .WorkerComponents import WorkerComponents


class WorkerProcess:
    # ------------------------------
    # Class fields
    # ------------------------------

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

        if not self._lock_file.lock_file_safe():
            raise Exception(f"[ ERROR ] Failed to lock file at {LOCK_FILE_PATH}. Aborting...")

        self._should_threads_work = False

        Logger().log_info("Created Worker Process instance", LogLevel.LOW_FREQ)

    def destroy(self):
        self._lock_file.unlock_file()
        self._should_threads_work = False
        self._cli_socket.close()

        self._cli_thread.join()

        Logger().log_info("Correctly destroyed Worker Process instance", LogLevel.LOW_FREQ)

    # ------------------------------
    # Class interaction
    # ------------------------------

    def get_uptime_str(self) -> str:
        uptime_seconds = (time.perf_counter_ns() - self._creation_time) / (1000 * 1000 * 1000)

        days = int(uptime_seconds // (24 * 3600))
        hours = int((uptime_seconds % (24 * 3600)) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)

        # Pretty print the uptime
        uptime_str = []
        if days > 0:
            uptime_str.append(f"{days} day{'s' if days > 1 else ''}")
        if hours > 0:
            uptime_str.append(f"{hours} hour{'s' if hours > 1 else ''}")
        if minutes > 0:
            uptime_str.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
        if seconds > 0 or len(uptime_str) == 0:
            uptime_str.append(f"{seconds} second{'s' if seconds > 1 else ''}")

        return ', '.join(uptime_str)

    def start_processing(self):
        self._should_threads_work = True

        self._stop_sem = Semaphore(0)

        # Start CLI thread
        self._cli_thread = Thread(target=self._worker_cli_thread_guarded)
        self._cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._cli_thread.start()

    def wait_for_stop(self):
        self._stop_sem.acquire()

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

        Logger().log_info("Thread stopped...", LogLevel.LOW_FREQ)

    def _worker_cli_thread(self) -> None:
        self._cli_socket.bind(("localhost", SettingsLoader().get_settings().process_port))
        self._cli_socket.listen()
        self._cli_socket.settimeout(5)

        while self._should_threads_work:
            try:
                conn, addr = self._cli_socket.accept()
            except OSError as e:
                if e.errno != errno.EBADF or self._should_threads_work != False:
                    Logger().log_error(f"Failed to accept incoming connection: {e}", LogLevel.LOW_FREQ)
                continue
            except Exception as e:
                Logger().log_error(f"Failed to accept incoming connection: {e}", LogLevel.LOW_FREQ)
                continue

            Logger().log_info(f"Received connection from: {addr}", LogLevel.MEDIUM_FREQ)
            try:
                data = conn.recv(1024).decode()
            except Exception as e:
                Logger().log_error(f"Failed to translate message: {data}. Root of the problem: {e}", LogLevel.LOW_FREQ)
                continue

            Logger().log_info(f"Received command payload: {data}", LogLevel.MEDIUM_FREQ)
            try:
                cli_translator = CliTranslator(WorkerComponents().get_worker_cli(), self._stop_sem)
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
