from fastapi.testclient import TestClient

from services.api.main import app


client = TestClient(app)


def test_cases_endpoint_lists_seeded_case():
    response = client.get("/api/cases")
    assert response.status_code == 200
    payload = response.json()
    assert any(item["id"] == "arabian_sea_demo" for item in payload)


def test_run_endpoint_returns_deterministic_top_candidate():
    response = client.post(
        "/api/cases/arabian_sea_demo/run",
        json={"mode": "full", "seed": 26143, "use_cached_result": True},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["vessels"][0]["vessel_id"] == "vessel_a"
