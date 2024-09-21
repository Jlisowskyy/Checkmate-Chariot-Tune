from .BaseManagerTestModule import BaseManagerTestModule, append_test_module_builder
from ..ModuleBuilder import ModuleBuilder
from ..ModuleHelpers import ConfigSpecElement, build_submodule_spec_element, UiType
from ..SubModuleMgr import SubModuleMgr
from ..Submodules.TrainingMethodsModules.BaseTrainingMethodModule import BaseTrainingMethodModule
from ..Submodules.TrainingMethodsModules.SimpleTrainingModule import build_submodule_spec_configured


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
        super().__init__([
            # build_submodule_spec_configured(
            #     BaseManagerTestModule.MODULE_TYPE_NAME,
            #     BaseManagerTestModule.MODULE_NAME,
            #     "chess_training_module",
            #     "Chess Training Module",
            #     UiType.String,
            #     SubModuleMgr().get_all_submodules_by_type(BaseTrainingMethodModule.MODULE_TYPE_NAME),
            # )
        ])

    # ------------------------------
    # Abstract methods
    # ------------------------------

    def _get_build_spec_internal(self) -> list[ConfigSpecElement]:
        pass

    def build(self, json_config: dict[str, list[str]]) -> any:
        pass

    def _get_config_spec_internal(self) -> list[ConfigSpecElement]:
        pass


append_test_module_builder("BaseChessModule", lambda: BaseManagerChessModuleBuilder())
