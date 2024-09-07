import os

from Utils.Logger import Logger, LogLevel
from Utils.SettingsLoader import SettingsLoader
from .WorkerLib.WorkerComponents import WorkerComponents
from .WorkerLib.WorkerSettings import WorkerSettings

LOGGER_PATH = "/tmp/worker.log"
SETTINGS_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/settings.json"


def worker_process_init():
    # init logger
    Logger(LOGGER_PATH, False, LogLevel.MEDIUM_FREQ)

    try:
        WorkerComponents().init_components()
    except Exception as e:
        Logger().log_error(f"Failed to start worker process: {e}", LogLevel.LOW_FREQ)

        if not WorkerComponents().is_inited():
            WorkerComponents().destroy_components()

    if WorkerComponents().is_inited():
        # init SettingsLoader
        SettingsLoader(WorkerSettings, SETTINGS_PATH)

        WorkerComponents().get_worker_process().start_processing()
        WorkerComponents().get_worker_process().wait_for_stop()

        WorkerComponents().destroy_components()
        SettingsLoader().destroy()

    Logger().destroy()
