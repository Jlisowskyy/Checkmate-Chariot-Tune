from typing import TYPE_CHECKING, Union

from Utils.GlobalObj import GlobalObj

if TYPE_CHECKING:
    from .TestJobMgr import TestJobMgr
    from .TestTaskMgr import TestTaskMgr
    from .WorkerMgr import WorkerMgr


class ManagerComponents(metaclass=GlobalObj):
    # ------------------------------
    # Class fields
    # ------------------------------

    _test_job_mgr: Union['TestJobMgr', None]
    _test_task_mgr: Union['TestTaskMgr', None]
    _worker_mgr: Union['WorkerMgr', None]

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self):
        self._test_job_mgr = None
        self._test_task_mgr = None
        self._worker_mgr = None

    # ------------------------------
    # Class interaction
    # ------------------------------

    def init_components(self) -> None:
        from .TestJobMgr import TestJobMgr
        from .TestTaskMgr import TestTaskMgr
        from .WorkerMgr import WorkerMgr

        self._test_job_mgr = TestJobMgr()
        self._test_task_mgr = TestTaskMgr()
        self._worker_mgr = WorkerMgr()



    def destroy_components(self) -> None:
        if self._test_job_mgr:
            self._test_job_mgr.destroy()
        if self._test_task_mgr:
            self._test_task_mgr.destroy()
        if self._worker_mgr:
            self._worker_mgr.destroy()

    def is_inited(self) -> bool:
        return self._test_job_mgr is not None and self._test_task_mgr is not None and self._worker_mgr is not None

    def get_test_job_mgr(self) -> Union['TestJobMgr', None]:
        return self._test_job_mgr

    def get_test_task_mgr(self) -> Union['TestTaskMgr', None]:
        return self._test_task_mgr

    def get_worker_mgr(self) -> Union['WorkerMgr', None]:
        return self._worker_mgr


