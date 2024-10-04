import os

from ProjectInfo.ProjectInfo import ProjectInfoInstance
from Utils.Logger import Logger, LogLevel
from Utils.SettingsLoader import SettingsLoader
from Worker.WorkerLib.Cli import Cli
from Worker.WorkerLib.WorkerSettings import WorkerSettings

SETTINGS_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/settings.json"


def main_cli(args: list[str]) -> int:
    # init logger
    Logger("./cli.log", False, LogLevel.MEDIUM_FREQ)
    SettingsLoader(WorkerSettings, SETTINGS_PATH)

    cli = Cli()
    rv = cli.parse_args(args)

    SettingsLoader().destroy()
    Logger().destroy()

    return rv
