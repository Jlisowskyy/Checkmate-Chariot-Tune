from abc import abstractmethod, ABC

from Modules.Module import Module
from Modules.ModuleBuilder import ModuleBuilderFactory
from Modules.Submodules.SubModulesRegistry import append_submodule_builders


class BaseTrainingMethodModule(Module, ABC):
    # ------------------------------
    # Class fields
    # ------------------------------

    SUBMODULE_TYPE = "TrainingMethod"

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, submodule_name: str) -> None:
        super().__init__(submodule_name)

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
append_submodule_builders(BaseTrainingMethodModule.SUBMODULE_TYPE, TrainingMethodModuleBuilders)

def append_test_module_builder(module: str, builder: ModuleBuilderFactory) -> None:
    if module not in TrainingMethodModuleBuilders:
        TrainingMethodModuleBuilders[module] = builder
