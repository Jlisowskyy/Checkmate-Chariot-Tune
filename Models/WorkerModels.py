from pydantic import BaseModel

from Models.GlobalModels import CommandResult


class WorkerModel(BaseModel):
    name: str
    version: int
    cpus: int
    memoryMB: int


class WorkerRegistration(BaseModel):
    result: CommandResult
    session_token: int


class WorkerAuth(BaseModel):
    name: str
    session_token: str
