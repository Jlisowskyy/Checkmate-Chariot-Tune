from abc import ABC, abstractmethod

from .BaseModule import BaseModule
from .ChessTournamentModules.BaseChessTournamentModule import BaseChessTournamentModule

class BaseChessModule(BaseModule, ABC):
    # ------------------------------
    # Class fields
    # ------------------------------

    _chess_tournament_module: BaseChessTournamentModule

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, chess_tournament_module: BaseChessTournamentModule) -> None:
        super().__init__()
        self._chess_tournament_module = chess_tournament_module

    # ------------------------------
    # Worker methods
    # ------------------------------

    async def load_module_config_from_mgr(self, arg_str: str) -> None:
        pass

    async def build_module(self, build_path: str) -> None:
        await self._chess_tournament_module.build_module(build_path)
        await self.build_engine(build_path)

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
    # Helper methods
    # ------------------------------


    # ------------------------------
    # Chess module abstracts
    # ------------------------------

    @abstractmethod
    async def build_engine(self, build_path: str) -> None:
        pass