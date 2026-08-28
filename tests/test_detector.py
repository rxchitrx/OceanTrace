from services.api.detection.baseline_detector import detect_candidate_slick


def test_detector_returns_score_and_polygon():
    payload = {
        "type": "Polygon",
        "coordinates": [[[0.0, 0.0], [0.2, 0.0], [0.2, 0.1], [0.0, 0.1], [0.0, 0.0]]],
    }
    result = detect_candidate_slick(payload)
    assert result["score"] > 0.0
    assert result["polygon"]["type"] == "Polygon"
