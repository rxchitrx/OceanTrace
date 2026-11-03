# Additional datasets deep search — OceanTrace

**Date:** 2026-11-03  
**Participants:** User (task owner); Codex research sub-agent  
**Source:** User-requested exhaustive public-web research, plus current vault claims in `Project.md`, `Wayfinding/OceanTrace - ANN-DL implementation spec.md`, `Wayfinding/Assets/Dataset Profile - OceanTrace.md`, and `Wayfinding/Tickets/Survey scene-split SAR datasets and recover the SOS mapping.md`.  
**Scope:** Find usable oil-spill SAR masks/negatives/provenance, vessel AIS trajectory data, and evidence useful for co-located spill/AIS/metocean or drift validation. No bulk data were downloaded; no account or author contact was made.

## Follow-up verification — 2026-11-03
The independent [[College projects/OceanTrace/Sessions/2026-11-03 - Cantarell acquisition group verification|Cantarell audit]] supersedes the unresolved grouping caveat below: all 173 sample IDs are unique; manifests contain 16/4/4 source groups across 108/43/22 tiles, matched to 24 distinct Sentinel-1 SAFE acquisitions with no cross-split overlap. The earlier train group list below was incomplete. Catalogue matching supports acquisition separation; archive pixel lineage is not independently proven. Binary masks combine oil spills and natural seeps as SLICK.

## Executive finding

The strongest immediately useful addition is the **Cantarell Sentinel-1 oil spill/seep segmentation dataset**: 173 image/mask tiles (800×600), 8/16-bit georeferenced rasters, vector polygons, per-tile manifests, and train/validation/test grouping by source image, archived under CC BY 4.0. Its explicit source-image grouping enables a defensible internal holdout, subject to validating that the source-image grouping corresponds to acquisition scenes in the current archive. It is a promising compatible data addition after radiometry/label harmonization, but its positive class combines anthropogenic spills and natural seepage.

For the broader external test, **DARTIS is a substantial, genuinely open object-level hard-negative and scene-provenance resource**, but it provides boxes/XML, not oil pixel masks. A scene-disjoint evaluation can be created from its product IDs/acquisition times, while reporting detection metrics rather than pixel IoU.

The three Zenodo Sentinel-1 Parts I–III remain the most directly usable dual-pol pixel-mask corpus with positive, look-alike, and no-oil examples. However, the prior note overstated what its metadata establishes: neither the record pages nor paper-derived evidence reviewed here establishes that Part III is scene-disjoint from Parts I–II, gives a 685-scene count, or provides source-scene IDs in the packaged test labels. It is a separate test part, not a verified scene-held-out benchmark. The complete archive is ~96.5 GB, not a small sprint dataset.

Other high-value, newer candidates:

- **QPOSD**: 41 UAVSAR L-band fully polarimetric scenes from the Gulf of Mexico, four-class pixel masks (oil, look-alike, sea, land), 3.87 GB archive, CC BY 4.0. It is strong external-test/pretraining material but has a different sensor and nine-channel polarimetric representation. The Zenodo API identifies current version DOI `10.5281/zenodo.19258036`, parent concept `10.5281/zenodo.18143758`; the paper and record are recent, so confirm archive contents/split protocol before adopting.
- **GlobalOSD-SAR**: 100,329 positives and 100,134 negatives from Sentinel-1 (2014–2020), CC BY 4.0; the Zenodo archive inspected contains shapefile components (~89 MB), not imagery. It records coordinates, acquisition date, and source type (natural seep, platform, ship). Useful as a candidate/crop index and provenance-rich external weak-label resource after matching/download of original scenes; not a segmentation dataset.

## What I inspected

