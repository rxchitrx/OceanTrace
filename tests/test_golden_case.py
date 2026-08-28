from datetime import datetime

from services.api.case_runner import run_case


def test_golden_case_is_deterministic_and_complete():
    first = run_case("arabian_sea_demo", seed=26143)
    second = run_case("arabian_sea_demo", seed=26143)

    assert first == second
    assert first.analysis_mode == "full"
    assert first.vessels[0].vessel_id == "vessel_a"
    assert first.release_window is not None
    assert first.release_window.start == datetime.fromisoformat("2026-01-14T03:00:00+00:00")
    assert first.release_window.end == datetime.fromisoformat("2026-01-14T09:00:00+00:00")
    assert len(first.source_region.heatmap_points) == 180
    assert len(first.particles) == 10
    assert any("synthetic" in warning.lower() for warning in first.warnings)
