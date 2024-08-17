from fastapi import APIRouter, WebSocket
from .WorkerModels import *

router = APIRouter()


@router.get("/worker/get-test", tags=["worker"])
async def get_test():
    return {"message": "Hello World"}


@router.websocket("/worker/perform-test")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
