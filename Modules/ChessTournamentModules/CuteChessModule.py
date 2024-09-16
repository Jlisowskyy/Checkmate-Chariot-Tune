from .BaseChessTournamentModule import BaseChessTournamentModule


class CuteChessModule(BaseChessTournamentModule):
    # ------------------------------
    # Class fields
    # ------------------------------

    SUBDIR_NAME = "CuteChess"
    _exec_path: str | None

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        super().__init__()

        self._exec_path = None

    # ------------------------------
    # Class interaction
    # ------------------------------

    async def build_module(self, build_path: str) -> None:
        pass

    async def load_config(self, config: str) -> None:
        pass

    async def play_game(self, args: str) -> None:
        pass