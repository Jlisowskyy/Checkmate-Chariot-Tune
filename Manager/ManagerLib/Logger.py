from .GlobalObj import GlobalObj
from threading import Lock
from typing import TextIO
from datetime import datetime


class Logger(metaclass=GlobalObj):
    _log_stdout: bool
    _log_file_name: str
    _log_file: TextIO
    _lock: Lock

    def __init__(self, path: str, shouldLogStdIn: bool):
        self._log_stdout = shouldLogStdIn
        self._log_file_name = path
        self._lock = Lock()

        try:
            self._log_file = open(self._log_file_name, 'a')
        except Exception as e:
            raise Exception(f"Logger must be able to start to proceed further. Logger fail cause: {e}")

    @staticmethod
    def wrap_log(msg: str) -> str:
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        return f"[{date_str}] {msg}"

    @staticmethod
    def wrap_info(msg: str) -> str:
        return Logger.wrap_log(f"[ INFO ] {msg}")

    @staticmethod
    def wrap_error(msg: str) -> str:
        return Logger.wrap_log(f"[ ERROR ] {msg}")

    def log(self, msg: str) -> None:
        if self._log_stdout:
            print(msg)

        with self._lock:
            self._log_file.write(msg)

    def log_info(self, msg: str) -> None:
        self.log(Logger.wrap_info(msg))

    def log_error(self, msg: str) -> None:
        self.log(Logger.wrap_error(msg))