- Read vault `AGENTS.md`, `SOUL.md`, Project Ideas Index, OceanTrace `Project.md`, the implementation spec, dataset profile, and the scene-split/SOS mapping ticket. These are historical/current project context, not primary-source proof.
- Opened primary source pages for Zenodo Parts I–III, DARTIS PANGAEA/ESSD, CERTH/M4D, NOAA IncidentNews, NOAA WebGNOME, and the Cantarell GitHub dataset and its dataset card/split CSV manifests.
- Queried Zenodo REST API metadata (HTTP 200) for SOS, all Sentinel-1 Parts I–III, GlobalOSD-SAR, QPOSD, and Cantarell records to inspect exact license identifiers, archive names, and byte sizes. I did not download any dataset archive.
- Read Cantarell train/val/test manifests remotely (small CSVs) and compared the sample group IDs across splits. All tiles with the same `IMG_XX` prefix stay in one split: train uses IMG_01/02/04/05, validation IMG_12/13/15/19, test IMG_07/17/20/26. The project card describes these as acquisition/source-image groups. The full scene-to-Sentinel product mapping was not verified in the files inspected.
- Read current small nearby-vessel dataset cards (EnvShip-Voyage and EnvShip-Bench) and NOAA incident catalogue fields. No raw AIS or SAR archive was downloaded.

## Corrections to prior claims

### Refined Deep-SAR SOS scene mapping

The examined Zenodo record contains the anonymous chip release already described in the prior profile; no acquisition/product IDs, date, coordinates, or parent-scene mapping were found in the record. The original CBD-Net publication/repository and original SOS distribution were not exhaustively re-downloaded in this session, so I cannot independently prove universal impossibility across every public mirror. Best-supported conclusion remains: **no public mapping is currently identified; scene-held-out splitting from Refined SOS alone is unsupported.** Do not claim an 80:20 “scene split.” A fresh, purpose-built recovery crawl would need to examine every original repo/supplement and mirror archive before stating “impossible from all public artifacts.”

### CERTH/M4D dataset gate — confirmed

The official M4D page confirms Sentinel-1 images and masks; about 1,000 train and 110 test images; five classes; around 400 MB; and collection dates 2015-09-28 through 2017-10-31. It explicitly requires reading terms, sending a project abstract with an institutional email, and for undergraduate/postgraduate students, the supervisor must submit and name the student; they cannot collaborate with researchers without a full-time academic contract. Thus the access gate is real. The page calls it “specific terms of use”; it is not an open download. It is not appropriate to treat “college noncommercial” as satisfying those terms automatically. The official page does not establish a scene-disjoint split, parent scene IDs, or an open license. Its mask task is multi-class pixel labels, but reproducing it is contingent on an access agreement.

### Sentinel-1 SAR Oil Spill Parts I–III — verified, with key caveat

Official Zenodo record descriptions confirm:

- **Part I**: 1,200 2048×2048×2 VV/VH Sigma0-in-dB GeoTIFF image/mask pairs, oil-positive set. Image archive 40.7 GB; mask archive 6.2 MB.
- **Part II**: 685 look-alike and 685 no-oil images, also with masks marked entirely background (look-alike is not delineated as a separate pixel class). Image archives 23.0 GB + 22.9 GB; mask archives ~426.8 kB + ~416.7 kB.
- **Part III**: test part with 150 oil, 150 look-alike, 150 no-oil images and corresponding masks; 2048×2048×2 VV/VH; single archive 9.9 GB.
- **Combined nominal count**: 3,020 images across all three parts (1,200 + 1,370 + 450). This replaces the prior 2,850 count.
- **Total listed archive size**: 96,504,749,181 bytes (~96.5 GB decimal) compressed; this is too large for a casual “download all” plan.
- The Zenodo pages label files georeferenced but state explicitly that masks are not georeferenced. The public record descriptions do not expose a scene-ID manifest or prove any source scene disjointness between parts. A separate Part III record and test designation are not sufficient to establish independent acquisitions.
- The prior “685 full Sentinel-1 scenes” claim is unsupported by the Zenodo records and should be removed unless a paper/supplement directly substantiates it. A paper may mention this corpus but the inspected records do not provide that count.
- The live Zenodo REST API metadata explicitly returns `cc-by-4.0` for Parts I–III (verified 2026-11-03).
- Scene/acquisition dates and IDs can potentially be recovered from georeferenced image TIFF metadata or original source manifests, but the archive is large and no archive content was downloaded here. Treat that as an open check, not established fact.

### DARTIS — boxes, no mask

