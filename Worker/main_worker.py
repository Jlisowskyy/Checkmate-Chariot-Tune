import time
import os

from .WorkerLib.WorkerProcess import WorkerProcess
from Utils.Logger import Logger, LogLevel
from Utils.SettingsLoader import SettingsLoader
from .WorkerLib.WorkerSettings import WorkerSettings

LOGGER_PATH = "/tmp/worker.log"
SETTINGS_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/settings.json"


def worker_process_init():
    worker_process = None

    # init logger
    Logger(LOGGER_PATH, False, LogLevel.LOW_FREQ)

    try:
        worker_process = WorkerProcess()
    except Exception as e:
        Logger().log_error(f"Failed to start worker process: {e}", LogLevel.LOW_FREQ)

        if worker_process is not None:
            worker_process.destroy()
        worker_process = None

    if worker_process is not None:
        # init SettingsLoader
        SettingsLoader(WorkerSettings, SETTINGS_PATH)

        worker_process.start_processing()

    time.sleep(10)
    print("ELO")

    Logger().destroy()
