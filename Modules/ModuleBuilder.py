from abc import abstractmethod, ABC
from typing import TypeVar, Generic

from Modules.ModuleHelpers import ConfigSpecElement

T = TypeVar('T')


class ModuleBuilder(ABC, Generic[T]):
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
    def build(self, json_config: dict[str, str]) -> T:
        pass

    @abstractmethod
    def get_config_spec(self) -> list[ConfigSpecElement]:
        pass

    @abstractmethod
    def get_next_submodule_needed(self, json_config: dict[str, str]) -> ConfigSpecElement:
        pass
