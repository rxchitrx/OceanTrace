# Presentation phase and expanded matching

Date: 2026-11-03
Source: Direct user instructions; deadline approximately four hours from this phase request.

## User-confirmed scope
- Next presentation must identify datasets, preprocessing steps and framework. Research paper draft is owned by a teammate; do not create one.
- Full-resolution scene matching is now authorized for all 8,070 images, superseding earlier 50-only restrictions. Delegate implementation, execution and verification to GPT-6 Luna Medium.
- User requests a standalone HTML presentation, using the existing Animation visuals and Anatomy style, initially listing all sources and underlying dataset details. Delegate it to GPT-6.1 Terra Low.
- Parent handles broader preprocessing and AIS data readiness. Learning remains hands-on and phone-friendly; user asked assistant to select examples and show visuals here.

## Current evidence
- First full-mapping delegate stopped after reading: no code, run, files or verification. A new execution-focused retry is required; no full-corpus result is established.
- Full read-only SOS audit finished: 8,070 images and masks, no read errors/dimension mismatches; all image RGB channels identical. Masks: 4,800 RGB, 3,270 grayscale; 1,847 have intermediate gray values. At diagnostic threshold128: 331 empty and57 full masks. Threshold remains a proposal, not applied training preprocessing. Source: Data/Preprocessing/sos-audit.json and sos-audit.csv.
- Existing AIS sample has99 records across98 vessels, only7seconds, unsuitable for trajectory training. A bounded NOAA2020-07-01 daily archive is downloading; real continuity/coverage still needs inspection. See Data/AIS/acquisition.json.
- Proposed framework: Python/NumPy/Pillow/OpenCV/rasterio preprocessing; PyTorch for U-Net/LSTM training. Training framework adoption and training execution are not yet established.

## Handoff boundaries
Matching delegate: Tools/sos-mapping/, Data/SOS/full_mapping/, its own session note. Presentation delegate: Presentation/, its own session note. Parent: Data/Preprocessing/, Data/AIS/ and source decisions. Preserve pilot artifacts and original Animation files. Parent will consolidate shared overview updates.

## User steering and execution correction
User instructs that delegates must never use fast modes. Do not enable fast/priority service modes; this is independent of the explicitly chosen reasoning effort. User is directly managing the Terra presentation agent: leave Presentation/ and that agent under user direction.
Second Luna delegate wrote an unvalidated brute-force draft but stopped at system-Python missing cv2. Parent verified the existing .venv312 has OpenCV/rasterio and replaced the per-tile brute-force search with native per-scene SIFT feature indexes and FLANN retrieval in Tools/sos-mapping/indexed.py. Native search passed12known-location/rotation controls and4negative controls; full scene-by-scene run is now active, not completed.
Discovered train/val filename reuse:8070 distinct split/name keys but6455bare names. Full matcher keys include split/name. Fixed browser pilot-filter and prepare.py lookup to include split. Existing full pilot actually used33train/17val (current selected_50.json), rather than the initially fetched40/10; earlier manifest reconstruction keyed only by bare ID reassigned7selected entries before matching. Keep baseline artifacts and disclose this distinction; do not claim frozen sample identity across those two stages.

## Completed SAR preparation
All8,070 pairs processed into a separate prepared baseline and verified. Lossless RGB-to-L images; mask gray>=128 becomes foreground (documented agent baseline choice), stored0/255 with float32 targets0/1 atload; images normalizeby255 atload to1×256×256float32. Existing split preserved without scene-disjoint claim, originals retained, no training/augmentation. Evidence: Data/Preprocessing/sos-prepared-summary.json and manifest.csv; summary for evaluators: Data/Preprocessing/README.md. Full native matching and NOAA download/continuity audit continue independently. Presentation remains under user/Terra direction.

## AIS source readiness
NOAA2020-07-01 full daily ZIP downloaded and CRCverified.8,529,554national records scanned; northernGulf bbox yielded2,228,788clean records across3,359retained vessel IDs, with5,673segments >=2hours and >=120reports under a provisional5-minute gapbreak rule. Counts reconcile after253exactduplicates and66conflictingtimestamp records removed. Example2has actual movement (0–7.2knots,1,143reports,maxgap229seconds); example3mostlystationary, showing that continuity alone is not movement quality. Data/AIS/README.md documents actualsteps and pending speed/jump checks, sequence/gap policies and training. No SAR pairing established. Native matcher now yields Sentinel candidates; parent visually inspected train/sentinel_926 and train/sentinel_1358 against alignedsource crops from5Aug2017. This remains preliminary untilall7compatible scenes finish and ambiguity/regression checks run.

## AIS stop-context check — 2026-11-04
User requested sending the real full-day speed chart to the existing Terra presentation agent and asked whether the04–06UTCzero-speed region meant missing AIS or being atsea. Parent checked actualrecords:86reports, SOG0–0.3knots, longestgap199seconds,49exact-zero readings. All86positions intersect USGSNHD Area-LargeScale polygon189374 (FTYPE336/FCODE33600CanalDitch), nearMatagordaTexas. This is a mappedwaterway stop withAISpresent, not an observed2-hourgap or verifiedoffshore anchoring. Mooring notestablished; reportednavstatus0throughout canlag actualactivity. Fulltrackmaxgap229seconds; no>5min gapunderprovisionalrule.
SourceJSON/GeoJSON and presentationhandoff saved underData/AIS/example-track-2-context.json, nhd-stopped-position-layer-9.geojson and EXAMPLE-FOR-PRESENTATION.md. User authorized parent to askTerra toaddthisrealdata visualto latestdeck; implementationrequestsent to existingTerrachat, preservinguseredits andwithoutfastmode. During actualmissinginterval exactlocationunknown; estimatesmustnotbe shownasobservations.

## All-corpus matcher completed — 2026-11-04
All8,070patches searched against compatible native source indexes.1,541candidates(557PALSAR+984Sentinel);6,529unknown/ambiguous;zeroautoassignments. Automatedstructural/evidencechecks passed,16softwarecontrols passed and6representativepairs visuallyreviewed. Native retrieval missed7pilot candidates; directcoordinate rechecks support them, so reportincomplete recall,not recoveredmappingaccuracy. No scene-disjointsplit or training. Fullreport:Data/SOS/full_mapping/REPORT.md. SARinputsandcontinuousAISsourcepreparation arealso complete; speed/jumpchecks,resampling,gapmasksandtraining remainfuturework. Presentation remainsuser/Terraowned.
