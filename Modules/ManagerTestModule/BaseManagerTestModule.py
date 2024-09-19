from abc import abstractmethod, ABC
from typing import Callable

from Utils.UiTypes import UiType


class BaseManagerTestModule(ABC):
    # ------------------------------
    # Class fields
    # ------------------------------

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        pass

    # ------------------------------
    # Abstract methods
    # ------------------------------

    @abstractmethod
    async def prepare_config_args(self) -> str:
        pass

    @abstractmethod
    async def prepare_test_args(self) -> str:
        pass

    @abstractmethod
    async def sync_test_results(self, response: str) -> None:
        pass

    @staticmethod
    @abstractmethod
    async def get_module_config_submodules() -> list[str]:
        pass

    # [Name, Description, Type]
    @staticmethod
    @abstractmethod
    async def get_config_fields(config: list[str]) -> list[[str, str, UiType]]:
        pass

ManagerTestModuleFactoryMethods: dict[str, Callable[[dict[str, str]], BaseManagerTestModule]] = {}


def append_test_module_factory_method(module: str, factory: Callable[[dict[str, str]], BaseManagerTestModule]) -> None:
    if module not in ManagerTestModuleFactoryMethods:
        ManagerTestModuleFactoryMethods[module] = factory
