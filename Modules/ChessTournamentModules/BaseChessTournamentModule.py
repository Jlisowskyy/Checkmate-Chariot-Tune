import json

from abc import abstractmethod, ABC

from Utils.Logger import Logger, LogLevel
from ..BuildableModule import BuildableModule


class BaseChessTournamentModule(BuildableModule, ABC):
    # ------------------------------
    # Class fields
    # ------------------------------

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, exec_path: str, tournament_name: str) -> None:
        super().__init__(exec_path, tournament_name)

    # ------------------------------
    # Basic Methods
    # ------------------------------

    async def load_config(self, config: str) -> None:
        Logger().log_info(f"Loading config for tournament: {self._obj_name}", LogLevel.LOW_FREQ)

        config_parsed = json.loads(config)

        if "engines" not in config_parsed:
            raise Exception("No engines found in config")

        if "tested_engine" not in config_parsed:
            raise Exception("No tested_engine found in config")

        if not isinstance(config_parsed["engines"], list) and all(
                isinstance(elem, str) for elem in config_parsed["engines"]):
            raise Exception("Engines were provided in invalid format")

        if not isinstance(config_parsed["tested_engine"], str):
            raise Exception("Tested_engine was provided in invalid format")

        if config_parsed["tested_engine"] not in config_parsed["engines"]:
            config_parsed["engines"].append(config_parsed["tested_engine"])


        try:
            await self._load_config_internal(config_parsed)
        except Exception as e:
            Logger(f"Failed to log config for {self._obj_name} by error: {e}", LogLevel.LOW_FREQ)
            raise e

        Logger().log_info(f"Config correctly loaded for tournament: {self._obj_name}", LogLevel.LOW_FREQ)

    # ------------------------------
    # Abstract Methods
    # ------------------------------

    @abstractmethod
    async def _load_config_internal(self, config: any) -> None:
        pass

    @abstractmethod
    async def play_game(self, args: dict[str, str]) -> str:
        pass
