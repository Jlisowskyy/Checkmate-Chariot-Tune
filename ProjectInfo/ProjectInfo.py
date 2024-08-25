import json
import os
from enum import Enum

FILE_PATH = os.path.dirname(os.path.abspath(__file__))
VERSIONS_PATH = f"{FILE_PATH}/versions.json"
BUILD_DATA_PATH = f"{FILE_PATH}/build_data.json"


class ProjectInfo:
    # ------------------------------
    # Class fields
    # ------------------------------

    _version_table: list[str]
    _build_data: {str: str}

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self):
        with open(VERSIONS_PATH, "r") as f:
            obj = json.load(f)
        self._version_table = obj["versions"]

        with open(BUILD_DATA_PATH, "r") as f:
            obj = json.load(f)
        self._build_data = obj

    # ------------------------------
    # Class interaction
    # ------------------------------

    def get_current_version_desc(self) -> str:
        return self._version_table[-1]

    def get_current_version(self) -> int:
        return len(self._version_table) - 1

    def get_version_desc(self, version: int) -> str:
        return self._version_table[version] if version < len(self._version_table) else "Unknown"

    def get_version(self, version: str) -> int | None:
        for idx in range(0, len(self._version_table)):
            if self._version_table[idx] == version:
                return idx
        return None

    def is_version_known(self, version: int) -> bool:
        return 0 <= version < len(self._version_table)

    def display_known_versions(self) -> None:
        print("Known versions:")
        for version in self._version_table:
            print(version)

    def display_info(self, component: str) -> None:
        print(f"Checkmate-Chariot-Tune:\n"
              f"Author: Jakub Lisowski\n"
              f"Description: Distributed framework used to tune parameters for Checkmate-Chariot chess engine\n"
              f"Component: {component}\n"
              f"Version: {self.get_current_version_desc()}\n")

    def get_build_config(self, opt_name: str) -> str:
        if opt_name not in self._build_data:
            raise Exception(f"Build config with name: {opt_name} not found!")
        return self._build_data[opt_name]


ProjectInfoInstance = ProjectInfo()
