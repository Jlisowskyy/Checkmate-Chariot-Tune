import json

from Models.OrchestratorModels import ConfigSpecElement, UiType
from Modules.Submodules.ChessTournamentModules.BaseChessTournamentModule import BaseChessTournamentModule
from Utils.Helpers import validate_dict_str, validate_string, validate_dict_str_str
from .BaseWorkerTestModule import BaseWorkerTestModule, append_test_module_builder
from ..ModuleBuilder import ModuleBuilder
from ..ModuleHelpers import build_submodule_spec_element
from ..SubModuleMgr import SubModuleMgr


# ------------------------------
# Module Implementation
# ------------------------------

class ChessWorkerTestModule(BaseWorkerTestModule):
    # ------------------------------
    # Class fields
    # ------------------------------

    MODULE_NAME = "BaseChessModule"
    _chess_tournament_module: BaseChessTournamentModule

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, chess_tournament_module: BaseChessTournamentModule) -> None:
        super().__init__(ChessWorkerTestModule.MODULE_NAME)
        self._chess_tournament_module = chess_tournament_module

    # ------------------------------
    # Worker methods
    # ------------------------------

    async def configure_module(self, json_parsed: any, prefix: str) -> None:
        await self._chess_tournament_module.configure_module(json_parsed, prefix)

    async def configure_build(self, json_parsed: any, prefix: str) -> None:
        await self._chess_tournament_module.configure_build(json_parsed, prefix)

    async def build_module(self) -> None:
        await self._chess_tournament_module.build_module()

    async def run_single_test(self, arg_str: str, seed: int) -> str:
        parsed_json = json.loads(arg_str)

        validate_dict_str(parsed_json)

        if "opponent" not in parsed_json:
            raise Exception("Missing opponent in json")

        validate_string(parsed_json["opponent"])
        opponent = parsed_json["opponent"]

        if "params" not in parsed_json:
            raise Exception("Missing params in json")

        validate_dict_str_str(parsed_json["params"])
        params = parsed_json["params"]

        result = await self._chess_tournament_module.play_game(params, opponent, seed)
        return result

    # ------------------------------
    # Helper methods
    # ------------------------------

# ------------------------------
# Builder Implementation
# ------------------------------

class ChessWorkerTestModuleBuilder(ModuleBuilder):
    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        super().__init__(
            [
                build_submodule_spec_element(
                    BaseChessTournamentModule.SUBMODULE_TYPE,
                    "chess_tournament_module",
                    "Chess tournament module used to run tests",
                    UiType.String,
                    SubModuleMgr().get_all_submodules_by_type(BaseChessTournamentModule.SUBMODULE_TYPE),
                )
            ],
            ChessWorkerTestModule.MODULE_NAME
        )

    # ------------------------------
    # Abstract methods
    # ------------------------------

    def _get_config_spec_internal(self, prefix: str) -> list[ConfigSpecElement]:
        return []

    def _get_build_spec_internal(self, prefix: str) -> list[ConfigSpecElement]:
        return []

    def build(self, json_config: dict[str, list[str]], name_prefix: str = "") -> any:
        return ChessWorkerTestModule(
            **self._build_submodules(json_config, name_prefix)
        )


append_test_module_builder(ChessWorkerTestModule.MODULE_NAME, lambda: ChessWorkerTestModuleBuilder())
