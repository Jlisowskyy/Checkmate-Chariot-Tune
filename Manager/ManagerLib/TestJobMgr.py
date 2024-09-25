import asyncio
from collections import deque
from threading import Thread, Lock, Condition
from typing import Deque

from Manager.ManagerLib.TestJob import TestJobRequest
from Models.OrchestratorModels import JobState, WORKABLE_STATES, QUEUEABLE_STATES
from Utils.Logger import Logger, LogLevel
from Utils.RWLock import ObjectModel
from Utils.SettingsLoader import SettingsLoader


class TestJob():
    # ------------------------------
    # Class fields
    # ------------------------------

    _task_id: int
    _task_gen_num: int

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, task_id: int, task_gen_num: int) -> None:
        super().__init__()
        self._task_id = task_id
        self._task_gen_num = task_gen_num

    # ------------------------------
    # Abstract methods implementation
    # ------------------------------

    def run(self) -> None:
        pass

    # ------------------------------
    # Class interaction
    # ------------------------------

    def get_task_id(self) -> int:
        return self._task_id

    def get_task_gen_num(self) -> int:
        return self._task_gen_num

    # ------------------------------
    # Private methods
    # ------------------------------


class TestJobMgr(ObjectModel):
    # ------------------------------
    # Internal objects
    # ------------------------------

    class TestJobThreadData:
        tid: int
        thread: Thread
        cond: bool

        def __init__(self, tid: int, thread: Thread):
            self.tid = tid
            self.thread = thread
            self.cond = True

    # ------------------------------
    # Class fields
    # ------------------------------

    thread_counter: int = 0
    thread_counter_lock: Lock = Lock()

    _threads: dict[int, TestJobThreadData]

    _job_queues: dict[JobState, Deque[TestJobRequest]]

    _cv: Condition

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        super().__init__()
        self._startup_worker_threads(SettingsLoader().get_settings().job_threads)
        self._threads = {}
        self._cv = Condition()
        self._job_queues = {state: deque() for state in QUEUEABLE_STATES}

        Logger().log_info("Test Job Manager correctly initialized", LogLevel.LOW_FREQ)

    def destroy(self) -> None:
        self._stop_worker_threads(len(self._threads))

        Logger().log_info(f"Remaining requests in queue will be lost: {self.get_num_requests()}", LogLevel.LOW_FREQ)
        Logger().log_info("Test Job Manager destroyed", LogLevel.LOW_FREQ)

    # ------------------------------
    # Class interaction
    # ------------------------------

    def stop_task_jobs(self, task_id: int, task_gen_num: int) -> None:
        pass

    def update_thread_count(self, new_thread_count: int) -> None:
        if new_thread_count < 1:
            Logger().log_error("Thread count cannot be less than 1", LogLevel.LOW_FREQ)
            return

        if new_thread_count > len(self._threads):
            self._startup_worker_threads(new_thread_count - len(self._threads))

        if new_thread_count < len(self._threads):
            self._stop_worker_threads(len(self._threads) - new_thread_count)

        Logger().log_info(f"Thread count updated to {new_thread_count}", LogLevel.LOW_FREQ)

    def get_worker_thread_count(self) -> int:
        with self.get_lock().read():
            return len(self._threads)

    def get_num_requests(self) -> int:
        with self.get_lock().read():
            return sum(len(q) for q in self._job_queues.values())

    def add_request(self, request: TestJobRequest) -> None:
        if request.get_state() not in self._job_queues:
            raise ValueError(f"Invalid job state: {request.get_state()}")

        with self.get_lock().write():
            self._job_queues[request.get_state()].append(request)
        self.signal_threads()

    def signal_threads(self) -> None:
        self._cv.notify_all()

    # ------------------------------
    # Private methods
    # ------------------------------

    def _startup_worker_threads(self, thread_count: int) -> None:
        Logger().log_info(f"Starting {thread_count} worker threads", LogLevel.LOW_FREQ)

        with self.get_lock().write():
            for i in range(thread_count):
                self._register_thread_unlocked()

    def _register_thread_unlocked(self) -> None:
        with self.thread_counter_lock:
            tid = self.thread_counter
            self.thread_counter += 1

        thread = Thread(target=lambda: self._worker_thread_func_starter(tid))
        self._threads[tid] = TestJobMgr.TestJobThreadData(tid, thread)

        thread.start()

    def _mark_for_stop_unlocked(self, tid: int) -> None:
        self._threads[tid].cond = False

    def _unregister_thread_unlocked(self, tid: int) -> None:
        self._threads[tid].thread.join()
        self._threads.pop(tid)

    def _stop_worker_threads(self, thread_count: int) -> None:
        Logger().log_info(f"Stopping {thread_count} worker threads from {len(self._threads)}", LogLevel.LOW_FREQ)

        with self.get_lock().write():
            threads_to_stop = list(self._threads.keys())[:thread_count]

            for tid in threads_to_stop:
                self._mark_for_stop_unlocked(tid)

            for tid in threads_to_stop:
                self._unregister_thread_unlocked(tid)

    def _get_next_request(self) -> TestJobRequest | None:
        for state in WORKABLE_STATES:
            with self.get_lock().write():
                if len(self._job_queues[state]) > 0:
                    return self._job_queues[state].popleft()

        return None

    def _worker_thread_func_starter(self, tid: int) -> None:
        Logger().log_info(f"Worker thread {tid} started", LogLevel.MEDIUM_FREQ)
        asyncio.run(self._worker_thread_func(tid))
        Logger().log_info(f"Worker thread {tid} stopped", LogLevel.MEDIUM_FREQ)

    async def _worker_thread_func(self, tid: int) -> None:
        with self.get_lock().read():
            thread_info = self._threads[tid]

        while thread_info.cond:

            request = self._get_next_request()
            while request is not None:

                try:
                    await request.run()
                except Exception as e:
                    Logger().log_error(f"Error in job execution: {e}", LogLevel.LOW_FREQ)
                    request.try_to_fail(str(e))

                if not thread_info.cond:
                    break

                request = self._get_next_request()

            if not thread_info.cond:
                break

            self._cv.acquire()
