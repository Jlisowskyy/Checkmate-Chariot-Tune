import json
import os
from enum import Enum

VERSIONS_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/versions.json"


class ProjectInfo:
    _version_table: list[str]

    def __init__(self):
        with open(VERSIONS_PATH, "r") as f:
            obj = json.load(f)
        self._version_table = obj["versions"]

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
