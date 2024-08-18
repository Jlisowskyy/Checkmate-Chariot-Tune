from fastapi import APIRouter, WebSocket
from .WorkerModels import *
from .GlobalModels import *
# from ..ManagerLib.WorkerMgr import WorkerMgr

router = APIRouter()


@router.post("/worker/register", tags=["worker"])
async def register(worker: WorkerModel) -> WorkerRegistration:
    # result, token = WorkerMgr().register(worker)

    return WorkerRegistration(result=CommandResult(result=result), session_token=token)


@router.websocket("/worker/perform-test")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
