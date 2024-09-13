import os
from threading import Thread, Lock
from time import sleep
from typing import Type, Callable

from pydantic import BaseModel

from .GlobalObj import GlobalObj
from .Logger import Logger, LogLevel


class SettingsLoader(metaclass=GlobalObj):
    _settings_class: Type[BaseModel]
    _settings: BaseModel
    _settings_path: str
    _last_edit_time: float
    _thread_should_work: bool
    _thread: Thread
    _lock: Lock
    _events: list[Callable[[BaseModel], None]]

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self, settings_class: Type[BaseModel], path: str):
        try:
            self._settings_class = settings_class
            self._settings_path = path

            if os.path.exists(path):
                self._settings = self.parse_settings(path)
                self.save_settings(path)
            else:
                self._settings = self._settings_class()
                self.save_settings(path)
        except Exception as e:
            raise Exception(f"Error occurred during loading initial settings: {e}")

        self._last_edit_time = os.path.getmtime(self._settings_path)
        self._lock = Lock()
        self._events = list[Callable[[BaseModel], None]]()

        self._thread_should_work = True
        self._thread = Thread(target=self._settings_loader_thread)
        self._thread.start()

    def destroy(self):
        self._thread_should_work = False
        self._thread.join()

        Logger().log_info("Settings Loader destroyed", LogLevel.LOW_FREQ)

    # ------------------------------
    # Class interaction
    # ------------------------------

    def parse_settings(self, path: str) -> BaseModel:
        with open(path, 'r') as f:
            content = f.read()
        return self._settings_class.model_validate_json(content)

    def parse_settings_log(self, path: str) -> BaseModel:
        model = self.parse_settings(path)
        Logger().log_info("New settings loaded", LogLevel.MEDIUM_FREQ)
        return model

    def save_settings(self, path) -> None:
        with open(path, 'w') as f:
            f.write(self._settings.model_dump_json(indent=2))

    def get_settings(self) -> BaseModel:
        with self._lock:
            return self._settings

    def add_event(self, event: Callable[[BaseModel], None]) -> None:
        with self._lock:
            self._events.append(event)

    # ------------------------------
    # Private methods
    # ------------------------------

    def _settings_loader_thread(self):
        while self._thread_should_work:
            sleep(0.1)
            self._periodic_settings_reload()

    def _run_events_unlocked(self):
        for event in self._events:
            event(self._settings)

    def _periodic_settings_reload(self):
        mod_time = os.path.getmtime(self._settings_path)

        if mod_time > self._last_edit_time:
            self._last_edit_time = mod_time
            with self._lock:
                try:
                    self._settings = self.parse_settings_log(self._settings_path)
                except Exception as e:
                    Logger().log_error(f"Failed to parse settings after init: {e}", LogLevel.LOW_FREQ)
                    self.save_settings(self._settings_path)
                self._run_events_unlocked()
