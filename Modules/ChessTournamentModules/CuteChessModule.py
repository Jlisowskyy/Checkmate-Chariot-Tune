import os.path

from Utils.Helpers import run_shell_command
from .BaseChessTournamentModule import BaseChessTournamentModule
from ..EngineModule.BaseEngineModule import EngineFactoryMethods, BaseEngineModule


class CuteChessModule(BaseChessTournamentModule):
    # ------------------------------
    # Class fields
    # ------------------------------

    SUBDIR_NAME: str = "CuteChess"
    TOURNAMENT_NAME: str = "CuteChess"
    EXEC_NAME: str = "cutechess-cli"
    CONFIG_FILE: str = "engines.json"

    _build_dir: str
    _config_file_path: str

    _tested_engine: str
    _start_arguments: str
    _engines: dict[str, BaseEngineModule]

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, build_dir: str) -> None:
        self._build_dir = str(os.path.join(build_dir, CuteChessModule.SUBDIR_NAME))
        exec_path = os.path.join(self._build_dir, CuteChessModule.EXEC_NAME)

        super().__init__(exec_path, CuteChessModule.TOURNAMENT_NAME)

        self._config_file_path = str(os.path.join(self._build_dir, CuteChessModule.CONFIG_FILE))
        self._tested_engine = ""
        self._start_arguments = ""
        self._engines = {}

    # ------------------------------
    # Abstract methods implementation
    # ------------------------------

    async def _build_internal(self) -> None:
        cwd = self._build_dir
        cpus = os.cpu_count()

        run_shell_command(f"git clone https://github.com/cutechess/cutechess {cwd}")
        run_shell_command("cmake .", cwd)
        run_shell_command(f"make cli -j{cpus}", cwd)


    async def _load_config_internal(self, config: any) -> None:
        self._tested_engine = config["tested_engine"]

        engines_config = {}
        for engine in config["engines"]:
            self._prepare_config_for_engine(engines_config, config, engine)


    async def play_game(self, args: dict[str, str]) -> str:
        pass

    # ------------------------------
    # Class interaction
    # ------------------------------

    def _prepare_config_for_engine(self, config_out: dict[str, any], config_in: any, engine_name: str) -> None:
        if engine_name not in EngineFactoryMethods:
            raise Exception(f"Provided engine: {engine_name} is not supported!")

        if engine_name in self._engines:
            return

        factory = EngineFactoryMethods[engine_name]
        self._engines[engine_name] = factory()