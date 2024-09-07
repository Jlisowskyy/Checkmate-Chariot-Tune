import os
import time

from psutil import pid_exists

from Utils.Logger import Logger, LogLevel

LOCK_FILE_PATH = f"/tmp/Checkmate-Chariot-Worker.lock"


class LockFile:
    # ------------------------------
    # Class fields
    # ------------------------------

    _path: str

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, path: str):
        self._path = path

    # ------------------------------
    # Class interaction
    # ------------------------------

    def lock_file_exists(self) -> bool:
        return os.path.exists(self._path)

    def get_locked_process_pid(self) -> int | None:
        try:
            with open(self._path, "r") as f:
                rv = int(f.read())
                return rv
        except Exception as e:
            Logger().log_info(f"Failed to read lock file by reason: {e}", LogLevel.LOW_FREQ)
            return None

    def is_locked_process_existing(self) -> bool:
        pid = self.get_locked_process_pid()

        return pid is not None and pid_exists(pid)

    def lock_file(self) -> bool:
        try:
            fd = os.open(self._path, os.O_EXCL | os.O_CREAT | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
        except Exception as e:
            Logger().log_info(f"Failed to lock file: {e}", LogLevel.LOW_FREQ)
            return False

        Logger().log_info("Correctly locked the file", LogLevel.LOW_FREQ)
        return True

    def lock_file_safe(self) -> bool:
        if not self.is_locked_process_existing():
            if os.path.exists(self._path):
                os.remove(self._path)

            return self.lock_file()
        return False

    def unlock_file(self) -> bool:
        pid = self.get_locked_process_pid()

        if pid is not None and pid == os.getpid():
            os.remove(self._path)

            Logger().log_info("Correctly released lock file", LogLevel.LOW_FREQ)
            return True
        Logger().log_info("Failed to release lock file", LogLevel.LOW_FREQ)
        return False

    def await_creation(self, pid: int, timeout_ms: int) -> None:
        NS_TO_MS = 1000 * 1000

        init_time = time.perf_counter_ns()
        act_time = time.perf_counter_ns()

        while (act_time - init_time) / NS_TO_MS < timeout_ms:
            if os.path.exists(self._path):
                break

            time.sleep(0.1)
            act_time = time.perf_counter_ns()

        if (act_time - init_time) / NS_TO_MS >= timeout_ms:
            raise Exception(f"Lock file failed to create after: {timeout_ms}ms")

        if self.get_locked_process_pid() != pid:
            Logger().log_warning(f"Created file contains: {self.get_locked_process_pid()} pid"
                                 f" but was given: {pid} pid",
                                 LogLevel.LOW_FREQ)

    # ------------------------------
    # Private methods
    # ------------------------------
