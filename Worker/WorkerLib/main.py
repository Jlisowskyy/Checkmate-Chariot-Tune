import os
from .cli import CliTranslator
from Utils.Logger import Logger, LogLevel
from Utils.SettingsLoader import SettingsLoader
from Worker.WorkerLib.WorkerSettings import WorkerSettings
from Worker.WorkerLib.WorkerInstance import WorkerInstance

SETTINGS_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/settings.json"


# TODOS:
# - make WorkerInstance not global
# - finish retries
# - finish unregister
# - create settings refresh

def main(args: list[str]) -> None:
    # init logger
    Logger("./log.txt", False, LogLevel.MEDIUM_FREQ)

    # init SettingsLoader
    SettingsLoader(WorkerSettings, SETTINGS_PATH)

    # init worker object
    WorkerInstance()

    # init worker CLI
    CliTranslator().parse_args(args).parse_stdin()
