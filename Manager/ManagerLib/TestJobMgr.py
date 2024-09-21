from Utils.Logger import Logger, LogLevel

class TestJobMgr():
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

    def stop_task_jobs(self, task_id: int, task_gen_num: int) -> None:
        pass

    # ------------------------------
    # Private methods
    # ------------------------------
