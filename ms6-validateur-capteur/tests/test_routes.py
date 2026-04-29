from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_validate_endpoint_returns_classification():
    response = client.post("/validate", json={"sensor": "c02", "value": 500.0})

    assert response.status_code == 200
    assert response.json()["level"] == "normal"


def test_validate_endpoint_rejects_unknown_sensor():
    response = client.post(
        "/validate",
        json={"sensor": "unknown", "value": 500.0},
    )

    assert response.status_code == 200
    assert response.json()["valid"] is False
    assert response.json()["level"] == "unknown"
    assert response.json()["message"] == "capteur non répértorié"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
