import secrets
import time
from threading import Thread, Lock
from fastapi import WebSocket

from Models.WorkerModels import WorkerAuth
from .ErrorTable import ErrorTable
from ...Models.WorkerModels import WorkerModel, WorkerUnregister
from ...ProjectInfo.ProjectInfo import ProjectInfoInstance
from ...Utils.GlobalObj import GlobalObj
from ...Utils.Logger import Logger, LogLevel
from ...Utils.SettingsLoader import SettingsLoader

MIN_WORKER_VERSION = ProjectInfoInstance.get_version(ProjectInfoInstance.get_bu1ild_config("MIN_WORKER_VERSION"))


class Worker:
    # ------------------------------
    # Class fields
    # ------------------------------

    _instance_count: int = 0

    model: WorkerModel
    activity_timestamp: float
    session_token: int

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, model: WorkerModel):
        self.model = model
        self.activity_timestamp = time.perf_counter()

        random_bits = secrets.randbits(32)
        self.session_token = (Worker._instance_count << 32) + random_bits

        Worker._instance_count += 1


class WorkerMgr(metaclass=GlobalObj):
    # ------------------------------
    # Class fields
    # ------------------------------

    _workers: dict[str, Worker]

    _workersAuditor: Thread
    _shouldWork: bool

    _workers_lock: Lock
    _workers_queue_lock: Lock
    _workers_name_lookup_lock: Lock
    _workers_queue: list[Worker]

    _worker_timeout: int

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self):
        self._shouldWork = True
        self._workers = dict[str, Worker]()

        self._workers_lock = Lock()
        self._workers_queue_lock = Lock()
        self._workers_name_lookup_lock = Lock()
        self._workers_queue = list[Worker]()

        self._workersAuditor = Thread(target=self._worker_audit_thread)
        self._workersAuditor.start()

        Logger().log_info("WorkerMgr created", LogLevel.LOW_FREQ)

    def destroy(self) -> None:
        self._shouldWork = False
        self._workersAuditor.join()

        Logger().log_info("WorkerMgr destroyed", LogLevel.LOW_FREQ)

    # ------------------------------
    # Class interaction
    # ------------------------------

    def register(self, worker: WorkerModel) -> [ErrorTable, int]:
        with self._workers_queue_lock:
            if worker.name in self._workers_queue:
                return [ErrorTable.WORKER_ALREADY_REGISTERED, 0]

            with self._workers_name_lookup_lock:
                if worker.name in self._workers.keys():
                    return [ErrorTable.WORKER_ALREADY_REGISTERED, 0]

                token = self._register_worker_unlocked(worker)

        return [ErrorTable.SUCCESS, token]

    def unregister(self, unregister_request: WorkerUnregister) -> ErrorTable:
        self._move_workers()  # Apply early queue processing

        with self._workers_name_lookup_lock:
            user_found = (unregister_request.name in self._workers.keys())

        if user_found:
            with self._workers_lock:
                with self._workers_name_lookup_lock:
                    return self.unregister_unlocked(unregister_request)
        return ErrorTable.WORKER_NOT_FOUND

    def unregister_unlocked(self, unregister_request: WorkerUnregister) -> ErrorTable:
        if self._workers[unregister_request.name].session_token == unregister_request.session_token:
            del self._workers[unregister_request.name]
            Logger().log_info(f"Worker: {unregister_request.name} unregistered", LogLevel.MEDIUM_FREQ)
            return ErrorTable.SUCCESS
        return ErrorTable.INVALID_TOKEN

    def worker_loop(self, socket: WebSocket):
        # TODO: ADD LOGIC
        raise NotImplementedError()

    def bump_ka(self, worker_auth: WorkerAuth) -> ErrorTable:
        # TODO: ADD LOGIC
        raise NotImplementedError()

    # ------------------------------
    # Private methods
    # ------------------------------

    def _register_worker_unlocked(self, worker_model: WorkerModel) -> int:
        worker = Worker(worker_model)
        self._workers_queue.append(worker)

        Logger().log_info(f"Registered worker with name: {worker_model.name} and session token: {worker.session_token}",
                          LogLevel.MEDIUM_FREQ)

        return worker.session_token

    def _timeout_worker(self, worker_name: str, inactivity: float) -> None:
        Logger().log_info(f"Worker: {worker_name} timeout, inactivity: {inactivity}s", LogLevel.MEDIUM_FREQ)
        del self._workers[worker_name]

    def _audit_workers(self) -> None:
        Logger().log_info("Audit started", LogLevel.HIGH_FREQ)
        with self._workers_lock:
            for worker in list(self._workers.keys()):
                with self._workers_name_lookup_lock:
                    time_now = time.perf_counter()
                    inactivity = time_now - self._workers[worker].activity_timestamp

                    if inactivity > SettingsLoader().get_settings().worker_timeout:
                        self._timeout_worker(worker, inactivity)
        Logger().log_info("Audit finished", LogLevel.HIGH_FREQ)

    def _move_workers(self) -> None:
        Logger().log_info("Registrations hardening started", LogLevel.HIGH_FREQ)
        with self._workers_queue_lock:
            while len(self._workers_queue) != 0:
                worker = self._workers_queue.pop()
                with self._workers_lock:
                    with self._workers_name_lookup_lock:
                        self._workers[worker.model.name] = worker
                        Logger().log_info(f"Worker: {worker.model.name} moved from queue to db", LogLevel.HIGH_FREQ)
        Logger().log_info("Registrations hardening finished", LogLevel.HIGH_FREQ)

    def _worker_audit_thread(self) -> None:
        while self._shouldWork:
            time.sleep(0.1)

            self._audit_workers()
            self._move_workers()
