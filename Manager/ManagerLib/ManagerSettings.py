from ...Utils.Logger import LogLevel
from pydantic import BaseModel


class ManagerSettings(BaseModel):
    mgr_num_workers: int = 4
    logger_path: str = "./log.txt"
    log_std_out: bool = False
    log_level: int = LogLevel.MEDIUM_FREQ
    worker_timeout: int = 10