The ESSD data descriptor makes the annotation type clear: oil objects are Pascal VOC XML object boxes; no-oil images have no object annotations. It specifically positions DARTIS as object-based coarse detection, with boxes and product/geographic metadata. There is no pixel-level oil segmentation mask release. Do not call the XML annotations masks or list DARTIS as a segmentation-label set. The dataset is a strong object-detection/hard-negative and provenance resource.

The 2025 ESSD article and PANGAEA record give **1,365 oil patches / 3,225 oil objects and 2,290 no-oil patches**, totaling 3,655 patches. Older ESSD article body text says 2,990 no-oil; its Table 1 and PANGAEA’s deposited record agree on 2,290, so 2,990 is likely a prose typo, but use the dataset record count and flag the paper inconsistency.

PANGAEA provides a data table of acquisition product IDs, acquisition start/stop, patch corner coordinates, and patch names; the article explains these support retrieval of the original products. Whole-product grouping is therefore feasible. The paper says two interpreters jointly inspected the 2019 Sentinel-1 coverage, labeling only dark forms they both agreed were oil; it acknowledges possible non-petroleum chemical slicks and no independent chemical confirmation. Treat labels as expert SAR interpretation with supporting incident context, not chemical truth. No direct evidence that its images are same scenes as other sets, but they are 2019 Eastern Mediterranean Sentinel-1 VV; screen by product ID/date/geography if combining with any overlapping archive.

## Ranked practical shortlist

### 1. Refined SOS + Cantarell — compatible mask training (with different caveats)

- **Refined Deep-SAR SOS 2025**: Zenodo 10.5281/zenodo.15298010; reported CC BY 4.0; 8,070 256×256 chips and masks (6,455 train/1,615 validation) from Sentinel-1 + ALOS PALSAR; 8-bit RGB encodings; Deepwater Horizon Gulf of Mexico and Persian Gulf sources are reported in the prior CBD-Net evidence, but source-chip IDs are missing. Best simple starting supervision, but mixed sensors, no reliable parent-scene split, and sampled masks may need binarization/quality audit.
- **Cantarell 2026**: DOI 10.5281/zenodo.22214144 (current Zenodo version 10.5281/zenodo.22728926); CC BY 4.0. 173 Sentinel-1 C-band tiles, each 800×600, binary masks; 385 labeled polygons (327 spills, 58 natural seeps), 8-/16-bit georeferenced rasters and vector overlays. January–September 2020, Cantarell/Gulf of Mexico. Explicit train/val/test manifests 108/43/22 tiles grouped by source-image ID, and all tiles for a given `IMG_XX` are in only one split. Split is useful but tiny; verify `IMG_XX` to product ID mapping and whether each ID maps 1:1 to a full acquisition before calling it scene-disjoint. Positive class deliberately conflates spill/seep, so keep a label-source/uncertainty field or restrict labels by polygon class where credible. Sentinel-1 modality and pixel masks make it a plausible supplementary segmentation training source after radiometry/scale/mask harmonization; its 800×600/16-bit TIFF pipeline is not drop-in with SOS 256 RGB chips.
- This is the best practical merge candidate found, but merge only after checking scene-level overlap and preserving spill-vs-seep classes; do not silently label seeps as anthropogenic oil spills.

### 2. DARTIS — external scene-grouped object detection and hard negatives

- PANGAEA DOI 10.1594/PANGAEA.980773; ESSD article DOI 10.5194/essd-17-6807-2025; code DOI 10.5281/zenodo.17789853; CC BY 4.0 (record/article).
- 3,655 8-bit JPG patches, nominal 640×640 (some larger to preserve objects), Sentinel-1A/B GRD IW VV, Eastern Mediterranean in 2019. 1,365 oil patches / 3,225 object boxes; 2,290 no-oil patches. No-oil subgroup metadata derived from K-means is a heuristic category grouping; a patch may contain more than one phenomenon and subgroup is not a confirmed unique cause. No-oil patches have no masks/boxes.
- Distinct strengths: product ID, acquisition time, coordinates, scene-based split potential; positives plus real dark-signature negatives; article offers detailed interpretation of SAR look-alikes. Access is through PANGAEA tables and code/Zenodo links; the image files/access packaging should be checked before assuming a convenient single download (record page gives `data points`, not archive byte size).
- Role: cross-region Sentinel-1 object-detection test, false-alarm stress test, or background examples. Not pixel-IoU test. Screen product IDs for complete-scene grouping and any overlap with patches duplicated in other dataset archives.

