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

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        super().__init__()
        self._state = JobState.CREATED
        self._failure_reasons = []

        with self._test_job_counter_lock:
            self._test_job_id = TestJobRequest._test_job_counter
            TestJobRequest._test_job_counter += 1

        self._worker = None
        self._result_payload = ""

    # ------------------------------
    # Abstract methods
    # ------------------------------

    @abstractmethod
    async def _process_prepared_internal(self) -> str:
        pass

    @abstractmethod
    async def _process_completed_internal(self, payload: str) -> None:
        pass

    # ------------------------------
    # Class interaction
    # ------------------------------

    def get_state(self) -> JobState:
        with self.get_lock().read():
            return self._state

    def get_id(self) -> int:
        return self._test_job_id

    def prepare_job(self, worker: Worker) -> None:
        with self.get_lock().write():
            if self._worker is not None:
                raise Exception("Worker already set for job!")

            if self._state != JobState.CREATED:
                raise Exception("Job state is not prepared!")

            if worker.get_state() != WorkerState.CONNECTED:
                raise Exception("Worker is not connected!")

            self._worker = worker
            self._state = JobState.PREPARED

    def detach_from_worker(self) -> None:
        with self.get_lock().write():
            if self._worker is None:
                raise Exception("Worker not set for job!")

            self._worker = None
            self._state = JobState.CREATED

    def get_failure_counter(self) -> int:
        with self.get_lock().read():
            return len(self._failure_reasons)

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
            self._failure_reasons.append(reason)

            if len(self._failure_reasons) <= SettingsLoader().get_settings().job_failures_limit:
                return

            self._state = JobState.FAILED

        ManagerComponents().get_test_job_mgr().add_request(self)
        if self._worker is not None:
            self._worker.on_job_failed()

        with self.get_lock().write():
            self._worker = None

    async def run(self) -> None:
        if self.get_state() not in WORKABLE_STATES:
            raise Exception("Job is not in a workable state!")

        if self.get_state() == JobState.PREPARED:
            await self._process_prepared()
        elif self.get_state() == JobState.COMPLETED:
            await self._process_completed()
        elif self.get_state() in WORKABLE_STATES:
            raise Exception("Job state is not implemented!")
        else:
            raise Exception("Job state is not workable!")

    # ------------------------------
    # Private methods
    # ------------------------------

    async def _process_prepared(self) -> None:
        with self.get_lock().read():
            if self._state != JobState.PREPARED:
                raise Exception("Job state is not prepared!")

            worker = self._worker

        if worker.get_state() != WorkerState.CONNECTED:
            raise Exception("Worker is not connected!")

        socket = worker.get_conn_socket()
        payload = await self._process_prepared_internal()

        await socket.send_text(payload)

        with self.get_lock().write():
            self._state = JobState.INFLIGHT
        worker.on_job_started()
        ManagerComponents().get_test_job_mgr().add_request(self)

    async def _process_completed(self) -> None:
        with self.get_lock().read():
            if self._state != JobState.COMPLETED:
                raise Exception("Job state is not completed!")

        await self._process_completed_internal(self._result_payload)

        with self.get_lock().write():
            self._state = JobState.HARDENED

        self._worker.on_job_completed()
