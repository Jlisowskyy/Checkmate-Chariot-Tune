from Models.OrchestratorModels import ConfigSpecElement
from Modules.ModuleBuilder import ModuleBuilder
from Modules.NonBuildableModule import NonBuildableModule
from Modules.Submodules.TrainingMethodsModules.BaseTrainingMethodModule import BaseTrainingMethodModule, \
    append_test_module_builder


# ------------------------------
# Module Implementation
# ------------------------------


class SimpleTrainingModule(BaseTrainingMethodModule, NonBuildableModule):
    # ------------------------------
    # Class fields
    # ------------------------------

    MODULE_NAME = "SimpleTrainingModule"

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        super().__init__(SimpleTrainingModule.MODULE_NAME)

    # ------------------------------
    # Basic Methods
    # ------------------------------

    # ------------------------------
    # Abstract Methods
    # ------------------------------

    async def get_next_game_args(self) -> str:
        return ""

    async def save_game_result(self, result: str) -> None:
        return

    async def get_best_params(self) -> str:
        return ""

    async def rebuild_model(self) -> None:
        return

    async def harden_model(self) -> None:
        return

    async def configure_module(self, json_parsed: any, prefix="") -> None:
        return


# ------------------------------
# Builder Implementation
# ------------------------------

class SimpleTrainingMethodBuilder(ModuleBuilder):

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        super().__init__([], SimpleTrainingModule.MODULE_NAME)

    # ------------------------------
    # Abstract methods implementation
    # ------------------------------

    def _get_config_spec_internal(self, prefix: str) -> list[ConfigSpecElement]:
        return []

    def build(self, json_config: dict[str, list[str]], name_prefix: str = "") -> any:
        return SimpleTrainingModule()

    def _get_build_spec_internal(self, prefix: str) -> list[ConfigSpecElement]:
        return []


append_test_module_builder(SimpleTrainingModule.MODULE_NAME, lambda: SimpleTrainingMethodBuilder())
