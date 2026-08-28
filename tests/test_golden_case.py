from services.api.case_runner import run_case


def test_golden_case_is_deterministic_and_ranks_expected_vessel():
    result = run_case("arabian_sea_demo")
    assert result.vessels[0].vessel_id == "vessel_a"
    assert result.release_window.confidence_band == "moderate"
    assert "Controlled demonstration scenario." in result.warnings
