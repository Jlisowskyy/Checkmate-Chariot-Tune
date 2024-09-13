from fastapi import APIRouter, WebSocket

from ..ManagerLib.ManagerComponents import ManagerComponents
from ..ManagerLib.WorkerMgr import WorkerMgr
from ...Models.WorkerModels import *
from ...Utils.Logger import Logger, LogLevel

router = APIRouter()


@router.post("/worker/register", tags=["worker"])
async def register(worker: WorkerModel) -> WorkerRegistration:
    Logger().log_info(f"Received worker register request with payload: {worker.model_dump_json()}",
                      LogLevel.MEDIUM_FREQ)
    result, token = ManagerComponents().get_worker_mgr().register(worker)
    response = WorkerRegistration(result=CommandResult(result=result.name), session_token=token)
    Logger().log_info(f"Sending worker register response: {response}", LogLevel.MEDIUM_FREQ)

    return response


@router.delete("/worker/unregister", tags=["worker"])
async def unregister(unregisterRequest: WorkerUnregister) -> CommandResult:
    Logger().log_info(f"Received worker unregister request with payload: {unregisterRequest}", LogLevel.MEDIUM_FREQ)
    result = ManagerComponents().get_worker_mgr().unregister(unregisterRequest)
    response = CommandResult(result=result.name)
    Logger().log_info(f"Sending unregister response: {response}", LogLevel.MEDIUM_FREQ)
    return response


@router.websocket("/worker/perform-test")
async def websocket_endpoint(websocket: WebSocket):
    with await websocket.accept() as websocket:
        ManagerComponents().get_worker_mgr().worker_loop(websocket)

