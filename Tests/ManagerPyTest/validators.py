from fastapi.testclient import TestClient
from httpx import Response


def validate_post_getter(client: TestClient, url: str) -> Response:
    response = client.post(url)
    assert response.status_code == 200
    return response


def validate_get_getter(client: TestClient, url: str) -> Response:
    response = client.get(url)
    assert response.status_code == 200
    return response


def validate_post_payload(client: TestClient, url: str, json: any) -> Response:
    response = client.post(url, json=json)
    assert response.status_code == 200
    return response
