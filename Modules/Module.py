from abc import abstractmethod, ABC

class Module(ABC):
    # ------------------------------
    # Class fields
    # ------------------------------

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        pass

    # ------------------------------
    # Abstract Methods
    # ------------------------------

    @abstractmethod
    async def build_module(self) -> None:
        pass

    @abstractmethod
    async def configure_module(self, json: str) -> None:
        pass

