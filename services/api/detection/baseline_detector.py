from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable
from xml.etree import ElementTree

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage


def _pixel_to_lonlat(
    x: float,
    y: float,
    width: int,
    height: int,
    bounds: Dict[str, float],
) -> tuple[float, float]:
    longitude = bounds["west"] + (x / width) * (bounds["east"] - bounds["west"])
    latitude = bounds["north"] - (y / height) * (bounds["north"] - bounds["south"])
    return longitude, latitude


def _bbox_polygon(
    bbox: tuple[int, int, int, int],
    width: int,
    height: int,
    bounds: Dict[str, float],
) -> Dict[str, Any]:
    min_x, min_y, max_x, max_y = bbox
    west, north = _pixel_to_lonlat(min_x, min_y, width, height, bounds)
    east, south = _pixel_to_lonlat(max_x, max_y, width, height, bounds)
    return {
        "type": "Polygon",
        "coordinates": [[
            [round(west, 7), round(south, 7)],
            [round(east, 7), round(south, 7)],
            [round(east, 7), round(north, 7)],
            [round(west, 7), round(north, 7)],
            [round(west, 7), round(south, 7)],
        ]],
    }


def _orientation_and_elongation(component: np.ndarray) -> tuple[float, float]:
    ys, xs = np.nonzero(component)
    if len(xs) < 3:
        return 0.0, 1.0
    points = np.column_stack((xs, -ys)).astype(float)
    covariance = np.cov(points, rowvar=False)
    values, vectors = np.linalg.eigh(covariance)
    values = np.maximum(values, 1e-9)
    major_index = int(np.argmax(values))
    major = vectors[:, major_index]
    orientation = float(np.degrees(np.arctan2(major[1], major[0])) % 180.0)
    elongation = float(np.sqrt(values.max() / values.min()))
    return orientation, elongation


def _component_candidates(
    darkness: np.ndarray,
    normalized: np.ndarray,
    mask: np.ndarray,
) -> list[Dict[str, Any]]:
    labels, _ = ndimage.label(mask)
    objects = ndimage.find_objects(labels)
    candidates: list[Dict[str, Any]] = []

    for label_id, object_slice in enumerate(objects, start=1):
        if object_slice is None:
            continue
        component = labels == label_id
        area = int(component.sum())
        if area < 45:
            continue

        y_slice, x_slice = object_slice
        min_x, max_x = int(x_slice.start), int(x_slice.stop)
        min_y, max_y = int(y_slice.start), int(y_slice.stop)
        bbox_area = max(1, (max_x - min_x) * (max_y - min_y))
        fill_ratio = area / bbox_area
        area_fraction = area / component.size
        if area_fraction > 0.35:
            continue

        ring = ndimage.binary_dilation(component, iterations=8) & ~component
        inside_intensity = float(normalized[component].mean())
        outside_intensity = float(normalized[ring].mean()) if ring.any() else inside_intensity
        contrast = max(0.0, outside_intensity - inside_intensity)
        orientation, elongation = _orientation_and_elongation(component)
        perimeter = int((component & ~ndimage.binary_erosion(component)).sum())

        contrast_score = min(1.0, contrast / 0.18)
        size_score = min(1.0, area / max(600.0, component.size * 0.025))
        coherence_score = min(1.0, fill_ratio / 0.32)
        shape_score = min(1.0, max(0.0, elongation - 1.0) / 5.0)
        darkness_score = min(1.0, float(darkness[component].mean()) / 0.16)
        score = (
            0.34 * contrast_score
            + 0.24 * size_score
            + 0.16 * coherence_score
            + 0.14 * shape_score
            + 0.12 * darkness_score
        )

        candidates.append(
            {
                "score": score,
                "bbox": (min_x, min_y, max_x, max_y),
                "area": area,
                "perimeter": perimeter,
                "fill_ratio": fill_ratio,
                "orientation": orientation,
                "elongation": elongation,
                "mean_intensity": inside_intensity,
                "surrounding_intensity": outside_intensity,
                "contrast": contrast,
            }
        )

    return sorted(candidates, key=lambda item: item["score"], reverse=True)


