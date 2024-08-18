from .GlobalObj import GlobalObj
from ..ProjectInfo.ProjectInfo import ProjectInfoInstance
from ..Api.WorkerModels import WorkerModel
from .Logger import Logger, LogLevel

from threading import Thread
import time

MIN_WORKER_VERSION = ProjectInfoInstance.get_version(ProjectInfoInstance.get_build_config("MIN_WORKER_VERSION"))


class WorkerMgr(metaclass=GlobalObj):
    _workers: list[WorkerModel]
    _workersAuditor: Thread
    _shouldWork: bool

    def __init__(self):
        self._shouldWork = True
        self._workers = []

        self._workersAuditor = Thread(target=self.worker_audit_thread)
        self._workersAuditor.start()

        Logger.get_instance().log_info("WorkerMgr created", LogLevel.LOW_FREQ)

    def destroy(self):
        self._shouldWork = False
        self._workersAuditor.join()

    def worker_audit_thread(self):
        while self._shouldWork:
            print("ELO")
            time.sleep(5)

        Logger.get_instance().log_info("WorkerMgr Audit thread stopped", LogLevel.LOW_FREQ)
