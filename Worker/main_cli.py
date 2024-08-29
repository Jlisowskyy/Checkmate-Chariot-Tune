from Utils.Logger import Logger, LogLevel
from ProjectInfo.ProjectInfo import ProjectInfoInstance
from .WorkerLib.Cli import Cli
from Utils.SettingsLoader import SettingsLoader
from .WorkerLib.WorkerSettings import WorkerSettings
import os

SETTINGS_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/settings.json"


def main_cli(args: list[str]) -> None:
    # init logger
    Logger("./cli.log", False, LogLevel.MEDIUM_FREQ)
    SettingsLoader(WorkerSettings, SETTINGS_PATH)

    ProjectInfoInstance.display_info("CLI")

    cli = Cli()
    cli.parse_args(args)

    SettingsLoader().destroy()
    Logger().destroy()
