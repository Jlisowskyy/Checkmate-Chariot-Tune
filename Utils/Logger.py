import inspect
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
    _log_level: LogLevel

    _log_file: TextIO

    _log_que_lock: Lock
    _io_flusher: Thread
    _should_flush: bool
    _log_que: list[str]

    _journal_path: str
    _journal_file: TextIO | None
    _journal_lock: Lock
    _journal_que: list[Exception]

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, path: str, shouldLogStdIn: bool, logLevel: LogLevel, error_journal_path: str = ""):
        # Base settings
        self._log_stdout = shouldLogStdIn

        # Logging settings
        self._log_file_name = path
        self._log_que_lock = Lock()
        self._log_level = logLevel
        self._log_que = []

        try:
            self._log_file = open(self._log_file_name, 'a')
        except Exception as e:
            raise Exception(f"Logger must be able to start to proceed further. Logger fail cause: {e}")

        # Error journal settings
        self._journal_path = error_journal_path
        self._journal_lock = Lock()
        self._journal_que = []

        if self._journal_path != "":
            try:
                self._journal_file = open(self._journal_path, 'a')
            except Exception as e:
                raise Exception(
                    f"Error journal must be able to start to proceed further. Error journal fail cause: {e}")
        else:
            self._journal_file = None

        # Start flushing thread
        self._should_flush = True
        self._io_flusher = Thread(target=self._io_flusher_thread)
        self._io_flusher.start()

        self.log_info("Logger started", LogLevel.LOW_FREQ)

    # ------------------------------
    # Class interaction
    # ------------------------------

    def save_error_to_journal(self, error: Exception) -> None:
        if self._journal_file is None:
            return

        with self._journal_lock:
            self._journal_que.append(error)

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
        return Logger.wrap_log(Logger.wrap_thread(Logger._get_caller_info(f"WARN  {msg}")))

    @staticmethod
    def wrap_info(msg: str) -> str:
        return Logger.wrap_log(Logger.wrap_thread(Logger._get_caller_info(f"INFO  {msg}")))

    @staticmethod
    def wrap_error(msg: str) -> str:
        return Logger.wrap_log(Logger.wrap_thread(Logger._get_caller_info(f"ERROR {msg}")))

    @staticmethod
    def wrap_thread(msg: str) -> str:
        return f" {get_ident()} {msg}"

    @staticmethod
    def wrap_freq(msg: str, log_level: LogLevel) -> str:
        return f" {log_level.name:12} {msg}"

    @staticmethod
    def _get_caller_info(msg: str) -> str:
        frame = inspect.stack()[3]
        filename = os.path.basename(frame.filename)
        lineno = frame.lineno
        return f"{filename}:{lineno} {msg}"

    def log(self, msg: str, log_level: LogLevel) -> None:
        if log_level > self._log_level:
            return

        with self._log_que_lock:
            self._log_que.append(msg)

    def log_info(self, msg: str, log_level: LogLevel) -> None:
        self.log(Logger.wrap_info(Logger.wrap_freq(msg, log_level)), log_level)

    def log_error(self, msg: str, log_level: LogLevel) -> None:
        self.log(Logger.wrap_error(Logger.wrap_freq(msg, log_level)), log_level)

    def log_warning(self, msg: str, log_level: LogLevel) -> None:
        self.log(Logger.wrap_warning(Logger.wrap_freq(msg, log_level)), log_level)

    # ------------------------------
    # Private methods
    # ------------------------------

    @staticmethod
    def _format_error(error: Exception) -> str:
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            error_type = type(error).__name__
            error_message = str(error)

            formatted_error = f"=== Exception logged at {current_time} ===\n"
            formatted_error += f"Type: {error_type}\n\n"
            formatted_error += f"Message: {error_message}\n\n"

            import traceback
            tb = traceback.extract_tb(error.__traceback__)

            formatted_error += "Traceback (most recent call last):\n"
            for frame in tb:
                filename = frame.filename
                line_number = frame.lineno
                function_name = frame.name
                line_content = frame.line

                formatted_error += f"[{filename}] [{line_number}] [{function_name}]\n"
                if line_content:
                    formatted_error += f"    {line_content.strip()}\n"

            additional_info = {k: v for k, v in error.__dict__.items() if not k.startswith('__')}
            if additional_info:
                formatted_error += "\nAdditional Information:\n"
                for key, value in additional_info.items():
                    formatted_error += f"  {key}: {value}\n"

            import platform
            formatted_error += "\nSystem Information:\n"
            formatted_error += f"  Python version: {platform.python_version()}\n"
            formatted_error += f"  OS: {platform.system()} {platform.release()}\n"

            formatted_error += "=" * 50 + "\n"
            return formatted_error
        except Exception as formatting_error:
            return f"Error while formatting exception: {str(formatting_error)}\nOriginal error: {str(error)}\n"

    def _io_flusher_thread(self) -> None:
        while self._should_flush:
            time.sleep(0.01)

            with self._log_que_lock:
                if len(self._log_que) != 0:
                    self._flush_log_buffer_unlocked()

            with self._journal_lock:
                if len(self._journal_que) != 0:
                    self._flush_journal_buffer_unlocked()

        with self._log_que_lock:
            self._flush_log_buffer_unlocked()

    def _flush_journal_buffer_unlocked(self) -> None:
        full_msg = "\n".join([self._format_error(error) for error in self._journal_que]) + "\n"
        self._journal_que.clear()

        self._journal_file.write(full_msg)

        self._journal_file.flush()
        os.fsync(self._journal_file.fileno())

    def _flush_log_buffer_unlocked(self) -> None:
        full_msg = "\n".join(self._log_que) + "\n"
        self._log_que.clear()

        if self._log_stdout:
            print(full_msg)

        self._log_file.write(full_msg)

        self._log_file.flush()
        os.fsync(self._log_file.fileno())
