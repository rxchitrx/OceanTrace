from __future__ import annotations

from typing import Dict, List


def build_reasons(components: Dict[str, float], gap_count: int) -> tuple[List[str], List[str]]:
    reasons: List[str] = []
    warnings: List[str] = []
    if components["origin_region_overlap"] >= 0.7:
        reasons.append("Track intersects the high-probability source region.")
    if components["release_time_match"] >= 0.5:
        reasons.append("Vessel was present during the estimated release window.")
    if components["drift_consistency"] >= 0.7:
        reasons.append("Forward drift remains consistent with the observed slick direction.")
    if components["ais_data_quality"] >= 0.75:
        reasons.append("AIS coverage is adequate for this candidate.")
    if gap_count > 0:
        warnings.append("AIS gap overlaps part of the release window.")
    return reasons, warnings
