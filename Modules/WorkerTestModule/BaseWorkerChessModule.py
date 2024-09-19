import json

from Modules.Submodules.ChessTournamentModules.BaseChessTournamentModule import TournamentFactoryMethods, BaseChessTournamentModule
from .BaseWorkerTestModule import BaseWorkerTestModule, append_test_module_factory_method


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

    # ------------------------------
    # Helper methods
    # ------------------------------


def build_from_json(arg: dict[str, str]) -> ChessWorkerTestModule:
    if "chess_tournament_module" not in arg:
        raise Exception("Missing chess_tournament_module in json")

    if "build_dir" not in arg:
        raise Exception("Missing build_dir in json")

    chess_tournament_module_name = arg["chess_tournament_module"]
    build_dir = arg["build_dir"]
    chess_tournament_module = TournamentFactoryMethods[chess_tournament_module_name](build_dir, arg)
    return ChessWorkerTestModule(chess_tournament_module)


append_test_module_factory_method("BaseChessModule", build_from_json)
