from abc import abstractmethod, ABC

class BaseChessTournamentModule(ABC):
    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        pass

    # ------------------------------
    # Worker methods
    # ------------------------------

    @abstractmethod
    async def build_module(self, build_path: str) -> None:
        pass

    @abstractmethod
    async def load_config(self, config: str) -> None:
        pass

    @abstractmethod
    async def play_game(self, args: str) -> None:
        pass


