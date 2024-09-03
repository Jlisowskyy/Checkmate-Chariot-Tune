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

    _workerCli: Union['NetConnectionMgr', None]
    _testJobMgr: Union['TestJobMgr', None]
    _workerProcess: Union['WorkerProcess', None]

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self):
        self._workerCli = None
        self._testJobMgr = None
        self._workerProcess = None

    # ------------------------------
    # Class interaction
    # ------------------------------

    def init_components(self) -> None:
        from .NetConnectionMgr import NetConnectionMgr
        from .TestJobsMgr import TestJobMgr
        from .WorkerProcess import WorkerProcess

        self._workerProcess = WorkerProcess()
        self._testJobMgr = TestJobMgr()
        self._workerCli = NetConnectionMgr()

    def destroy_components(self) -> None:
        if self._testJobMgr:
            self._testJobMgr.destroy()
        if self._workerProcess:
            self._workerProcess.destroy()

    def is_inited(self) -> bool:
        return self._workerCli is not None and self._testJobMgr is not None and self._workerProcess is not None

    def get_worker_cli(self) -> Union['NetConnectionMgr', None]:
        return self._workerCli

    def get_test_job_mgr(self) -> Union['TestJobMgr', None]:
        return self._testJobMgr

    def get_worker_process(self) -> Union['WorkerProcess', None]:
        return self._workerProcess
