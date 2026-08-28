from pathlib import Path

import numpy as np
from PIL import Image

from services.api.case_runner import ROOT, run_case
from services.api.detection.baseline_detector import detect_candidate_slick


BOUNDS = {"north": 10.0, "south": 9.0, "east": 21.0, "west": 20.0}


def test_detector_reads_pixels_and_finds_dark_region(tmp_path: Path):
    rng = np.random.default_rng(4)
    pixels = np.clip(rng.normal(170, 20, size=(128, 128)), 0, 255).astype(np.uint8)
    pixels[35:95, 42:88] = np.clip(pixels[35:95, 42:88] * 0.22, 0, 255)
    image_path = tmp_path / "sar.png"
    Image.fromarray(pixels).save(image_path)

    result = detect_candidate_slick(image_path, BOUNDS)

    assert result["method"] == "adaptive_dark_region_v1"
    assert result["features"]["bbox_xmin"] <= 45
    assert result["features"]["bbox_xmax"] >= 85
    assert result["features"]["local_contrast"] > 0.25


def test_real_dartis_patch_matches_published_annotation():
    result = run_case("dartis_validation")

    assert result.analysis_mode == "detection_only"
    assert result.detector_evaluation is not None
    assert result.detector_evaluation["best_bbox_iou"] >= 0.90
    assert result.detector_evaluation["matched_at_iou_0_50"] is True
    assert (ROOT / "data/cases/dartis_validation/ATTRIBUTION.md").exists()
