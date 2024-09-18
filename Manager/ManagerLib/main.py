import os

from .ManagerComponents import ManagerComponents
from .ManagerSettings import ManagerSettings, update_logger_freq
from ...ProjectInfo.ProjectInfo import ProjectInfoInstance
from ...Utils.Logger import Logger, LogLevel
from ...Utils.SettingsLoader import SettingsLoader

SETTINGS_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/settings.json"


def startup():
    # load settings
    settings = SettingsLoader(ManagerSettings, SETTINGS_PATH).get_settings()
    SettingsLoader().add_event(update_logger_freq)

    # init logger
    Logger(settings.logger_path, settings.log_std_out, LogLevel(settings.log_level))

    # init singleton managers:
    ManagerComponents().init_components()

    # Display initial info
    ProjectInfoInstance.display_info("Manager")


def cleanup():
    ManagerComponents().destroy_components()
