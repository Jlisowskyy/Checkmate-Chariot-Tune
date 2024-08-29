from pydantic import BaseModel


class WorkerSettings(BaseModel):
    unregister_retries: int = 10
    retry_timestep: float = 1
    thread_retries: int = 10
    process_port: int = 60101
