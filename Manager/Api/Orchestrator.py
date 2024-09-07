from fastapi import APIRouter

from ...Models.OrchestratorModels import *

router = APIRouter()


@router.post("/orchestrator/enqueue-test", tags=["orchestrator"])
async def enqueue_test(test: TestDescription) -> CommandResult:
    return CommandResult(resultCode="")


@router.get("/orchestrator/get-tests", tags=["orchestrator"])
async def get_tests(auth: AuthInfo) -> TestInfo:
    return TestInfo(result=CommandResult(resultCode=""), tests=[])


@router.get("/orchestrator/read-results", tags=["orchestrator"])
async def get_results(test_access: TestAccessInfo) -> TestResults:
    return TestResults(result=CommandResult(resultCode=""), tests=[])


@router.get("/orchestrator/get-backup", tags=["orchestrator"])
async def get_backup(test_access: TestAccessInfo) -> Backup:
    return Backup(result=CommandResult(resultCode=""), tests=[])


@router.delete("/orchestrator/delete-test", tags=["orchestrator"])
async def delete_test(test_access: TestAccessInfo) -> CommandResult:
    return CommandResult(resultCode="")


@router.post("/orchestrator/stop-test", tags=["orchestrator"])
async def stop_test(test_access: TestAccessInfo) -> CommandResult:
    return CommandResult(resultCode="")


@router.post("/orchestrator/start-test", tags=["orchestrator"])
async def start_test(test_access: TestAccessInfo) -> CommandResult:
    return CommandResult(resultCode="")
