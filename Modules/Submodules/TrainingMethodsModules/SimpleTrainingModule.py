from .BaseTrainingMethodModule import BaseTrainingMethodModule

class SimpleTrainingModule(BaseTrainingMethodModule):
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

    async def get_next_game_args(self) -> str:
        pass

    async def save_game_result(self, result: str) -> None:
        pass

    async def get_best_params(self) -> str:
        pass

    async def rebuild_model(self) -> None:
        pass

    async def harden_model(self) -> None:
        pass
