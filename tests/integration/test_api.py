import pytest
from fastapi.testclient import TestClient

from web_log_reports.main import create_app

LINE = '127.0.0.1 - - [12/Nov/2026:10:00:00 +0400] "GET / HTTP/1.1" 200 123'


@pytest.fixture
def client():
    with TestClient(create_app()) as instance:
        yield instance


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_ingest_and_analyze(client):
    response = client.post("/logs", json={"lines": [LINE, LINE.replace("200 123", "500 10")]})
    assert response.status_code == 201
    assert response.json() == {"accepted": 2}
    assert client.get("/stats").json() == {
        "requests": 2,
        "errors": 1,
        "error_rate_percent": 50.0,
        "bytes_sent": 133,
    }


def test_invalid_batch_is_atomic(client):
    response = client.post("/logs", json={"lines": [LINE, "broken"]})
    assert response.status_code == 400
    assert client.get("/stats").json()["requests"] == 0


@pytest.mark.parametrize("payload", [{"lines": []}, {"lines": [1]}, {}])
def test_request_validation(client, payload):
    assert client.post("/logs", json=payload).status_code == 422
