import sys
import socket
import time
import json
from typing import Callable
from threading import Thread, Lock, get_ident, Semaphore

from Utils.SettingsLoader import SettingsLoader
from .WorkerCLI import WorkerCLI
from .LockFile import LockFile, LOCK_FILE_PATH
from Utils.Logger import Logger, LogLevel
from .CliTranslator import CliTranslator


class WorkerProcess:
    # ------------------------------
    # Class fields
    # ------------------------------

    _should_threads_work: bool
    _stop_sem: Semaphore

    _lock_file: LockFile
    _worker_cli: WorkerCLI

    _cli_thread: Thread
    _cli_socket: socket.socket

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self):
        self._lock_file = LockFile(LOCK_FILE_PATH)

        if not self._lock_file.lock_file_safe():
            raise Exception(f"[ ERROR ] Failed to lock file at {LOCK_FILE_PATH}. Aborting...")

        self._should_threads_work = False
        self._worker_cli = WorkerCLI()

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

        Logger().log_info("Thread stopped", LogLevel.LOW_FREQ)

    def _worker_cli_thread(self) -> None:
        self._cli_socket.bind(("localhost", SettingsLoader().get_settings().process_port))
        self._cli_socket.listen()
        self._cli_socket.settimeout(5)

        while self._should_threads_work:
            try:
                conn, addr = self._cli_socket.accept()
            except Exception as e:
                Logger().log_error(f"Failed to accept incoming connection: {e}", LogLevel.MEDIUM_FREQ)
                continue

            Logger().log_info(f"Received connection from: {addr}", LogLevel.MEDIUM_FREQ)
            try:
                with conn:
                    data = conn.recv(1024).decode()
                    Logger().log_info(f"Received command payload: {data}", LogLevel.MEDIUM_FREQ)

                    cli_translator = CliTranslator(self._worker_cli, self._stop_sem)
                    cli_translator.parse_args(json.loads(data)["args"])
            except Exception as e:
                Logger().log_error(f"Failed to translate message: {data}. Root of the problem: {e}", LogLevel.LOW_FREQ)

    def _worker_cli_thread_guarded(self):
        WorkerProcess._thread_guard(self._worker_cli_thread)
