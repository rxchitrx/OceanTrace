"""Authenticated, resumable ASF downloads. Secret file is never copied or logged.

Use --token-file with the private file delivered by T3's secret prompt.
Default downloads all 21 catalogue-resolved source products, about 6.64 GB.
"""
import argparse
import concurrent.futures
import json
import zipfile
from pathlib import Path
import asf_search
from tenacity import retry, stop_after_attempt, wait_exponential

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'Data/SOS'

def main():
    parser = argparse.ArgumentParser()
    auth = parser.add_mutually_exclusive_group(required=True)
    auth.add_argument('--token-file', type=Path)
    auth.add_argument('--credentials-file', type=Path)
    auth.add_argument('--username-file', type=Path)
    parser.add_argument('--password-file', type=Path)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    if args.token_file:
        token = args.token_file.read_text().strip().removeprefix('Bearer ').strip()
        session = asf_search.ASFSession().auth_with_token(token)
    elif args.username_file:
        if not args.password_file:
            raise SystemExit('--password-file required with --username-file')
        session = asf_search.ASFSession().auth_with_creds(args.username_file.read_text().strip(), args.password_file.read_text().strip())
    else:
        raw = args.credentials_file.read_text().strip()
        lines = [line for line in raw.splitlines() if line.strip()]
        if len(lines) == 1 and len(raw.split()) == 2:
            lines = raw.split()
        if raw.startswith('{'):
            value = json.loads(raw)
            lines = [value['username'], value['password']]
        if len(lines) != 2:
            raise SystemExit('Private credential file must contain exactly two lines.')
        session = asf_search.ASFSession().auth_with_creds(lines[0].strip(), lines[1])
    rows = json.loads((DATA / 'metadata/scenes.json').read_text())
    archive_dir = DATA / 'archives/scenes'
    archive_dir.mkdir(parents=True, exist_ok=True)
    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=2, min=2, max=30), reraise=True)
    def one(row):
        url = row.get('asf_download_url', row['download_url'])
        dest = archive_dir / url.rsplit('/', 1)[-1]
        if dest.exists():
            with zipfile.ZipFile(dest) as z:
                assert z.testzip() is None
            return row['published_id']
        if args.check_only:
            with session.get(url, headers={'Range': 'bytes=0-31'}, stream=True, timeout=60) as r:
                r.raise_for_status()
                assert next(r.iter_content(4))[:2] == b'PK'
            print(row['published_id'], 'authenticated archive accessible', flush=True)
            return row['published_id']
        part = dest.with_suffix('.zip.part')
        offset = part.stat().st_size if part.exists() else 0
        headers = {'Range': f'bytes={offset}-'} if offset else {}
        with session.get(url, headers=headers, stream=True, timeout=(30, 120)) as r:
            r.raise_for_status()
            append = offset > 0 and r.status_code == 206
            if append:
                assert r.headers.get('Content-Range', '').startswith(f'bytes {offset}-')
            with part.open('ab' if append else 'wb') as f:
                for chunk in r.iter_content(1024 * 1024):
                    f.write(chunk)
        with zipfile.ZipFile(part) as z:
            assert z.testzip() is None
        part.replace(dest)
        print(row['published_id'], 'archive verified', dest.stat().st_size, flush=True)
        return row['published_id']
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(one, rows))

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        # Redirect URLs may contain short-lived signed download credentials.
        # Keep them out of shared project logs.
        raise SystemExit('Scene acquisition stopped: ' + type(exc).__name__ + '. Partial downloads are preserved.') from None
