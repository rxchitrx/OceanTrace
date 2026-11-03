"""Download the public refined release in verified HTTP ranges, then check MD5."""
import concurrent.futures
import hashlib
import time
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'Data/SOS/archives'
SIZE = 1148063776
CHUNK = 4 * 1024 * 1024
URL = 'https://zenodo.org/records/15298010/files/images.zip?download=1'

def part(i):
    start, end = i * CHUNK, min(SIZE, (i + 1) * CHUNK) - 1
    path = DEST / 'parts' / f'{i:04}.part'
    if path.exists() and path.stat().st_size == end - start + 1:
        return path
    for attempt in range(5):
        try:
            r = requests.get(URL, headers={'Range': f'bytes={start}-{end}'}, timeout=120)
            r.raise_for_status()
            assert r.status_code == 206 and r.headers.get('Content-Range') == f'bytes {start}-{end}/{SIZE}'
            assert len(r.content) == end - start + 1
            path.write_bytes(r.content)
            return path
        except Exception:
            if attempt == 4:
                raise
            time.sleep(2 ** attempt)

if __name__ == '__main__':
    (DEST / 'parts').mkdir(parents=True, exist_ok=True)
    count = (SIZE + CHUNK - 1) // CHUNK
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as pool:
        for n, _ in enumerate(pool.map(part, range(count)), 1):
            if n % 10 == 0 or n == count:
                print(f'{n}/{count} chunks ready', flush=True)
    digest = hashlib.md5()
    target = DEST / 'images.zip'
    with target.with_suffix('.zip.tmp').open('wb') as output:
        for i in range(count):
            data = (DEST / 'parts' / f'{i:04}.part').read_bytes()
            output.write(data)
            digest.update(data)
    assert digest.hexdigest() == 'e5272875611e8b5a2a0d49972224c842', digest.hexdigest()
    target.with_suffix('.zip.tmp').replace(target)
    print('Verified images.zip MD5', digest.hexdigest(), flush=True)
