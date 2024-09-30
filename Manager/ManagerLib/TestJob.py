from abc import ABC, abstractmethod
from asyncio import Lock

from Manager.ManagerLib.ManagerComponents import ManagerComponents
from Manager.ManagerLib.Worker import Worker
from Models.OrchestratorModels import JobState, WorkerState, WORKABLE_STATES
from Utils.RWLock import ObjectModel
from Utils.SettingsLoader import SettingsLoader


class TestJobRequest(ObjectModel, ABC):
    # ------------------------------
    # Class fields
    # ------------------------------

    _test_job_counter: int = 0
    _test_job_counter_lock: Lock = Lock()

    _test_job_id: int
    _state: JobState

    _worker: Worker | None

    _failure_reasons: list[str]

    _result_payload: str

    _task_id: int
    _task_gen_num: int

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, task_id: int, task_gen_num: int) -> None:
        super().__init__()
        self._state = JobState.CREATED
        self._failure_reasons = []

        with self._test_job_counter_lock:
            self._test_job_id = TestJobRequest._test_job_counter
            TestJobRequest._test_job_counter += 1

        self._worker = None
        self._result_payload = ""
        self._task_id = task_id
        self._task_gen_num = task_gen_num

    # ------------------------------
    # Abstract methods
    # ------------------------------

    @abstractmethod
    async def _process_prepared_unlocked_internal(self) -> str:
        pass

    @abstractmethod
    async def _process_completed_unlocked_internal(self, payload: str) -> None:
        pass

    # ------------------------------
    # Class interaction
    # ------------------------------

    def get_task_id(self) -> int:
        return self._task_id

    def get_task_gen_num(self) -> int:
        return self._task_gen_num

    def get_state(self) -> JobState:
        with self.get_lock().read():
            return self._state

    def get_id(self) -> int:
        return self._test_job_id

    def prepare_job(self, worker: Worker) -> None:
        with self.get_lock().write():
            self._prepare_job_unlocked(worker)

    def detach_from_worker(self) -> None:
        with self.get_lock().write():
            self._detach_from_worker_unlocked()

    def get_failure_counter(self) -> int:
        with self.get_lock().read():
            return len(self._failure_reasons)

    def is_attached_to_worker(self) -> bool:
        with self.get_lock().read():
            return self._is_attached_to_worker_unlocked()

    def get_failure_reasons(self) -> list[str]:
        with self.get_lock().read():
            return self._failure_reasons

    def get_result_payload(self) -> str:
        with self.get_lock().read():
            return self._result_payload

    def set_result_payload(self, payload: str) -> None:
        with self.get_lock().write():
            self._result_payload = payload

    def try_to_fail(self, reason: str) -> None:
        with self.get_lock().write():
            self._try_to_fail_unlocked(reason)

        ManagerComponents().get_test_job_mgr().add_request(self)

    def abort_job(self) -> None:
        with self.get_lock().write:
            self._abort_job_unlocked()

    async def run(self) -> None:
        with self.get_lock().write():
            await self._run_unlocked()


    # ------------------------------
    # Private methods
    # ------------------------------

    def _abort_job_unlocked(self) -> None:
        if self._is_attached_to_worker_unlocked():
            self._detach_from_worker_unlocked()

    def _prepare_job_unlocked(self, worker: Worker) -> None:
        if self._is_attached_to_worker_unlocked():
            raise Exception("Worker already set for job!")

        if self._state != JobState.CREATED:
            raise Exception("Job state is not prepared!")

        if worker.get_state() != WorkerState.CONNECTED:
            raise Exception("Worker is not connected!")

        self._worker = worker
        self._state = JobState.PREPARED

    def _detach_from_worker_unlocked(self) -> None:
        if self._worker is None:
            raise Exception("Worker not set for job!")

        self._worker = None
        self._state = JobState.CREATED

    def _is_attached_to_worker_unlocked(self) -> bool:
        return self._worker is not None

    def _try_to_fail_unlocked(self, reason: str) -> None:
        self._failure_reasons.append(reason)

        if len(self._failure_reasons) <= SettingsLoader().get_settings().job_failures_limit:
            self._state = JobState.FAILED

            if self._worker is not None:
                self._worker.on_job_failed()

            self._worker = None

    async def _run_unlocked(self) -> None:
        if self._state not in WORKABLE_STATES:
            raise Exception("Job is not in a workable state!")

        if self._worker is None:
            raise Exception("Job is not attached to any worker!")

        if self._state == JobState.PREPARED:
            await self._process_prepared_unlocked()
        elif self._state == JobState.COMPLETED:
            await self._process_completed_unlocked()
        elif self._state in WORKABLE_STATES:
            raise Exception("Job state is not implemented!")
        else:
            raise Exception("Job state is not workable!")

    async def _process_prepared_unlocked(self) -> None:
        if self._worker.get_state() != WorkerState.CONNECTED:
            raise Exception("Worker is not connected!")

        socket = self._worker.get_conn_socket()
        payload = await self._process_prepared_unlocked_internal()

        await socket.send_text(payload)

        self._state = JobState.INFLIGHT
        self._worker.on_job_started()
        ManagerComponents().get_test_job_mgr().add_request(self)

    async def _process_completed_unlocked(self) -> None:
        await self._process_completed_unlocked_internal(self._result_payload)

        self._state = JobState.HARDENED
        self._worker.on_job_completed()
