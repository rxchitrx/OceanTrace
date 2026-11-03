# SOS matching pilot and hands-on preprocessing

Date: 2026-11-03
Participants: User; Codex parent agent
Source: User explicitly authorized downloading all 21 original source scenes into the project folder, making the patch collection browsable, implementing automated matching, and testing only 50 varied patches.

## User learning preference
User wants hands-on involvement throughout preprocessing and sufficient understanding to explain what was done to evaluators. Mapping is provenance recovery within data preparation, before scene-grouped splitting and model training. Later preprocessing should use concise explanations, small user-led steps and inspection of actual outputs. Do not infer agreement to full-dataset matching or training. Current acquisition and 50-patch pilot remain authorized.

## Verified artifacts and progress
- All 21 published scene IDs resolve to archive products: 14 PALSAR Level-1.5 and 7 Sentinel-1A GRD. The two ALPSRS identifiers are valid in ASF; retain them. The final shortened Sentinel identifier resolves to a product containing 01E0ED_DB39; the published typo remains preserved in metadata.
- NASA Earthdata account/ASF first-use setup completed by user. Authenticated HTTP-range access succeeded for all 21 archives. Credentials are private, outside the vault; none are copied into notes/code.
- ASF compressed source archives total approximately 6.64 GB (earlier 13 GB estimate was based on other catalogue size representations). Full raw archive payloads are preserved. First PALSAR archive was downloaded and ZIP-CRC checked, and its full HH band exported to TIFF.
- All 21 public catalogue previews saved under Data/SOS/previews and displayed in the conversation. They are not full matching rasters.
- Fifty actual refined SOS patches were downloaded via ZIP byte ranges and checked against member CRCs and uncompressed sizes: 25 PALSAR + 25 Sentinel, 40 train + 10 val. The deterministic selection spans five mask-coverage quantiles per sensor. Data/SOS/Browse-50.html allows offline image/mask browsing. Masks are source annotations, not model predictions.
- Data/SOS/pilot/selected_50.json freezes those 50 IDs. Larger collection preparation preserves the selection.
- Implemented acquisition, safe extraction, offline browser, SIFT/affine/correlation pilot and visible candidate-comparison outputs under Tools/sos-pilot. Six synthetic software controls passed (four rotations; blank and unrelated rejection). Python files compiled successfully.
- Attempting the real matching command correctly returned blocked_missing_full_source_rasters with zero attempted real matches. No recovered scene assignments or real-match accuracy is established.

## Active acquisition
The resumable pipeline is acquiring remaining scene archives and the 1.148 GB Refined SOS image archive. It will verify the archive checksum, extract all 8,070 patches, export full source rasters, create Data/SOS/Browse.html and run only the fixed 50-patch pilot. Progress/logs: Data/SOS/pilot/acquisition-and-pilot.log and status.json. Transfers are slow; do not claim completed downloads or results without inspecting current files/status.

## Limits
HH/VV band selection and log/percentile scaling are candidate matching choices, not proof of the original SOS preprocessing. Original calibration, noise, rotation, speckle filtering and contrast may differ. Matches remain candidate_needs_review or unknown; thresholds are uncalibrated. Inspect aligned crops, geometry and competing-scene scores before using any mapping for evaluation. No scene membership is inferred from anonymous patch numbering.

## Next step
Finish verified acquisition, inspect the first real 50-patch results, and involve the user in checking candidate matches. Start broader preprocessing only as a hands-on learning stage; no training or full-dataset matching was authorized.

## Phone-based walkthrough
User explored the 50 patches and is now away from the laptop, learning on a phone. They explicitly asked the assistant to select examples and show images directly in the conversation, rather than assigning laptop/file-opening tasks. Selected palsar_1839 for its branching shape; displayed image/mask/overlay controls and a reduced rendering of the first full source raster, explicitly labeled as an unverified pair. Continue small, visual explanations here; this preference does not authorize full-dataset matching or training.

## Completed pilot — 2026-11-03
Acquisition and the fixed 50-patch test finished successfully. Verified 21 source rasters and 8,070 extracted patches. Results: 12 candidate_needs_review (all PALSAR), 38 unknown (13 PALSAR + all 25 Sentinel), zero automatic assignments. Parent visually inspected three candidate comparisons (palsar_2396, palsar_1375, palsar_280); boundaries look consistent after alignment. No real-data accuracy estimate or full-dataset mapping is established. The teaching example palsar_1839 remains unknown. Detailed report: [Pilot results](../Data/SOS/pilot/RESULTS.md); all-image browser: [Browse](../Data/SOS/Browse.html). Earlier acquisition status paragraphs are historical. Next proposed work is investigating Sentinel failures within the same 50, before expanding; no new experiment decision is inferred.

## Sentinel diagnostic
Parent checked source dimensions, search scales and selected band, then ran three known-location controls from one Sentinel source (not extra SOS patches). All three registered in native local tiles; none in the shrunken whole scene. This points to resolution/feature-coverage limitations, without isolating their contributions or proving that they explain all real failures. See [updated results](../Data/SOS/pilot/RESULTS.md). Next proposed step is full-resolution tile searching on the same fixed pilot. No full-dataset expansion or training has occurred.
