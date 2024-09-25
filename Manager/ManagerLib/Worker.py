import secrets
import time
from threading import Lock

from fastapi import WebSocket

from Manager.ManagerLib.ErrorTable import ErrorTable
from Models.WorkerModels import WorkerModel, WorkerAuth
from Utils.RWLock import RWLock, ObjectModel
from Models.OrchestratorModels import WorkerState

class Worker(ObjectModel):
    # ------------------------------
    # Class fields
    # ------------------------------

    _counter_lock: Lock = Lock()
    _instance_count: int = 0

    _model: WorkerModel
    _activity_timestamp: float
    _session_token: int
    _is_marked_for_deletion: bool

    _conn_socket: WebSocket | None
    _state: WorkerState

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, model: WorkerModel):
        super().__init__()

        self._model = model
        self._activity_timestamp = time.perf_counter()

        with Worker._counter_lock:
            counter = Worker._instance_count

        random_bits = secrets.randbits(32)
        self._session_token = (counter << 32) + random_bits

        with Worker._counter_lock:
            Worker._instance_count += 1

        self._conn_socket = None
        self._state = WorkerState.REGISTERED


    # ------------------------------
    # Class interaction
    # ------------------------------

    def bump_activity(self) -> None:
        with self.get_lock().write():
            self._activity_timestamp = time.perf_counter()

    def get_last_activity(self) -> float:
        with self.get_lock().read():
            return self._activity_timestamp

    def get_model(self) -> WorkerModel:
        with self.get_lock().read():
            return self._model

    def get_session_token(self) -> int:
        with self.get_lock().read():
            return self._session_token

    def is_marked_for_deletion(self) -> bool:
        with self.get_lock().read():
            return self._state == WorkerState.MARKED_FOR_DELETE

    def mark_for_deletion(self) -> None:
        with self.get_lock().write():
            self._state = WorkerState.MARKED_FOR_DELETE

            if self._conn_socket is not None:
                self._conn_socket.close()

    def is_same(self, worker_name: str) -> bool:
        with self.get_lock().read():
            return self._model.name == worker_name and self._is_marked_for_deletion == False

    def is_same_auth(self, worker: WorkerAuth) -> bool:
        with self.get_lock().read():
            return self._model.name == worker.name and \
                self._session_token == worker.session_token and \
                self._is_marked_for_deletion == False

    def set_conn_socket(self, socket: WebSocket) -> ErrorTable:
        with self.get_lock().write():
            if self._conn_socket is not None:
                return ErrorTable.WORKER_ALREADY_CONNECTED

            if self._is_marked_for_deletion:
                return ErrorTable.WORKER_MARKED_FOR_DELETE

            if self._state != WorkerState.REGISTERED:
                return ErrorTable.WORKER_WRONG_STATE

            self._conn_socket = socket
            self._state = WorkerState.CONNECTED
            return ErrorTable.SUCCESS

    def unset_conn_socket(self) -> None:
        with self.get_lock().write():
            self._conn_socket = None

    def get_conn_socket(self) -> WebSocket | None:
        with self.get_lock().read():
            return self._conn_socket

    def get_state(self) -> WorkerState:
        with self.get_lock().read():
            return self._state
