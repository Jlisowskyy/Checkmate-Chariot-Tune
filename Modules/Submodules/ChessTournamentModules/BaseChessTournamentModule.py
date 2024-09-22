from abc import abstractmethod, ABC

from Modules.BuildableModule import BuildableModule
from Utils.Logger import Logger, LogLevel
from ..SubModulesRegistry import append_submodule_builders
from ...ModuleBuilder import ModuleBuilderFactory, ModuleBuilder
from ...ModuleHelpers import ConfigSpecElement, build_config_spec_element, UiType, get_config_prefixed_name
from ...SubModuleMgr import SubModuleMgr


# ------------------------------
# Module Implementation
# ------------------------------


class BaseChessTournamentModule(BuildableModule, ABC):
    SUBMODULE_TYPE: str = "BaseChessTournamentModule"

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

    def __init__(self, obj_name: str) -> None:
        super().__init__(obj_name)

    # ------------------------------
    # Basic Methods
    # ------------------------------

    async def configure_module(self, json_parsed: any, prefix: str) -> None:
        Logger().log_info(f"Loading config for tournament: {self._obj_name}", LogLevel.MEDIUM_FREQ)

        try:
            config_parsed = self._validate_and_parse_config_json(json_parsed, prefix)
            self._extract_tournament_params(config_parsed)

            await self._load_config_internal(config_parsed)
        except Exception as e:
            Logger().log_info(f"Failed to get config for {self._obj_name} by error: {e}", LogLevel.MEDIUM_FREQ)
            raise e

        Logger().log_info(f"Config correctly loaded for tournament: {self._obj_name}", LogLevel.MEDIUM_FREQ)

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

    def _validate_and_parse_config_json(self, config: any, prefix: str) -> any:
        engines_name = get_config_prefixed_name(prefix, "engines")
        tested_engine_name = get_config_prefixed_name(prefix, "tested_engine")
        engine_startup_name = get_config_prefixed_name(prefix, "engine_startup_commands")

        if not isinstance(config, dict):
            raise Exception("Config must be a dictionary")

        if not all(isinstance(elem, str) for elem in config.keys()):
            raise Exception("Config must be a dictionary with string keys")

        if engines_name not in config:
            raise Exception("No engines found in config")

        if tested_engine_name not in config:
            raise Exception("No tested_engine found in config")

        if not isinstance(config[engines_name], list) or not all(
                isinstance(elem, str) for elem in config[engines_name]):
            raise Exception("Engines were provided in invalid format")

        if not isinstance(config[tested_engine_name], str):
            raise Exception("Tested_engine was provided in invalid format")

        if config[tested_engine_name] not in config[engines_name]:
            config[engines_name].append(config[tested_engine_name])

        if engine_startup_name in config:
            if ((not isinstance(config[engine_startup_name], dict) or
                 not all(isinstance(elem, str) for elem in config[engine_startup_name].keys()) or
                 not all(isinstance(elem, dict) for elem in config[engine_startup_name].values()) or
                 not all(all(isinstance(dict_elem, str) for dict_elem in elem) for elem in
                         config[engine_startup_name].values())) or
                    not all(all(isinstance(dict_elem, str) for dict_elem in elem) for elem in
                            config[engine_startup_name].keys())):
                raise Exception("Engine_startup_commands was provided in invalid format")

        return config

    @staticmethod
    def _parse_and_validate(config: dict[str, any], prefix: str, return_type: type, name: str, default_value: any,
                            min_value: any,
                            max_value: any) -> any:
        prefixed_name = get_config_prefixed_name(prefix, name)

        if not isinstance(default_value, return_type):
            raise Exception(f"Invalid type for default value of {prefixed_name} in config")

        if not isinstance(min_value, return_type):
            raise Exception(f"Invalid type for min value of {prefixed_name} in config")

        if not isinstance(max_value, return_type):
            raise Exception(f"Invalid type for max value of {prefixed_name} in config")

        if prefixed_name not in config:
            return default_value

        if not isinstance(config[prefixed_name], return_type):
            raise Exception(f"Invalid type for {prefixed_name} in config")

        if config[prefixed_name] < min_value or config[prefixed_name] > max_value:
            raise Exception(f"Invalid value for {prefixed_name} in config. Is not in range [{min_value}, {max_value}]")

        return config[prefixed_name]

    def _extract_tournament_params(self, config: dict[str, any], prefix: str) -> None:
        INFINITY = 2 ** 32

        self._hash_size_mb = self._parse_and_validate(config, prefix, int, "process_memory_limit", 128, 16, INFINITY)

        self._starting_total_time_s = self._parse_and_validate(config, prefix, int, "starting_total_time_s", 60, 1,
                                                               INFINITY)

        self._increment_time = self._parse_and_validate(config, prefix, float, "increment_time", 0.1, 0.0,
                                                        float(INFINITY))

        self._draw_move_silent_moves = self._parse_and_validate(config, prefix, int, "draw_move_silent_moves", 100, 10,
                                                                INFINITY)
        self._draw_move_count_within_points_range = self._parse_and_validate(config, prefix, int,
                                                                             "draw_move_count_within_points_range", 5,
                                                                             1, INFINITY)
        self._draw_zero_point_range = self._parse_and_validate(config, prefix, int, "draw_zero_point_range", 5, 1,
                                                               INFINITY)

        self._resign_diff_point_range = self._parse_and_validate(config, prefix, int, "resign_diff_point_range", 100, 1,
                                                                 INFINITY)
        self._resign_minimal_moves_above_range = self._parse_and_validate(config, prefix, int,
                                                                          "resign_minimal_moves_above_range", 10, 1,
                                                                          INFINITY)


