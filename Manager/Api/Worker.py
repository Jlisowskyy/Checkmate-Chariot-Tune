from fastapi import APIRouter, WebSocket

from ..ManagerLib.ErrorTable import ErrorTable
from ..ManagerLib.ManagerComponents import ManagerComponents
from ...Models.WorkerModels import *
from ...Utils.Logger import Logger, LogLevel

router = APIRouter()


@router.post("/worker/register", tags=["worker"])
async def register(worker: WorkerModel) -> WorkerRegistration:
    Logger().log_info(f"Received worker register request with payload: {worker.model_dump_json()}",
                      LogLevel.MEDIUM_FREQ)

    try:
        result, token = ManagerComponents().get_worker_mgr().register(worker)
    except Exception as e:
        Logger().log_error(f"Failed to register worker by unknown reason: {e}", LogLevel.MEDIUM_FREQ)
        result = ErrorTable.UNKNOWN_ERROR
        token = 0x0

    response = WorkerRegistration(result=CommandResult(result=result.name), session_token=token)
    Logger().log_info(f"Sending worker register response: {response}", LogLevel.MEDIUM_FREQ)

    return response


@router.delete("/worker/unregister", tags=["worker"])
async def unregister(unregisterRequest: WorkerAuth) -> CommandResult:
    Logger().log_info(f"Received worker unregister request with payload: {unregisterRequest}", LogLevel.MEDIUM_FREQ)

    try:
        result = ManagerComponents().get_worker_mgr().unregister(unregisterRequest)
    except Exception as e:
        Logger().log_error(f"Failed to process unregister request by unknown reason: {e}", LogLevel.MEDIUM_FREQ)
        result = ErrorTable.UNKNOWN_ERROR

    response = CommandResult(result=result.name)
    Logger().log_info(f"Sending unregister response: {response}", LogLevel.MEDIUM_FREQ)
    return response


@router.post("/worker/bump_ka", tags=["worker"])
async def bump_ka(worker: WorkerAuth) -> CommandResult:
    Logger().log_info("Received worker bump_ka request", LogLevel.HIGH_FREQ)

    try:
        result = ManagerComponents().get_worker_mgr().bump_ka(worker)
    except Exception as e:
        Logger().log_error(f"Failed to process bump ka request by unknown reason: {e}", LogLevel.HIGH_FREQ)
        result = ErrorTable.UNKNOWN_ERROR

    response = CommandResult(result=result.name)
    Logger().log_info(f"Sending worker bump_ka response: {response}", LogLevel.HIGH_FREQ)

    return response


@router.websocket("/worker/perform-test")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    addr = websocket.client
    Logger().log_info(f"Received active connection from: {addr}", LogLevel.MEDIUM_FREQ)

    try:
        await ManagerComponents().get_worker_mgr().worker_socket_accept(websocket)
    except Exception as e:
        Logger().log_error(f"Error occurred during active connection: {e}", LogLevel.LOW_FREQ)
        await websocket.close()
        return

    Logger().log_info(f"Active connection to {addr} closed", LogLevel.MEDIUM_FREQ)
