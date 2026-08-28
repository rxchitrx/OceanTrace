import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.api.case_runner import run_case


if __name__ == "__main__":
    result = run_case("arabian_sea_demo")
    print(result.model_dump_json(indent=2))
