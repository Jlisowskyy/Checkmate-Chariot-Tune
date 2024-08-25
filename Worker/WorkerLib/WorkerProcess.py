import time
import os


def worker_process_init():
    worker_process = None
    try:
        worker_process = WorkerProcess()
        worker_process.start_processing()
        time.sleep(60)
    finally:
        if worker_process is not None:
            worker_process.destroy()


class WorkerProcess:
    # ------------------------------
    # Class fields
    # ------------------------------

    LOCK_FILE_PATH = f"/tmp/Checkmate-Chariot-Worker.lock"
    _lock_file_fd: int

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self):
        self._lock_file_fd = -1
        self._lock_process_file()

    def destroy(self):
        self._release_process_file()

    # ------------------------------
    # Class interaction
    # ------------------------------

    def start_processing(self):
        pass

    # ------------------------------
    # Private methods
    # ------------------------------

    def _lock_process_file(self):
        self._lock_file_fd = os.open(self.LOCK_FILE_PATH, os.O_EXCL | os.O_CREAT | os.O_WRONLY)
        os.write(self._lock_file_fd, str(os.getpid()).encode())

    def _release_process_file(self):
        os.close(self._lock_file_fd)
        os.remove(self.LOCK_FILE_PATH)
