from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.api.case_runner import _case_dir, case_payload, load_case


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate an OceanTrace case manifest and assets")
    parser.add_argument("case_id", nargs="?", default="arabian_sea_demo")
    arguments = parser.parse_args()
    manifest = load_case(arguments.case_id)
    directory = _case_dir(arguments.case_id)
    required = [
        directory / manifest.image_path,
        directory / manifest.image_bounds_path,
        directory / manifest.spill_polygon,
    ]
    if manifest.annotation_path:
        required.append(directory / manifest.annotation_path)
    if manifest.forcing:
        required.extend(
            [directory / manifest.forcing.wind_path, directory / manifest.forcing.current_path]
        )
    if manifest.ais_path:
        required.append(directory / manifest.ais_path)
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit("Missing case assets:\n" + "\n".join(missing))
    payload = case_payload(arguments.case_id)
    print(
        f"Validated {manifest.id}: {len(payload['available_layers'])} layers, "
        f"{len(payload['ais_tracks'])} AIS tracks"
    )