### 3. Trujillo-Acatitla Parts I–III — pixel-mask source and balanced test, with provenance caveat

- Exact counts, file sizes, channels, and mask semantics above. Sentinel-1 VV/VH georeferenced input + binary oil foreground masks; test contains oil/look-alike/no-oil categories. Article describes labels tied to spill reports from NOAA and EMSA CleanSeaNet, but these are not ground truth for every pixel edge. In no-oil/look-alike set, all pixels map to non-oil mask; therefore cannot score explicit look-alike segmentation class.
- CC BY 4.0 is reported by secondary HF metadata; verify license in the Zenodo record API/rights before use. Open Zenodo download pages require no login, but the full archive is large.
- Role: potentially good independent-source test once source scene disjointness and archive acquisition IDs are verified. Until then call it “held-out Part III dataset evaluation,” not scene-disjoint generalization.

### 4. QPOSD — high-value external test/pretraining, modality-incompatible with current dual-pol model

- Zenodo record DOI 10.5281/zenodo.19258036; parent/concept 10.5281/zenodo.18143758; metadata API returns CC BY 4.0 and a 3,871,940,048-byte `QPOSD.zip` plus two small example scripts.
- Author record/paper claim 41 UAVSAR L-band quad-pol scenes, Gulf of Mexico, 2010–2022; per-scene 9-channel real-valued polarimetric coherence matrix representation; pixel-level classes sea, oil, look-alike, land (>80 million labelled pixels), spatial resolution ~6×4 m. Label workflow combines manual labels, Random Forest label propagation, and manual refinement. The resulting labels are not equivalent to independently manual-validated spill boundaries throughout; inspect article methods and masks before making strong ground-truth claims.
- No train/val/test split or scene-disjoint protocol verified from the visible metadata. Scripts are openly listed; archive is 3.87 GB and no full archive was downloaded. Confirm version/record and inspect README/file inventory before use. The journal source gives DOI 10.1016/j.dib.2026.112773. One Zenodo concept/version DOI discrepancy is normal versioning, not a duplicate dataset.
- Role: separate external domain/polarimetric robustness benchmark or pretraining only. Not merge-compatible with single-channel SOS or dual-pol Sentinel inputs without a deliberately multimodal model.

### 5. CERTH/M4D — technically strong masks but gated

- Official M4D page confirms ~1,000 train/110 test, ~400 MB, Sentinel-1, 5-class masks and EMSA CleanSeaNet-derived incident selection, but access requires a formal institutional request and supervisor involvement for students. No license or scene-disjoint test identity is exposed on the public page. Research-only terms are not self-granted by student status.
- Role: pursue only if the supervisor is willing to review and accept the official terms; otherwise not part of sprint shortlist. Do not redistribute or train without granted access.

## Wider SAR inventory and roles

