from pydantic import BaseModel


class WorkerModel(BaseModel):
    name: str
    cpus: int
    memoryMB: int
