from Utils.Logger import Logger, LogLevel
from Worker.WorkerLib.TestTask import TestTask
from Worker.WorkerLib.WorkerComponents import StopType, BlockType, WorkerComponents


class TestJobMgr:
    # ------------------------------
    # Class fields
    # ------------------------------

    _are_new_jobs_globally_blocked: bool
    _ongoing_tasks: dict[str, TestTask]

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        self._are_new_jobs_globally_blocked = True
        self._ongoing_tasks = dict[str, TestTask]()

    def destroy(self) -> None:
        self.destroy_ongoing_jobs()

    # ------------------------------
    # Class interaction
    # ------------------------------

    # task_name == "" => stop all
    def abort_jobs(self, task_name: str = "") -> None:
        Logger().log_info(f"Brutal job stopping started "
                          f"{f"for task: {task_name}" if task_name != "" else "for all tasks"}",
                          LogLevel.LOW_FREQ)

    # task_name == "" => stop all

    def stop_jobs(self, task_name: str = "") -> None:
        Logger().log_info(f"Gentle job stopping started "
                          f"{f"for task: {task_name}" if task_name != "" else "for all tasks"}",
                          LogLevel.LOW_FREQ)

    def destroy_ongoing_jobs(self) -> None:
        # TODO: there might be a race
        self._are_new_jobs_globally_blocked = True
        stop_type = WorkerComponents().get_worker_process().get_stop_type()

        if stop_type == StopType.gentle_stop:
            self.stop_jobs()
        elif stop_type == StopType.abort_stop:
            self.abort_jobs()
        else:
            raise Exception(f"Received unknown stop type: {stop_type}")

    # task_name == "" => block all tasks
    def block_new_jobs(self, block_type: BlockType, task_name: str = "") -> None:
        type_value = True if block_type == BlockType.enable else False

        if task_name == "":
            self._are_new_jobs_globally_blocked = type_value
        elif task_name in self._ongoing_tasks:
            self._ongoing_tasks[task_name].is_blocked = type_value
        else:
            raise Exception(f"Received unknown task name: {task_name}")

    # ------------------------------
    # Private methods
    # ------------------------------

    def _is_new_job_blocked_for_task(self, task_name: str) -> bool:
        if task_name not in self._ongoing_tasks:
            raise Exception(f"Received unknown task name: {task_name}")

        return self._ongoing_tasks[task_name].is_blocked or self._are_new_jobs_globally_blocked

    # ------------------------------
    # RPC procedures
    # ------------------------------

    def _log_msg(self, msg: str) -> str:
        Logger().log_info(msg, LogLevel.HIGH_FREQ)

        return WorkerComponents().get_conn_mgr().prepare_success_response()

    def _stop_working_gently(self) -> str:
        pass

    def _stop_working_abort(self) -> str:
        pass

    def _init_test_setup(self):
        pass
