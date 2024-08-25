from ...Utils.Logger import LogLevel, Logger
from pydantic import BaseModel


class ManagerSettings(BaseModel):
    mgr_num_workers: int = 4
    logger_path: str = "./log.txt"
    log_std_out: bool = False
    log_level: int = LogLevel.MEDIUM_FREQ
    worker_timeout: int = 10


def update_logger_freq(settings: ManagerSettings) -> None:
    Logger().set_log_level(LogLevel(settings.log_level))
