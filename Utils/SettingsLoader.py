from .GlobalObj import GlobalObj
import os
from typing import Type
from pydantic import BaseModel


class SettingsLoader(metaclass=GlobalObj):
    _settings_class: Type[BaseModel]
    _settings: BaseModel

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, settings_class: Type[BaseModel], path: str):
        try:
            self._settings_class = settings_class

            if os.path.exists(path):
                self._settings = self.parse_settings(path)
                self.save_settings(path)
            else:
                self._settings = self._settings_class()
                self.save_settings(path)
        except Exception as e:
            raise Exception(f"Error occurred during loading settings: {e}")

    # ------------------------------
    # Class interaction
    # ------------------------------

    def parse_settings(self, path: str) -> BaseModel:
        with open(path, 'r') as f:
            content = f.read()
        return self._settings_class.model_validate_json(content)

    def save_settings(self, path) -> None:
        with open(path, 'w') as f:
            f.write(self._settings.model_dump_json(indent=2))

    def get_settings(self) -> BaseModel:
        return self._settings
