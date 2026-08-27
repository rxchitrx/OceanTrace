# OCEANTRACE

## Explainable oil-spill investigation from satellite imagery, ocean drift, and vessel trajectories

OCEANTRACE is a software prototype for investigating suspected oil spills at sea. It combines satellite imagery, environmental drift data, and AIS vessel trajectories to produce:

1. A candidate slick detection.
2. A probable source region and release-time window.
3. A ranked list of vessels that are compatible with the evidence.
4. An explanation of why each vessel was ranked where it was.

OCEANTRACE is being developed for SIH26143, the Smart India Hackathon problem statement:

> Leveraging satellite imagery to determine oil spills at sea along with AIS data correlations to identify the vessel responsible for the spill.

The prototype is designed for maritime and environmental investigation support. It produces investigative leads; it does not establish legal responsibility.

## Why this project matters

Oil slicks are difficult to interpret from a single image. A dark region in Synthetic Aperture Radar (SAR) imagery may be oil, but it may also be a low-wind area, biogenic film, rain cell, current front, ship wake, wave shadow, or another look-alike.

Even when a slick is genuine, the nearest vessel is not automatically the likely source. Wind, currents, release time, AIS coverage, and the vessel's previous trajectory must be considered together.

OCEANTRACE follows this investigation workflow:

```text
SEE → VERIFY → TRACE → CORRELATE → RANK
```

## Phase 1 prototype

The internal college-phase prototype is intentionally focused on one reliable end-to-end case:

```text
Preloaded SAR scene
        ↓
Candidate slick detection
        ↓
Wind/current particle simulation
        ↓
Probable source-region heatmap
        ↓
Three vessel trajectories
        ↓
Explainable evidence ranking
        ↓
Investigator dashboard
```

### Planned demonstration cases

#### End-to-end controlled case

A controlled Arabian Sea or Indian-coast scenario containing:

- A preloaded SAR image or SAR-derived raster.
- A candidate spill polygon.
- An archived wind/current snapshot.
- Three AIS vessel trajectories.
- One simulated source vessel.
- At least one nearby but incorrect vessel.
- A release-time window with known ground truth for evaluation.

The UI will explicitly identify simulated AIS data and will never present the result as proof of guilt.

#### Detection validation case

A public labelled SAR example, such as DARTIS or the CSIRO Sentinel-1 dataset, will be used to demonstrate oil/look-alike detection and report baseline metrics.

## Core capabilities

### 1. Candidate slick detection

The first detector will be an explainable baseline:

- SAR intensity normalization.
- Noise reduction.
- Sea and border masking.
- Dark-region candidate extraction.
- Connected-component filtering.
- Geometry and texture feature extraction.
- Candidate slick score.

This baseline is deliberately useful for debugging and reproducibility. A CNN or U-Net segmentation model can be added after the complete workflow is stable.

### 2. Probabilistic source reconstruction

The drift engine will generate source hypotheses across a location and time grid. Each hypothesis will be forward-simulated to the observed satellite time using:

- Ocean-current velocity.
- Wind velocity and windage.
- Diffusion or controlled perturbations.
- Multiple release-time hypotheses.

The resulting source map will show a high-, medium-, and low-probability region. The system will not claim that a single exact source point can always be recovered.

### 3. AIS trajectory correlation

AIS processing will:

- Validate coordinates and timestamps.
- Sort positions by vessel.
- Remove impossible records.
- Interpolate only short gaps.
- Flag long gaps.
- Measure source-region overlap.
- Measure compatibility with the release window.
- Compare vessel trajectory and drift direction.

An AIS gap will be reported as a data-quality limitation, not as proof of deliberate concealment.

### 4. Explainable vessel ranking

The first ranking model will be a transparent weighted score:

```text
Source-region overlap       35%
Release-time compatibility  20%
Forward-drift consistency   25%
Trajectory/heading match    10%
AIS data quality            10%
```

The output is a lead score, not a calibrated attribution probability.

Example explanation:

```text
✓ Track intersects the high-probability source region
✓ Vessel was present during the estimated release window
✓ Forward simulation reproduces the observed slick direction
✓ AIS coverage is adequate
⚠ A 2-hour AIS gap overlaps part of the release window
```

## Proposed architecture

```text
React + TypeScript dashboard
              │
              ▼
          FastAPI API
              │
     ┌────────┼────────┐
     ▼        ▼        ▼
   SAR      Drift      AIS
 detector   engine   processor
     └────────┼────────┘
              ▼
       Evidence engine
              ▼
     Results as JSON/GeoJSON
```

### Technology choices

| Layer | Phase 1 choice |
|---|---|
| Frontend | React, TypeScript, Vite |
| Mapping | Leaflet with GeoJSON overlays |
| Backend | Python and FastAPI |
| Geospatial processing | GeoPandas, Shapely, PyProj |
| Numerical processing | NumPy, Pandas, SciPy |
| Raster processing | Rasterio and OpenCV/scikit-image |
| Storage | Local case files and SQLite if needed |
| Drift model | Local particle simulator, with an OpenDrift adapter later |
| Testing | Pytest plus deterministic golden-case tests |

