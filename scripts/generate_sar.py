from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]


def _latlon_to_pixel(
    latitude: float,
    longitude: float,
    bounds: dict[str, float],
    size: int,
) -> tuple[int, int]:
    y = int(size * (bounds["north"] - latitude) / (bounds["north"] - bounds["south"]))
    x = int(size * (longitude - bounds["west"]) / (bounds["east"] - bounds["west"]))
    return x, y


def generate_controlled_sar(case_id: str, *, force: bool = False) -> Path:
    case_dir = ROOT / "data" / "cases" / case_id
    manifest = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
    if manifest["scenario_type"] != "controlled_demo":
        raise ValueError("Only controlled demonstration imagery may be generated locally")
    output = case_dir / manifest["image_path"]
    if output.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite {output}; pass --force to regenerate")

    bounds = json.loads((case_dir / manifest["image_bounds_path"]).read_text(encoding="utf-8"))
    spill = json.loads((case_dir / manifest["spill_polygon"]).read_text(encoding="utf-8"))
    coordinates = spill["geometry"]["coordinates"][0]
    size = 512
    rng = np.random.default_rng(manifest.get("random_seed", 26143))
    base = np.clip(rng.rayleigh(scale=120, size=(size, size)), 0, 255).astype(np.uint8)
    image = Image.fromarray(base, mode="L")
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    pixels = [_latlon_to_pixel(lat, lon, bounds, size) for lon, lat in coordinates]
    draw.polygon(pixels, fill=205)
    mask_array = np.asarray(mask, dtype=np.float32) / 255.0
    darkened = np.asarray(image, dtype=np.float32) * (1.0 - 0.72 * mask_array)
    Image.fromarray(np.clip(darkened, 0, 255).astype(np.uint8), mode="L").save(output)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate controlled OceanTrace SAR imagery")
    parser.add_argument("--case", default="arabian_sea_demo")
    parser.add_argument("--force", action="store_true")
    arguments = parser.parse_args()
    print(generate_controlled_sar(arguments.case, force=arguments.force))
