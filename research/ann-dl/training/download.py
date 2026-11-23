"""Download and verify the author's PALSAR split against its Drive listing."""
import concurrent.futures
import hashlib
import io
import json
import re
import time
from threading import local
from collections import Counter, defaultdict
from pathlib import Path

import requests
from PIL import Image

ROOT = Path(__file__).resolve().parent
DEST = ROOT / 'original-palsar'
COUNTS = {'train': 3101, 'test': 776}
CLIENT = local()
PATTERN = re.compile(r'(\d+)_(sat\.jpg|mask\.png)')
CHECKSUMS = ROOT / 'expected-sha256.txt'
VERIFIED = ROOT / 'verified-sha256.txt'

def manifest():
    rows = []
    names = defaultdict(set)
    seen = set()
    for line in (ROOT / 'drive-manifest.jsonl').read_text().splitlines():
        row = json.loads(line)
        match = PATTERN.fullmatch(row['name'])
        if not match or row['id'] in seen or row['size'] <= 0:
            raise ValueError(row)
        seen.add(row['id'])
        split = 'train' if row['kind'] == 'train' else 'test'
        name, suffix = match.groups()
        if suffix in names[split, name]:
            raise ValueError(row)
        names[split, name].add(suffix)
        rows.append((split, name, suffix, row))
    assert Counter(split for split, _ in names) == COUNTS
    assert all(value == {'sat.jpg', 'mask.png'} for value in names.values())
    return sorted(rows)

def verify(content, row, suffix, expected_digest):
    if len(content) != row['size']:
        raise ValueError(f"expected {row['size']} bytes, received {len(content)}")
    with Image.open(io.BytesIO(content)) as image:
        assert image.size == (256, 256)
        assert image.format == ('JPEG' if suffix == 'sat.jpg' else 'PNG')
        image.load()
    if hashlib.sha256(content).hexdigest() != expected_digest:
        raise ValueError('SHA-256 differs from the original release')

def fetch(item, expected_digest):
    split, name, suffix, row = item
    path = DEST / split / row['name']
    if path.exists():
        try:
            verify(path.read_bytes(), row, suffix, expected_digest)
            return
        except (ValueError, OSError, AssertionError):
            pass
    if not hasattr(CLIENT, "session"):
        CLIENT.session = requests.Session()
    for attempt in range(4):
        try:
            response = CLIENT.session.get(
                'https://drive.usercontent.google.com/download',
                params={'export': 'download', 'id': row['id'], 'confirm': 't'}, timeout=(8, 25))
            response.raise_for_status()
            verify(response.content, row, suffix, expected_digest)
            temp = path.with_suffix('.part')
            temp.write_bytes(response.content)
            temp.replace(path)
            return
        except (requests.RequestException, OSError, ValueError, AssertionError) as error:
            if attempt == 3:
                raise RuntimeError(f"{split}/{name}_{suffix}: {error}") from error
            time.sleep(0.5 * 2**attempt)

if __name__ == '__main__':
    rows = manifest()
    checksum_bytes = CHECKSUMS.read_bytes()
    checksums = {}
    for line in checksum_bytes.decode('ascii').splitlines():
        digest, path = line.split('  ', 1)
        checksums[path] = digest
    paths = {f"{split}/{row['name']}" for split, _, _, row in rows}
    if checksums.keys() != paths:
        raise SystemExit('Drive manifest and pinned SHA-256 listing describe different files')
    VERIFIED.unlink(missing_ok=True)
    for split in COUNTS:
        (DEST / split).mkdir(parents=True, exist_ok=True)
    print(f'Drive manifest: {dict(COUNTS)} pairs, {len(rows)} files', flush=True)
    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
        pending = [pool.submit(fetch, item, checksums[f"{item[0]}/{item[3]['name']}"])
                   for item in rows]
        for i, result in enumerate(concurrent.futures.as_completed(pending), 1):
            try:
                result.result()
            except RuntimeError as e:
                failures.append(str(e))
            if i % 250 == 0 or i == len(rows):
                print(f'{i}/{len(rows)} checked; {len(failures)} failed', flush=True)
    if failures:
        (ROOT / 'download-failures.json').write_text(json.dumps(failures, indent=2)+'\n')
        raise SystemExit(f'{len(failures)} files failed; rerun to resume')
    (ROOT / 'download-failures.json').unlink(missing_ok=True)
    temporary = VERIFIED.with_suffix('.tmp')
    temporary.write_bytes(checksum_bytes)
    temporary.replace(VERIFIED)
    print('Complete original PALSAR split verified', flush=True)
