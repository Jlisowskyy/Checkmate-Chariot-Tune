from pydantic import BaseModel


class WorkerSettings(BaseModel):
    unregister_retries: int = 10
