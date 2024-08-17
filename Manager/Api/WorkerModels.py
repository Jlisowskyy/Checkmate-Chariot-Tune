from pydantic import BaseModel


class WorkerModel(BaseModel):
    name: str
    version: int
    cpus: int
    memoryMB: int
