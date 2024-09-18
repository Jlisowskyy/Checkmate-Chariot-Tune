from abc import ABC, abstractmethod
from typing import Callable


class BaseTrainingMethodModule(ABC):
    # ------------------------------
    # Class fields
    # ------------------------------

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


TrainingMethodModuleFactoryMethods: dict[str, Callable[[dict[str, str]], BaseTrainingMethodModule]] = {}


def append_test_module_factory_method(module: str,
                                      factory: Callable[[dict[str, str]], BaseTrainingMethodModule]) -> None:
    if module not in TrainingMethodModuleFactoryMethods:
        TrainingMethodModuleFactoryMethods[module] = factory
