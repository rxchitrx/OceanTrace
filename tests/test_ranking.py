from services.api.case_runner import run_case


def test_golden_case_ranks_source_track_above_nearest_observation_track():
    result = run_case("arabian_sea_demo", seed=26143)

    assert result.vessels[0].vessel_id == "vessel_a"
    assert result.vessels[0].components["origin_region_overlap"] > 0.7
    assert result.vessels[0].components["drift_consistency"] > 0.7
    assert result.vessels[1].vessel_id == "vessel_b"
    assert result.vessels[0].lead_score > result.vessels[1].lead_score + 20


def test_long_ais_gap_is_reported_only_when_window_overlaps():
    result = run_case("arabian_sea_demo", seed=26143)
    vessel_c = next(vessel for vessel in result.vessels if vessel.vessel_id == "vessel_c")

    assert any("AIS gap" in warning for warning in vessel_c.warnings)
