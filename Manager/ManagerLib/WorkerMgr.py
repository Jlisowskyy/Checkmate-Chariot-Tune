import time
from threading import Thread, Lock, Condition

from fastapi import WebSocket
from pydantic import BaseModel

from Models.GlobalModels import CommandResult
from Models.WorkerModels import WorkerAuth
from Utils.Helpers import convert_ns_to_s, convert_s_to_ns
from .ErrorTable import ErrorTable
from .Worker import Worker
from ...Models.WorkerModels import WorkerModel
from ...ProjectInfo.ProjectInfo import ProjectInfoInstance
from ...Utils.Logger import Logger, LogLevel
from ...Utils.SettingsLoader import SettingsLoader

MIN_WORKER_VERSION = ProjectInfoInstance.get_version(ProjectInfoInstance.get_bu1ild_config("MIN_WORKER_VERSION"))


class WorkerMgr:
    # ------------------------------
    # Class fields
    # ------------------------------

    _workers: dict[str, Worker]

    _workersAuditor: Thread
    _shouldWork: bool

    _workers_lock: Lock
    _workers_queue_lock: Lock
    _workers_queue: list[Worker]
    _move_cv: Condition

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self):
        self._shouldWork = True
        self._workers = dict[str, Worker]()

        self._workers_lock = Lock()
        self._workers_queue_lock = Lock()
        self._move_cv = Condition()
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
                    return WorkerMgr.unregister_unlocked(self._workers[unregister_request.name], unregister_request)

        Logger().log_info(f"Worker with name: {unregister_request.name} not able to be unregister"
                          f" because was not found", LogLevel.LOW_FREQ)
        return ErrorTable.WORKER_NOT_FOUND

    @staticmethod
    def unregister_unlocked(worker: Worker, unregister_request: WorkerAuth) -> ErrorTable:
        if worker.get_session_token() == unregister_request.session_token:
            worker.mark_for_deletion()
            Logger().log_info(f"Worker with name: {unregister_request.name} marked for deletion", LogLevel.LOW_FREQ)
            return ErrorTable.SUCCESS
        return ErrorTable.INVALID_TOKEN

    async def worker_socket_accept(self, websocket: WebSocket) -> None:
        self._wait_for_registration_move()

        auth = await websocket.receive_json()
        worker_auth = WorkerAuth.model_validate_json(auth)

        with self._workers_lock:
            if worker_auth.name not in self._workers.keys():
                await websocket.send_json(CommandResult(result=ErrorTable.WORKER_NOT_FOUND.name).model_dump_json())
                raise Exception("Worker not found")

            worker = self._workers[worker_auth.name]

            if worker.get_session_token() != worker_auth.session_token:
                await websocket.send_json(CommandResult(result=ErrorTable.INVALID_TOKEN.name).model_dump_json())
                raise Exception("Session token not match")

        Logger().log_info(f"Correctly authenticated worker: {worker.get_model().name}", LogLevel.MEDIUM_FREQ)

        status = worker.set_conn_socket(websocket)
        await websocket.send_json(CommandResult(result=status.name).model_dump_json())

        if status != ErrorTable.SUCCESS:
            raise Exception(f"Failed to bond worker: {worker.get_model().name} with socket: {status.name}")

        Logger().log_info(f"Worker: {worker.get_model().name} correctly bonded with loop socket", LogLevel.MEDIUM_FREQ)


    def bump_ka(self, worker_auth: WorkerAuth) -> ErrorTable:
        with self._workers_queue_lock:
            for queue_worker in self._workers_queue:
                if queue_worker.is_same(worker_auth.name):
                    return self._bump_ka_internal(queue_worker, worker_auth)

            with self._workers_lock:
                if worker_auth.name in self._workers.keys() and \
                        not self._workers[worker_auth.name].is_marked_for_deletion():
                    return self._bump_ka_internal(self._workers[worker_auth.name], worker_auth)

        Logger().log_info(f"KA for {worker_auth.name} not bumped due to: Worker not found", LogLevel.LOW_FREQ)
        return ErrorTable.WORKER_NOT_FOUND

    # ------------------------------
    # Private methods
    # ------------------------------

    @staticmethod
    async def _worker_loop_send_msg(worker: Worker, websocket: WebSocket, msg: BaseModel) -> None:
        msg_str = msg.model_dump_json()

        Logger().log_info(f"Sending msg: {msg_str} to worker: {worker.get_model().name}", LogLevel.HIGH_FREQ)

        try:
            await websocket.send_json(msg_str)
        except Exception as e:
            if worker.is_marked_for_deletion():
                raise Exception("Worker is marked for deletion. Aborting worker loop...")
            else:
                raise e

        Logger().log_info(f"Msg: {msg_str} sent to worker with name: {worker.get_model().name}", LogLevel.HIGH_FREQ)

    @staticmethod
    async def _worker_loop_rcv_msg(worker: Worker, websocket: WebSocket) -> str:
        Logger().log_info(f"Receiving msg for worker: {worker.get_model().name}", LogLevel.HIGH_FREQ)

        try:
            msg = await websocket.receive_json()
        except Exception as e:
            if worker.is_marked_for_deletion():
                raise Exception("Worker is being deleted. Aborting...")
            else:
                raise e

        Logger().log_info(f"Received msg: {msg} for worker: {worker.get_model().name}", LogLevel.HIGH_FREQ)

        return msg

    @staticmethod
    def _bump_ka_internal(worker: Worker, worker_auth: WorkerAuth) -> ErrorTable:
        if worker.get_session_token() != worker_auth.session_token:
            Logger().log_info(f"KA for {worker_auth.name} not bumped due to: Invalid token", LogLevel.LOW_FREQ)
            return ErrorTable.INVALID_TOKEN

        worker.bump_activity()
        Logger().log_info(f"KA for {worker_auth.name} correctly bumped", LogLevel.LOW_FREQ)

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
                worker.mark_for_deletion()
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
                    self._workers[worker.get_model().name] = worker
                Logger().log_info(f"Worker: {worker.get_model().name} moved from queue to db", LogLevel.HIGH_FREQ)

        with self._move_cv:
            self._move_cv.notify_all()

        Logger().log_info("Registrations hardening finished", LogLevel.HIGH_FREQ)

    def _worker_audit_thread(self) -> None:
        BASE_SLEEP_TIME_NS = convert_s_to_ns(0.1)
        execution_time = 0

        while self._shouldWork:
            sleep_time = convert_ns_to_s(max(0, BASE_SLEEP_TIME_NS - execution_time))
            execution_time = max(0, execution_time - BASE_SLEEP_TIME_NS)

            time.sleep(sleep_time)

            Logger().log_info("Audit thread woke up", LogLevel.HIGH_FREQ)

            time_before = time.perf_counter_ns()
            self._move_workers()
            self._audit_workers()
            time_after = time.perf_counter_ns()

            execution_time += time_after - time_before

    def _wait_for_registration_move(self) -> None:
        with self._move_cv:
            self._move_cv.wait()
