import time
from threading import Thread, Lock

from fastapi import WebSocket

from Models.WorkerModels import WorkerAuth
from . import Worker
from .ErrorTable import ErrorTable
from ...Models.WorkerModels import WorkerModel
from ...ProjectInfo.ProjectInfo import ProjectInfoInstance
from ...Utils.GlobalObj import GlobalObj
from ...Utils.Logger import Logger, LogLevel
from ...Utils.SettingsLoader import SettingsLoader

MIN_WORKER_VERSION = ProjectInfoInstance.get_version(ProjectInfoInstance.get_bu1ild_config("MIN_WORKER_VERSION"))


class WorkerMgr(metaclass=GlobalObj):
    # ------------------------------
    # Class fields
    # ------------------------------

    _workers: dict[str, Worker]

    _workersAuditor: Thread
    _shouldWork: bool

    _workers_lock: Lock
    _workers_queue_lock: Lock
    _workers_move_lock: Lock
    _workers_audit_lock: Lock
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
        self._workers_move_lock = Lock()
        self._workers_audit_lock = Lock()
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
            for queue_worker in self._workers_queue:
                if queue_worker.is_same(worker.name):
                    Logger().log_info(f"Not able to register worker with name: {worker.name}: Already registered",
                                      LogLevel.LOW_FREQ)
                    return [ErrorTable.WORKER_ALREADY_REGISTERED, 0]

            with self._workers_lock:
                if worker.name in self._workers.keys() and not self._workers[worker.name].is_marked_for_deletion():
                    Logger().log_info(f"Not able to register worker with name: {worker.name}: Already registered",
                                      LogLevel.LOW_FREQ)
                    return [ErrorTable.WORKER_ALREADY_REGISTERED, 0]

            token = self._register_worker_unlocked(worker)

        return [ErrorTable.SUCCESS, token]

    def unregister(self, unregister_request: WorkerAuth) -> ErrorTable:
        with self._workers_queue_lock:
            for queue_worker in self._workers_queue:
                if queue_worker.is_same(unregister_request.name):
                    return WorkerMgr.unregister_unlocked(queue_worker, unregister_request)

            with self._workers_lock:
                if unregister_request.name in self._workers.keys() and \
                        self._workers[unregister_request.name].is_same(unregister_request.name):
                    return WorkerMgr.unregister_unlocked(queue_worker, unregister_request)

        Logger().log_info(f"Worker with name: {unregister_request.name} not able to be unregister"
                          f" because was not found", LogLevel.LOW_FREQ)
        return ErrorTable.WORKER_NOT_FOUND

    @staticmethod
    def unregister_unlocked(worker: Worker, unregister_request: WorkerAuth) -> ErrorTable:
        if worker.get_session_token() == unregister_request.session_token:
            worker.mark_for_deletion()
            Logger().log_info(f"Worker with name: {worker.name} marked for deletion", LogLevel.LOW_FREQ)
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
        token = worker.get_session_token()
        self._workers_queue.append(worker)

        Logger().log_info(f"Registered worker with name: {worker_model.name} and session token: {token}",
                          LogLevel.MEDIUM_FREQ)

        return token

    def _audit_workers(self) -> None:
        Logger().log_info("Audit started", LogLevel.HIGH_FREQ)
        to_kick_workers_list = []

        for [name, worker] in self._workers:
            time_now = time.perf_counter()
            inactivity = time_now - worker.activity_timestamp

            if inactivity > SettingsLoader().get_settings().worker_timeout:
                Logger().log_info(f"Worker: {name} timeout, inactivity: {inactivity}s", LogLevel.MEDIUM_FREQ)
                to_kick_workers_list.append(name)
            elif worker.is_marked_for_deletion():
                Logger().log_info(f"Worker: {name} marked for deletion is being removed", LogLevel.MEDIUM_FREQ)
                to_kick_workers_list.append(name)

        with self._workers_lock:
            for inactive_worker in to_kick_workers_list:
                del self._workers[inactive_worker]

        Logger().log_info("Audit finished", LogLevel.HIGH_FREQ)

    def _move_workers(self) -> None:
        Logger().log_info("Registrations hardening started", LogLevel.HIGH_FREQ)
        with self._workers_queue_lock:
            while len(self._workers_queue) != 0:
                worker = self._workers_queue.pop()

                if worker.is_marked_for_deletion():
                    continue

                with self._workers_lock:
                    self._workers[worker.model.name] = worker
                Logger().log_info(f"Worker: {worker.model.name} moved from queue to db", LogLevel.HIGH_FREQ)
        Logger().log_info("Registrations hardening finished", LogLevel.HIGH_FREQ)

    def _worker_audit_thread(self) -> None:
        while self._shouldWork:
            time.sleep(0.5)

            self._move_workers()
            self._audit_workers()
