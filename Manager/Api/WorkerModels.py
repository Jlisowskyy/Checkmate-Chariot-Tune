from pydantic import BaseModel
from .GlobalModels import CommandResult


class WorkerModel(BaseModel):
    name: str
    version: int
    cpus: int
    memoryMB: int


class WorkerRegistration(BaseModel):
    result: CommandResult
    session_token: str
