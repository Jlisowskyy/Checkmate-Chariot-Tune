from pydantic import BaseModel
from .GlobalObj import GlobalObj
from .Logger import LogLevel
import os
import json
import dataclasses
import sys


class Settings(BaseModel):
    mgr_num_workers: int = 4
    logger_path: str = "./log.txt"
    log_std_out: bool = False
    log_level: int = LogLevel.MEDIUM_FREQ


class SettingsLoader(metaclass=GlobalObj):
    _settings: Settings

    def __init__(self, path: str):
        try:
            if os.path.exists(path):
                self._settings = SettingsLoader.parse_settings(path)
                self.save_settings(path)
            else:
                self._settings = Settings()
                self.save_settings(path)
        except Exception as e:
            raise Exception(f"Error occurred during loading settings: {e}")

    @staticmethod
    def parse_settings(path: str) -> Settings:
        with open(path, 'r') as f:
            content = f.read()
        return Settings.model_validate_json(content)

    def save_settings(self, path) -> None:
        with open(path, 'w') as f:
            f.write(self._settings.model_dump_json(indent=2))

    def get_settings(self) -> Settings:
        return self._settings