# ------------------------------
# Builder Implementation
# ------------------------------

class BaseChessTournamentModuleBuilder(ModuleBuilder, ABC):
    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, submodules: list[ConfigSpecElement], submodule_type: str, submodule_name: str) -> None:
        super().__init__(submodules, submodule_type, submodule_name)

    # ------------------------------
    # Basic Methods
    # ------------------------------

    def _get_config_spec_internal(self, prefix: str) -> list[ConfigSpecElement]:
        config_spec: list[ConfigSpecElement] = [
            build_config_spec_element(
                f"{prefix}.{BaseChessTournamentModule.SUBMODULE_TYPE}",
                "starting_total_time_s",
                "Starting total time for each player in seconds",
                UiType.String,
                None,
                True
            ),
            build_config_spec_element(
                f"{prefix}.{BaseChessTournamentModule.SUBMODULE_TYPE}",
                "increment_time",
                "Increment time for each player in seconds",
                UiType.String,
                None,
                True
            ),
            build_config_spec_element(
                f"{prefix}.{BaseChessTournamentModule.SUBMODULE_TYPE}",
                "draw_move_silent_moves",
                "How many moves must be done to enter possible draw state",
                UiType.String,
                None,
                True
            ),
            build_config_spec_element(
                f"{prefix}.{BaseChessTournamentModule.SUBMODULE_TYPE}",
                "draw_move_count_within_points_range",
                "How many moves must be done inside abs(0 - draw_zero_point_range)"
                " points during draw state to trigger draw",
                UiType.String,
                None,
                True
            ),
            build_config_spec_element(
                f"{prefix}.{BaseChessTournamentModule.SUBMODULE_TYPE}",
                "draw_zero_point_range",
                "Range of points to trigger draw",
                UiType.String,
                None,
                True
            ),
            build_config_spec_element(
                f"{prefix}.{BaseChessTournamentModule.SUBMODULE_TYPE}",
                "resign_diff_point_range",
                "Range of points to trigger resign",
                UiType.String,
                None,
                True
            ),
            build_config_spec_element(
                f"{prefix}.{BaseChessTournamentModule.SUBMODULE_TYPE}",
                "resign_minimal_moves_above_range",
                "Minimal moves above resign_diff_point_range to trigger resign",
                UiType.String,
                None,
                True
            ),
            build_config_spec_element(
                f"{prefix}.{BaseChessTournamentModule.SUBMODULE_TYPE}",
                "engines",
                "List of engines to play against in tournament",
                UiType.StringList,
                SubModuleMgr().get_all_submodules_by_type("Engine"),
                False
            ),
            build_config_spec_element(
                f"{prefix}.{BaseChessTournamentModule.SUBMODULE_TYPE}",
                "tested_engine",
                "Main engine to test",
                UiType.String,
                None,
                False
            ),
            build_config_spec_element(
                f"{prefix}.{BaseChessTournamentModule.SUBMODULE_TYPE}",
                "engine_startup_commands",
                "Startup commands for engines",
                UiType.StringDictStringStringDict,
                None,
                True
            ),
        ]

        config_spec.extend(self._get_config_spec_internal_chess_tournament(prefix))

        return config_spec

    # ------------------------------
    # Abstract Methods
    # ------------------------------

    @abstractmethod
    def _get_config_spec_internal_chess_tournament(self, prefix: str) -> list[ConfigSpecElement]:
        pass


# ------------------------------
# Builders Map
# ------------------------------

TournamentFactoryMethods: dict[str, ModuleBuilderFactory] = {}
append_submodule_builders("ChessTournament", TournamentFactoryMethods)

def append_tournament_builder(tournament: str,
                              builder: ModuleBuilderFactory) -> None:
    if tournament not in TournamentFactoryMethods:
        TournamentFactoryMethods[tournament] = builder
