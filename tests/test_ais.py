from services.api.ais.cleaner import validate_rows
from services.api.ais.interpolator import detect_gaps


def test_gap_detection_flags_long_intervals():
    rows = validate_rows(
        [
            {
                "vessel_id": "a",
                "name": "A",
                "mmsi": "1",
                "timestamp": "2026-01-14T00:00:00Z",
                "latitude": "18.0",
                "longitude": "68.0",
                "speed_over_ground": "10",
                "course_over_ground": "25",
                "vessel_type": "tanker",
            },
            {
                "vessel_id": "a",
                "name": "A",
                "mmsi": "1",
                "timestamp": "2026-01-14T03:00:00Z",
                "latitude": "18.1",
                "longitude": "68.1",
                "speed_over_ground": "10",
                "course_over_ground": "27",
                "vessel_type": "tanker",
            },
        ]
    )
    gaps = detect_gaps(rows)
    assert gaps["a"][0]["duration_minutes"] == 180.0
