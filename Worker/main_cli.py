import os

from Worker.WorkerLib.CliTranslator import CliTranslator
from Utils.Logger import Logger, LogLevel
from Utils.SettingsLoader import SettingsLoader
from Worker.WorkerLib.WorkerSettings import WorkerSettings
from Worker.WorkerLib.WorkerCLI import WorkerCLI

SETTINGS_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/settings.json"


def main_cli(args: list[str]) -> None:
    # init logger
    Logger("./log.txt", False, LogLevel.MEDIUM_FREQ)

    # init SettingsLoader
    SettingsLoader(WorkerSettings, SETTINGS_PATH)

    # init worker object
    instance = WorkerCLI()

    # init worker CLI
    CliTranslator(instance).parse_args(args).parse_stdin()

    SettingsLoader().destroy()
    Logger().destroy()