PostGIS, authentication, cloud deployment, and microservices are intentionally out of scope for the internal prototype.

## Planned repository structure

```text
apps/web/                 React dashboard
services/api/             FastAPI application
services/api/detection/   SAR candidate detection
services/api/drift/       Particle simulation and source search
services/api/ais/         AIS cleaning and trajectory processing
services/api/ranking/     Evidence scoring and explanations
data/cases/               Reproducible demo cases
scripts/                  Data preparation and evaluation commands
tests/                    Unit and end-to-end golden-case tests
IMPLEMENTATION_PLAN.md    Detailed build plan
```

## Data and provenance

Potential data sources include:

- DARTIS for accessible oil-slick and look-alike examples.
- CSIRO Sentinel-1 imagery chips for practical baseline testing.
- Copernicus Sentinel-1 catalogue and products for future ingestion.
- ERA5 historical wind fields.
- Copernicus Marine or INCOIS current products.
- Global Fishing Watch for vessel-presence context where appropriate.
- Authorised Indian AIS data as a future integration.

Live satellite downloads and unrestricted historical Indian AIS are not Phase 1 dependencies. The demo will run from a complete, versioned local case so a network failure cannot break the presentation.

Every case should record:

- Data source and licence.
- Acquisition or observation time.
- Coordinate reference system.
- Processing version.
- Whether the data is real, simulated, or approximated.
- Known limitations.

## Running status

This repository currently contains the project documentation and implementation plan. The application code will be added incrementally, beginning with the dependency gate described in [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md).

## Scientific and legal boundaries

OCEANTRACE must not claim that:

- Every dark SAR patch is oil.
- A source point can always be reconstructed exactly.
- An AIS gap proves intentional concealment.
- The top-ranked vessel is legally responsible.
- One dataset score represents global performance.
- The SAR + AIS + drift combination is unprecedented.

The correct wording is:

> OCEANTRACE ranks vessels as investigative leads using uncertainty-aware, explainable evidence fusion.

## Evaluation plan

### Slick detection

- Precision.
- Recall.
- F1 score.
- Intersection over Union.
- Look-alike false-positive rate.
- Scene-level performance.

### Source reconstruction

- True-source containment in the predicted region.
- Distance from the true source to the predicted centroid.
- Release-time error.
- Ensemble coverage.
- Sensitivity to wind/current perturbations.

### Vessel ranking

- Top-1 accuracy on controlled cases.
- Top-3 recall.
- Mean reciprocal rank.
- True-vessel versus distractor score gap.
- False-attribution rate.

All validation splits should be by scene, incident, or region where possible, not random pixels from the same scene.

## Demo narrative

1. Select the controlled case.
2. Show the SAR image and candidate slick overlay.
3. Run source reconstruction.
4. Show the source heatmap and release-time window.
5. Display the three vessel tracks.
6. Compare the nearest vessel with the evidence-ranked lead.
7. Open the top candidate and show the score breakdown.
8. Show uncertainty and AIS-quality warnings.
9. Explain that the output is an investigative lead, not legal proof.

## Research references

- [SIH26143 problem statement](https://raw.githubusercontent.com/vedantchalke36/sih-2026-problem-statements/main/ps_2026/SIH26143.md)
- [Brekke and Solberg, satellite oil-spill detection](https://doi.org/10.1016/j.rse.2004.11.015)
- [Topouzelis, SAR dark formation detection](https://doi.org/10.3390/s8106642)
- [Krestenitis et al., deep neural-network detection](https://doi.org/10.3390/rs11151762)
- [Dagestad et al., OpenDrift](https://gmd.copernicus.org/articles/11/1405/2018/)
- [Longépé et al., SAR + AIS + forward drift](https://doi.org/10.1016/j.marpolbul.2015.08.006)
- [Liu et al., vessel discharge tracing](https://doi.org/10.1016/j.ocecoaman.2021.105783)
- [Luo et al., multi-source ship tracing](https://doi.org/10.1016/j.marpolbul.2024.116808)
- [EMSA CleanSeaNet](https://www.emsa.europa.eu/csn-menu.html)
- [INCOIS Online Oil Spill Advisory System](https://oosa.incois.gov.in/OOSA/)

## License and contribution policy

The repository licence and contribution policy are to be finalized by the project owners. Before adding external datasets, models, code, or imagery, verify that their licences permit the intended use and redistribution.

Contributors should:

- Keep changes focused.
- Preserve provenance for every data asset.
- Add tests for scoring and geospatial calculations.
- Avoid unsupported scientific or legal claims.
- Document whether outputs are real, simulated, or approximated.
