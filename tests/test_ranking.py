from datetime import datetime, timezone

from services.api.ranking.scorer import score_vessels


def test_ranking_prefers_nearer_track_with_release_match():
    tracks = {
        "vessel_a": [
            {
                "name": "A",
                "mmsi": "1",
                "vessel_type": "tanker",
                "timestamp": "2026-01-14T04:00:00Z",
                "latitude": "18.9",
                "longitude": "69.0",
                "course_over_ground": "45",
            }
        ],
        "vessel_b": [
            {
                "name": "B",
                "mmsi": "2",
                "vessel_type": "cargo",
                "timestamp": "2026-01-13T20:00:00Z",
                "latitude": "17.0",
                "longitude": "66.0",
                "course_over_ground": "220",
            }
        ],
    }
    ranked = score_vessels(
        tracks,
        {"vessel_a": [], "vessel_b": []},
        {"latitude": 18.91, "longitude": 69.01},
        {
            "start": datetime(2026, 1, 14, 3, 0, tzinfo=timezone.utc),
            "end": datetime(2026, 1, 14, 9, 0, tzinfo=timezone.utc),
        },
    )
    assert ranked[0]["vessel_id"] == "vessel_a"
