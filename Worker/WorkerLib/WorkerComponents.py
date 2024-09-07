from enum import IntEnum
from Utils.GlobalObj import GlobalObj

class StopType(IntEnum):
    gentle_stop = 0
    abort_stop = 1


class BlockType(IntEnum):
    enable = 0
    disable = 1


from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .NetConnectionMgr import NetConnectionMgr
    from .TestJobsMgr import TestJobMgr
    from .WorkerProcess import WorkerProcess


class WorkerComponents(metaclass=GlobalObj):
    # ------------------------------
    # Class fields
    # ------------------------------

    _connection_mgr: Union['NetConnectionMgr', None]
    _test_job_mgr: Union['TestJobMgr', None]
    _worker_process: Union['WorkerProcess', None]

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self):
        self._connection_mgr = None
        self._test_job_mgr = None
        self._worker_process = None

    # ------------------------------
    # Class interaction
    # ------------------------------

    def init_components(self) -> None:
        from .NetConnectionMgr import NetConnectionMgr
        from .TestJobsMgr import TestJobMgr
        from .WorkerProcess import WorkerProcess

        self._worker_process = WorkerProcess()
        self._test_job_mgr = TestJobMgr()
        self._connection_mgr = NetConnectionMgr()

    def destroy_components(self) -> None:
        if self._test_job_mgr:
            self._test_job_mgr.destroy()
        if self._worker_process:
            self._worker_process.destroy()
        if self._connection_mgr:
            self._connection_mgr.destroy()

    def is_inited(self) -> bool:
        return self._connection_mgr is not None and self._test_job_mgr is not None and self._worker_process is not None

    def get_conn_mgr(self) -> Union['NetConnectionMgr', None]:
        return self._connection_mgr

    def get_test_job_mgr(self) -> Union['TestJobMgr', None]:
        return self._test_job_mgr

    def get_worker_process(self) -> Union['WorkerProcess', None]:
        return self._worker_process