| Candidate | What it really provides | Role / limitation |
|---|---|---|
| **GlobalOSD-SAR** (Zenodo 10.5281/zenodo.15286918; parent 10.5281/zenodo.15286917; CC BY 4.0) | 100,329 positives + 100,134 lookalikes (author record); point/polygon shapefile pairs only, ~89 MB total by API file list; coordinates/date/source labels (natural seep/platform/ship). | Excellent provenance-rich crop manifest for Sentinel-1 archive retrieval, event/source-type analysis, and hard-negative mining; not imagery or masks. The record does not establish a train/test split or define negative taxonomy in enough detail; scene-level overlap control must be constructed by acquisition date/product after original scenes are fetched. Do not count it as 200k image chips. |
| **CSIRO Sentinel-1 oil/non-oil** | Reported 5,630 400×400 VV grayscale patches (1,905 oil, 3,725 non-oil); no pixel masks, coordinates/product IDs/split metadata not verified from a primary dataset artifact. | Classification/pretraining/hard negatives only if primary source and license/access are established. Recent paper reuses it but no authoritative data landing page verified here. |
| **Najoui Gulf of Guinea/Envisat** (ESSD 2022; Zenodo 10.5281/zenodo.6470470; 10.5281/zenodo.6907743) | ~18,063 interpreted slick locations from 3,644 Envisat ASAR scenes (2002–2012), plus a 100-georeferenced-spill subset. Includes natural seeps and anthropogenic spills; geospatial points/polygons, not pixel masks. | External location/source-occurrence study; useful for SAR scene retrieval or regional context. Different C-band legacy sensor, no verified pixel segmentation or AIS co-location. Reuse labels conservatively and maintain seep/spill distinction. |
| **NOAA SAR wind products** | Sentinel-1-derived high-resolution wind, netCDF/GeoTIFF with acquisition time/location, open NOAA NCEI catalogue. | Scene-level wind/metocean context and SAR environmental covariate; not oil labels. Verify coverage and product availability for matched spill times. |
| **Other user-uploaded Kaggle/HF mirrors** | Often copies/rehosts SOS, Parts I–III, or M4D; some metadata cards claim masks/license absent upstream. | Deduplicate by source hashes/DOI/filenames; do not treat rehosting as new labels, a new license, or evidence of parent-scene mapping. |

## AIS and drift additions

### Practical direct AIS track data

- **NOAA Marine Cadastre AIS** remains the best self-built 15/30/60-minute missing-segment benchmark candidate: raw individual-vessel timestamps and positions, but very large year archives. Pick a small coastal geography/time window near a chosen SAR event; avoid downloading annual archives unnecessarily. USCG redistribution terms/NOAA caveat in the earlier Dataset Profile still need to be honored; “generally public domain” is not blanket permission to redistribute raw AIS.
- **DMA AIS** is source material for research trajectory benchmarks, but the public DMA archive did not yield an explicit license in this review. Do not assume reuse/redistribution permission from free download.

### Ready-made trajectory benchmark (not a spill dataset)

- **EnvShip-Voyage: Long-Term Ship Trajectory Imputation**, Hugging Face `mark000071/Ship_trajectory_interpolation`: dataset card describes 179,131 windows / 3,636,544 rows / 3 GB, 6 months of Danish AIS, cargo/tanker vessels, 5-minute grid, 6h and 12h windows, frozen masks and vessel-disjoint split. Despite the 5-minute samples, its masks are a long-gap imputation benchmark and can support gap-reconstruction baselines; check what actual mask horizons/terms support 15/30/60-minute subsets. One-hour/day domain, Denmark, vessel class restrictions; no spill event labels and its public mirrored license was not verified in the page excerpt inspected.
- **EnvShip-Bench**, Hugging Face card: DMA and NOAA source branches, train/val/test shards, 30 historical +30 future points at 20-second spacing (10-minute observe and prediction horizons), raw samples plus a subset of source raw monthly files, construction code. Useful for short-horizon trajectory forecasting only; not a missing 15–60 minute gap benchmark. License and scenario split-by-vessel details remain to check before adopting; no spill alignment.

### Real incident / drift evidence graph (joinable, not pre-packaged)

- **NOAA IncidentNews raw incidents.csv** is a directly downloadable ~2 MB public-domain CSV; fields include incident name, notification date (not necessarily spill occurrence time), approximate lat/lon, threat/commodity, possible release amount and response measures. NOAA says it covers selected events where its OR&R supported response, not all US spills. This is a good event index, not a precise spill-time ground truth.
- **NOAA AIS** can provide nearby vessel tracks and **ERA5/CMEMS/NOAA SAR winds** can supply forcing for selected event-time windows; **Sentinel-1 products** can be retrieved by time/location for SAR observation. These are separate datasets requiring an explicit join and temporal/position uncertainty. Coincidence does not prove source vessel.
- **GlobalOSD-SAR** supplies slick coordinates + scene date and broad source categories for many globally distributed Sentinel-1 detections, potentially enabling this join for oil source candidates, but not exact spill release times, vessel IDs, or verified source attribution.
- **NOAA WebGNOME/PyGNOME** is official open spill trajectory/fate model tooling and NOAA provides incident event indexing. GNOME trajectories are model predictions given spill scenarios, not independent observed trajectories. Use to compare model mechanics, not to claim validated historical drift.
- **COSMO/MedSOSIS drifting-object database** reports ~1,700 Mediterranean drifter and object trajectories including Prestige incident deployments, quality control caveats, and a normalized GeoJSON convention. It is a potential empirical drift-validation resource, but not a public oil-slick+AIS dataset; access mechanism/data terms were not verified in this session.
- A strong co-located benchmark pairing actual SAR spill delineation, AIS vessel trajectories, observed slick drift, and gridded metocean forcing was **not found**. This is the main remaining evidence gap. A defensible demo may choose a documented incident and independently assemble the layers, while reporting time/position uncertainty and whether the observed path is a surface slick, drifter, or model trajectory.

