from .BaseManagerTestModule import BaseManagerTestModule, append_test_module_factory_method
from Utils.UiTypes import UiType
from ..Submodules.TrainingMethodsModules.BaseTrainingMethodModule import BaseTrainingMethodModule, TrainingMethodModuleFactoryMethods


class BaseManagerChessModule(BaseManagerTestModule):
    # ------------------------------
    # Class fields
    # ------------------------------

    _chess_training_module: BaseTrainingMethodModule

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, training_module: BaseTrainingMethodModule) -> None:
        super().__init__()
        self._chess_training_module = training_module

    # ------------------------------
    # Abstract methods
    # ------------------------------

    async def prepare_config_args(self) -> str:
        pass

    async def prepare_test_args(self) -> str:
        return await self._chess_training_module.get_next_game_args()

    async def sync_test_results(self, response: str) -> None:
        await self._chess_training_module.save_game_result(response)

    # [Name, Description, Type]
    @staticmethod
    async def get_config_fields(config: list[str]) -> list[[str, str, UiType]]:
        return [

        ]

def build_from_json(arg: dict[str, str]) -> BaseManagerChessModule:
    if "chess_training_module" not in arg:
        raise Exception("Missing chess_training_module in json")
    if arg["chess_training_module"] not in TrainingMethodModuleFactoryMethods:
        raise Exception("Invalid chess_training_module in json")
    return BaseManagerChessModule(TrainingMethodModuleFactoryMethods[arg["chess_training_module"]](arg))



append_test_module_factory_method("BaseChessModule", build_from_json)
