from Utils.Logger import Logger, LogLevel
from ProjectInfo.ProjectInfo import ProjectInfoInstance
from .WorkerLib.Cli import Cli

def main_cli(args: list[str]) -> None:
    # init logger
    Logger("./log.txt", False, LogLevel.MEDIUM_FREQ)

    ProjectInfoInstance.display_info("CLI")

    cli = Cli()

    Logger().destroy()
