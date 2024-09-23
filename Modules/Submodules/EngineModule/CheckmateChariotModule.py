import os

from Models.OrchestratorModels import ConfigSpecElement, UiType
from Utils.Helpers import run_shell_command, validate_string
from .BaseEngineModule import BaseEngineModule, append_engine_builder
from ...ModuleBuilder import ModuleBuilder
from ...ModuleHelpers import build_config_spec_element, get_config_prefixed_name
from ...NonConfigurableModule import NonConfigurableModule


# ------------------------------
# Module Implementation
# ------------------------------


class CheckmateChariotModule(BaseEngineModule, NonConfigurableModule):
    # ------------------------------
    # Class fields
    # ------------------------------

    SUBDIR_NAME = "CheckmateChariot"
    ENGINE_NAME = "Checkmate-Chariot"
    MODULE_NAME = "CheckmateChariotModule"

    _build_commit: str | None

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        self._build_commit = None

        super().__init__(CheckmateChariotModule.MODULE_NAME)

    # ------------------------------
    # Abstract methods implementation
    # ------------------------------

    async def _configure_build_internal(self, json_parsed: dict[str, any], prefix: str) -> None:
        exec_path = os.path.join(self._build_dir, CheckmateChariotModule.ENGINE_NAME)
        exec_path_name = get_config_prefixed_name(prefix, self._module_name, "exec_path")

        if exec_path_name in json_parsed:
            raise Exception(f"Duplicate key: {exec_path_name} found in json config!")

        json_parsed[exec_path_name] = exec_path

        commit_name = get_config_prefixed_name(prefix, self._module_name, "commit")
        if commit_name in json_parsed:
            validate_string(json_parsed[commit_name])
            self._build_commit = json_parsed[commit_name]


    async def _build_internal(self) -> None:
        cwd = self._build_dir
        cpus = os.cpu_count()

        run_shell_command(f"git clone https://github.com/Jlisowskyy/Checkmate-Chariot {cwd}")

        if self._build_commit is not None:
            run_shell_command(f"git checkout {self._build_commit}", cwd)

        run_shell_command("cmake CMakeLists.txt -DCMAKE_BUILD_TYPE=Release", cwd)
        run_shell_command(f"make -j{cpus}", cwd)

    async def get_config(self) -> dict[str, str]:
        rv = {
            "protocol": "uci",
            "ponder": "true",
            "initStrings": "\"setoption name OwnBook value true\""
        }

        return rv

    async def get_param_command(self, param_name: str, param_value: str) -> str:
        return f"tune {param_name} {param_value}"


# ------------------------------
# Builder Implementation
# ------------------------------

class CheckmateChariotModuleBuilder(ModuleBuilder):
    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        super().__init__([], CheckmateChariotModule.MODULE_NAME)

    # ------------------------------
    # Abstract methods
    # ------------------------------

    def _get_config_spec_internal(self, prefix: str) -> list[ConfigSpecElement]:
        return []

    def _get_build_spec_internal(self, prefix: str) -> list[ConfigSpecElement]:
        return [
            build_config_spec_element(
                CheckmateChariotModule.MODULE_NAME,
                "commit",
                "Commit to base build on",
                UiType.String,
                None,
                True,
            )
        ]

    def build(self, json_config: dict[str, list[str]], name_prefix: str = "") -> any:
        return CheckmateChariotModule()


append_engine_builder(CheckmateChariotModule.ENGINE_NAME, CheckmateChariotModuleBuilder)
