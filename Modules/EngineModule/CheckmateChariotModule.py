import os

from .BaseEngineModule import BaseEngineModule, append_engine_factory_method
from Utils.Helpers import run_shell_command


class CheckmateChariotModule(BaseEngineModule):
    # ------------------------------
    # Class fields
    # ------------------------------

    SUBDIR_NAME = "CheckmateChariot"
    ENGINE_NAME = "Checkmate-Chariot"

    _build_dir: str
    _build_commit: str

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, build_path: str, commit: str) -> None:
        self._build_commit = commit
        self._build_dir = str(os.path.join(build_path, CheckmateChariotModule.SUBDIR_NAME))
        exec_path = str(os.path.join(build_path, CheckmateChariotModule.ENGINE_NAME))

        super().__init__(exec_path, CheckmateChariotModule.ENGINE_NAME)

    # ------------------------------
    # Abstract methods implementation
    # ------------------------------

    async def _build_engine_internal(self, build_path: str) -> None:
        cwd = self._build_dir
        cpus = os.cpu_count()

        run_shell_command("git clone https://github.com/Jlisowskyy/Checkmate-Chariot", cwd)

        if self._build_commit != "":
            run_shell_command(f"git checkout {self._build_commit}", cwd)

        run_shell_command("cmake CMakeLists.txt -DCMAKE_BUILD_TYPE=Release", cwd)
        run_shell_command(f"make -j{cpus}", cwd)

    async def _get_start_arguments(self) -> list[str]:
        return []

    async def _get_param_command(self, param_name: str, param_value: str) -> str:
        return f"tune {param_name} {param_value}"


def build_from_json(build_path: str, json: dict[str, str]) -> CheckmateChariotModule:
    commit = json["commit"] if "commit" in json else ""
    return CheckmateChariotModule(build_path, commit)

append_engine_factory_method(CheckmateChariotModule.ENGINE_NAME, build_from_json)