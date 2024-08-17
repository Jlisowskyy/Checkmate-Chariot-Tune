from fastapi import FastAPI
from .Api import Orchestrator, Worker


Manager = FastAPI()
Manager.include_router(Orchestrator.router)
Manager.include_router(Worker.router)

