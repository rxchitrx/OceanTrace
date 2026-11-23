# OceanTrace research and preprocessing

This directory preserves the research notes, presentation, preprocessing evidence, and SOS provenance investigation. The existing application remains at the repository root. No neural model training is claimed here.

## Contents

- `Project.md` and `Research/`: decisions, source evidence, findings and limitations.
- `Presentation/index.html`: HTML presentation; accompanying local data must be restored for its data assets.
- `Animation/`: project illustrations.
- [`datasets/`](../../datasets.dvc): original archives, 8,070 patches, prepared image/mask pairs and AIS data (DVC).
- `datasets/samples/`: one example patch image and a reference snapshot of the third-party DARTIS repo (DVC).

## Restore data from the SSD

Git contains code, notes and the small `.dvc` manifests. The `ssd` remote stores the data in `/Volumes/APFS/OceanTrace-DVC/store` on the external SSD.

Install DVC, connect the SSD, and run these commands from the repository root:

```sh
python3 -m pip install 'dvc==3.67.1'
dvc cache dir --local /Volumes/APFS/OceanTrace-DVC/cache
dvc config --local cache.type reflink,copy
dvc pull -r ssd datasets.dvc
```

If the drive mounts elsewhere, set its path locally before pulling:

```sh
dvc remote modify --local ssd url /your/mount/OceanTrace-DVC/store
```

The cache is a working copy used by DVC; `store` is the DVC remote. Both are on the same SSD. Original research files were left in the vault. Virtual environments, Python caches, credentials, nested Git metadata, and unfinished download fragments are excluded.

## Restore data from DagsHub

The [public OceanTrace mirror](https://dagshub.com/rxchitrx/OceanTrace) stores DVC data for the research project. Run these commands from the repository root with an authorized DagsHub token supplied as both `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in your shell environment.

```sh
python3 -m pip install 'dvc[s3]==3.67.1'
dvc pull -r dagshub datasets.dvc
```

## Track training runs and models

Set `MLFLOW_TRACKING_URI` to `https://dagshub.com/rxchitrx/OceanTrace.mlflow`. Supply your DagsHub username and token through `MLFLOW_TRACKING_USERNAME` and `MLFLOW_TRACKING_PASSWORD`. Use the same server for run metrics, model artifacts, and registered models. [DagsHub MLflow setup](https://dagshub.com/docs/integration_guide/mlflow_tracking/)

## Reproduce and update

The executed preprocessing used Python 3.12.12 with NumPy, Pillow, rasterio and pyogrio. No Python environment is kept in the repository; recreate one separately if needed. Consult the session notes before running large downloads or jobs. Credentials are supplied privately at runtime.

After changing data, run `dvc add datasets`, then `dvc push -r ssd` and `dvc push -r dagshub`. Commit the changed `datasets.dvc` manifest along with the relevant code and notes.

## Status and limitations

- All 8,070 image/mask pairs were audited and prepared. Supplied masks use an explicit baseline threshold of 128; original masks are preserved.
- A 2026-11 search of all 8,070 patches against full-resolution source scenes produced 1,541 review candidates and 6,529 unresolved patches, with zero automatically accepted assignments. That mapping work was retired on 2026-11-06 and its outputs removed; no verified provenance crosswalk or scene-disjoint split exists.
- A real NOAA AIS day was audited and regional tracks extracted. This 2020 data is not paired with the 2010/2017 SOS scenes.
- PyTorch is the proposed training framework. The completed processing uses Python/NumPy/Pillow/OpenCV/rasterio; model training and final training splits remain future work.

Dataset source terms and attribution are recorded in the research notes. DVC storage does not grant additional rights to underlying third-party data.