def detect_candidate_slick(
    image_path: Path,
    bounds: Dict[str, float],
) -> Dict[str, Any]:
    """Detect the strongest coherent dark formation in a georeferenced SAR patch.

    This is an explainable classical baseline, not a calibrated oil classifier. It
    reads the image pixels directly and never receives the reference annotation.
    """

    image = Image.open(image_path).convert("L").filter(ImageFilter.MedianFilter(size=3))
    pixels = np.asarray(image, dtype=np.float32)
    height, width = pixels.shape
    low, high = np.percentile(pixels, [1.0, 99.0])
    normalized = np.clip((pixels - low) / max(high - low, 1.0), 0.0, 1.0)

    local = ndimage.gaussian_filter(normalized, sigma=1.2)
    background_sigma = max(8.0, min(height, width) / 35.0)
    background = ndimage.gaussian_filter(normalized, sigma=background_sigma)
    darkness = np.clip(background - local, 0.0, 1.0)

    margin = max(3, int(min(height, width) * 0.015))
    interior = darkness[margin:-margin, margin:-margin]
    threshold = max(0.035, float(np.percentile(interior, 91.5)))
    mask = (darkness >= threshold) & (local <= np.percentile(local, 47.0))
    mask[:margin, :] = False
    mask[-margin:, :] = False
    mask[:, :margin] = False
    mask[:, -margin:] = False
    mask = ndimage.binary_closing(mask, iterations=2)
    mask = ndimage.binary_opening(mask, iterations=1)
    mask = ndimage.binary_fill_holes(mask)

    candidates = _component_candidates(darkness, normalized, mask)
    if not candidates:
        raise ValueError("No coherent dark formation was found in the SAR image")

    best = candidates[0]
    min_x, min_y, max_x, max_y = best["bbox"]
    return {
        "polygon": _bbox_polygon(best["bbox"], width, height, bounds),
        "score": round(float(best["score"]), 3),
        "method": "adaptive_dark_region_v1",
        "features": {
            "image_width_px": float(width),
            "image_height_px": float(height),
            "candidate_count": float(len(candidates)),
            "area_px": float(best["area"]),
            "area_fraction": round(best["area"] / (width * height), 6),
            "perimeter_px": float(best["perimeter"]),
            "fill_ratio": round(float(best["fill_ratio"]), 4),
            "elongation": round(float(best["elongation"]), 3),
            "orientation_deg": round(float(best["orientation"]), 2),
            "mean_intensity": round(float(best["mean_intensity"]), 4),
            "surrounding_intensity": round(float(best["surrounding_intensity"]), 4),
            "local_contrast": round(float(best["contrast"]), 4),
            "threshold": round(threshold, 4),
            "bbox_xmin": float(min_x),
            "bbox_ymin": float(min_y),
            "bbox_xmax": float(max_x),
            "bbox_ymax": float(max_y),
        },
    }


def parse_pascal_voc_boxes(annotation_path: Path) -> list[tuple[int, int, int, int]]:
    root = ElementTree.parse(annotation_path).getroot()
    boxes: list[tuple[int, int, int, int]] = []
    for object_node in root.findall("object"):
        if (object_node.findtext("name") or "").lower() != "oil":
            continue
        box = object_node.find("bndbox")
        if box is None:
            continue
        boxes.append(
            (
                int(float(box.findtext("xmin", "0"))),
                int(float(box.findtext("ymin", "0"))),
                int(float(box.findtext("xmax", "0"))),
                int(float(box.findtext("ymax", "0"))),
            )
        )
    return boxes


def bbox_iou(a: Iterable[float], b: Iterable[float]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    intersection_width = max(0.0, min(ax2, bx2) - max(ax1, bx1))
    intersection_height = max(0.0, min(ay2, by2) - max(ay1, by1))
    intersection = intersection_width * intersection_height
    union = max(0.0, (ax2 - ax1) * (ay2 - ay1)) + max(
        0.0, (bx2 - bx1) * (by2 - by1)
    ) - intersection
    return intersection / union if union > 0 else 0.0


def evaluate_pascal_voc_detection(
    detector: Dict[str, Any],
    annotation_path: Path,
) -> Dict[str, Any]:
    features = detector["features"]
    predicted = (
        features["bbox_xmin"],
        features["bbox_ymin"],
        features["bbox_xmax"],
        features["bbox_ymax"],
    )
    boxes = parse_pascal_voc_boxes(annotation_path)
    overlaps = [bbox_iou(predicted, box) for box in boxes]
    best_iou = max(overlaps, default=0.0)
    return {
        "annotation_format": "Pascal VOC",
        "reference_object_count": len(boxes),
        "best_bbox_iou": round(best_iou, 4),
        "matched_at_iou_0_25": best_iou >= 0.25,
        "matched_at_iou_0_50": best_iou >= 0.50,
    }
