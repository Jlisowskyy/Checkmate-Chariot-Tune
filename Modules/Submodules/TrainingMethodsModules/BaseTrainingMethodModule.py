from abc import abstractmethod

from ..SubModulesRegistry import append_submodule_builders
from ...ModuleBuilder import ModuleBuilderFactory
from ...ModuleHelpers import ConfigSpecElement, UiType, build_submodule_spec_element
from ...NonBuildableModule import NonBuildableModule


class BaseTrainingMethodModule(NonBuildableModule):
    # ------------------------------
    # Class fields
    # ------------------------------

    SUBMODULE_TYPE_NAME = "TrainingMethod"

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        pass

    # ------------------------------
    # Basic Methods
    # ------------------------------

    # ------------------------------
    # Abstract Methods
    # ------------------------------

    @abstractmethod
    async def get_next_game_args(self) -> str:
        pass

    @abstractmethod
    async def save_game_result(self, result: str) -> None:
        pass

    @abstractmethod
    async def get_best_params(self) -> str:
        pass

    @abstractmethod
    async def rebuild_model(self) -> None:
        pass

    @abstractmethod
    async def harden_model(self) -> None:
        pass


TrainingMethodModuleBuilders: dict[str, ModuleBuilderFactory] = {}
append_submodule_builders(BaseTrainingMethodModule.SUBMODULE_TYPE_NAME, TrainingMethodModuleBuilders)

def append_test_module_builder(module: str, builder: ModuleBuilderFactory) -> None:
    if module not in TrainingMethodModuleBuilders:
        TrainingMethodModuleBuilders[module] = builder
