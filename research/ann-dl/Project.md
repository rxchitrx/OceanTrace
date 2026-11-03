# OceanTrace

## Summary
Maritime investigation decision support: screen satellite SAR for candidate slicks, estimate possible release regions/times using drift, and correlate AIS tracks to rank possible source vessels with explainable uncertainty. Not chemical confirmation or proof of legal responsibility.

## Status
**Active: ANN/DL only.** User confirms the team was not selected for SIH and is no longer pursuing that lane.

Working prototype remains the classical detection + drift + AIS web application; no trained ANN models reported. The team-agreed direction is captured in the supplied PPT: U-Net CNN segmentation, LSTM vessel-track forecasting, and physics-based drift. These are planned components, not implemented/trained models.

**Next submission:** PPT + prototype. User reports both are available and plans to demonstrate the existing web application. Submission is **probably Wednesday**, per user; exact date not confirmed. The supplied PPT's six slides were inspected via text extraction; the web application was not audited in this session. The deck is dated 30 September 2026, which does not establish the submission date.

Source: [[College projects/OceanTrace/Sessions/ANN status clarification|Direct user status clarification]].

## Related academic lanes
- **SIH baseline (historical, no longer pursued):** classical detection, drift, AIS correlation, transparent ranking, and investigator dashboard; existing application reused for ANN prototype presentation.
- **ANN/DL extension (active):** current PPT title is *Deep Learning Based Oil Spill Attribution Using CNN and LSTM*. Earlier working title was *Multimodal Deep Learning for Marine Oil Spill Source Tracking*.

## Agreed model direction — supplied PPT
- **U-Net CNN:** pixel-wise candidate slick segmentation; skip connections preserve boundaries (slide 5).
- **LSTM:** AIS vessel-track forecasting/sequence-gap handling, not oil drift or a polluter classifier; compare with Kalman and constant-speed baselines (slides 4–5).
- **Physics-based drift:** wind/current transport for slick source reconstruction; LSTM does not replace it (slide 5).
- **Evaluation plan:** classical threshold baseline M0, scene-wise splits/shared metrics, refined Deep-SAR SOS masks, DARTIS hard-negative stress testing (boxes, not pixel masks), and comparison against physics-only ranking (slide 4).

Exact U-Net/LSTM configurations, training setup, fusion/ranking details, and drift implementation are not specified in the extracted slide text. Dataset and literature claims are deck statements, not freshly verified facts.

These are related scopes of the same product, not two unrelated ideas. Earlier ResNet–GRU–MLP proposals remain historical alternatives, not the settled minimum.

## Historical decisions and evidence
- User selected OceanTrace after initially considering EW scanning: SIH source messages #325/#1018.
- Later user chose to explore extending an existing OceanTrace repository: ANN/DL message 3980.
- ANN/DL inventory records historical baseline tests, frontend build, and recovery of both demo flows. The August SIH record's unbuilt status precedes that later progress.
- Arabian Sea end-to-end case is synthetic. DARTIS case is single-real-image detector validation, not verified real vessel attribution.
- No trained U-Net/ResNet/GRU/LSTM/fusion model is established in the recovered ANN/DL record.

## Open questions and risks
- Exact Wednesday date remains tentative.
- Model configurations, training schedule, dataset readiness, and implementation details remain uncaptured.
- Dataset access, acquisition-level split metadata, masks versus boxes, AIS coverage, and code reuse/license permission need verification.
- Do not merge unrelated published, synthetic, single-patch, and end-to-end results into a claimed system accuracy.

## Next step
For the upcoming PPT/prototype submission, present the existing application as a working classical baseline and U-Net/LSTM as the agreed next implementation, not completed ANN work.

## Presentation artifacts
- [Minimal top-view animation](Animation/top-view.html) — 42-second monochrome alternative with a light morning fading into dark night, and equal-length recorded tracks before and after the AIS gap. User-approved visual direction, refined on 23 October 2026. Original detailed version retained. [[College projects/OceanTrace/Sessions/2026-10-23 - Problem animation|User feedback and verification]].
- [Problem animation](Animation/index.html) — standalone 40-second interactive illustration of night-time AIS shutdown, oily-waste discharge, departure, and restored transmission. Created from the user's visual brief on 23 October 2026; not a real incident or application result. [[College projects/OceanTrace/Sessions/2026-10-23 - Problem animation|Brief, implementation choices and verification]].

