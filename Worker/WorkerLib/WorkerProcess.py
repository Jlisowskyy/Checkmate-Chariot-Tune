import sys

from LockFile import LockFile, LOCK_FILE_PATH


class WorkerProcess:
    # ------------------------------
    # Class fields
    # ------------------------------

    _lock_file: LockFile

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self):
        self._lock_file = LockFile(LOCK_FILE_PATH)

        if not self._lock_file.lock_file_safe():
            print(f"[ ERROR ] Failed to lock file at {LOCK_FILE_PATH}. Aborting...", file=sys.stderr)
            sys.exit(1)

    def destroy(self):
        self._lock_file.unlock_file()

    # ------------------------------
    # Class interaction
    # ------------------------------

    def start_processing(self):
        pass

    # ------------------------------
    # Private methods
    # ------------------------------
