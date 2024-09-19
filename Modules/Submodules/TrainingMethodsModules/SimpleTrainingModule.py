from .BaseTrainingMethodModule import BaseTrainingMethodModule, append_test_module_factory_method

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


def build_from_json(_: dict[str, str]) -> BaseTrainingMethodModule:
    return SimpleTrainingModule()


append_test_module_factory_method("SimpleTrainingModule", build_from_json)
