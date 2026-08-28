from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict

from services.api.ais.cleaner import load_ais_rows, validate_rows
from services.api.ais.features import grouped_tracks
from services.api.ais.interpolator import detect_gaps, interpolate_short_gaps
from services.api.detection.baseline_detector import (
    detect_candidate_slick,
    evaluate_pascal_voc_detection,
)
from services.api.drift.forcing import load_forcing
from services.api.drift.source_search import search_source_region
from services.api.ranking.scorer import score_vessels
from services.api.schemas import AnalysisResult, CaseManifest, CasePayload, CaseSummary


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "cases"
GENERATED_DIR = ROOT / "generated"
SAFE_CASE_ID = re.compile(r"^[A-Za-z0-9_-]+$")


def _case_dir(case_id: str) -> Path:
    if not SAFE_CASE_ID.fullmatch(case_id):
        raise FileNotFoundError("Invalid case identifier")
    case_dir = (DATA_DIR / case_id).resolve()
    if DATA_DIR.resolve() not in case_dir.parents:
        raise FileNotFoundError("Invalid case identifier")
    return case_dir


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def list_cases() -> list[Dict[str, Any]]:
    cases: list[Dict[str, Any]] = []
    for case_dir in sorted(DATA_DIR.iterdir()):
        manifest_path = case_dir / "case.json"
        if not manifest_path.exists():
            continue
        manifest = CaseManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
        cases.append(
            CaseSummary(
                id=manifest.id,
                region=manifest.region,
                scenario_type=manifest.scenario_type,
                observation_time=manifest.observation_time,
                analysis_mode=(
                    "full" if manifest.scenario_type == "controlled_demo" else "detection_only"
                ),
            ).model_dump(mode="json")
        )
    return cases


def load_case(case_id: str) -> CaseManifest:
    case_path = _case_dir(case_id) / "case.json"
    if not case_path.exists():
        raise FileNotFoundError(case_id)
    manifest = CaseManifest.model_validate_json(case_path.read_text(encoding="utf-8"))
    if manifest.id != case_id:
        raise ValueError(f"Case directory and manifest id do not match: {case_id}")
    return manifest


def case_payload(case_id: str) -> Dict[str, Any]:
    manifest = load_case(case_id)
    case_dir = _case_dir(case_id)
    spill = _read_json(case_dir / manifest.spill_polygon)
    expected_path = case_dir / "expected_result.json"
    expected = _read_json(expected_path) if expected_path.exists() else {}
    tracks: Dict[str, list[dict]] = {}
    if manifest.ais_path:
        ais_rows = validate_rows(load_ais_rows(case_dir / manifest.ais_path))
        tracks = interpolate_short_gaps(grouped_tracks(ais_rows))

    available_layers = ["sar_image", "spill_polygon"]
    if manifest.scenario_type == "controlled_demo":
        available_layers.extend(["source_heatmap", "particle_paths", "ais_tracks"])
    payload = CasePayload(
        manifest=manifest,
        spill_polygon=spill,
        expected_result=expected,
        available_layers=available_layers,
        ais_tracks=tracks,
    )
    return payload.model_dump(mode="json")


def _result_path(case_id: str, seed: int) -> Path:
    return GENERATED_DIR / f"{case_id}-seed-{seed}.json"


def load_cached_result(case_id: str, seed: int = 26143) -> AnalysisResult | None:
    path = _result_path(case_id, seed)
    if not path.exists():
        return None
    return AnalysisResult.model_validate_json(path.read_text(encoding="utf-8"))


def load_result(case_id: str, run_id: str) -> AnalysisResult | None:
    if run_id == "latest":
        candidates = sorted(
            GENERATED_DIR.glob(f"{case_id}-seed-*.json"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        ) if GENERATED_DIR.exists() else []
        if not candidates:
            return None
        return AnalysisResult.model_validate_json(candidates[0].read_text(encoding="utf-8"))
    prefix = f"{case_id}-seed-"
    if not run_id.startswith(prefix):
        return None
    try:
        seed = int(run_id.removeprefix(prefix))
    except ValueError:
        return None
    return load_cached_result(case_id, seed)


def run_case(case_id: str, seed: int = 26143) -> AnalysisResult:
    manifest = load_case(case_id)
    case_dir = _case_dir(case_id)
    spill = _read_json(case_dir / manifest.spill_polygon)
    bounds = _read_json(case_dir / manifest.image_bounds_path)
    detector = detect_candidate_slick(case_dir / manifest.image_path, bounds)
    detector_evaluation = None
    if manifest.annotation_path:
        detector_evaluation = evaluate_pascal_voc_detection(
            detector,
            case_dir / manifest.annotation_path,
        )

    base_payload: Dict[str, Any] = {
        "run_id": f"{manifest.id}-seed-{seed}",
        "analysis_mode": (
            "full" if manifest.scenario_type == "controlled_demo" else "detection_only"
        ),
        "detector": detector,
        "detector_evaluation": detector_evaluation,
        "warnings": list(manifest.notes),
        "metadata": {
            "case_id": manifest.id,
            "seed": seed,
            "observation_time": manifest.observation_time.isoformat(),
            "scenario_type": manifest.scenario_type,
            "data_sources": manifest.data_sources,
        },
    }

    if manifest.scenario_type == "controlled_demo":
        if manifest.forcing is None or manifest.ais_path is None:
            raise ValueError("Full analysis cases require forcing and AIS inputs")
        wind = load_forcing(case_dir / manifest.forcing.wind_path)
        current = load_forcing(case_dir / manifest.forcing.current_path)
        ais_rows = validate_rows(load_ais_rows(case_dir / manifest.ais_path))
        tracks = grouped_tracks(ais_rows)
        interpolated = interpolate_short_gaps(tracks)
        gaps = detect_gaps(ais_rows)
        drift = search_source_region(
            manifest.observation_time,
            detector["polygon"],
            wind,
            current,
            seed=seed,
            expected_age_hours=manifest.release_time_prior_hours,
        )
        vessels = score_vessels(
            interpolated,
            gaps,
            drift["source_region"],
            drift["release_window"],
            manifest.observation_time,
            detector["polygon"],
            wind,
            current,
        )
        base_payload.update(
            {
                "source_region": drift["source_region"],
                "release_window": drift["release_window"],
                "particles": drift["particles"],
                "vessels": vessels,
            }
        )
        base_payload["metadata"]["drift_diagnostics"] = drift["diagnostics"]

    result = AnalysisResult.model_validate(base_payload)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    _result_path(manifest.id, seed).write_text(result.model_dump_json(indent=2), encoding="utf-8")
    return result
