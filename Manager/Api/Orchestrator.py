from fastapi import APIRouter

from Manager.ManagerLib.ManagerComponents import ManagerComponents
from Models.OrchestratorModels import *
from Modules.ModuleMgr import ModuleMgr
from Modules.SubModuleMgr import SubModuleMgr

router = APIRouter()

# ------------------------------
# Task API
# ------------------------------

@router.post("/orchestrator/task/create", tags=["orchestrator"])
async def create_task(task: TaskCreateRequest) -> TaskCreateResult:
    return ManagerComponents().get_test_task_mgr().api_create_task(task)

@router.post("/orchestrator/task/stop", tags=["orchestrator"])
async def stop_task(task: TaskOperationRequest) -> CommandResult:
    return ManagerComponents().get_test_task_mgr().api_stop_task(task)

@router.post("/orchestrator/task/build", tags=["orchestrator"])
async def build_task(task: TaskOpRequestWithConfig) -> CommandResult:
    return ManagerComponents().get_test_task_mgr().api_build_task(task)

@router.post("/orchestrator/task/config", tags=["orchestrator"])
async def config_task(task: TaskOpRequestWithConfig) -> CommandResult:
    return ManagerComponents().get_test_task_mgr().api_config_task(task)

@router.post("/orchestrator/task/reconfig", tags=["orchestrator"])
async def reconfig_task(task: TaskOperationRequest) -> CommandResult:
    return ManagerComponents().get_test_task_mgr().api_reconfig_task(task)

@router.post("/orchestrator/task/schedule", tags=["orchestrator"])
async def schedule_task(task: TaskOperationRequest) -> CommandResult:
    return ManagerComponents().get_test_task_mgr().api_schedule_task(task)

@router.post("/orchestrator/task/init", tags=["orchestrator"])
async def init_task(task: TaskInitRequest) -> TaskInitResponse:
    return ManagerComponents().get_test_task_mgr().api_init_task(task)

@router.post("/orchestrator/task/query/minimal", tags=["orchestrator"])
async def query_task_minimal() -> TaskMinimalQueryAllResponse:
    return ManagerComponents().get_test_task_mgr().api_minimal_query_all_tasks()

@router.post("/orchestrator/task/config/spec", tags=["orchestrator"])
async def query_task_config_spec(task: TaskOperationRequest) -> TaskConfigSpecResponse:
    return ManagerComponents().get_test_task_mgr().api_get_task_config_spec(task)

@router.post("/orchestrator/task/build/spec", tags=["orchestrator"])
async def query_task_build_spec(task: TaskOperationRequest) -> TaskConfigSpecResponse:
    return ManagerComponents().get_test_task_mgr().api_get_task_build_spec(task)

@router.post("/orchestrator/task/query/full", tags=["orchestrator"])
async def query_task_full(task: TaskOperationRequest) -> TestTaskFullQuery:
    return ManagerComponents().get_test_task_mgr().api_get_task_query(task)

@router.get("/orchestrator/modules/get/available", tags=["orchestrator"])
async def query_available_modules() -> ModuleQueryResponse:
    modules = ModuleMgr().get_all_modules()

    return ModuleQueryResponse(modules=modules)

@router.get("/orchestrator/submodules/get/active", tags=["orchestrator"])
async def query_active_submodules() -> SubModuleQueryResponse:
    modules = SubModuleMgr().get_all_submodules()

    return SubModuleQueryResponse(submodules=modules)

# ------------------------------
# Worker API
# ------------------------------

