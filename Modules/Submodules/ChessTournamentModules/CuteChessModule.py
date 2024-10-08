import json
import os.path
from subprocess import Popen, PIPE

from Models.OrchestratorModels import ConfigSpecElement
from Modules.ModuleHelpers import get_config_prefixed_name
from Modules.Submodules.ChessTournamentModules.BaseChessTournamentModule import BaseChessTournamentModule, \
    append_tournament_builder, \
    BaseChessTournamentModuleBuilder
from Modules.Submodules.EngineModule.BaseEngineModule import BaseEngineModule
from Utils.Helpers import run_shell_command, dump_content_to_file_on_crash
from Utils.Logger import Logger, LogLevel


# ------------------------------
# Module Implementation
# ------------------------------


class CuteChessModule(BaseChessTournamentModule):
    # ------------------------------
    # Class fields
    # ------------------------------

    SUBDIR_NAME: str = "CuteChess"
    TOURNAMENT_NAME: str = "CuteChess"
    EXEC_NAME: str = "cutechess-cli"
    CONFIG_FILE: str = "engines.json"

    _config_file_path: str

    _tested_engine: str
    _start_arguments: str
    _engines: dict[str, BaseEngineModule]

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, tested_engines: list[BaseEngineModule]) -> None:

        super().__init__(tested_engines, CuteChessModule.TOURNAMENT_NAME)

        self._config_file_path = ""
        self._tested_engine = ""
        self._start_arguments = ""
        self._engines = {}

    # ------------------------------
    # Abstract methods implementation
    # ------------------------------

    async def _build_internal_chess_tournament(self) -> None:
        cwd = self._build_dir
        cpus = os.cpu_count()

        run_shell_command(f"git clone https://github.com/cutechess/cutechess {cwd}")
        run_shell_command("cmake .", cwd)
        run_shell_command(f"make cli -j{cpus}", cwd)

    async def _configure_build_chess_tournament(self, json_parsed: dict[str, any], prefix: str) -> None:
        self._config_file_path = os.path.join(self._build_dir, CuteChessModule.CONFIG_FILE)
        exec_path_name = get_config_prefixed_name(prefix, self._module_name, "exec_path")

        if exec_path_name in json_parsed:
            raise Exception(f"Exec path: {exec_path_name} is not allowed to be provided for CuteChessModule!")

        exec_path = os.path.join(self._build_dir, CuteChessModule.EXEC_NAME)
        json_parsed[exec_path_name] = exec_path

    async def _load_config_internal(self, config: dict[str, any], prefix: str) -> None:
        await self._prepare_config_for_engines(config, prefix)
        self._prepare_config_for_tournament()

    async def play_game(self, args: dict[str, str], enemy_engine: str, game_seed: int) -> str:
        Logger().log_info(f"Starting game (seed: {game_seed}) with args: {args}"
                          f" and enemy engine: {enemy_engine}", LogLevel.HIGH_FREQ)
        seed = game_seed % 2
        tested_engine = self._engines[self._tested_engine]

        param_str = ""
        for param_name, param_value in args.items():
            try:
                float(param_value)
            except Exception:
                raise Exception(f"Provided value: {param_value} for param: {param_name} is not a number!")

            param_str += f"initstr=\"{tested_engine.get_param_command(param_name, param_value)}\" "

        tested_engine_args = f"{self._tested_engine} {param_str}"
        enemy_engine_args = f"{enemy_engine}"

        [first_engine, second_engine] = [tested_engine_args, enemy_engine_args] if seed == 0 else [enemy_engine_args,
                                                                                                   tested_engine_args]

        full_start_args = f"-engine conf={first_engine} -engine conf={second_engine} {self._start_arguments}"
        result = self._start_cute_chess_and_extract_result(full_start_args, seed)
        Logger().log_info(f"Game (with seed: {game_seed}) finished with result: {result}", LogLevel.HIGH_FREQ)

        return result

    # ------------------------------
    # Private Methods
    # ------------------------------

    async def _prepare_config_for_engine(self, config_out: list[dict[str, str]], engine_name: str) -> None:

        engine = self._engines[engine_name]
        engine_config = await engine.get_config()

        filtered_config: dict[str, str] = {
            "protocol": engine_config["protocol"] if "protocol" in engine_config else "uci"}

        if "ponder" in engine_config:
            filtered_config["ponder"] = engine_config["ponder"]

        if "initStrings" in engine_config:
            filtered_config["initStrings"] = engine_config["initStrings"]

        filtered_config["command"] = engine.get_exec_path()
        filtered_config["name"] = engine_name

        config_out.append(filtered_config)

    async def _prepare_config_for_engines(self, config: dict[str, any], prefix: str) -> None:
        tested_engine_name = get_config_prefixed_name(prefix, self._module_name, "tested_engine")

        self._tested_engine = config[tested_engine_name]
        engines_config: list[dict[str, str]] = []
        for engine in self._engines.keys():
            await self._prepare_config_for_engine(
                engines_config,
                engine
            )

        with open(self._config_file_path, 'w') as json_file:
            json.dump(engines_config, json_file, indent=2)

    def _prepare_config_for_tournament(self) -> None:
        args = "--each "

        minutes = self._starting_total_time_s // 60
        seconds = self._starting_total_time_s % 60
        tc_time = f"{minutes}:{seconds}"

        args += f"tc=40/{tc_time}+{self._increment_time} "
        args += f"option.Hash={self._hash_size_mb}"
        args += (f"-draw movenumber={self._draw_move_silent_moves} "
                 f"movecount={self._draw_move_count_within_points_range} score={self._draw_zero_point_range} ")
        args += f"-resign movecount={self._resign_minimal_moves_above_range} score={self._resign_diff_point_range} "

        self._start_arguments = args

    def _start_cute_chess_and_extract_result(self, start_args: str, seed: int) -> str:
        result_map = {0: "W", 1: "L", 2: "D"}

        command = f"{self.get_exec_path()} {start_args}"
        process = Popen(command, shell=True, stdout=PIPE)
        output = process.communicate()[0].decode("utf-8")

        if process.returncode != 0:
            dump_content_to_file_on_crash(output)
            raise Exception(f"Failed to run cutechess-cli with command: {command}")

        for line in output.splitlines():
            if line.startswith('Finished game'):
                if ": 1-0" in line:
                    return result_map[seed % 2]
                elif ": 0-1" in line:
                    return result_map[(seed % 2) ^ 1]
                elif ": 1/2-1/2" in line:
                    return result_map[2]
                else:
                    dump_content_to_file_on_crash(output)
                    raise Exception(f"Failed to parse finished game from line: {line}")

        dump_content_to_file_on_crash(output)
        raise Exception(f"Failed to find finished game line in output from game played with command: {command}")


# ------------------------------
# Builder Implementation
# ------------------------------

class CuteChessModuleBuilder(BaseChessTournamentModuleBuilder):
    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        super().__init__([], CuteChessModule.TOURNAMENT_NAME)

    # ------------------------------
    # Abstract methods implementation
    # ------------------------------

    def _get_config_spec_internal_chess_tournament(self, prefix: str) -> list[ConfigSpecElement]:
        return []

    def build(self, json_config: dict[str, list[str]], name_prefix: str = "") -> any:
        return CuteChessModule(
            **self._build_submodules(json_config, name_prefix)
        )

    def _get_build_spec_internal(self, prefix: str) -> list[ConfigSpecElement]:
        return []


append_tournament_builder(CuteChessModule.TOURNAMENT_NAME, CuteChessModuleBuilder)
