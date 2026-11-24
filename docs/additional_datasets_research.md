# External SAR Oil-Spill & Trajectory Datasets

Curated survey of external SAR oil-spill, hard-negative, and vessel-trajectory datasets evaluated for OceanTrace, with verified formats, sizes, and licenses.

## SAR Oil-Spill Datasets

| Dataset | Sensor & Coverage | Size & Annotations | License / Access | Best Role in OceanTrace |
|---|---|---|---|---|
| **[Refined Deep-SAR SOS](https://zenodo.org/records/15298010)** | ALOS PALSAR (GoM 2010) + Sentinel-1A (Persian Gulf 2017) | 8,070 `256×256` chips + binary masks | CC BY 4.0 (open) | Primary training baseline. Official split leaks 19/20 scenes; use `scene_matching/outputs/scene_disjoint_split.csv` for leak-free evaluation. |
| **[Cantarell (2020)](https://zenodo.org/records/22728926)** ([GitHub](https://github.com/Garcia-INPE/oilspill-detection-dataset)) | Sentinel-1 C-band, Bay of Campeche (Jan–Sep 2020) | 173 `800×600` georeferenced tiles, binary masks + 385 polygons (327 spills, 58 seeps), 24 distinct Sentinel-1 acquisitions | CC BY 4.0 (open) | Best small, acquisition-grouped pixel-mask dataset for transfer testing. Keep spill vs. natural seep labels distinct. |
| **[DARTIS (2019)](https://doi.pangaea.de/10.1594/PANGAEA.980773)** ([ESSD paper](https://essd.copernicus.org/articles/17/6807/2025/)) | Sentinel-1A/B IW VV, Eastern Mediterranean (2019) | 3,655 `640×640` JPGs: 1,365 oil (3,225 objects) + 2,290 no-oil; **Pascal VOC XML boxes** (no pixel masks) + full SAFE product IDs & timestamps | CC BY 4.0 (open) | Cross-region object-detection & hard-negative (false-alarm) evaluation with clean scene-disjoint grouping. |
| **[Zenodo Sentinel-1 Parts I–III](https://zenodo.org/records/8346860)** ([Part II](https://zenodo.org/records/8253899), [Part III](https://zenodo.org/records/13761290)) | Sentinel-1 VV/VH Sigma0 dB (global, NOAA + EMSA CleanSeaNet) | 3,020 `2048×2048×2` GeoTIFFs (~96.5 GB total): 1,200 oil, 1,370 look-alike/no-oil, 450 test + binary masks | CC BY 4.0 (open) | Large external dual-pol test set (especially Part III, 9.9 GB). Verify scene disjointness from TIFF metadata before claiming independent acquisitions. |
| **[QPOSD (2026)](https://zenodo.org/records/19258036)** ([paper](https://doi.org/10.1016/j.dib.2026.112773)) | UAVSAR L-band quad-pol, Gulf of Mexico (2010–2022) | 41 scenes, 9-channel coherence matrix, 4-class masks (oil, look-alike, sea, land), 3.87 GB | CC BY 4.0 (open) | Future polarimetric / cross-sensor robustness benchmark; not drop-in with single/dual-pol models. |
| **[GlobalOSD-SAR](https://zenodo.org/records/15286918)** | Sentinel-1 global (2014–2020) | 100,329 positives + 100,134 negatives as **shapefiles only** (~89 MB, no imagery) | CC BY 4.0 (open) | Event/coordinate manifest for fetching original Sentinel-1 scenes and mining hard negatives. |
| **[CERTH / M4D](https://m4d.iti.gr/oil-spill-detection-dataset/)** | Sentinel-1 (2015–2017) | ~1,000 train + 110 test, 5-class masks (~400 MB) | Gated (requires supervisor institutional request) | Skip unless formal academic access is requested and approved. |

## AIS, Incident & Drift Resources

- **[NOAA Marine Cadastre AIS](https://marinecadastre.gov/ais/):** Primary source for real U.S. vessel trajectories (2010 GoM `.gdb` for DWH matching; 2020+ daily CSVs for LSTM gap-imputation benchmarks).
- **[NOAA IncidentNews (`incidents.csv`)](https://incidentnews.noaa.gov/raw/index):** ~3 MB public CSV of NOAA-supported spill incidents (e.g., DWH record `#8220`); useful as an event index, though dates may reflect notification rather than exact release time.
- **[NOAA WebGNOME](https://gnome.orr.noaa.gov/doc/introduction.html):** Open oil-spill trajectory/fate modeling tool for comparing physical drift mechanics (modeled trajectories, not observed ground truth).
- **[EnvShip-Voyage](https://huggingface.co/datasets/mark000071/Ship_trajectory_interpolation) & [EnvShip-Bench](https://huggingface.co/datasets/mark000071/EnvShip-Bench_An_Environment-Enhanced_Benchmark_for_Short-Term_Vessel_Trajectory_Prediction):** Ready-made AIS trajectory imputation/forecasting datasets on Hugging Face, but both currently lack explicit license declarations — verify terms before adopting.
