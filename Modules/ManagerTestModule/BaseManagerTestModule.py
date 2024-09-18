from abc import abstractmethod, ABC
from typing import Callable


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
    # Manager methods
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


ManagerTestModuleFactoryMethods: dict[str, Callable[[dict[str, str]], BaseManagerTestModule]] = {}


def append_test_module_factory_method(module: str, factory: Callable[[dict[str, str]], BaseManagerTestModule]) -> None:
    if module not in ManagerTestModuleFactoryMethods:
        ManagerTestModuleFactoryMethods[module] = factory
