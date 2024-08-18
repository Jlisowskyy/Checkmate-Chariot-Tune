from fastapi import FastAPI
from contextlib import asynccontextmanager

from .Api import Orchestrator, Worker
from .ManagerLib.main import startup, cleanup


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Process starting actions
    startup()
    yield

    # Process stopping actions
    cleanup()


# init api:
Manager = FastAPI(lifespan=lifespan)
Manager.include_router(Orchestrator.router)
Manager.include_router(Worker.router)
