from datetime import datetime, timezone

from services.api.ais.features import distance_km
from services.api.drift.particle_model import advect_point
from services.api.drift.source_search import search_source_region


SPILL = {
    "type": "Polygon",
    "coordinates": [[[68.95, 18.92], [69.08, 18.95], [69.11, 19.03], [68.99, 19.06], [68.95, 18.92]]],
}
WIND = {"u": 4.8, "v": 2.1, "units": "m/s", "uncertainty": 0.8}
CURRENT = {"u": 0.18, "v": 0.07, "units": "m/s", "uncertainty": 0.04}


def test_particle_advection_uses_meters_per_second():
    latitude, longitude = advect_point(19.0, 69.0, 3600.0, 1.0, 0.0)
    travelled = distance_km(19.0, 69.0, latitude, longitude)

    assert 3.55 <= travelled <= 3.65


def test_source_search_returns_reproducible_ensemble():
    observation = datetime(2026, 1, 14, 12, 0, tzinfo=timezone.utc)
    first = search_source_region(observation, SPILL, WIND, CURRENT, seed=55)
    second = search_source_region(observation, SPILL, WIND, CURRENT, seed=55)

    assert first == second
    assert len(first["source_region"]["heatmap_points"]) == 180
    assert len(first["particles"]) == 10
    assert first["diagnostics"]["ensemble_members"] == 180
    assert first["release_window"]["start"] < first["release_window"]["end"]


def test_source_search_changes_with_seed():
    observation = datetime(2026, 1, 14, 12, 0, tzinfo=timezone.utc)
    first = search_source_region(observation, SPILL, WIND, CURRENT, seed=1)
    second = search_source_region(observation, SPILL, WIND, CURRENT, seed=2)

    assert first["source_region"]["heatmap_points"] != second["source_region"]["heatmap_points"]