## Integration recommendation

1. Use SOS only for the initial mask training baseline, with source-level leakage plainly stated; audit all mask binarization before metrics.
2. Add Cantarell as the first small, scene-grouped pixel-mask transfer dataset after inspecting source-image/product mapping and separating seep from spill labels where possible. Preserve a dataset-source flag and keep the original source-specific test untouched.
3. Use DARTIS as an independent, acquisition-grouped object-detection and hard-negative assessment. Convert output masks to boxes/connected components for fair comparison; do not calculate DARTIS pixel IoU.
4. Treat Sentinel-1 Part III as a separate external dataset test, not a scene-disjoint test until its source scene IDs are established and checked against Parts I/II. Sample/archive size is a real operational cost.
5. Consider QPOSD as a later polarimetric domain-transfer experiment; defer for a minimal dual-pol U-Net pipeline.
6. Use GlobalOSD-SAR and NOAA IncidentNews as candidate event/source indices. They support data assembly but do not themselves deliver co-located AIS truth or proof of attribution.
7. For AIS imputation use a bounded raw NOAA slice or the ready-made EnvShip-Voyage subset after confirming its license; evaluate 15/30/60-minute synthetic missing blocks against dead reckoning, constant-speed, and Kalman baselines. Do not equate synthetic block masking with real AIS dropout behavior.

## Open verification items / blockers

- Verify the Zenodo `metadata.license` fields for all three Trujillo-Acatitla records before use. The third-party CC BY claim is insufficient.
- Inspect a small sample of Parts I/II/III archive contents (or published manifest) for actual source product IDs, acquisition dates, geographic spread, near-duplicate patches, mask class semantics, and whether Part III scenes are disjoint. Do not fetch the ~96.5 GB archive wholesale; request/file-range/tooling plan if needed.
- Resolve the 685-scene claim from the article text/supplement, or remove it. Current record metadata does not support it.
- Inspect the complete QPOSD article methods/Zenodo ZIP file listing and scene identifiers, and verify a split design. The very recent 2026 release is promising but not yet a reviewed/evaluated benchmark here.
- Check Cantarell original scenes/source provenance and the precise split grouping; map `IMG_XX` IDs to acquisitions, then test group disjointness programmatically before calling it scene-disjoint. Clarify whether “slick” labels include natural seeps by design (card says yes).
- Verify GlobalOSD-SAR data dictionary for geometry meaning, source-label semantics, temporal precision, negative provenance, and retrieval instructions; shapefiles contain labels, not imagery.
- Verify EnvShip dataset licenses and that vessel IDs are disjoint (Voyage says yes; Bench requires checking). Decide if its interval/mask patterns match 15/30/60 minutes exactly.
- Choose a real event and check whether timestamps in NOAA IncidentNews denote report notification rather than event time; search incident-specific documents for precise date/location before alignment.
- Confirm DMA AIS data terms; preserve source-specific NOAA caveats.

## Primary source links

### Segmentation / oil-slick SAR

