# Scene-matched AIS acquisition — 4 November 2026

Participants: Rachit and Codex. Source: user identified that the2020 benchmark was unrelated to SOS dates and explicitly requested the entire AIS data for the21 source scenes' times, dates and areas. User wants actual source data, not another random benchmark or synthetic substitute.

## Verified scene inventory and action

All21 scenes have catalogue polygons and exact UTC acquisition start/end. Extracted the downloaded-product-matched PALSAR features and Sentinel product metadata into Data/AIS/scene-matched/scene-manifest.json and scene-footprints.geojson. Source selection uses the actual source polygon/date, not tile-mapping progress.

Seven complete NOAA monthly zone archives derived: Zones15/16 for May, June, July2010, and Zone15 for August2010. Downloads started, resume enabled, two workers, expected length/CRC/SHA256 checks. Full originals retained. Extraction waits for verified archives, inspects actual GDAL layers/CRS/schema, exports every available point inside each source polygon on its full UTC acquisition date, retaining monthly sources for wider lookback. No new downsampling or interpolation. Available source download is not proof of per-scene observation coverage; coverage counts follow extraction.

Installed pyogrio0.13.0 and packaging26.3 in the existing Python3.12 environment and pinned requirements. OpenFileGDB driver is available. Extraction code compiled, but actual database queries await the first complete archive and are not yet claimed verified.

## Seven Persian Gulf scenes

NOAA's official coverage statement excludes foreign waters. No raw2017 Gulf track archive obtained from searched public sources. GFW public APIs do not expose the map viewer's raw vessel tracks; the Mendeley Gulf AIS-like dataset is synthetic and was not substituted. VesselFinder advertises custom-area archives back to2009, with availability and pricing determined by request. Spire special archive requests may support older data; its ordinary historical-position API starts inDecember2018. No provider contacted or purchase/terms acceptance made.

Prepared exact union polygon, full5–14August2017 UTC dates and all-vessel position fields in persian-gulf-2017-request.geojson and `Research/AIS PERSIAN-GULF-ACCESS.md`. Asked user asynchronously whether college/provider access exists. Source access for those seven scenes remains unresolved, not zero traffic.

## Background-job recovery

During the acquisition turn, found the image-mapping process and its finalizer were no longer running at20,635 saved scene/scale queries; no exit event/cause was available. Resumed from intact checkpoints. Introduced Tools/background_job.py to run jobs in independent sessions with exit status/PIDs in ignored .dvc/tmp/jobs, so loss of an interactive tool session is not taken as completion. Restarted resumable AIS download/extraction under the same supervisor. Mapping advanced past21,000 queries after restart. Finalization waits for active AIS writers before taking a DVC snapshot.

## Current status and next step

Downloads and extraction waiting/running, not completed. Raw2017 AIS access pending. See Research/AIS scene-matched README.md and machine-local job/download status for live evidence. Verify the first actual geodatabase query, then actual per-scene coverage and timestamp/geographic predicates before reporting matched data acquired. Preserve originals; do not start training or unrelated2020 preprocessing.

## Alternative2017 access follow-up

User has no provider access; asked whether educational email helps and what other sources exist. Kpler research invitation is a request route, not an automatic free-access guarantee. New strongest case-specific lead: SkyTruth's original Kuwait investigation used AIS for the same dates. VTExplorer and LLISeasearcher are commercial/institutional request leads, exact coverage unverified. UNGP documented archive startsOctober2018. OpenOceanNetwork API tested with actual2017 Gulf/global queries, both200empty; unfiltered sample2026. Exact responses and primary links saved under the acquisition folder. No outbound contact, account creation or purchase.

## First empirical NOAA coverage check

User explicitly authorized verifying2010NOAAcoverage. First sourceZone16May2010 completed564,296,634bytes, allZIPCRCs verified,SHA2569237a6815e134d8a326373032e37e4fce94a4df69816d771b5c3cd0309757f74. OpenFileGDB actualschema/CRSEPSG4326 verified. Three28May scene exports contain78/9171/3830full-day scene-membership rows. DirectGDALpolygonmask queries match all exportedsourceFIDs; exactUTCdate and originalpolygon predicates checked for everyrow.

At acquisition±15minutes: scene540zero reports; scene560155reports/18publishedAISIDs; scene58059reports/4IDs. Before/after acquisition brackets≤5minutes:0/7/2IDs respectively. Other11scenes pendingdownloads, notzero-coverage. Noidentity, culprit or continuous-ground-truth claims.

verify_ais_coverage.py writesrolling coverage-audit.json/CSV andCOVERAGE.md. Extraction invokes verification after each completedarchive. Resumedextractor from intactparts underownbackgroundsupervisor; no duplicate downloador fullmappingjobstarted. First-three barplot rendered inchat. Further2010verification remainsautomatic/pending sources.
