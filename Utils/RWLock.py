from abc import ABC, abstractmethod
from contextlib import contextmanager
from threading import Lock
from typing import Generator

from Utils.Logger import Logger, LogLevel


class AbstractRWLock(ABC):
    # ------------------------------
    # Class fields
    # ------------------------------

    _read_counter: int
    _access_lock: Lock

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        self._read_counter = 0
        self._access_lock = Lock()

    def __del__(self) -> None:
        if self._read_counter < 0:
            Logger().log_error("Read counter on RWLock was negative!", LogLevel.LOW_FREQ)

    # ------------------------------
    # Class interaction
    # ------------------------------

    @abstractmethod
    def get_read(self) -> None:
        pass

    @abstractmethod
    def get_write(self) -> None:
        pass

    @abstractmethod
    def release_write(self) -> None:
        pass

    @abstractmethod
    def release_read(self) -> None:
        pass

    # ------------------------------
    # Private methods
    # ------------------------------

    def _get_read_counter(self) -> int:
        with self._access_lock:
            return self._read_counter

    def _increment_read_counter(self) -> int:
        with self._access_lock:
            self._read_counter += 1
            return self._read_counter

    def _decrement_read_counter(self) -> int:
        with self._access_lock:
            self._read_counter -= 1
            return self._read_counter


class BaseRWLock(AbstractRWLock):
    # ------------------------------
    # Class fields
    # ------------------------------

    _obj_lock: Lock

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        super().__init__()
        self._obj_lock = Lock()

    # ------------------------------
    # Class interaction
    # ------------------------------

    def get_read(self) -> None:
        if self._increment_read_counter() == 1:
            self._obj_lock.acquire()

    def get_write(self) -> None:
        self._obj_lock.acquire()

    def release_write(self) -> None:
        self._obj_lock.release()

    def release_read(self) -> None:
        if self._decrement_read_counter() == 0:
            self._obj_lock.release()


class ExtendedRWLock(AbstractRWLock):
    # ------------------------------
    # Class fields
    # ------------------------------

    _obj_lock: Lock
    _write_lock: Lock

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        super().__init__()
        self._obj_lock = Lock()
        self._write_lock = Lock()

    # ------------------------------
    # Class interaction
    # ------------------------------

    def get_read(self) -> None:
        with self._write_lock:
            if self._increment_read_counter() == 1:
                self._obj_lock.acquire()

    def get_write(self) -> None:
        self._write_lock.acquire()
        self._obj_lock.acquire()

    def release_write(self) -> None:
        self._obj_lock.release()
        self._write_lock.release()

    def release_read(self) -> None:
        if self._decrement_read_counter() == 0:
            self._obj_lock.release()


class RWLockWrapper:
    # ------------------------------
    # Class fields
    # ------------------------------

    _rw_lock: AbstractRWLock

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, rw_lock: AbstractRWLock) -> None:
        self._rw_lock = rw_lock

    # ------------------------------
    # Class interaction
    # ------------------------------

    def get_read(self) -> None:
        self._rw_lock.get_read()

    def get_write(self) -> None:
        self._rw_lock.get_write()

    def release_read(self) -> None:
        self._rw_lock.release_read()

    def release_write(self) -> None:
        self._rw_lock.release_write()

    @contextmanager
    def read(self) -> Generator[None, None, None]:
        self._rw_lock.get_read()

        try:
            yield
        except Exception as e:
            Logger().log_error(f"RW lock caught error: {e}", LogLevel.HIGH_FREQ)
            raise e
        finally:
            self._rw_lock.release_read()

    @contextmanager
    def write(self) -> Generator[None, None, None]:
        self._rw_lock.get_write()

        try:
            yield
        except Exception as e:
            Logger().log_error(f"RW lock caught error: {e}", LogLevel.HIGH_FREQ)
            raise e
        finally:
            self._rw_lock.release_write()


class BaseRWLockWrapper(RWLockWrapper):
    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        super().__init__(BaseRWLock())


class ExtendedRwLockWrapper(RWLockWrapper):
    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        super().__init__(ExtendedRWLock())


class OperableModel:
    # ------------------------------
    # Class fields
    # ------------------------------

    _op_lock: Lock

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        self._op_lock = Lock()

    # ------------------------------
    # Class interaction
    # ------------------------------

    @contextmanager
    def perform_operation(self):
        if not self._op_lock.acquire(blocking=False):
            raise ValueError("Operation already in progress")

        try:
            yield
        except Exception as e:
            Logger().log_error(f"Exception caught during operation: {e}", LogLevel.HIGH_FREQ)
            raise e
        finally:
            self._op_lock.release()


class RWLockModel:
    # ------------------------------
    # Class fields
    # ------------------------------

    _rw_lock: RWLockWrapper

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, rw_lock_wrapper: RWLockWrapper) -> None:
        self._rw_lock = rw_lock_wrapper

    # ------------------------------
    # Class interaction
    # ------------------------------

    def get_lock(self) -> RWLockWrapper:
        return self._rw_lock


class MgrModel(RWLockModel, OperableModel):
    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        super().__init__(ExtendedRwLockWrapper())


class ObjectModel(RWLockModel, OperableModel):
    # ------------------------------
    # Class fields
    # ------------------------------

    _gen_num: int

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        super().__init__(BaseRWLockWrapper())
        self._gen_num = 0

    # ------------------------------
    # Class interaction
    # ------------------------------

    def get_gen_num_unlocked(self) -> int:
        return self._gen_num

    def get_gen_num_locked(self) -> int:
        with self.get_lock().read():
            return self.get_gen_num_unlocked()

    def increment_gen_num_unlocked(self) -> None:
        self._gen_num += 1

    def increment_gen_num_locked(self) -> None:
        with self.get_lock().write():
            self.increment_gen_num_unlocked()
