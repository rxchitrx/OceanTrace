from datetime import datetime, timezone

from services.api.drift.source_search import search_source_region


def test_source_search_returns_heatmap_and_release_window():
    result = search_source_region(
        datetime(2026, 1, 14, 12, 0, tzinfo=timezone.utc),
        (19.0, 69.0),
        {"u": 0.012, "v": 0.006},
        {"u": -0.004, "v": 0.002},
    )
    assert len(result["source_region"]["heatmap_points"]) == 15
    assert result["release_window"]["confidence_band"] == "moderate"
