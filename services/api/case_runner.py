from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from services.api.ais.cleaner import load_ais_rows, validate_rows
from services.api.ais.features import grouped_tracks
from services.api.ais.interpolator import detect_gaps, interpolate_short_gaps
from services.api.detection.baseline_detector import detect_candidate_slick
from services.api.drift.forcing import load_forcing
from services.api.drift.source_search import search_source_region
from services.api.ranking.scorer import score_vessels
from services.api.schemas import AnalysisResult, CaseManifest, CasePayload, CaseSummary


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "cases"
GENERATED_DIR = ROOT / "generated"


def _case_dir(case_id: str) -> Path:
    return DATA_DIR / case_id


def list_cases() -> list[Dict[str, Any]]:
    cases: list[Dict[str, Any]] = []
    for case_dir in sorted(DATA_DIR.iterdir()):
        manifest_path = case_dir / "case.json"
        if manifest_path.exists():
            manifest = CaseManifest.model_validate_json(
                manifest_path.read_text(encoding="utf-8")
            )
            cases.append(
                CaseSummary(
                    id=manifest.id,
                    region=manifest.region,
                    scenario_type=manifest.scenario_type,
                    observation_time=manifest.observation_time,
                ).model_dump(mode="json")
            )
    return cases


def load_case(case_id: str) -> CaseManifest:
    case_path = _case_dir(case_id) / "case.json"
    return CaseManifest.model_validate_json(case_path.read_text(encoding="utf-8"))


def case_payload(case_id: str) -> Dict[str, Any]:
    manifest = load_case(case_id)
    case_dir = _case_dir(case_id)
    spill = json.loads((case_dir / manifest.spill_polygon).read_text(encoding="utf-8"))
    expected = json.loads((case_dir / "expected_result.json").read_text(encoding="utf-8"))
    
    ais_rows = validate_rows(load_ais_rows(case_dir / manifest.ais_path))
    tracks = grouped_tracks(ais_rows)
    interpolated = interpolate_short_gaps(tracks)
    
    payload = CasePayload(
        manifest=manifest,
        spill_polygon=spill,
        expected_result=expected,
        available_layers=[
            "sar_image",
            "spill_polygon",
            "source_heatmap",
            "particle_paths",
            "ais_tracks",
        ],
        ais_tracks=interpolated,
    )
    return payload.model_dump(mode="json")


def _result_path(case_id: str, seed: int) -> Path:
    return GENERATED_DIR / f"{case_id}-seed-{seed}.json"


def load_cached_result(case_id: str, seed: int = 26143) -> AnalysisResult | None:
    path = _result_path(case_id, seed)
    if not path.exists():
        return None
    return AnalysisResult.model_validate_json(path.read_text(encoding="utf-8"))


def run_case(case_id: str, seed: int = 26143) -> AnalysisResult:
    manifest = load_case(case_id)
    case_dir = _case_dir(case_id)
    spill = json.loads((case_dir / manifest.spill_polygon).read_text(encoding="utf-8"))
    wind = load_forcing(case_dir / manifest.forcing.wind_path)
    current = load_forcing(case_dir / manifest.forcing.current_path)
    ais_rows = validate_rows(load_ais_rows(case_dir / manifest.ais_path))
    tracks = grouped_tracks(ais_rows)
    interpolated = interpolate_short_gaps(tracks)
    gaps = detect_gaps(ais_rows)
    detector = detect_candidate_slick(spill["geometry"])
    coordinates = spill["geometry"]["coordinates"][0]
    centroid_lat = sum(point[1] for point in coordinates[:-1]) / (len(coordinates) - 1)
    centroid_lon = sum(point[0] for point in coordinates[:-1]) / (len(coordinates) - 1)
    drift = search_source_region(manifest.observation_time, (centroid_lat, centroid_lon), wind, current)
    vessels = score_vessels(interpolated, gaps, drift["source_region"]["centroid"], drift["release_window"])
    warnings = [
        "Controlled demonstration scenario.",
        "AIS tracks are simulated.",
        "Output is an investigative lead, not legal attribution.",
    ]
    result = AnalysisResult.model_validate(
        {
            "run_id": f"{manifest.id}-seed-{seed}",
            "detector": detector,
            "source_region": drift["source_region"],
            "release_window": drift["release_window"],
            "particles": drift["particles"],
            "vessels": vessels,
            "warnings": warnings,
            "metadata": {
                "case_id": manifest.id,
                "seed": seed,
                "observation_time": manifest.observation_time.isoformat(),
            },
        }
    )
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = _result_path(manifest.id, seed)
    output_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    legacy_output_path = GENERATED_DIR / f"{manifest.id}-analysis.json"
    legacy_output_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    return result
