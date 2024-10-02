from pydantic import BaseModel

from Manager.ManagerLib.ManagerComponents import ManagerComponents
from Utils.Helpers import ensure_path_exists
from Utils.Logger import LogLevel, Logger


class ManagerSettings(BaseModel):
    mgr_num_workers: int = 4
    logger_path: str = "./log.txt"
    log_std_out: bool = False
    log_level: int = LogLevel.MEDIUM_FREQ
    worker_timeout: int = 10
    build_dir: str = "/tmp/Checkmate-Chariot-tune-builds/"
    job_threads: int = 8
    job_failures_limit: int = 3


def update_logger_freq(settings: BaseModel) -> None:
    Logger().set_log_level(LogLevel(settings.log_level))

def update_build_dir(settings: BaseModel) -> None:
    ensure_path_exists(settings.build_dir)

def update_job_threads(settings: BaseModel) -> None:
    ManagerComponents().get_test_job_mgr().update_thread_count(settings.job_threads)