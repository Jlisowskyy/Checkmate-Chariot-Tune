from typing import TYPE_CHECKING, Union

from Utils.GlobalObj import GlobalObj

if TYPE_CHECKING:
    from .TestJobMgr import TestJobMgr
    from .TestTaskMgr import TestTaskMgr
    from .WorkerMgr import WorkerMgr
    from Modules.ModuleMgr import ModuleMgr
    from Modules.SubModuleMgr import SubModuleMgr


class ManagerComponents(metaclass=GlobalObj):
    # ------------------------------
    # Class fields
    # ------------------------------

    _test_job_mgr: Union['TestJobMgr', None]
    _test_task_mgr: Union['TestTaskMgr', None]
    _worker_mgr: Union['WorkerMgr', None]
    _submodule_mgr: Union['SubModuleMgr', None]
    _module_mgr: Union['ModuleMgr', None]

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self):
        self._test_job_mgr = None
        self._test_task_mgr = None
        self._worker_mgr = None
        self._submodule_mgr = None
        self._module_mgr = None

    # ------------------------------
    # Class interaction
    # ------------------------------

    def init_components(self) -> None:
        from .TestJobMgr import TestJobMgr
        from .TestTaskMgr import TestTaskMgr
        from .WorkerMgr import WorkerMgr
        from Modules.ModuleMgr import ModuleMgr
        from Modules.SubModuleMgr import SubModuleMgr

        self._test_job_mgr = TestJobMgr()
        self._test_task_mgr = TestTaskMgr()
        self._worker_mgr = WorkerMgr()
        self._submodule_mgr = SubModuleMgr()
        self._module_mgr = ModuleMgr()


    def destroy_components(self) -> None:
        if self._test_job_mgr:
            self._test_job_mgr.destroy()
        if self._test_task_mgr:
            self._test_task_mgr.destroy()
        if self._worker_mgr:
            self._worker_mgr.destroy()
        if self._submodule_mgr:
            self._submodule_mgr.destroy()
        if self._module_mgr:
            self._module_mgr.destroy()

    def is_inited(self) -> bool:
        return self._test_job_mgr is not None and self._test_task_mgr is not None and self._worker_mgr is not None and \
            self._submodule_mgr is not None and self._module_mgr is not None

    def get_test_job_mgr(self) -> Union['TestJobMgr', None]:
        return self._test_job_mgr

    def get_test_task_mgr(self) -> Union['TestTaskMgr', None]:
        return self._test_task_mgr

    def get_worker_mgr(self) -> Union['WorkerMgr', None]:
        return self._worker_mgr

    def get_submodule_mgr(self) -> Union['SubModuleMgr', None]:
        return self._submodule_mgr

    def get_module_mgr(self) -> Union['ModuleMgr', None]:
        return self._module_mgr
