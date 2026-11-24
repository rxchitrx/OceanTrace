# OceanTrace

**Explainable oil-spill investigation from SAR imagery, environmental drift, and vessel trajectories.**

OceanTrace is the completed Phase 1 prototype for Smart India Hackathon problem statement **SIH26143**. It converts a suspected marine slick into a reproducible investigation workflow:

```text
SAR scene → dark-region detection → source reconstruction → AIS correlation → ranked leads
```

The system does **not** declare a vessel guilty. It ranks investigative leads and exposes the evidence, uncertainty, provenance, and data-quality limitations behind each score.

The repository contains the runnable Phase 1 app and a separate ANN/DL research track. Start with [Quick start](#quick-start) to run the demo or [Research datasets](#research-datasets) to work with training data.

## Phase 1 status

The internal-college demo path is implemented and verified.

| Capability | Status | Evidence in the prototype |
|---|---:|---|
| Pixel-based SAR candidate detection | Complete | Adaptive dark-region detector reads image pixels and returns GeoJSON |
| Real labelled validation asset | Complete | DARTIS `ow-0010`, original Pascal VOC annotation, CC BY 4.0 |
| Probabilistic source reconstruction | Complete | 180 deterministic wind/current/windage hypotheses |
| Independent forward validation | Complete | Source candidates are drifted forward and compared with the observed slick |
| AIS cleaning and gap handling | Complete | Validation, sorting, deduplication, short-gap interpolation, long-gap warnings |
| Explainable vessel ranking | Complete | Five visible evidence components and human-readable reasons |
| Investigation dashboard | Complete | Two case modes, map layers, timeline, lead selection, errors, provenance |
| Deterministic API and result retrieval | Complete | Fixed seed, generated JSON, arbitrary-seed and latest-result retrieval |
| Automated verification | Complete | Detector, drift, AIS, ranking, API, and golden-case tests |

Production deployment, authorised Indian AIS feeds, live Sentinel ingestion, and legal attribution are intentionally outside Phase 1.

## Demo cases

### 1. Arabian Sea controlled investigation

This is the complete end-to-end walkthrough. Its SAR raster, wind/current vectors, and three AIS tracks are explicitly synthetic so the source is known and the ranking can be tested.

The case is designed so that the vessel nearest the observed slick is not automatically the strongest lead. OceanTrace must reconstruct the earlier source area and compare vessel histories.

A reference run with seed `26143` produces:

| Output | Reference result |
|---|---:|
| Detector confidence | 79.4% |
| Ensemble hypotheses | 180 |
| Release window | 03:00–09:00 UTC |
| MV Ocean Star | 94.0 |
| MV Coastal Trader | 56.8 |
| MV Horizon | 9.8 |

These are controlled-case acceptance values, not real-world accuracy claims.

### 2. DARTIS real-SAR validation

This case runs detection only on the real Sentinel-1-derived DARTIS patch `ow-0010`. It deliberately has no AIS or forcing data and therefore performs no vessel ranking.

The bundled asset includes:

- The original 640 × 640 JPEG patch.
- Its original Pascal VOC XML annotation.
- A GeoJSON representation for map display.
- Source, citation, and licence details in [`ATTRIBUTION.md`](data/cases/dartis_validation/ATTRIBUTION.md).

The current detector obtains a best bounding-box IoU of `0.9647` against the two labelled oil objects. This is a one-patch engineering validation, not a dataset-wide benchmark.

## How it works

### 1. SAR detector

`services/api/detection/baseline_detector.py`:

1. Loads and median-filters the grayscale image.
2. Performs robust percentile normalization.
3. Estimates local background with Gaussian filters.
4. Builds an adaptive dark-region mask.
5. Applies morphological cleanup and connected-component analysis.
6. Scores candidates using contrast, coherence, size, elongation, and darkness.
7. Converts the strongest pixel bounding box into georeferenced GeoJSON.

The detector never receives the annotation during inference. For labelled cases, evaluation happens afterward through Pascal VOC bounding-box IoU.

### 2. Drift reconstruction

`services/api/drift/` uses velocities in metres per second and converts displacement to latitude/longitude using Earth geometry. The controlled run evaluates combinations of:

- Five release-time hypotheses.
- Three windage settings.
- Twelve uncertainty perturbations.

The 180-member ensemble produces weighted source points, probability regions, a release window, representative particle paths, and run diagnostics. Strong candidates are independently simulated forward to the satellite observation time.

### 3. AIS correlation

`services/api/ais/` validates vessel positions, groups tracks, interpolates only short gaps, preserves long gaps as warnings, and derives:

- Source-region distance and compatibility.
- Presence within the release window.
- Course and reconstructed-trajectory consistency.
- AIS coverage quality.

### 4. Evidence ranking

`services/api/ranking/` combines five transparent components:

```text
Source-region compatibility  35%
Release-window coverage      20%
Forward-drift consistency    25%
Trajectory/course match      10%
AIS data quality             10%
```

The final `0–100` value is a lead score, not a calibrated probability of responsibility.

## Architecture

```text
React + TypeScript + Leaflet
          │ JSON / GeoJSON
          ▼
       FastAPI
          │
  ┌───────┼────────┐
  ▼       ▼        ▼
 SAR    Drift     AIS
  └───────┼────────┘
          ▼
  Evidence ranking
          ▼
 generated/<case>-seed-<seed>.json
```

All case-critical rasters and inputs are local. Internet map tiles add geographic context but are not required for the SAR overlay or analysis.

## Repository structure

```text
apps/web/                 Investigation dashboard
services/api/             FastAPI routes, schemas, and orchestration
services/api/detection/   Pixel detector and annotation evaluation
services/api/drift/       Particle advection and source search
services/api/ais/         AIS cleaning, interpolation, and features
services/api/ranking/     Lead scoring and explanations
data/cases/               Small demo inputs tracked in Git
datasets.dvc              DVC manifest for the research dataset snapshot
datasets/                 Research data restored by DVC
models/                   Single-model SAR oil-spill training scripts (CBDNet, DeepLabv3+, OFCN, Shaban CNN+U-Net)
scene_matching/           SAR scene-matching pipeline, 3,605-patch WGS84 tables, leak-free split, visuals, and log
presentation/             HTML slide decks, PowerPoint deck, and SAR/AIS animations
docs/                     Project overview, research notes, and AIS/dataset audits
.dvc/config               Dataset remote configuration
scripts/                  Case validation, generation, and evaluation tools
tests/                    Unit, API, and golden-case verification
IMPLEMENTATION_PLAN.md    Phase 1 acceptance plan and completion record
```

## Quick start

### Requirements

- Python 3.11 or newer
- Node.js 20 or newer
- npm

### 1. Install the backend

Using `uv`:

```bash
uv venv
uv pip install --python .venv/bin/python -r requirements.txt
```

Or using standard Python:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 2. Install the frontend

```bash
cd apps/web
npm ci
cd ../..
```

### 3. Start the demo

Terminal 1:

```bash
.venv/bin/python -m uvicorn services.api.main:app --reload
```

Terminal 2:

```bash
cd apps/web
npm run dev
```

Open `http://127.0.0.1:5173`.

## Verification commands

Run all automated checks:

```bash
.venv/bin/python -m pytest -q
cd apps/web && npm run build
```

Validate the case bundles:

```bash
.venv/bin/python scripts/prepare_case.py arabian_sea_demo
.venv/bin/python scripts/prepare_case.py dartis_validation
```

Run the controlled analysis from the command line:

```bash
.venv/bin/python scripts/run_case.py
```

Evaluate the real DARTIS patch:

```bash
.venv/bin/python scripts/evaluate_detector.py --case dartis_validation
```

Generated results are written to `generated/`, which is intentionally ignored by Git.

## API

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/health` | Service status and version |
| GET | `/api/cases` | List available cases and analysis modes |
| GET | `/api/cases/{case_id}` | Manifest, layers, polygon, and AIS tracks |
| GET | `/api/cases/{case_id}/sar/image` | Local SAR image |
| GET | `/api/cases/{case_id}/sar/bounds` | Geographic image bounds |
| POST | `/api/cases/{case_id}/run` | Execute deterministic analysis |
| GET | `/api/cases/{case_id}/results/{run_id}` | Retrieve a generated result; `latest` is supported |

Example request:

```json
{
  "mode": "full",
  "seed": 26143,
  "use_cached_result": false
}
```

The DARTIS case returns `analysis_mode: "detection_only"` even when invoked through the same run endpoint.

## Demo sequence

1. Start with **Arabian Sea** and point out the synthetic-data labels.
2. Run the full analysis.
3. Show the reconstructed 03:00–09:00 release window and source region.
4. Compare the three AIS trajectories and their lead scores.
5. Open the top lead and explain each weighted component.
6. Select **Eastern Mediterranean Sea — DARTIS 2019**.
7. Run detector validation and show the real patch, annotation, and IoU.
8. Close on the visible limitation: investigative support, not legal attribution.

## Scientific, legal, and data boundaries

OceanTrace must not be presented as proving that:

- Every dark SAR formation is oil.
- One source point can always be recovered exactly.
- An AIS gap implies deliberate concealment.
- The highest-ranked vessel caused a spill.
- Performance on one DARTIS patch generalizes to all seas or sensors.

Real operational use would require broader scene-level validation, calibrated uncertainty, authorised AIS, archived environmental products, incident review, and independent corroborating evidence.

## Data provenance

- The Arabian Sea case is project-generated controlled data.
- DARTIS `ow-0010` is redistributed under CC BY 4.0 with its original annotation and attribution.
- No live or restricted Indian AIS data is included.

Before adding any new imagery, model, vessel feed, or environmental product, record its source, licence, timestamp, CRS, processing history, and whether it is real, simulated, or approximated.

## Licence

The project-code licence is not yet selected by the repository owners. The DARTIS asset retains its own CC BY 4.0 terms and attribution. Do not assume that the absence of a top-level code licence grants redistribution rights.

## Research datasets

The demo reads `data/cases/` and runs from a fresh Git clone after installing dependencies. Use `datasets/` for ANN/DL work. Git tracks [the DVC manifest](datasets.dvc), while the data files are restored from DagsHub or the project SSD.

| Location after restoration | What it contains |
|---|---|
| `datasets/SOS/archives/` | Image and mask ZIPs from the Refined SOS release, with the supplied split. |
| `datasets/SOS/patches/train/` | 6,455 extracted SAR image patches for training. |
| `datasets/SOS/patches/val/` | 1,615 held-out SAR image patches. |
| `datasets/SOS/metadata/`, `pilot/`, and `previews/` | Source metadata and retained sample and preview material. |
| `datasets/Preprocessing/sos-prepared/{train,val}/{images,masks}/` | Prepared image/mask pairs, organized by the supplied split. The parent preprocessing folder also contains audit reports and a pairing manifest. |
| `datasets/AIS/archives/` and `datasets/AIS/scene-matched/` | Retained NOAA AIS inputs, extracted position files, and coverage evidence. General AIS audits and examples are under `datasets/AIS/`. |
| `datasets/samples/` | An example SOS patch and a reference copy of the DARTIS tools. |

SOS combines 3,877 ALOS PALSAR and 4,193 Sentinel-1A patches. To use the supplied masks, pair each patch with the same split and filename in `masks.zip`. The prepared masks use a threshold of 128 and remain available for reproducing the earlier baseline. The supplied split has no verified patch-to-source-scene crosswalk, so report its results as patch-split performance. The 2020 AIS example is separate from the 2010 and 2017 SOS acquisitions.

### Restore from DagsHub

From the repository root, install DVC with S3 support. Use an authorized DagsHub token provided through your shell environment as both `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.

```sh
python3 -m pip install 'dvc[s3]==3.67.1'
dvc pull -r dagshub datasets.dvc
```

On the [public DagsHub mirror](https://dagshub.com/rxchitrx/OceanTrace), use **Files** on `main` to check that `datasets/SOS/patches` is indexed. Then use **Datasets → Add New Source → Choose from existing data**, select that repository folder, and name the source `sos-refined-patches`. Save `train/` and `val/` as separate dataset views. The source has one row per image. Pairing the masks is a separate step in the training loader. [DagsHub datasource guide](https://dagshub.com/docs/use_cases/data_engine/connect_datasource/)

### Models, scene matching, presentation, and docs

- [Models](models/README.md) provides setup, dataset verification, and single-model training scripts for CBDNet, DeepLabv3+, OFCN, and the Shaban CNN gate + U-Net comparison.
- [Scene matching](scene_matching/README.md) holds the SAR scene-matching & georeferencing pipeline, 3,605-patch WGS84 matches, leak-free `scene_disjoint_split.csv`, visual spot-checks, and [EXPERIMENT_LOG.md](scene_matching/EXPERIMENT_LOG.md).
- [Presentation](presentation/index.html) and [animations](presentation/animations/) explain the problem and workflow.
- [Project overview](docs/Project.md) and [docs](docs/) preserve acquisition details, preprocessing checks, AIS audits, and historical mapping notes.
