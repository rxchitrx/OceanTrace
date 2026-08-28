import json
from pathlib import Path
import numpy as np
from PIL import Image

def generate_sar():
    cases = [
        {
            "id": "arabian_sea_demo",
            "dir": Path("e:/Project/SIH/OceanTrace/data/cases/arabian_sea_demo"),
            "image_path": Path("e:/Project/SIH/OceanTrace/data/cases/arabian_sea_demo/sar.png"),
            "bounds": {"north": 19.15, "south": 18.75, "east": 69.25, "west": 68.75},
            "coords": [[68.95, 18.92], [69.08, 18.95], [69.11, 19.03], [68.99, 19.06]]
        },
        {
            "id": "dartis_validation",
            "dir": Path("e:/Project/SIH/OceanTrace/data/cases/dartis_validation"),
            "image_path": Path("e:/Project/SIH/OceanTrace/data/cases/dartis_validation/image/sar.png"),
            "bounds": {"north": 19.35, "south": 18.95, "east": 68.4, "west": 67.9},
            "coords": [[68.1, 19.1], [68.2, 19.1], [68.2, 19.2], [68.1, 19.2]]
        }
    ]

    np.random.seed(42)
    shape = (512, 512)

    for case in cases:
        base = np.random.rayleigh(scale=120, size=shape)
        bounds = case["bounds"]
        
        def latlon_to_pixel(lat, lon):
            y = int(512 * (bounds["north"] - lat) / (bounds["north"] - bounds["south"]))
            x = int(512 * (lon - bounds["west"]) / (bounds["east"] - bounds["west"]))
            return x, y

        pixels = [latlon_to_pixel(lat, lon) for lon, lat in case["coords"]]
        
        min_x = min(p[0] for p in pixels)
        max_x = max(p[0] for p in pixels)
        min_y = min(p[1] for p in pixels)
        max_y = max(p[1] for p in pixels)
        
        for y in range(512):
            for x in range(512):
                if min_x <= x <= max_x and min_y <= y <= max_y:
                    cx, cy = (min_x + max_x) // 2, (min_y + max_y) // 2
                    dx, dy = (x - cx) / (max_x - min_x), (y - cy) / (max_y - min_y)
                    if dx*dx + dy*dy <= 0.25:
                        base[y, x] = base[y, x] * 0.3

        base = np.clip(base, 0, 255).astype(np.uint8)
        img = Image.fromarray(base, mode='L')
        case["image_path"].parent.mkdir(parents=True, exist_ok=True)
        img.save(case["image_path"])
        
        with open(case["dir"] / "sar_bounds.json", "w") as f:
            json.dump(bounds, f, indent=2)
            
        print(f"Generated SAR image and bounds for {case['id']}")

if __name__ == "__main__":
    generate_sar()
