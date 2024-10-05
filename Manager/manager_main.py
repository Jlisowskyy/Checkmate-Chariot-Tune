from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Manager.Api import Orchestrator, Worker
from Manager.ManagerLib.StartupProcedures import startup, cleanup


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

Manager.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
