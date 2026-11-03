"""Fetch only 50 selected ZIP members with HTTP ranges and per-member CRC checks."""
import concurrent.futures
import io
import json
import struct
import zipfile
import zlib
from pathlib import Path
import requests
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'Data/SOS'
SIZE = 1148063776
URL = 'https://zenodo.org/records/15298010/files/images.zip?download=1'

def read_range(start, end):
    r = requests.get(URL, headers={'Range': f'bytes={start}-{end}'}, timeout=120)
    r.raise_for_status()
    assert r.status_code == 206 and r.headers.get('Content-Range') == f'bytes {start}-{end}/{SIZE}'
    return r.content

def main():
    directory = DATA / 'metadata/images-central-directory.bin'
    if not directory.exists():
        directory.write_bytes(read_range(SIZE - 2 * 1024 * 1024, SIZE - 1))
    tail = directory.read_bytes()
    # zipfile handles a central-directory-only buffer by compensating header offsets;
    # add back the missing file prefix when calculating member offsets.
    z = zipfile.ZipFile(io.BytesIO(tail))
    members = {(Path(n.filename).parent.name, Path(n.filename).name): n for n in z.infolist()
               if n.filename.endswith('.png') and '__MACOSX' not in n.filename}
    prefix = SIZE - len(tail)
    records = []
    with zipfile.ZipFile(ROOT / 'data_samples/masks.zip') as masks:
        for n in masks.namelist():
            if not n.endswith('.png') or '__MACOSX' in n:
                continue
            split, filename = Path(n).parent.name, Path(n).name
            mask = np.asarray(Image.open(masks.open(n)).convert('L')) >= 128
            records.append(dict(id=filename[:-4], sensor=filename.split('_')[0], split=split,
                                file=f'patches/{split}/{filename}', oil_fraction=float(mask.mean()), mask_member=n))
        selected = []
        for sensor in ('palsar', 'sentinel'):
            pool = sorted([p for p in records if p['sensor'] == sensor], key=lambda p: (p['oil_fraction'], p['id']))
            for bin_id, indices in enumerate(np.array_split(np.arange(len(pool)), 5)):
                # Even positions cover the observed coverage range; deterministic.
                for i in np.linspace(0, len(indices) - 1, 5, dtype=int):
                    selected.append(dict(pool[int(indices[i])], coverage_bin=bin_id))
        for p in selected:
            (DATA / 'pilot' / (p['id'] + '_mask.png')).write_bytes(masks.read(p['mask_member']))
    assert len(selected) == len({p['id'] for p in selected}) == 50
    (DATA / 'pilot/selected_50.json').write_text(json.dumps(selected, indent=2))
    def fetch(p):
        dest = DATA / p['file']
        member = members[p['split'], p['id'] + '.png']
        if dest.exists() and zlib.crc32(dest.read_bytes()) == member.CRC:
            return
        offset = member.header_offset + prefix
        header = read_range(offset, offset + 29)
        fields = struct.unpack('<IHHHHHIIIHH', header)
        assert fields[0] == 0x04034B50
        start = offset + 30 + fields[-2] + fields[-1]
        compressed = read_range(start, start + member.compress_size - 1)
        payload = zlib.decompress(compressed, -15) if member.compress_type == zipfile.ZIP_DEFLATED else compressed
        assert len(payload) == member.file_size and zlib.crc32(payload) == member.CRC
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(payload)
        print(p['id'], 'CRC verified', flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        list(executor.map(fetch, selected))
    print('50 pilot patches downloaded; selection spans both sensors and mask-coverage quintiles.')

if __name__ == '__main__':
    main()
