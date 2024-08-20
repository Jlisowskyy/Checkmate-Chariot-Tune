from ...Utils.GlobalObj import GlobalObj
from ...ProjectInfo.ProjectInfo import ProjectInfoInstance
from ...Models.WorkerModels import WorkerModel, WorkerUnregister
from ...Utils.Logger import Logger, LogLevel
from .SettingsLoader import SettingsLoader
from .ErrorTable import ErrorTable

from threading import Thread, Lock
import time
from queue import Queue
import secrets

MIN_WORKER_VERSION = ProjectInfoInstance.get_version(ProjectInfoInstance.get_build_config("MIN_WORKER_VERSION"))


class Worker:
    _instance_count: int = 0

    model: WorkerModel
    activity_timestamp: float
    token: int

    def __init__(self, model: WorkerModel):
        self.model = model
        self.activity_timestamp = time.perf_counter()

        random_bits = secrets.randbits(32)
        self.token = (Worker._instance_count << 32) + random_bits

        Worker._instance_count += 1


class WorkerMgr(metaclass=GlobalObj):
    _workers: dict[str, Worker]

    _workersAuditor: Thread
    _shouldWork: bool

    _workers_lock: Lock
    _workers_queue_lock: Lock
    _workers_name_lookup_lock: Lock
    _workers_queue: Queue[Worker]

    _worker_timeout: int

    def __init__(self):
        self._shouldWork = True
        self._workers = dict[str, Worker]()

        self._workers_lock = Lock()
        self._workers_queue_lock = Lock()
        self._workers_name_lookup_lock = Lock()
        self._workers_queue = Queue[Worker]()

        settings = SettingsLoader().get_settings()
        self._worker_timeout = settings.worker_timeout

        self._workersAuditor = Thread(target=self._worker_audit_thread)
        self._workersAuditor.start()

        Logger().log_info("WorkerMgr created", LogLevel.LOW_FREQ)

    def register(self, worker: WorkerModel) -> [ErrorTable, int]:
        with self._workers_queue_lock:
            if worker_name in self._workers_queue:
                return [ErrorTable.WORKER_ALREADY_REGISTERED, 0]

            with self._workers_name_lookup_lock:
                if worker_name in self._workers.keys():
                    return [ErrorTable.WORKER_ALREADY_REGISTERED, 0]

                token = self._register_worker_unlocked(worker)

        return [ErrorTable.SUCCESS, token]

    def unregister(self, unregister_request: WorkerUnregister) -> [ErrorTable]:
        with self._workers_queue_lock:
            if worker_name in self._workers_queue:
                self._move_workers()  # Apply early queue processing

        user_found = False
        with self._workers_name_lookup_lock:
            user_found = (worker_name in self._workers)

        if user_found:
            with self._workers_lock:
                with self._workers_name_lookup_lock:
                    return self.unregister_unlocked(unregister_request)
        return ErrorTable.WORKER_NOT_FOUND

    def unregister_unlocked(self, unregister_request: WorkerUnregister) -> [ErrorTable]:
        if self._workers[unregister_request.name].token == unregister_request.token:
            del self._workers[unregister_request.name]
            return ErrorTable.SUCCESS
        return ErrorTable.INVALID_TOKEN

    def destroy(self) -> None:
        self._shouldWork = False
        self._workersAuditor.join()

        Logger().log_info("WorkerMgr destroyed", LogLevel.LOW_FREQ)

    def _register_worker_unlocked(self, worker_model: WorkerModel) -> int:
        worker = Worker(worker_model)
        self._workers_queue.put(worker)

        Logger().log_info(f"Registered worker with name: {worker_model.name} and session token: {worker.token}",
                          LogLevel.MEDIUM_FREQ)

        return worker.token

    def _timeout_worker(self, worker_name: str, inactivity: float) -> None:
        Logger().log_info(f"Worker: {worker_name} timeout: {inactivity}s", LogLevel.HIGH_FREQ)
        del self._workers[worker_name]

    def _audit_workers(self) -> None:
        with self._workers_lock:
            for worker in list(self._workers.keys()):
                with self._workers_name_lookup_lock:
                    time_now = time.perf_counter()
                    inactivity = time_now - self._workers[worker].start_time

                    if inactivity > self._worker_timeout:
                        self.timeout_worker(worker, inactivity)

    def _move_workers(self) -> None:
        with self._workers_queue_lock:
            while not self._workers_queue.empty():
                worker = self._workers_queue.get()
                with self._workers_lock:
                    with self._workers_name_lookup_lock:
                        self._workers[worker.model.name] = worker

    def _worker_audit_thread(self) -> None:
        while self._shouldWork:
            time.sleep(0.1)

            self._audit_workers()
            self._move_workers()
