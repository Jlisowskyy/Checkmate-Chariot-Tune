import json
from enum import IntEnum
from threading import Lock

from Manager.ManagerLib.ManagerComponents import ManagerComponents
from Modules.ManagerTestModule.BaseManagerTestModule import BaseManagerTestModule
from Modules.ModuleBuilder import ModuleBuilder
from Modules.ModuleMgr import ModuleMgr
from Utils.Helpers import validate_dir, validate_dict_str_list_str, validate_dict_str
from Utils.Logger import Logger, LogLevel
from Utils.RWLock import ObjectModel


class TaskState(IntEnum):
    UNINITIATED = 0
    INITIATED = 1
    BUILT = 2
    READY = 3
    SCHEDULED = 4


class TestTask(ObjectModel):
    # ------------------------------
    # Class fields
    # ------------------------------

    _obj_counter: int = 0
    _obj_counter_lock: Lock = Lock()

    _build_dir: str
    _module_name: str
    _state: TaskState
    _task_id: int

    _config_json: str
    _build_config_json: str

    _worker_init: dict[str, list[str]]
    _manager_init: dict[str, list[str]]

    _task_module: BaseManagerTestModule | None

    _worker_module_builder: ModuleBuilder
    _manager_module_builder: ModuleBuilder

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, module_name: str, build_dir: str) -> None:
        super().__init__()
        self._module_name = module_name
        self._build_dir = build_dir
        self._state = TaskState.UNINITIATED
        self._task_module = None

        validate_dir(build_dir)
        ModuleMgr().validate_module(module_name)

        with TestTask._obj_counter_lock:
            self._task_id = TestTask._obj_counter
            TestTask._obj_counter += 1

        Logger().log_info(f"Test Task object with {module_name} correctly created", LogLevel.MEDIUM_FREQ)

    # ------------------------------
    # State changing methods
    # ------------------------------

    def try_to_init(self, submodules_json: str) -> str:
        submodules_parsed: dict[str, dict[str, list[str]]] = json.loads(submodules_json)
        validate_dict_str(submodules_parsed)

        if "worker_init" not in submodules_parsed or "manager_init" not in submodules_parsed:
            raise ValueError("\"worker_init\" and \"manager_init\" keys must be present in submodules_json")

        validate_dict_str_list_str(submodules_parsed["worker_init"])
        validate_dict_str_list_str(submodules_parsed["manager_init"])

        worker_init = submodules_parsed["worker_init"]
        manager_init = submodules_parsed["manager_init"]

        with self.perform_operation():
            with self.get_lock().read():
                if self._state != TaskState.UNINITIATED:
                    raise ValueError(f"Task {self._task_id} already initiated")

            lacking_manager_module = self._manager_module_builder.get_next_submodule_needed(manager_init)
            lacking_worker_module = self._worker_module_builder.get_next_submodule_needed(worker_init)

            with self.get_lock().write():
                self._manager_init = manager_init
                self._worker_init = worker_init

            if lacking_manager_module is not None and lacking_worker_module is not None:
                self._try_to_init_modules()
                self._change_state(TaskState.INITIATED)

            return rv

    def try_to_build(self, config_json: str) -> None:
        with self.perform_operation():
            with self.get_lock().read():
                if self._state != TaskState.INITIATED:
                    raise ValueError(f"Task {self._task_id} not initiated")

            self._build_submodules(config_json)

            with self.get_lock().write():
                self._build_config_json = config_json

            self._change_state(TaskState.BUILT)

    def try_to_config(self, config_json: str) -> None:
        with self.perform_operation():
            with self.get_lock().read():
                if self._state != TaskState.BUILT:
                    raise ValueError(f"Task {self._task_id} not built")

            self._config_submodules(config_json)

            with self.get_lock().write():
                self._config_json = config_json

            self._change_state(TaskState.READY)

    def try_to_reconfig_task(self) -> None:
        with self.perform_operation():
            with self.get_lock().read():
                state = self._state
                if state != TaskState.READY or state != TaskState.SCHEDULED:
                    raise ValueError(f"Task {self._task_id} not ready or scheduled to reconfig")

            if state == TaskState.SCHEDULED:
                ManagerComponents().get_test_job_mgr().stop_task_jobs(self._task_id, self.get_gen_num_locked())

            self._change_state(TaskState.BUILT)

    def try_to_schedule_task(self) -> None:
        with self.perform_operation():
            with self.get_lock().read():
                if self._state != TaskState.READY:
                    raise ValueError(f"Task {self._task_id} not ready")

            self._change_state(TaskState.SCHEDULED)

    def try_to_stop_task(self) -> None:
        with self.perform_operation():
            with self.get_lock().read():
                if self._state != TaskState.SCHEDULED:
                    raise ValueError(f"Task {self._task_id} not scheduled")

            self._change_state(TaskState.READY)

    # ------------------------------
    # getters and setters
    # ------------------------------

    def get_task_id(self) -> int:
        return self._task_id

    def get_task_state(self) -> TaskState:
        with self.get_lock().read():
            return self._state

    def get_module_name(self) -> str:
        return self._module_name

    def get_build_dir(self) -> str:
        return self._build_dir

    def get_config_json(self) -> str:
        with self.get_lock().read():
            return self._config_json

    def get_submodules_config_json(self) -> str:
        with self.get_lock().read():
            return json.dumps(self._submodules_config_json)

    # ------------------------------
    # Other methods
    # ------------------------------

    def prepare_config_options(self) -> str:
        with self.get_lock().read():
            if self._state != TaskState.BUILT:
                raise ValueError(f"Task {self._task_id} must be in BUILT state")

        return ""

    # ------------------------------
    # Private methods
    # ------------------------------

    def _get_sub_modules_to_pick(self, submodules_json: dict[str, list[str]]) -> list:
        pass

    def _try_to_init_modules(self) -> None:
        pass

    def _build_submodules(self, config_json: str) -> None:
        pass

    def _config_submodules(self, config_json: str) -> None:
        pass


    def _change_state(self, new_state: TaskState) -> None:
        with self.get_lock().write():
            old_state = self._state
            self._state = new_state

        Logger().log_info(f"Task {self._task_id} state changed: {old_state} -> {new_state}", LogLevel.MEDIUM_FREQ)


class TestTaskMgr:
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

    def stop_task(self, task_id: int) -> None:
        pass

    # ------------------------------
    # Private methods
    # ------------------------------
