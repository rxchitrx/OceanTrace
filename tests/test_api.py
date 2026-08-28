from fastapi.testclient import TestClient

from services.api.main import app


client = TestClient(app)


def test_health_and_cases_endpoints():
    health = client.get("/api/health")
    cases = client.get("/api/cases")

    assert health.status_code == 200
    assert health.json()["version"] == "1.0.0"
    assert cases.status_code == 200
    assert {item["id"] for item in cases.json()} == {"arabian_sea_demo", "dartis_validation"}


def test_full_run_and_non_default_seed_result_retrieval():
    response = client.post(
        "/api/cases/arabian_sea_demo/run",
        json={"mode": "full", "seed": 123, "use_cached_result": False},
    )
    assert response.status_code == 200
    run_id = response.json()["run_id"]
    retrieved = client.get(f"/api/cases/arabian_sea_demo/results/{run_id}")

    assert run_id == "arabian_sea_demo-seed-123"
    assert retrieved.status_code == 200
    assert retrieved.json()["run_id"] == run_id


def test_detection_validation_case_does_not_invent_vessels():
    case = client.get("/api/cases/dartis_validation")
    response = client.post(
        "/api/cases/dartis_validation/run",
        json={"mode": "full", "seed": 26143, "use_cached_result": False},
    )

    assert case.status_code == 200
    assert case.json()["ais_tracks"] == {}
    assert response.status_code == 200
    assert response.json()["analysis_mode"] == "detection_only"
    assert response.json()["vessels"] == []
    assert response.json()["detector_evaluation"]["best_bbox_iou"] >= 0.90


def test_unknown_case_is_404():
    assert client.get("/api/cases/not-a-case").status_code == 404
