from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.api.case_runner import run_case


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate an OceanTrace detection case")
    parser.add_argument("--case", default="dartis_validation")
    parser.add_argument("--seed", type=int, default=26143)
    arguments = parser.parse_args()
    result = run_case(arguments.case, seed=arguments.seed)
    print(
        json.dumps(
            {
                "case_id": arguments.case,
                "detector": result.detector.model_dump(mode="json"),
                "evaluation": result.detector_evaluation,
            },
            indent=2,
        )
    )
