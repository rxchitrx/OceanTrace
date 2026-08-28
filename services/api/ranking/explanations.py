from __future__ import annotations

from typing import Dict, List


def build_reasons(
    components: Dict[str, float],
    overlapping_gap_count: int,
) -> tuple[List[str], List[str]]:
    reasons: List[str] = []
    warnings: List[str] = []
    if components["origin_region_overlap"] >= 0.65:
        reasons.append("Track intersects the strongest source hypotheses.")
    if components["release_time_match"] >= 0.65:
        reasons.append("Vessel positions cover the estimated release window.")
    if components["drift_consistency"] >= 0.65:
        reasons.append("Forward drift from the vessel track reproduces the observed slick location.")
    if components["trajectory_heading"] >= 0.7:
        reasons.append("Reported course is consistent with the reconstructed trajectory.")
    if components["ais_data_quality"] >= 0.8:
        reasons.append("AIS coverage is adequate for this candidate.")
    if overlapping_gap_count > 0:
        warnings.append(
            f"{overlapping_gap_count} AIS gap(s) overlap the estimated release window."
        )
    if components["release_time_match"] < 0.35:
        warnings.append("AIS coverage is weak during the estimated release window.")
    return reasons, warnings
