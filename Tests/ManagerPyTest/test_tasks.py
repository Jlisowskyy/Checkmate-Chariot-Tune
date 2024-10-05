from fastapi.testclient import TestClient

from Manager.manager_main import Manager

client = TestClient(Manager)

def test_create_task() -> None:
    assert 1 == 1