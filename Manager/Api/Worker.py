from fastapi import APIRouter, WebSocket
from .WorkerModels import *
from .GlobalModels import *

router = APIRouter()


@router.post("/worker/register", tags=["worker"])
async def register(worker: WorkerModel) -> CommandResult:
    return CommandResult(result="")

@router.websocket("/worker/perform-test")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
