import os
import time
from datetime import datetime
from enum import IntEnum
from threading import Lock, Thread, get_ident
from typing import TextIO

from .GlobalObj import GlobalObj


class LogLevel(IntEnum):
    LOW_FREQ = 0
    MEDIUM_FREQ = 1
    HIGH_FREQ = 2


class Logger(metaclass=GlobalObj):
    # ------------------------------
    # Class fields
    # ------------------------------

    _log_stdout: bool
    _log_file_name: str
    _log_file: TextIO
    _log_level: LogLevel
    _lock: Lock
    _io_flusher: Thread
    _should_flush: bool

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, path: str, shouldLogStdIn: bool, logLevel: LogLevel):
        self._log_stdout = shouldLogStdIn
        self._log_file_name = path
        self._lock = Lock()
        self._log_level = logLevel

        try:
            self._log_file = open(self._log_file_name, 'a')
        except Exception as e:
            raise Exception(f"Logger must be able to start to proceed further. Logger fail cause: {e}")

        self._should_flush = True
        self._io_flusher = Thread(target=self._io_flusher_thread)
        self._io_flusher.start()

        self.log_info("Logger started", LogLevel.LOW_FREQ)

    # ------------------------------
    # Class interaction
    # ------------------------------

    def destroy(self):
        self._should_flush = False
        self._io_flusher.join()

        self.log_info("Logger destroyed", LogLevel.LOW_FREQ)
        self._log_file.flush()
        self._log_file.close()

    def set_log_level(self, log_level: LogLevel) -> None:
        self._log_level = log_level
        self.log_info(f"Logger level set to: {log_level}", LogLevel.LOW_FREQ)

    @staticmethod
    def wrap_log(msg: str) -> str:
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        return f"{date_str} {msg}"

    @staticmethod
    def wrap_warning(msg: str) -> str:
        return Logger.wrap_log(Logger.wrap_thread(f"WARN  {msg}"))

    @staticmethod
    def wrap_info(msg: str) -> str:
        return Logger.wrap_log(Logger.wrap_thread(f"INFO  {msg}"))

    @staticmethod
    def wrap_error(msg: str) -> str:
        return Logger.wrap_log(Logger.wrap_thread(f"ERROR {msg}"))

    @staticmethod
    def wrap_thread(msg: str) -> str:
        return f" {get_ident()} {msg}"

    @staticmethod
    def wrap_freq(msg: str, log_level: LogLevel) -> str:
        return f" {log_level.name:12} {msg}"

    def log(self, msg: str, log_level: LogLevel) -> None:
        if log_level > self._log_level:
            return

        if self._log_stdout:
            print(msg)

        with self._lock:
            self._log_file.write(f"{msg}\n")

    def log_info(self, msg: str, log_level: LogLevel) -> None:
        self.log(Logger.wrap_info(Logger.wrap_freq(msg, log_level)), log_level)

    def log_error(self, msg: str, log_level: LogLevel) -> None:
        self.log(Logger.wrap_error(Logger.wrap_freq(msg, log_level)), log_level)

    def log_warning(self, msg: str, log_level: LogLevel) -> None:
        self.log(Logger.wrap_warning(Logger.wrap_freq(msg, log_level)), log_level)

    # ------------------------------
    # Private methods
    # ------------------------------

    def _io_flusher_thread(self):
        while self._should_flush:
            time.sleep(0.01)

            with self._lock:
                self._log_file.flush()
                os.fsync(self._log_file.fileno())
