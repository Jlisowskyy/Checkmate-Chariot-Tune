from abc import abstractmethod, ABC

from Modules.BuildableModule import BuildableModule
from Utils.Logger import Logger, LogLevel
from ..EngineModule.BaseEngineModule import BaseEngineModule
from ..SubModulesRegistry import append_submodule_builders
from ...ModuleBuilder import ModuleBuilderFactory, ModuleBuilder
from ...ModuleHelpers import ConfigSpecElement, build_config_spec_element, UiType, get_config_prefixed_name, \
    build_submodule_spec_element
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

    _engines: dict[str, BaseEngineModule]

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, tested_engines: list[BaseEngineModule], module_name: str) -> None:
        super().__init__(module_name)

        self._engines = {}

        if len(tested_engines) == 0:
            raise Exception("No engines provided for testing!")

        for engine in tested_engines:
            if engine.get_module_name() in self._engines:
                raise Exception(f"Engine: {engine.get_module_name()} already exists in engines!")

            self._engines[engine.get_module_name()] = engine

    # ------------------------------
    # Basic Methods
    # ------------------------------

    async def configure_module(self, json_parsed: any, prefix: str) -> None:
        Logger().log_info(f"Loading config for tournament: {self._obj_name}", LogLevel.MEDIUM_FREQ)

        try:
            config_parsed = self._validate_and_parse_config_json(json_parsed, prefix)
            self._extract_tournament_params(config_parsed, prefix)

            await self._load_config_internal(config_parsed, prefix)
        except Exception as e:
            Logger().log_info(f"Failed to get config for {self._obj_name} by error: {e}", LogLevel.MEDIUM_FREQ)
            raise e

        Logger().log_info(f"Config correctly loaded for tournament: {self._obj_name}", LogLevel.MEDIUM_FREQ)

    async def _build_internal(self) -> None:
        await self._build_internal_chess_tournament()

        for engine in self._engines.values():
            await engine.build_module()

    async def _configure_build_internal(self, json: dict[str, any], prefix: str) -> None:
        for engine in self._engines.values():
            await engine.configure_build(json, prefix)

        await self._configure_build_chess_tournament(json, prefix)

    # ------------------------------
    # Abstract Methods
    # ------------------------------

    @abstractmethod
    async def _build_internal_chess_tournament(self) -> None:
        pass

    @abstractmethod
    async def _configure_build_chess_tournament(self, json: dict[str, any], prefix: str) -> None:
        pass

    @abstractmethod
    async def _load_config_internal(self, config: any, prefix: str) -> None:
        pass

    @abstractmethod
    async def play_game(self, args: dict[str, str], enemy_engine: str, game_seed: int) -> str:
        pass

    # ------------------------------
    # Private methods
    # ------------------------------

    def _validate_and_parse_config_json(self, config: any, prefix: str) -> any:
        tested_engine_name = get_config_prefixed_name(prefix, self._module_name, "tested_engine")

        if not isinstance(config, dict):
            raise Exception("Config must be a dictionary")

        if not all(isinstance(elem, str) for elem in config.keys()):
            raise Exception("Config must be a dictionary with string keys")

        if not isinstance(config[tested_engine_name], str):
            raise Exception("Tested_engine was provided in invalid format")

        tested_engine_module_name = config[tested_engine_name]
        if tested_engine_module_name not in self._engines:
            raise Exception(f"Tested engine: {tested_engine_module_name} is not in engines list")

        return config

    def _parse_and_validate(self, config: dict[str, any], prefix: str, return_type: type, name: str, default_value: any,
                            min_value: any,
                            max_value: any) -> any:
        prefixed_name = get_config_prefixed_name(prefix, self._module_name, name)

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
    # Class fields
    # ------------------------------

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, submodules: list[ConfigSpecElement], submodule_name: str) -> None:
        super().__init__(
            submodules + [
                build_submodule_spec_element(
                    BaseEngineModule.SUBMODULE_TYPE_NAME,
                    "tested_engines",
                    "List of engines participating in testing",
                    UiType.StringList,
                    SubModuleMgr().get_all_submodules_by_type(BaseEngineModule.SUBMODULE_TYPE_NAME)
                )
            ],
            submodule_name
        )

    # ------------------------------
    # Basic Methods
    # ------------------------------

    def _get_config_spec_internal(self, prefix: str) -> list[ConfigSpecElement]:
        config_spec: list[ConfigSpecElement] = [
            build_config_spec_element(
                f"{prefix}.{self._submodule_name}",
                "starting_total_time_s",
                "Starting total time for each player in seconds",
                UiType.String,
                None,
                True
            ),
            build_config_spec_element(
                f"{prefix}.{self._submodule_name}",
                "increment_time",
                "Increment time for each player in seconds",
                UiType.String,
                None,
                True
            ),
            build_config_spec_element(
                f"{prefix}.{self._submodule_name}",
                "draw_move_silent_moves",
                "How many moves must be done to enter possible draw state",
                UiType.String,
                None,
                True
            ),
            build_config_spec_element(
                f"{prefix}.{self._submodule_name}",
                "draw_move_count_within_points_range",
                "How many moves must be done inside abs(0 - draw_zero_point_range)"
                " points during draw state to trigger draw",
                UiType.String,
                None,
                True
            ),
            build_config_spec_element(
                f"{prefix}.{self._submodule_name}",
                "draw_zero_point_range",
                "Range of points to trigger draw",
                UiType.String,
                None,
                True
            ),
            build_config_spec_element(
                f"{prefix}.{self._submodule_name}",
                "resign_diff_point_range",
                "Range of points to trigger resign",
                UiType.String,
                None,
                True
            ),
            build_config_spec_element(
                f"{prefix}.{self._submodule_name}",
                "resign_minimal_moves_above_range",
                "Minimal moves above resign_diff_point_range to trigger resign",
                UiType.String,
                None,
                True
            ),
            build_config_spec_element(
                f"{prefix}.{self._submodule_name}",
                "engines",
                "List of engines to play against in tournament",
                UiType.StringList,
                SubModuleMgr().get_all_submodules_by_type("Engine"),
                False
            ),
            build_config_spec_element(
                f"{prefix}.{self._submodule_name}",
                "tested_engine",
                "Main engine to test",
                UiType.String,
                None,
                False
            ),
            build_config_spec_element(
                f"{prefix}.{self._submodule_name}",
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
