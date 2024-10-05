from fastapi.testclient import TestClient

from Manager.manager_main import Manager

client = TestClient(Manager)