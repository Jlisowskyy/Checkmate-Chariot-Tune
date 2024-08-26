import os
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

        return True

    def lock_file_safe(self) -> bool:
        if not self.is_locked_process_existing():
            os.remove(self._path)

            return self.lock_file()
        return False

    def unlock_file(self) -> bool:
        pid = self.get_locked_process_pid()

        if pid is not None and pid == os.getpid():
            os.remove(self._path)
            return True
        return False

    # ------------------------------
    # Private methods
    # ------------------------------
