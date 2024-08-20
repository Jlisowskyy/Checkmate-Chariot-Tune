from .TestJobMgr import TestJobMgr
from .TestTaskMgr import TestTaskMgr
from .WorkerMgr import WorkerMgr
from .SettingsLoader import SettingsLoader
from ...ProjectInfo.ProjectInfo import ProjectInfoInstance
from ...Utils.Logger import Logger, LogLevel

import os

SETTINGS_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/settings.json"


def startup():
    # load settings
    settings = SettingsLoader(SETTINGS_PATH).get_settings()

    # init logger
    Logger(settings.logger_path, settings.log_std_out, LogLevel(settings.log_level))

    # init singleton managers:
    WorkerMgr()
    TestTaskMgr(settings.mgr_num_workers)
    TestJobMgr(settings.mgr_num_workers)

    # Display initial info
    ProjectInfoInstance.display_info("Manager")


def cleanup():
    WorkerMgr().destroy()
    Logger().destroy()
