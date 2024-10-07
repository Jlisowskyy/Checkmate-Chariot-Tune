import os

from Manager.ManagerLib.ManagerComponents import ManagerComponents
from Manager.ManagerLib.ManagerSettings import ManagerSettings, update_logger_freq, update_build_dir
from ProjectInfo.ProjectInfo import ProjectInfoInstance
from Utils.Logger import Logger, LogLevel
from Utils.SettingsLoader import SettingsLoader

SETTINGS_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/settings.json"


def startup():
    # load settings
    settings = SettingsLoader(ManagerSettings, SETTINGS_PATH).get_settings()

    # init logger
    Logger(settings.logger_path, settings.log_std_out, LogLevel(settings.log_level), settings.error_journal_path)

    SettingsLoader().add_event(update_logger_freq)
    SettingsLoader().add_event(update_build_dir)

    # ensure build dir exists
    update_build_dir(settings)

    # init singleton managers:
    ManagerComponents()
    ManagerComponents().init_components()

    # Display initial info
    ProjectInfoInstance.display_info("Manager")


def cleanup():
    ManagerComponents().destroy_components()

    SettingsLoader().destroy()
    Logger().destroy()
