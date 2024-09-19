from contextlib import contextmanager
from threading import Lock

from Utils.Logger import Logger, LogLevel


class RWLock:
    # ------------------------------
    # Class fields
    # ------------------------------

    _read_counter: int
    _access_lock: Lock
    _obj_lock: Lock

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        self._read_counter = 0
        self._access_lock = Lock()
        self._obj_lock = Lock()

    def destroy(self) -> None:
        if self._read_counter < 0:
            Logger().log_error("Read counter on RWLock was negative!", LogLevel.LOW_FREQ)

        # Wait till all read and write operations are released
        self.get_write()

    # ------------------------------
    # Class interaction
    # ------------------------------

    def get_read(self):
        with self._access_lock:
            if self._read_counter == 0:
                self._obj_lock.acquire()

            self._read_counter += 1

    def get_write(self):
        with self._access_lock:
            self._obj_lock.acquire()

    def release_write(self):
        with self._access_lock:
            self._obj_lock.release()

    def release_read(self):
        with self._access_lock:
            self._read_counter -= 1

            if self._read_counter == 0:
                self._obj_lock.release()

    @contextmanager
    def read(self):
        self.get_read()

        try:
            yield
        except Exception as e:
            Logger().log_error(f"RW lock caught error: {e}", LogLevel.HIGH_FREQ)
        finally:
            self.release_read()

    @contextmanager
    def write(self):
        self.get_write()

        try:
            yield
        except Exception as e:
            Logger().log_error(f"RW lock caught error: {e}", LogLevel.HIGH_FREQ)
        finally:
            self.get_write()


class LockableObject:
    # ------------------------------
    # Class fields
    # ------------------------------

    _lock: RWLock

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        self._lock = RWLock()

    def destroy(self) -> None:
        self._lock.destroy()

    # ------------------------------
    # Class interaction
    # ------------------------------

    def get_lock(self) -> RWLock:
        return self._lock
