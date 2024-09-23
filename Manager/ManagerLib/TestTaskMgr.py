import json
from collections.abc import Callable
from threading import Lock

from Manager.ManagerLib.ManagerComponents import ManagerComponents
from Models.GlobalModels import CommandResult
from Models.OrchestratorModels import TaskCreateRequest, TaskOperationRequest, TaskOpRequestWithConfig, \
    ConfigSpecElement, TaskInitResponse, TaskState, TaskMinimalQueryAllResponse, TestTaskMinimalQuery, \
    TaskConfigSpecResponse, TestTaskFullQuery
from Modules.ManagerTestModule.BaseManagerTestModule import BaseManagerTestModule
from Modules.ModuleBuilder import ModuleBuilder
from Modules.ModuleMgr import ModuleMgr
from Modules.WorkerTestModule.BaseWorkerTestModule import BaseWorkerTestModule
from Utils.Helpers import validate_dict_str_list_str, validate_dict_str
from Utils.Logger import Logger, LogLevel
from Utils.RWLock import ObjectModel
from Utils.SettingsLoader import SettingsLoader


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

    _task_name: str
    _task_description: str

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, module_name: str, task_name: str, task_description: str) -> None:
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

        self._task_name = task_name
        self._task_description = task_description

        with TestTask._obj_counter_lock:
            self._task_id = TestTask._obj_counter
            TestTask._obj_counter += 1

        Logger().log_info(f"Test Task object with {module_name} correctly created", LogLevel.MEDIUM_FREQ)

    # ------------------------------
    # State changing methods
    # ------------------------------

    def try_to_init(self, submodules_json: str) -> [ConfigSpecElement | None, ConfigSpecElement | None]:
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

            if lacking_manager_module is None and lacking_worker_module is None:
                self._try_to_init_modules()
                self._change_state(TaskState.INITIATED)

        return [lacking_worker_module, lacking_manager_module]

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

    def get_full_task_query(self) -> TestTaskFullQuery:
        with self.perform_operation():
            with self.get_lock().read():
                return TestTaskFullQuery(minimal_query=TestTaskMinimalQuery(task_id=self._task_id,
                                                                            name=self._task_name,
                                                                            description=self._task_description,
                                                                            module_name=self._module_name,
                                                                            task_state=self._state),
                                         worker_init_config=self._worker_init,
                                         manager_init_config=self._manager_init,
                                         worker_build_config=self._worker_build_config,
                                         manager_build_config=self._manager_build_config,
                                         worker_config=self._worker_config,
                                         manager_config=self._manager_config)

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

    def get_task_name(self) -> str:
        return self._task_name

    def get_task_description(self) -> str:
        return self._task_description

    def get_worker_config_spec_unguarded(self) -> list[ConfigSpecElement]:
        return self._worker_module_builder.get_config_spec(self._worker_init)

    def get_manager_config_spec_unguarded(self) -> list[ConfigSpecElement]:
        return self._manager_module_builder.get_config_spec(self._manager_init)

    def get_worker_build_spec_unguarded(self) -> list[ConfigSpecElement]:
        return self._worker_module_builder.get_build_spec(self._worker_init)

    def get_manager_build_spec_unguarded(self) -> list[ConfigSpecElement]:
        return self._manager_module_builder.get_build_spec(self._manager_init)


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

    def _validate_init_state_unlocked(self) -> None:
        if self._state == TaskState.UNINITIATED:
            raise ValueError(f"Task {self._task_id} not initiated")

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


