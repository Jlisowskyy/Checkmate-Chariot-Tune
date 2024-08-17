from fastapi import APIRouter
from .OrchestratorModels import *

router = APIRouter()


@router.post("/orchestrator/enqueue-test", tags=["orchestrator"])
async def enqueue_test(test: TestDescription) -> CommandResult:
    return CommandResult(resultCode=1)


@router.get("/orchestrator/get-tests", tags=["orchestrator"])
async def get_tests(auth: AuthInfo) -> TestInfo:
    return TestInfo(result=CommandResult(resultCode=0), tests=[])


@router.get("/orchestrator/read-results", tags=["orchestrator"])
async def get_results(test_access: TestAccessInfo) -> TestResults:
    return TestResults(result=CommandResult(resultCode=0), tests=[])


@router.get("/orchestrator/get-backup", tags=["orchestrator"])
async def get_backup():
    return {"message": "Hello World"}


@router.delete("/orchestrator/delete-test", tags=["orchestrator"])
async def delete_test():
    return {"message": "Hello World"}


@router.post("/orchestrator/stop-test", tags=["orchestrator"])
async def stop_test():
    return {"message": "Hello World"}


@router.post("/orchestrator/start-test", tags=["orchestrator"])
async def start_test():
    return {"message": "Hello World"}
