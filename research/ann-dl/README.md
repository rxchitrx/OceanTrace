# OceanTrace research and preprocessing

This directory preserves the research notes, presentation, acquisition scripts, preprocessing, and SOS provenance investigation. The existing application remains at the repository root. No neural model training is claimed here.

## Contents

- `Project.md` and `Sessions/`: decisions, source evidence, findings and limitations.
- `Presentation/index.html`: HTML presentation; accompanying local data must be restored for its data assets.
- `Animation/`: project illustrations.
- `Tools/sos-pilot/`: acquisition, dataset audit, model input preparation and AIS audit scripts.
- `Tools/sos-mapping/indexed.py`: executed full-corpus matcher; `verify_results.py` checks its results. `run.py` is an earlier unvalidated draft.
- `Data/`: original archives, full SAR scenes, 8,070 patches, prepared image/mask pairs, AIS data, mapping evidence and reports (DVC).
- `data_samples/`: initial samples and third-party dataset reference material (DVC).

## Restore data from the SSD

Git contains code, notes and the small `.dvc` manifests. The actual datasets are stored in `/Volumes/APFS/OceanTrace-DVC/store` on the external SSD. This local remote is not a cloud backup and is unavailable without that SSD.

Install DVC, connect the SSD, and run these commands from this directory:

```sh
python3 -m pip install 'dvc==3.67.1'
dvc cache dir --local /Volumes/APFS/OceanTrace-DVC/cache
dvc config --local cache.type reflink,copy
dvc pull
```

If the drive mounts elsewhere, set its path locally before pulling:

```sh
dvc remote modify --local ssd url /your/mount/OceanTrace-DVC/store
```

The cache is a working copy used by DVC; `store` is the DVC remote. Both are on the same SSD. Original research files were left in the vault. Virtual environments, Python caches, credentials, nested Git metadata, and unfinished download fragments are excluded.

## Reproduce and update

The executed preprocessing environment used Python 3.12.12. Recreate it separately using `Tools/sos-pilot/requirements.txt`; do not commit virtual environments. Consult the scripts and session notes before running large downloads or matching jobs. Credentials are supplied privately at runtime.

After changing data, run `dvc add Data data_samples`, then `dvc push`. Commit the changed `.dvc` manifests along with the relevant code and notes.

## Status and limitations

- All 8,070 image/mask pairs were audited and prepared. Supplied masks use an explicit baseline threshold of 128; original masks are preserved.
- All 8,070 patches were searched against compatible full-resolution source scenes. There are 1,541 review candidates and 6,529 unresolved patches, with zero automatically accepted scene assignments. Candidate results are not a verified provenance crosswalk or a scene-disjoint split.
- A real NOAA AIS day was audited and regional tracks extracted. This 2020 data is not paired with the 2010/2017 SOS scenes.
- PyTorch is the proposed training framework. The completed processing uses Python/NumPy/Pillow/OpenCV/rasterio; model training and final training splits remain future work.

Dataset source terms and attribution are recorded in the research notes. DVC storage does not grant additional rights to underlying third-party data.
