import json

from Modules.Submodules.ChessTournamentModules.BaseChessTournamentModule import TournamentFactoryMethods, BaseChessTournamentModule
from .BaseWorkerTestModule import BaseWorkerTestModule, append_test_module_builder
from ..ManagerTestModule.BaseManagerChessModule import BaseManagerChessModule
from ..ModuleBuilder import ModuleBuilder, T
from ..ModuleHelpers import ConfigSpecElement


# ------------------------------
# Module Implementation
# ------------------------------

class ChessWorkerTestModule(BaseWorkerTestModule):
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
        await self._chess_tournament_module.load_config(arg_str)

    async def build_module(self) -> None:
        await self._chess_tournament_module.build_module()

    async def run_single_test(self, arg_str: str, seed: int) -> str:
        parsed_json = json.loads(arg_str)

        if not isinstance(parsed_json, dict):
            raise Exception("Invalid json format")

        if "opponent" not in parsed_json:
            raise Exception("Missing opponent in json")

        opponent = parsed_json["opponent"]

        if not isinstance(opponent, str):
            raise Exception("Opponent must be a string")

        if "params" not in parsed_json:
            raise Exception("Missing params in json")

        params = parsed_json["params"]

        if not isinstance(params, dict):
            raise Exception("Params must be a dictionary")

        if not all(isinstance(value, str) for value in params.values()) or not all(
                isinstance(value, str) for value in params.keys()):
            raise Exception("Params must be a dictionary with string or int values")

        result = await self._chess_tournament_module.play_game(params, opponent, seed)
        return result

    # ------------------------------
    # Helper methods
    # ------------------------------

# ------------------------------
# Builder Implementation
# ------------------------------

class ChessWorkerTestModuleBuilder(ModuleBuilder):
    def _get_build_spec_internal(self) -> list[ConfigSpecElement]:
        pass

    def build(self, json_config: dict[str, str]) -> T:
        pass

    def _get_config_spec_internal(self) -> list[ConfigSpecElement]:
        pass

append_test_module_builder("BaseChessModule", lambda : ChessWorkerTestModuleBuilder())
