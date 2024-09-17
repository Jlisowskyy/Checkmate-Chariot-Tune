import json

from abc import abstractmethod, ABC
from typing import Callable

from Utils.Logger import Logger, LogLevel
from ..BuildableModule import BuildableModule


class BaseChessTournamentModule(BuildableModule, ABC):
    # ------------------------------
    # Class fields
    # ------------------------------

    _hash_size_mb: int
    _starting_total_time_s: int
    _increment_time: float
    _draw_move_silent_moves: int
    _draw_move_count_within_points_range: int
    _draw_zero_point_range: int
    _resign_diff_point_range: int
    _resign_minimal_moves_above_range: int

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

        config_parsed = self._validate_and_parse_config_json(config)
        self._extract_tournament_params(config_parsed)

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
    async def play_game(self, args: dict[str, str], enemy_engine: str, game_seed: int) -> str:
        pass

    # ------------------------------
    # Private methods
    # ------------------------------

    def _validate_and_parse_config_json(self, config: str) -> any:
        config_parsed = json.loads(config)

        if not isinstance(config_parsed, dict):
            raise Exception("Config must be a dictionary")

        if not all(isinstance(elem, str) for elem in config_parsed.keys()):
            raise Exception("Config must be a dictionary with string keys")

        if "engines" not in config_parsed:
            raise Exception("No engines found in config")

        if "tested_engine" not in config_parsed:
            raise Exception("No tested_engine found in config")

        if not isinstance(config_parsed["engines"], list) or not all(
                isinstance(elem, str) for elem in config_parsed["engines"]):
            raise Exception("Engines were provided in invalid format")

        if not isinstance(config_parsed["tested_engine"], str):
            raise Exception("Tested_engine was provided in invalid format")

        if config_parsed["tested_engine"] not in config_parsed["engines"]:
            config_parsed["engines"].append(config_parsed["tested_engine"])

        if "engine_startup_commands" in config_parsed:
            if ((not isinstance(config_parsed["engine_startup_commands"], dict) or
                 not all(isinstance(elem, str) for elem in config_parsed["engine_startup_commands"].keys()) or
                 not all(isinstance(elem, dict) for elem in config_parsed["engine_startup_commands"].values()) or
                 not all(all(isinstance(dict_elem, str) for dict_elem in elem) for elem in
                         config_parsed["engine_startup_commands"].values())) or
                    not all(all(isinstance(dict_elem, str) for dict_elem in elem) for elem in
                            config_parsed["engine_startup_commands"].keys())):
                raise Exception("Engine_startup_commands was provided in invalid format")

        return config_parsed

    @staticmethod
    def _parse_and_validate(config: dict[str, any], return_type: type, name: str, default_value: any, min_value: any,
                            max_value: any) -> any:
        if not isinstance(default_value, return_type):
            raise Exception(f"Invalid type for default value of {name} in config")

        if not isinstance(min_value, return_type):
            raise Exception(f"Invalid type for min value of {name} in config")

        if not isinstance(max_value, return_type):
            raise Exception(f"Invalid type for max value of {name} in config")

        if name not in config:
            return default_value

        if not isinstance(config[name], return_type):
            raise Exception(f"Invalid type for {name} in config")

        if config[name] < min_value or config[name] > max_value:
            raise Exception(f"Invalid value for {name} in config. Is not in range [{min_value}, {max_value}]")

        return config[name]

    def _extract_tournament_params(self, config: dict[str, any]) -> None:
        INFINITY = 2 ** 32

        self._hash_size_mb = self._parse_and_validate(config, int, "hash_size_mb", 128, 16, INFINITY)

        self._starting_total_time_s = self._parse_and_validate(config, int, "starting_total_time_s", 60, 1, INFINITY)

        self._increment_time = self._parse_and_validate(config, float, "increment_time", 0.1, 0.0, float(INFINITY))

        self._draw_move_silent_moves = self._parse_and_validate(config, int, "draw_move_silent_moves", 100, 10,
                                                                INFINITY)
        self._draw_move_count_within_points_range = self._parse_and_validate(config, int,
                                                                             "draw_move_count_within_points_range", 5,
                                                                             1, INFINITY)
        self._draw_zero_point_range = self._parse_and_validate(config, int, "draw_zero_point_range", 5, 1, INFINITY)

        self._resign_diff_point_range = self._parse_and_validate(config, int, "resign_diff_point_range", 100, 1,
                                                                 INFINITY)
        self._resign_minimal_moves_above_range = self._parse_and_validate(config, int,
                                                                          "resign_minimal_moves_above_range", 10, 1,
                                                                          INFINITY)


TournamentFactoryMethods: dict[str, Callable[[str, dict[str, str]], BaseChessTournamentModule]] = {}


def append_tournament_factory_method(tournament: str,
                                     factory: Callable[[str, dict[str, str]], BaseChessTournamentModule]) -> None:
    if tournament not in TournamentFactoryMethods:
        TournamentFactoryMethods[tournament] = factory
