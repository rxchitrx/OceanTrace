"""Preserve full archive payloads; export the HH/VV detected band to GeoTIFF."""
import json
import argparse
import zipfile
from pathlib import Path
import rasterio
from rasterio.shutil import copy as copy_raster
from rasterio.enums import Resampling
from PIL import Image
from match import normalize

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'Data/SOS'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--available-only', action='store_true')
    args = parser.parse_args()
    rows = json.loads((DATA / 'metadata/scenes.json').read_text())
    lineage = []
    for row in rows:
        url = row.get('asf_download_url', row['download_url'])
        archive = DATA / 'archives/scenes' / url.rsplit('/', 1)[-1]
        if not archive.exists() and args.available_only:
            continue
        folder = DATA / 'scenes/raw' / row['published_id'].replace(' ', '_')
        folder.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive) as z:
            for item in z.infolist():
                target = (folder / item.filename).resolve()
                if not target.is_relative_to(folder.resolve()):
                    raise ValueError('Unsafe archive path')
                if not target.exists():
                    z.extract(item, folder)
        candidates = [p for p in folder.rglob('*') if p.is_file() and
                      ((row['sensor'] == 'PALSAR' and p.name.startswith('IMG-HH')) or
                       (row['sensor'] != 'PALSAR' and p.suffix.lower() in ('.tif', '.tiff') and '-vv-' in p.name))]
        if len(candidates) != 1:
            raise ValueError(f'{row["published_id"]}: expected one HH/VV band, found {len(candidates)}')
        source = candidates[0]
        dest = DATA / 'scenes' / (row['published_id'].replace(' ', '_') + '.tif')
        if not dest.exists():
            copy_raster(source, dest, driver='GTiff', compress='deflate', tiled=True, BIGTIFF='IF_SAFER')
        with rasterio.open(dest) as raster:
            scale = min(1, 2400 / max(raster.shape))
            arr = raster.read(1, out_shape=tuple(max(1, round(v * scale)) for v in raster.shape),
                              resampling=Resampling.average, masked=True).filled(0)
            preview = DATA / 'scenes' / (dest.stem + '-full-raster-preview.jpg')
            Image.fromarray(normalize(arr)).save(preview, quality=92)
            lineage.append(dict(scene=row['published_id'], archive=str(archive.relative_to(DATA)),
                                member=str(source.relative_to(folder)), raster=str(dest.relative_to(DATA)),
                                shape=raster.shape, crs=str(raster.crs), band='HH' if row['sensor']=='PALSAR' else 'VV',
                                note='Candidate source product. Original SOS processing/polarization is not independently established.'))
        print(row['published_id'], 'full raster exported', flush=True)
    (DATA / 'metadata/raster_lineage.json').write_text(json.dumps(lineage, indent=2))

if __name__ == '__main__':
    main()
