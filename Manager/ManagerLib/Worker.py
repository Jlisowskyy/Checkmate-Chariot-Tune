import secrets
import time

from Models.WorkerModels import WorkerModel, WorkerAuth
from Utils.RWLock import RWLock


class Worker:
    # ------------------------------
    # Class fields
    # ------------------------------

    _instance_count: int = 0

    _model: WorkerModel
    _activity_timestamp: float
    _session_token: int
    _is_marked_for_deletion: bool
    _lock: RWLock

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, model: WorkerModel):
        self._lock = RWLock()

        self._model = model
        self._activity_timestamp = time.perf_counter()

        random_bits = secrets.randbits(32)
        self._session_token = (Worker._instance_count << 32) + random_bits

        Worker._instance_count += 1

    # ------------------------------
    # Class interaction
    # ------------------------------

    def bump_activity(self) -> None:
        with self._lock.write():
            self._activity_timestamp = time.perf_counter()

    def get_last_activity(self) -> float:
        with self._lock.read():
            return self._activity_timestamp

    def get_model(self) -> WorkerModel:
        with self._lock.read():
            return self._model

    def get_session_token(self) -> int:
        with self._lock.read():
            return self._session_token

    def is_marked_for_deletion(self) -> bool:
        with self._lock.read():
            return self._is_marked_for_deletion

    def mark_for_deletion(self) -> None:
        with self._lock.write():
            self._is_marked_for_deletion = True

    def get_lock(self) -> RWLock:
        return self._lock

    def is_same(self, worker_name: str) -> bool:
        with self._lock.read():
            return self._model.name == worker_name and self._is_marked_for_deletion == False

    def is_same_auth(self, worker: WorkerAuth) -> bool:
        with (self._lock.read()):
            return self._model.name == worker.name and \
                self._session_token == worker.session_token and \
                self._is_marked_for_deletion == False
