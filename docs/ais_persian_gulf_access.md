# Persian Gulf 2017: unresolved raw AIS access

Paths below are relative to `Data/AIS/scene-matched/`.

Seven original Sentinel-1A scene polygons and exact UTC acquisition times are recorded in scene-manifest.json. The union polygon and complete acquisition-date range, 5–14 August 2017 UTC, are in persian-gulf-2017-request.geojson. No raw position download for this area/time has been obtained.

## Sources checked

- NOAA explicitly excludes foreign waters and satellite AIS: https://coast.noaa.gov/data/marinecadastre/ais/faq.pdf . Its 2017 US files would not match these scenes.
- Global Fishing Watch's public APIs expose identity/events/aggregated presence; the official public request forum says map-viewer vessel tracks are not exposed through a public endpoint: https://global-fishing-watch.canny.io/data-requests/p/vessels-api . Aggregates are not a substitute for raw trajectories.
- The Mendeley Persian Gulf AIS-like dataset is explicitly synthetic and published for a different purpose: https://data.mendeley.com/datasets/dbwfcf3bzm/1 . Not downloaded as a match.
- VesselFinder advertises terrestrial/satellite historical records since 2009, with custom-area requests subject to availability and pricing: https://www.vesselfinder.com/historical-ais-data . This does not verify actual 2017 scene coverage.
- Spire's archive request documentation covers older history; its ordinary Historical Positions API starts in December2018 and therefore cannot directly serve our2017 scenes: https://documentation.spire.com/messages-api/ and https://documentation.spire.com/historical-positions-api/using-the-api/ . A special archive request/access agreement would be needed and its coverage must be checked.

## Concrete access request specification (not submitted)

Academic OceanTrace project. All observed vessels within the supplied union polygon, full UTC days from2017-08-05T00:00:00Z through2017-08-15T00:00:00Z exclusive. Both terrestrial and satellite observations where available, at native available cadence. Need UTC timestamp, MMSI (and IMO if available), latitude/longitude, SOG, COG, true heading, navigation status, source/receiver type and available position-quality flags. Preserve missingness and do not interpolate. CSV preferred, with source/schema/units and coverage statement. If broad export is impractical, supply counts/availability for each exact scene polygon/date first.

No provider contacted, purchase made or terms accepted. User has been asked whether college/provider access is available. This is a real acquisition gap, not evidence of zero traffic or proof no archive exists.

## Additional access search — 4 November 2026

- SkyTruth is a case-specific research-holder lead: John Amos's15August2017 article analyses the same10/14August Kuwait scenes and includes an AIS-derived DLB1600 track since5August. Ask whether the underlying records are retained/shareable or which provider supplied them. This is NOT a confirmed downloadable raw archive or all-vessel regional export. Source: https://skytruth.org/blog/satellite-imagery-reveals-scope-of-last-weeks-massive-oil-spill-in-kuwait . No contact made.
- VTExplorer advertises historical terrestrial AIS from2009 and accepts coordinates/date-based requests, with availability and pricing confirmed individually: https://www.vtexplorer.com/historical-data-en/ . Gulf2017 coverage not verified; do not assume data are independent of other commercial networks.
- Lloyd's List Intelligence /Seasearcher is another commercial or institutional-library inquiry route: https://www.lloydslistintelligence.com/solutions/seasearcher . Confirm actual2017 raw-position coverage and export rights before access/purchase; current marketing does not verify our exact area/dates.
- UN Global Platform documentation says its global AIS dataset starts October2018, so the documented archive does not solve August2017: https://millenniumindicators.un.org/wiki/spaces/AIS/pages/57999715/AIS%2Bdata%2Bat%2Bthe%2BUN%2BGlobal%2BPlatform .
- OpenOceanNetwork is a public historical-position API. Live bounded tests against /position on4November2026 returned HTTP200 and[] for both Gulf5–14August2017 and global5–14August2017; an unfiltered one-record request returned a2026position. Saved exact query URLs/responses in open-ocean-access-probe.json. This does not prove their archive has no other older data, but provides no usable2017 match. API docs: https://api.openoceannetwork.com/ .
- New-source search did not find a verified free full-region August2017 raw AIS download. Do not substitute synthetic or aggregate sources or treat named-vessel narrative as a complete candidate-vessel dataset.

## How published work obtained AIS — primary-source checks

User explicitly does not want approaching people/access requests. Checked acquisition statements instead of assuming published methods imply open raw data:

- Remote Sensing for Maritime Prompt Monitoring (2019), setup section: AIS supplied by ExactEarth and AstraPaging; paper does not establish a freely downloadable raw archive or identify whether their access was paid/donated. https://www.mdpi.com/2077-1312/7/7/202 .
- The2019 northeast Brazil oil spill: scenarios, SAR/traffic section: AIS supplied by CISMAR/MB, Integrated Center for Maritime Security/Brazilian Navy. This is an institutional source, not evidence that any student can download the same records. https://new.scielo.br/j/aabc/a/KJtdXzjnSt7DKQfNBQJMnqg/?ilang=en&lang=en .
- Ship Trajectory Reconstruction from AIS Sensory Data via Data Quality Control and Prediction (2020), section2: public MarineCadastre/NOAA data, Gulf of Mexico,11April2017. Trajectory reconstruction study, not matched Persian Gulf oil-vessel attribution. https://doi.org/10.1155/2020/7191296 .
- SkyTruth Cerulean methods data-source table(asof2025-05-01): AIS from SpireMaritime viaGlobalFishingWatch. A concrete operational oil-spill association system using supplied partner data, not proof that GFW public API exposes those raw tracks. https://skytruth.org/cerulean/methods .
- Marine Oil Pollution in an Area of High Economic Use: Statistical Analyses of SAR Data from the Western Java Sea (2022), availability statement listsMarineTraffic along withSAR/environmental sources; this statement is not itself a released raw AIS package. https://www.mdpi.com/2072-4292/14/4/880 .

Inference: a published paper and public methods do not guarantee public inputs. For a no-contact/no-commercial-access workflow, verified open coverage must guide which image/AIS cases are feasible. Continue2010 source downloads and measureactualcoverage; no new synthetic substitution, training, or scopechangeauthorized by this discussion. Seven2017scenes remain usable asSAR inputs but their rawAISmatch remains unfulfilled.
