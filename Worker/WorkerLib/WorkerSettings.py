from pydantic import BaseModel


class WorkerSettings(BaseModel):
    unregister_retries: int = 10
    retry_timestep: float = 1
    thread_retries: int = 10
    process_port: int = 60101
    connection_retries: int = 10
    gentle_stop_timeout: float = 15
    ka_interval: int = 10
