"""Run acquisition and the authorized 50-patch pilot; no secrets in saved outputs."""
import argparse
import concurrent.futures
import subprocess
import sys
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

def command(script, *args):
    subprocess.run([sys.executable, str(HERE / script), *args], check=True)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--username-file', required=True)
    p.add_argument('--password-file', required=True)
    args = p.parse_args()
    status = HERE.parents[1] / 'Data/SOS/pilot/status.json'
    status.write_text(json.dumps(dict(status='acquiring_full_source_rasters_and_patch_archive', selected_patches=50, attempted_real_matches=0), indent=2))
    def scenes():
        command('download_scenes.py', '--username-file', args.username_file, '--password-file', args.password_file)
        command('extract_scenes.py')
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        a = pool.submit(scenes)
        b = pool.submit(command, 'download_patches.py')
        b.result()
        command('prepare.py')
        a.result()
    # Refresh scene links now that full source products have been exported.
    command('prepare.py')
    command('match.py', '--controls')
    command('match.py')
