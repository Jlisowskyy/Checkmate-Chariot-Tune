from abc import abstractmethod, ABC

from Modules.Module import Module
from Modules.ModuleBuilder import ModuleBuilderFactory


class BaseManagerTestModule(ABC, Module):
    # ------------------------------
    # Class fields
    # ------------------------------

    MODULE_TYPE_NAME = "BaseManagerTestModule"

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, module_name: str) -> None:
        super().__init__(module_name)

    # ------------------------------
    # Abstract methods
    # ------------------------------

    @abstractmethod
    async def prepare_test_args(self) -> str:
        pass

    @abstractmethod
    async def sync_test_results(self, response: str) -> None:
        pass


ManagerTestModuleBuilders: dict[str, ModuleBuilderFactory] = {}


def append_test_module_builder(module: str, builder: ModuleBuilderFactory) -> None:
    if module not in ManagerTestModuleBuilders:
        ManagerTestModuleBuilders[module] = builder
