import json
from pathlib import Path


if __name__ == "__main__":
    result_path = Path("generated/arabian_sea_demo-analysis.json")
    if result_path.exists():
        payload = json.loads(result_path.read_text(encoding="utf-8"))
        print(json.dumps(payload["detector"], indent=2))
    else:
        print("Run scripts/run_case.py first to generate a detector output.")
