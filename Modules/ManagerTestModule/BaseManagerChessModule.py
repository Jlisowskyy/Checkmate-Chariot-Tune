from Models.OrchestratorModels import ConfigSpecElement, UiType
from .BaseManagerTestModule import BaseManagerTestModule, append_test_module_builder
from ..ModuleBuilder import ModuleBuilder
from ..ModuleHelpers import build_submodule_spec_element
from ..SubModuleMgr import SubModuleMgr
from ..Submodules.TrainingMethodsModules.BaseTrainingMethodModule import BaseTrainingMethodModule


# ------------------------------
# Module Implementation
# ------------------------------

class BaseManagerChessModule(BaseManagerTestModule):
    # ------------------------------
    # Class fields
    # ------------------------------

    MODULE_NAME = "BaseChessModule"
    _chess_training_module: BaseTrainingMethodModule

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, training_module: BaseTrainingMethodModule) -> None:
        super().__init__(BaseManagerChessModule.MODULE_NAME)
        self._chess_training_module = training_module

    # ------------------------------
    # Abstract methods
    # ------------------------------

    async def prepare_test_args(self) -> str:
        return await self._chess_training_module.get_next_game_args()

    async def sync_test_results(self, response: str) -> None:
        await self._chess_training_module.save_game_result(response)

    async def build_module(self) -> None:
        await self._chess_training_module.build_module()

    async def configure_build(self, json: any, prefix: str) -> None:
        await self._chess_training_module.configure_build(json, prefix)

    async def configure_module(self, json_parsed: str, prefix: str) -> None:
        await self._chess_training_module.configure_module(json_parsed, prefix)


# ------------------------------
# Builder Implementation
# ------------------------------

class BaseManagerChessModuleBuilder(ModuleBuilder):
    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        super().__init__(
            [
            build_submodule_spec_element(
                BaseTrainingMethodModule.SUBMODULE_TYPE,
                "training_module",
                "Chess training method used to find best parameters for algorithms",
                UiType.String,
                SubModuleMgr().get_all_submodules_by_type(BaseTrainingMethodModule.SUBMODULE_TYPE),
            )
            ],
            BaseManagerChessModule.MODULE_NAME
        )

    # ------------------------------
    # Abstract methods
    # ------------------------------

    def _get_config_spec_internal(self, prefix: str) -> list[ConfigSpecElement]:
        return []

    def _get_build_spec_internal(self, prefix: str) -> list[ConfigSpecElement]:
        return []

    def build(self, json_config: dict[str, list[str]], name_prefix: str = "" ) -> any:
        return BaseManagerChessModule(
            **self._build_submodules(json_config, name_prefix)
        )

append_test_module_builder("BaseChessModule", lambda: BaseManagerChessModuleBuilder())
