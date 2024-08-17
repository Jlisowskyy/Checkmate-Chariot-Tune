from fastapi import FastAPI
import os
import sys

from .Api import Orchestrator, Worker
from .ManagerLib import TestJobMgr, TestTaskMgr, WorkerMgr
from .ManagerLib import SettingsLoader

# load settings
SETTINGS_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/settings.json"
settings = SettingsLoader.SettingsLoader(SETTINGS_PATH).get_settings()

# init singleton managers:
WorkerMgr.WorkerMgr(settings.mgr_num_workers)
TestTaskMgr.TestTaskMgr(settings.mgr_num_workers)
TestJobMgr.TestJobMgr(settings.mgr_num_workers)

# init api:
Manager = FastAPI()
Manager.include_router(Orchestrator.router)
Manager.include_router(Worker.router)
