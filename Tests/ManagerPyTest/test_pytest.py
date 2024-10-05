from fastapi.testclient import TestClient

from Manager.manager_main import Manager

client = TestClient(Manager)

def test_pytest() -> None:
    response = client.get("/orchestrator/task/query/minimal")
    assert response.status_code == 200
    assert response.json() == {}