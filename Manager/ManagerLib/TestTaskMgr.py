from enum import IntEnum
from threading import Lock

from Modules.ModuleMgr import ModuleMgr
from Utils.GlobalObj import GlobalObj
from Utils.Logger import Logger, LogLevel
from Utils.RWLock import LockableObject


class TaskState(IntEnum):
    UNINITIATED = 0
    INITIATED = 1
    BUILT = 2
    READY = 3
    SCHEDULED = 4


class TestTask(LockableObject):
    # ------------------------------
    # Class fields
    # ------------------------------

    _obj_counter: int = 0
    _obj_counter_lock: Lock = Lock()

    _build_dir: str
    _module_name: str
    _state: TaskState
    _task_id: int


    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, module_name: str, build_dir: str) -> None:
        super().__init__()
        self._module_name = module_name
        self._build_dir = build_dir
        self._state = TaskState.UNINITIATED

        with TestTask._obj_counter_lock:
            self._task_id = TestTask._obj_counter
            TestTask._obj_counter += 1

        if self._module_name not in ModuleMgr().get_all_modules():
            raise ValueError(f"Module {module_name} not found")

        Logger().log_info(f"Test Task object with {module_name} correctly created", LogLevel.MEDIUM_FREQ)

    # ------------------------------
    # Class interaction
    # ------------------------------

    def try_to_init(self) -> list:
        pass



    # ------------------------------
    # Private methods
    # ------------------------------


class TestTaskMgr(metaclass=GlobalObj):
    # ------------------------------
    # Class fields
    # ------------------------------

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        Logger().log_info("Test Task Manager correctly initialized", LogLevel.LOW_FREQ)

    def destroy(self) -> None:
        Logger().log_info("Test Task Manager correctly destroyed", LogLevel.LOW_FREQ)

    # ------------------------------
    # Class interaction
    # ------------------------------

    # ------------------------------
    # Private methods
    # ------------------------------
