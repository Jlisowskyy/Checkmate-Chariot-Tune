from Utils.Logger import Logger, LogLevel
from ...Utils.GlobalObj import GlobalObj


class TestJobMgr(metaclass=GlobalObj):
    # ------------------------------
    # Class fields
    # ------------------------------

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        Logger().log_info("Test Job Manager correctly initialized", LogLevel.LOW_FREQ)

    def destroy(self) -> None:
        Logger().log_info("Test Job Manager destroyed", LogLevel.LOW_FREQ)

    # ------------------------------
    # Class interaction
    # ------------------------------

    # ------------------------------
    # Private methods
    # ------------------------------
