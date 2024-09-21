from .BaseManagerTestModule import BaseManagerTestModule, append_test_module_builder
from ..ModuleBuilder import ModuleBuilder
from ..ModuleHelpers import ConfigSpecElement, build_submodule_spec_element, UiType
from ..SubModuleMgr import SubModuleMgr
from ..Submodules.TrainingMethodsModules.BaseTrainingMethodModule import BaseTrainingMethodModule


# ------------------------------
# Module Implementation
# ------------------------------

class BaseManagerChessModule(BaseManagerTestModule):
    # ------------------------------
    # Class fields
    # ------------------------------

    MODULE_NAME = "BaseManagerChessModule"
    _chess_training_module: BaseTrainingMethodModule

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, training_module: BaseTrainingMethodModule) -> None:
        super().__init__()
        self._chess_training_module = training_module

    # ------------------------------
    # Abstract methods
    # ------------------------------

    async def prepare_test_args(self) -> str:
        return await self._chess_training_module.get_next_game_args()

    async def sync_test_results(self, response: str) -> None:
        await self._chess_training_module.save_game_result(response)

    async def build_module(self, json: str) -> None:
        await self._chess_training_module.build_module(json)

    async def configure_module(self, json: str) -> None:
        await self._chess_training_module.configure_module(json)


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
                BaseTrainingMethodModule.SUBMODULE_TYPE_NAME,
                "training_module",
                "Chess training method used to find best parameters for algorithms",
                UiType.String,
                SubModuleMgr().get_all_submodules_by_type(BaseTrainingMethodModule.SUBMODULE_TYPE_NAME),
            )
            ],
            BaseManagerChessModule.MODULE_TYPE_NAME,
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
