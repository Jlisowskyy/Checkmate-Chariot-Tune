from abc import ABC

from .BaseModule import BaseModule

class BaseChessModule(BaseModule, ABC):
    # ------------------------------
    # Class fields
    # ------------------------------

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        super().__init__()

    # ------------------------------
    # Worker methods
    # ------------------------------

    async def run_single_test(self, arg_str: str) -> None:
        pass

    # ------------------------------
    # Manager methods
    # ------------------------------

    async def prepare_test_args(self) -> str:
        pass

    async def sync_test_results(self, response: str) -> None:
        pass

    # ------------------------------
    # Manager methods
    # ------------------------------