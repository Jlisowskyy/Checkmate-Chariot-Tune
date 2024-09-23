import json
from enum import IntEnum
from threading import Lock

from Manager.ManagerLib.ManagerComponents import ManagerComponents
from Modules.ManagerTestModule.BaseManagerTestModule import BaseManagerTestModule
from Modules.ModuleBuilder import ModuleBuilder
from Modules.ModuleMgr import ModuleMgr
from Modules.WorkerTestModule.BaseWorkerTestModule import BaseWorkerTestModule
from Utils.Helpers import validate_dict_str_list_str, validate_dict_str
from Utils.Logger import Logger, LogLevel
from Utils.RWLock import ObjectModel
from Utils.SettingsLoader import SettingsLoader


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

    _module_name: str
    _state: TaskState
    _task_id: int

    _worker_init: dict[str, list[str]] | None
    _manager_init: dict[str, list[str]] | None

    _worker_build_config: dict[str, any] | None
    _manager_build_config: dict[str, any] | None

    _worker_config: dict[str, any] | None
    _manager_config: dict[str, any] | None

    _task_module: BaseManagerTestModule | None
    _worker_task_module: BaseWorkerTestModule | None

    _worker_module_builder: ModuleBuilder
    _manager_module_builder: ModuleBuilder

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, module_name: str) -> None:
        super().__init__()
        self._module_name = module_name
        self._state = TaskState.UNINITIATED

        ModuleMgr().validate_module(module_name)

        self._worker_init = None
        self._manager_init = None

        self._worker_build_config = None
        self._manager_build_config = None

        self._worker_config = None
        self._manager_config = None

        self._task_module = None
        self._worker_task_module = None

        self._worker_module_builder = ModuleMgr().get_module_worker_part(module_name)
        self._manager_module_builder = ModuleMgr().get_module_manager_part(module_name)

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

        rv = {}
        if lacking_manager_module is not None:
            rv["manager_init"] = lacking_manager_module.model_dump()

        if lacking_worker_module is not None:
            rv["worker_init"] = lacking_worker_module.model_dump()

        dumped_rv = json.dumps(rv)

        Logger().log_info(f"Task request to init modules with payload: {dumped_rv}", LogLevel.MEDIUM_FREQ)
        return dumped_rv

    def try_to_build(self, config_json: str) -> None:
        with self.perform_operation():
            with self.get_lock().read():
                if self._state != TaskState.INITIATED:
                    raise ValueError(f"Task {self._task_id} not initiated")

            self._build_submodules(config_json)
            self._change_state(TaskState.BUILT)

    def try_to_config(self, config_json: str) -> None:
        with self.perform_operation():
            with self.get_lock().read():
                if self._state != TaskState.BUILT:
                    raise ValueError(f"Task {self._task_id} not built")

            self._config_submodules(config_json)
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

            ManagerComponents().get_test_job_mgr().stop_task_jobs(self._task_id, self.get_gen_num_locked())
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

    def get_worker_build_config(self) -> dict[str, any]:
        with self.get_lock().read():
            return self._worker_build_config

    def get_manager_build_config(self) -> dict[str, any]:
        with self.get_lock().read():
            return self._manager_build_config

    def get_worker_config(self) -> dict[str, any]:
        with self.get_lock().read():
            return self._worker_config

    def get_manager_config(self) -> dict[str, any]:
        with self.get_lock().read():
            return self._manager_config

    def get_worker_init(self) -> dict[str, list[str]]:
        with self.get_lock().read():
            return self._worker_init

    def get_manager_init(self) -> dict[str, list[str]]:
        with self.get_lock().read():
            return self._manager_init

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

    def _try_to_init_modules(self) -> None:
        try:
            self._worker_task_module = self._worker_module_builder.build(self._worker_init)
        except Exception as e:
            Logger().log_error(f"Error while initializing worker module: {e}", LogLevel.LOW_FREQ)
            raise e

        try:
            self._task_module = self._manager_module_builder.build(self._manager_init)
        except Exception as e:
            Logger().log_error(f"Error while initializing manager module: {e}", LogLevel.LOW_FREQ)
            raise e

    def _build_submodules(self, config_json: str) -> None:
        json_parsed: dict[str, dict[str, any]] = json.loads(config_json)
        validate_dict_str(json_parsed)

        if "worker_build_config" not in json_parsed or "manager_build_config" not in json_parsed:
            raise ValueError("\"worker_build_config\" and \"manager_build_config\" keys must be present in config_json")

        validate_dict_str(json_parsed["worker_build_config"])
        validate_dict_str_list_str(json_parsed["manager_build_config"])

        worker_build_config = json_parsed["worker_build_config"]
        manager_build_config = json_parsed["manager_build_config"]

        worker_build_config["build_dir"] = SettingsLoader().get_settings().build_dir
        manager_build_config["build_dir"] = SettingsLoader().get_settings().build_dir

        try:
            self._worker_task_module.configure_build(worker_build_config)
            self._worker_task_module.build_module()
        except Exception as e:
            Logger().log_error(f"Error while building worker module: {e}", LogLevel.LOW_FREQ)
            raise e

        try:
            self._task_module.configure_build(manager_build_config)
            self._task_module.build_module()
        except Exception as e:
            Logger().log_error(f"Error while building manager module: {e}", LogLevel.LOW_FREQ)
            raise e

        with self.get_lock().write():
            self._worker_build_config = worker_build_config
            self._manager_build_config = manager_build_config


    def _config_submodules(self, config_json: str) -> None:
        parsed_json: dict[str, dict[str, any]] = json.loads(config_json)

        validate_dict_str(parsed_json)

        if "worker_config" not in parsed_json or "manager_config" not in parsed_json:
            raise ValueError("\"worker_config\" and \"manager_config\" keys must be present in config_json")

        validate_dict_str(parsed_json["worker_config"])
        validate_dict_str(parsed_json["manager_config"])

        worker_config = parsed_json["worker_config"]
        manager_config = parsed_json["manager_config"]

        try:
            self._worker_task_module.configure_module(worker_config)
        except Exception as e:
            Logger().log_error(f"Error while configuring worker module: {e}", LogLevel.LOW_FREQ)
            raise e

        try:
            self._task_module.configure_module(manager_config)
        except Exception as e:
            Logger().log_error(f"Error while configuring manager module: {e}", LogLevel.LOW_FREQ)
            raise e

        with self.get_lock().write():
            self._worker_config = worker_config
            self._manager_config = manager_config

    def _change_state(self, new_state: TaskState) -> None:
        with self.get_lock().write():
            old_state = self._state
            self._state = new_state

            self.increment_gen_num_unlocked()

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
