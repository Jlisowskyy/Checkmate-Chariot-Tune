import subprocess

from Utils.Logger import Logger, LogLevel
from BaseCli import BaseCli
import CliTranslator


class Cli(BaseCli):
    # ------------------------------
    # Class fields
    # ------------------------------

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self):
        super().__init__()

    # ------------------------------
    # Class interaction
    # ------------------------------

    def parse_args(self, args):
        pass

    # ---------------------------------------------
    # Abstract/Virtual methods implementation
    # ---------------------------------------------

    def execute_command(self, index: int) -> int:
        pass

    # ------------------------------
    # Private methods
    # ------------------------------

    # ------------------------------
    # Available Commands
    # ------------------------------

    @staticmethod
    def _deploy(index: int) -> int:
        process = subprocess.Popen(['python', ''])

        Logger().log_info("Worker process correctly deployed", LogLevel.LOW_FREQ)

        return index

    @staticmethod
    def _deploy_help() -> None:
        print(
            "syntax: --deploy\n\t"
            "Command will try to create a background process that will be responsible\n"
            "for all job processing"
        )