- [Refined Deep-SAR SOS, Zenodo record](https://zenodo.org/records/15298010)
- [CBD-Net original paper search entry](https://ieeexplore.ieee.org/document/9374722) (prior record; mapping requires renewed artifact audit)
- [Sentinel-1 Parts I, II, III on Zenodo](https://zenodo.org/records/8346860), [Part II](https://zenodo.org/records/8253899), [Part III](https://zenodo.org/records/13761290)
- [DARTIS ESSD data descriptor](https://essd.copernicus.org/articles/17/6807/2025/)
- [DARTIS PANGAEA dataset / metadata / README links](https://doi.pangaea.de/10.1594/PANGAEA.980773)
- [DARTIS code DOI](https://doi.org/10.5281/zenodo.17789853)
- [CERTH/M4D official dataset and access steps](https://m4d.iti.gr/oil-spill-detection-dataset/)
- [Cantarell public GitHub dataset](https://github.com/Garcia-INPE/oilspill-detection-dataset)
- [Cantarell dataset card](https://raw.githubusercontent.com/Garcia-INPE/oilspill-detection-dataset/main/DATASET_CARD.md)
- [Cantarell train manifest](https://raw.githubusercontent.com/Garcia-INPE/oilspill-detection-dataset/main/splits/train.csv), [validation](https://raw.githubusercontent.com/Garcia-INPE/oilspill-detection-dataset/main/splits/val.csv), [test](https://raw.githubusercontent.com/Garcia-INPE/oilspill-detection-dataset/main/splits/test.csv)
- [Cantarell Zenodo concept record](https://zenodo.org/records/22214144) and [current archive version record](https://zenodo.org/records/22728926)
- [QPOSD 2026 paper](https://doi.org/10.1016/j.dib.2026.112773); [QPOSD Zenodo concept](https://zenodo.org/records/18143758); [current version](https://zenodo.org/records/19258036)
- [GlobalOSD-SAR Zenodo record](https://zenodo.org/records/15286918)
- [GlobalOSD-SAR OpenAIRE metadata view](https://explore.openaire.eu/search/dataset?pid=10.5281%2Fzenodo.15286918)
- [CSIRO dataset source discussed in a recent paper](https://www.nature.com/articles/s41598-026-37081-1) (primary dataset accession not verified)
- [Najoui et al. Gulf of Guinea oil slick paper](https://essd.copernicus.org/articles/14/4569/2022/); [spatial dataset DOI 10.5281/zenodo.6470470](https://doi.org/10.5281/zenodo.6470470); [100 georeferenced spill set DOI 10.5281/zenodo.6907743](https://doi.org/10.5281/zenodo.6907743)

### AIS / incident / drift

- [NOAA Marine Cadastre AIS](https://marinecadastre.gov/ais/)
- [Danish Maritime Authority AIS](https://www.dma.dk/safety-at-sea/navigational-information/ais-data)
- [EnvShip-Voyage on Hugging Face](https://huggingface.co/datasets/mark000071/Ship_trajectory_interpolation)
- [EnvShip-Bench on Hugging Face](https://huggingface.co/datasets/mark000071/EnvShip-Bench_An_Environment-Enhanced_Benchmark_for_Short-Term_Vessel_Trajectory_Prediction)
- [NOAA IncidentNews CSV and data dictionary](https://incidentnews.noaa.gov/raw/index)
- [NOAA WebGNOME documentation](https://gnome.orr.noaa.gov/doc/introduction.html)
- [NOAA high-resolution Sentinel-1 SAR sea-surface wind catalogue](https://catalog.data.gov/dataset/noaa-high-resolution-sea-surface-winds-data-from-sar-on-the-sentinel-1-satellites)
- [COSMO / MedSOSIS drifter and drifting-object resources](https://cosmo.icm.csic.es/medosmosis/Activities.html)

## Outcome

**Recommendation:** add Cantarell as the first new, small segmentation candidate; preserve DARTIS for scene-level object-detection/hard-negative evaluation; keep SOS chip-split leakage caveat; downgrade the Parts I–III claim to “separate test part pending acquisition overlap verification.” Use GlobalOSD-SAR and NOAA incident data as event discovery/scene-matching inputs, not as image or AIS ground truth. The strongest real-world oil + AIS + metocean + observed-drift benchmark remains unresolved.

No project overview or ticket was edited, as requested. No user decision is inferred from these research recommendations.
