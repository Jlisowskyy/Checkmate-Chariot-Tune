from fastapi import APIRouter, WebSocket
from ...Models.WorkerModels import *
from ...Models.GlobalModels import *
from ..ManagerLib.WorkerMgr import WorkerMgr
from ...Utils.Logger import Logger, LogLevel

router = APIRouter()


@router.post("/worker/register", tags=["worker"])
async def register(worker: WorkerModel) -> WorkerRegistration:
    Logger().log_info(f"Received worker register request with payload: {worker.model_dump_json()}", LogLevel.MEDIUM_FREQ)
    result, token = WorkerMgr().register(worker)
    response = WorkerRegistration(result=CommandResult(result=result.name), session_token=token)
    Logger().log_info(f"Sending worker register response: {response}", LogLevel.MEDIUM_FREQ)

    return response


@router.delete("/worker/unregister", tags=["worker"])
async def unregister(unregisterRequest: WorkerUnregister) -> CommandResult:
    Logger().log_info(f"Received worker unregister request with payload: {unregisterRequest}", LogLevel.MEDIUM_FREQ)
    result = WorkerMgr().unregister(unregisterRequest)
    response = CommandResult(result=result.name)
    Logger().log_info(f"Sending unregister response: {response}", LogLevel.MEDIUM_FREQ)
    return response


@router.websocket("/worker/perform-test")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