## Sources
- [[College projects/OceanTrace/ANN_DL  Oil Slick (1).pptx|Supplied ANN PPT]] — model direction and evaluation plan, slides 4–5; current title, slide 1.
- [[SIH-inventory#Dedicated project record: OCEANTRACE / SIH26143 — selected|SIH selection and scope]]
- [[ANN-DL-inventory#2. OceanTrace — baseline SIH project|Historical baseline audit]]
- [[ANN-DL-inventory#3. OceanTrace-ML — architecture evolution and implementation plan|ANN/DL architecture evolution]]
- [[ANN-DL-inventory#14. Handoff: what is finished and what is not|Historical handoff]]

This overview summarizes imported Hermes inventories; source-message IDs are scoped to their original transcripts. External research and runtime claims have not been independently rechecked here.

## Dataset research — 3 November 2026
- [[College projects/OceanTrace/Sessions/2026-11-03 - Additional datasets deep search|New dataset survey]] identifies Cantarell as a promising small segmentation addition, plus QPOSD and GlobalOSD-SAR for different modalities/label roles. These are recommendations, not adopted decisions.
- Corrections: DARTIS has boxes, not pixel masks. Zenodo Parts I–III total 3,020 images; Part III acquisition independence remains unverified. Do not claim scene-disjoint evaluation until source overlap is checked.
- [[College projects/OceanTrace/Sessions/2026-11-03 - SOS provenance deep search|SOS provenance search]] recovered the published 21-scene inventory (Dong et al. 2023, Table 1), but no patch-to-scene crosswalk. Original Drive/Baidu manifests remain incompletely inspected. Split design and intra-scene overlap are unknown; leakage is possible, not proven.

- [[College projects/OceanTrace/Sessions/2026-11-03 - Original SOS share inspection|Original SOS share inspection]] reached sensor subfolders and read the original README; complete pagination remains unresolved and no crosswalk was recovered. Image matching remains a proposed fallback.

- [[College projects/OceanTrace/Sessions/2026-11-03 - Cantarell acquisition group verification|Cantarell verification]] confirms 173 unique samples (108/43/22), separated across 24 catalogue-matched Sentinel-1 acquisitions (16/4/4). Exact source timestamps/platforms match distinct SAFE products; original pixel lineage remains unverified. Binary masks combine 327 spill and 58 seepage polygons as SLICK. This supports acquisition-held-out slick segmentation evaluation, not spill-vs-seep classification or vessel attribution.

- [[College projects/OceanTrace/Sessions/2026-11-03 - SOS matching pilot and hands-on preprocessing|Authorized SOS matching pilot]]: source acquisition and fixed 50-patch experiment underway. User wants hands-on preprocessing and explanations for evaluators. All 21 archive access checks passed; downloads/real matching remain incomplete. Offline sample browser: [50 patches and masks](Data/SOS/Browse-50.html).

- [[College projects/OceanTrace/Sessions/2026-11-03 - AIS matched imagery deep research|AIS research]] identifies NOAA 2010 monthly zone archives overlapping DWH scene dates/regions as the best candidate pairing; actual point density/continuous tracks in scene windows remain unverified. NOAA 2020 CSVs are a separate LSTM benchmark candidate. No accessible raw AIS was found for the other SAR regions in the search; universal absence is not established. DWH is a well-source case, not vessel-attribution ground truth.

- SOS pilot completed: all 21 source rasters and 8,070 patches saved; exactly 50 tested, yielding 12 PALSAR candidates and 38 unknown, with zero automatic assignments. [Results](Data/SOS/pilot/RESULTS.md) · [All images](Data/SOS/Browse.html). Sentinel recovery remains unresolved; this is feasibility evidence, not measured mapping accuracy or full-corpus provenance.

- [SAR preprocessing baseline](Data/Preprocessing/README.md) prepared and verified for all8,070 pairs: lossless grayscale images, explicit128maskthreshold with originalsretained, normalized float32 loader. Original split preserved; no training or scene-disjointness claim. Full native matching and AIS track audit remain ongoing. User manages the HTML presentation with Terra.

- [Continuous AIS subset](Data/AIS/README.md) downloaded and audited: NOAA2020-07-01,2,228,788clean northernGulf records across3,359vessel IDs. Continuity examples verified; jump/speed checks, resampling, held-out gaps and training still pending. No pairing with SOS spill scenes is established.

- [Full native SOS search](Data/SOS/full_mapping/REPORT.md) completed2026-11-04:8,070patches searched;1,541candidates(557PALSAR/984Sentinel),6,529unknown/ambiguous,zeroautoassignments. Executionchecks/16softwarecontrols passed and6samplealignments inspected. Incomplete recall is demonstrated by7missedpilot candidates; this is not measuredmappingaccuracy or a completed scene-disjoint split.

- DVC setup (2026-11-04): dataset manifests and restore instructions added; local storage is `/Volumes/APFS/OceanTrace-DVC` on the project SSD. Publication targets `rxchitrx/OceanTrace` under `research/ann-dl/`. See [[College projects/OceanTrace/Sessions/2026-11-04 - DVC and GitHub publication|DVC publication record]] for storage boundaries and verification.