class TestTaskMgr(ObjectModel):
    # ------------------------------
    # Class fields
    # ------------------------------

    _task_container: dict[int, TestTask]

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        super().__init__()
        self._task_container = dict[int, TestTask]()

        Logger().log_info("Test Task Manager correctly initialized", LogLevel.LOW_FREQ)

    def destroy(self) -> None:
        Logger().log_info("Test Task Manager correctly destroyed", LogLevel.LOW_FREQ)

    # ------------------------------
    # Class interaction
    # ------------------------------

    def create_task(self, module_name: str, name: str, description: str) -> int:
        new_task = TestTask(module_name, name, description)

        with new_task.get_lock().write():
            self._task_container[new_task.get_task_id()] = new_task

        return new_task.get_task_id()

    def init_task(self, task_id: int, submodules_json: str) -> [ConfigSpecElement | None, ConfigSpecElement | None]:
        task = self._validate_and_get_task(task_id)
        return task.try_to_init(submodules_json)

    def stop_task(self, task_id: int) -> None:
        task = self._validate_and_get_task(task_id)
        task.try_to_stop_task()

    def build_task(self, task_id: int, config_json: str) -> None:
        task = self._validate_and_get_task(task_id)
        task.try_to_build(config_json)

    def config_task(self, task_id: int, config_json: str) -> None:
        task = self._validate_and_get_task(task_id)
        task.try_to_config(config_json)

    def reconfig_task(self, task_id: int) -> None:
        task = self._validate_and_get_task(task_id)
        task.try_to_reconfig_task()

    def schedule_task(self, task_id: int) -> None:
        task = self._validate_and_get_task(task_id)
        task.try_to_schedule_task()

    def get_task_query(self, task_id: int) -> TestTaskFullQuery:
        task = self._validate_and_get_task(task_id)
        return task.get_full_task_query()

    # ------------------------------
    # API methods
    # ------------------------------

    def api_create_task(self, task_create_request: TaskCreateRequest) -> CommandResult:
        try:
            task_id = self.create_task(task_create_request.module_name, task_create_request.name,
                                       task_create_request.description)
            return CommandResult(result="", task_id=task_id)
        except Exception as e:
            return CommandResult(result=f"Error while creating task: {e}", task_id=-1)

    def api_stop_task(self, op_request: TaskOperationRequest) -> CommandResult:
        return TestTaskMgr._prepare_simple_command_response(lambda: self.stop_task(op_request.task_id))

    def api_build_task(self, op_request: TaskOpRequestWithConfig) -> CommandResult:
        return TestTaskMgr._prepare_simple_command_response(
            lambda: self.build_task(op_request.task_id, op_request.config))

    def api_config_task(self, op_request: TaskOpRequestWithConfig) -> CommandResult:
        return TestTaskMgr._prepare_simple_command_response(
            lambda: self.config_task(op_request.task_id, op_request.config))

    def api_reconfig_task(self, op_request: TaskOperationRequest) -> CommandResult:
        return TestTaskMgr._prepare_simple_command_response(lambda: self.reconfig_task(op_request.task_id))

    def api_schedule_task(self, op_request: TaskOperationRequest) -> CommandResult:
        return TestTaskMgr._prepare_simple_command_response(lambda: self.schedule_task(op_request.task_id))

    def api_init_task(self, op_request: TaskOpRequestWithConfig) -> TaskInitResponse:
        try:
            lacking_worker_module, lacking_manager_module = self.init_task(op_request.task_id, op_request.config)
            return TaskInitResponse(worker_config_spec=lacking_worker_module,
                                    manager_config_spec=lacking_manager_module,
                                    result="")
        except Exception as e:
            return TaskInitResponse(worker_config_spec=None, manager_config_spec=None,
                                    result=f"Error while initializing task: {e}")

    def api_minimal_query_all_tasks(self) -> TaskMinimalQueryAllResponse:
        with self.get_lock().read():
            queries = [TestTaskMinimalQuery(task_id=task_id,
                                            name=task.get_task_name(),
                                            description=task.get_task_description(),
                                            module_name=task.get_module_name(),
                                            task_state=task.get_task_state())
                       for task_id, task in self._task_container.items()]

        return TaskMinimalQueryAllResponse(queries=queries)

    def api_get_task_config_spec(self, op_request: TaskOperationRequest) -> TaskConfigSpecResponse:
        task = self._validate_and_get_task(op_request.task_id)

        if task.get_task_state() == TaskState.UNINITIATED:
            return TaskConfigSpecResponse(worker_config_spec=None, manager_config_spec=None,
                                          result="Task not initiated")

        with task.get_lock().read():
            worker_config_spec = task.get_worker_config_spec_unguarded()
            manager_config_spec = task.get_manager_config_spec_unguarded()

        return TaskConfigSpecResponse(worker_config_spec=worker_config_spec, manager_config_spec=manager_config_spec,
                                      result="")

    def api_get_task_build_spec(self, op_request: TaskOperationRequest) -> TaskConfigSpecResponse:
        task = self._validate_and_get_task(op_request.task_id)

        if task.get_task_state() == TaskState.UNINITIATED:
            return TaskConfigSpecResponse(worker_config_spec=None, manager_config_spec=None,
                                          result="Task not initiated")

        with task.get_lock().read():
            worker_build_spec = task.get_worker_build_spec_unguarded()
            manager_build_spec = task.get_manager_build_spec_unguarded()

        return TaskConfigSpecResponse(worker_config_spec=worker_build_spec, manager_config_spec=manager_build_spec,
                                      result="")

    def api_get_task_query(self, op_request: TaskOperationRequest) -> TestTaskFullQuery:
        task = self._validate_and_get_task(op_request.task_id)
        return task.get_full_task_query()

    # ------------------------------
    # Private methods
    # ------------------------------

    @staticmethod
    def _prepare_simple_command_response(action: Callable[[], None]) -> CommandResult:
        try:
            action()
            return CommandResult(result="")
        except Exception as e:
            return CommandResult(result=f"Error while performing action: {e}")

    def _validate_task_exists_unlocked(self, task_id: int) -> None:
        if task_id not in self._task_container:
            raise ValueError(f"Task {task_id} not found")

    def _validate_and_get_task(self, task_id: int) -> TestTask:
        with self.get_lock().read():
            self._validate_task_exists_unlocked(task_id)
            return self._task_container[task_id]
