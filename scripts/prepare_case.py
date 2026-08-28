from pathlib import Path


if __name__ == "__main__":
    case_dir = Path("data/cases/arabian_sea_demo")
    print(f"Case assets are stored in: {case_dir.resolve()}")
