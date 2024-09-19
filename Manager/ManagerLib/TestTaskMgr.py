from Utils.Logger import Logger, LogLevel
from ...Utils.GlobalObj import GlobalObj


class TestTask:
    # ------------------------------
    # Class fields
    # ------------------------------

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        pass

    # ------------------------------
    # Class interaction
    # ------------------------------

    # ------------------------------
    # Private methods
    # ------------------------------


class TestTaskMgr(metaclass=GlobalObj):
    # ------------------------------
    # Class fields
    # ------------------------------

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        Logger().log_info("Test Task Manager correctly initialized", LogLevel.LOW_FREQ)

    def destroy(self) -> None:
        Logger().log_info("Test Task Manager correctly destroyed", LogLevel.LOW_FREQ)

    # ------------------------------
    # Class interaction
    # ------------------------------

    # ------------------------------
    # Private methods
    # ------------------------------
