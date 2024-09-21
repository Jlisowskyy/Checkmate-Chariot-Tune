from .BaseTrainingMethodModule import BaseTrainingMethodModule, append_test_module_builder
from ...ModuleBuilder import ModuleBuilder
from ...ModuleHelpers import ConfigSpecElement, build_config_spec_element, UiType, build_submodule_spec_element


# ------------------------------
# Module Implementation
# ------------------------------


class SimpleTrainingModule(BaseTrainingMethodModule):
    # ------------------------------
    # Class fields
    # ------------------------------

    MODULE_NAME = "SimpleTrainingModule"


    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        super().__init__()

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

    async def configure_module(self, json: str) -> None:
        return


# ------------------------------
# Builder Implementation
# ------------------------------

def build_config_spec_configured(
        name: str,
        description: str,
        ui_type: UiType,
        default_value: ConfigSpecElement.default_value_type,
        is_optional: bool
) -> ConfigSpecElement:
    return build_config_spec_element(
        BaseTrainingMethodModule.SUBMODULE_TYPE_NAME,
        SimpleTrainingModule.MODULE_NAME,
        name, description,
        ui_type, default_value,
        is_optional
    )

class SimpleTrainingModuleBuilder(ModuleBuilder):
    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        super().__init__([])

    # --------------------------------
    # Abstract Methods Implementation
    # --------------------------------

    def _get_build_spec_internal(self) -> list[ConfigSpecElement]:
        return []

    def build(self, json_config: dict[str, list[str]]) -> any:
        return SimpleTrainingModule()

    def _get_config_spec_internal(self) -> list[ConfigSpecElement]:
        return [
            build_config_spec_configured("Parameters", "Parameters for the training", UiType.StringStringDict, None,
                                         False),
        ]


append_test_module_builder(SimpleTrainingModule.MODULE_NAME, lambda: SimpleTrainingModuleBuilder())
