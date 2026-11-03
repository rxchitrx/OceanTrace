"""Read-only full SOS audit. Does not transform images, masks, splits or labels."""
import csv
import json
import zipfile
from collections import Counter
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'Data/SOS'
OUT = ROOT / 'Data/Preprocessing'

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    errors = []
    with zipfile.ZipFile(ROOT / 'data_samples/masks.zip') as masks:
        lookup = {(Path(n).parent.name, Path(n).name): n for n in masks.namelist()
                  if n.endswith('.png') and '__MACOSX' not in n}
        for i, path in enumerate(sorted((DATA / 'patches').rglob('*.png')), 1):
            key = path.parent.name, path.name
            try:
                with Image.open(path) as image:
                    image.load()
                    channels_equal = None
                    if image.mode == 'RGB':
                        a, b, c = image.split()
                        channels_equal = ImageChops.difference(a, b).getbbox() is None and ImageChops.difference(a, c).getbbox() is None
                    with Image.open(masks.open(lookup[key])) as mask:
                        mask.load()
                        gray = mask.convert('L')
                        hist = gray.histogram()
                        total = mask.width * mask.height
                        rows.append(dict(id=path.stem, split=key[0], sensor=path.stem.split('_')[0],
                                         image_width=image.width, image_height=image.height, image_mode=image.mode,
                                         image_rgb_channels_equal=channels_equal,
                                         mask_width=mask.width, mask_height=mask.height, mask_mode=mask.mode,
                                         dimensions_match=image.size == mask.size,
                                         mask_distinct_gray_values=sum(v > 0 for v in hist),
                                         mask_intermediate_pixels=sum(hist[1:255]),
                                         mask_foreground_fraction_at_128=sum(hist[128:]) / total))
            except Exception as exc:
                errors.append(dict(file=path.relative_to(ROOT).as_posix(), error=type(exc).__name__))
            if i % 1000 == 0:
                print(f'Audited {i} images', flush=True)
    summary = dict(images_audited=len(rows), errors=errors, masks_in_archive=len(lookup),
                   image_modes=dict(Counter(r['image_mode'] for r in rows)),
                   mask_modes=dict(Counter(r['mask_mode'] for r in rows)),
                   splits=dict(Counter(r['split'] for r in rows)),
                   sensors=dict(Counter(r['sensor'] for r in rows)),
                   dimension_mismatches=sum(not r['dimensions_match'] for r in rows),
                   rgb_images_with_unequal_channels=sum(r['image_rgb_channels_equal'] is False for r in rows),
                   masks_with_intermediate_gray_values=sum(r['mask_intermediate_pixels'] > 0 for r in rows),
                   empty_masks_after_threshold=sum(r['mask_foreground_fraction_at_128'] == 0 for r in rows),
                   full_masks_after_threshold=sum(r['mask_foreground_fraction_at_128'] == 1 for r in rows),
                   note='Threshold 128 is an audit diagnostic, not an adopted training-label conversion. No files modified.')
    (OUT / 'sos-audit.json').write_text(json.dumps(summary, indent=2))
    if rows:
        with (OUT / 'sos-audit.csv').open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    print(json.dumps(summary, indent=2), flush=True)

if __name__ == '__main__':
    main()
