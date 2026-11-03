# HTML presentation

Date: 2026-11-03. Agent: Codex design sub-agent.

A draft is at `Presentation/index.html`. It covers motivation, proposed model roles, SOS audit, preprocessing, pilot, AIS and evaluation, with research notes embedded as expandable source material. Existing animation and pilot images are referenced by relative paths and were not modified. The ship scenario is labeled fictional.

This draft is incomplete: source records have not been individually curated into the requested dataset-by-dataset catalogue, and historical research text may contain overclaims despite the prominent qualification. It has not been verified for navigation, broken assets, print, or 1280px/390px overflow. HTML preview rejected viewport-height units. Fix these and complete the source catalogue and verification before presenting.

## User revision
User supplied title-slide names and USNs and requested the animation immediately after the title, removal of presentation chrome except the slide counter, and a model-first narrative followed by preprocessing. Updated the draft accordingly, embedding the animation with its mobile cropping overridden and embedding optimized pilot images. Added explanations and qualified comparisons for U-Net, LSTM and physics. Arrow keys and swipe navigate; the animation retains its own controls. HTML preview loaded the initial slide at 390 and 1280 pixels without console errors. It did not exercise later slides, navigation, printing, or animation sizing; those checks and source-catalogue curation remain pending.

## Model and dataset revision
User requested an actual SAR/mask/overlay example, an LSTM visual, removal of the separate physics role, and a new dataset section after slide 6. Updated the HTML with the paired SOS `palsar_1839` image and source annotation; the overlay is explicitly an annotation visualization, not a prediction. The LSTM track is explicitly illustrative. Replaced the old later slides with SOS, the user's five candidate datasets and recommended priorities, a preprocessing status slide, and the existing research appendix. The user said the project will probably use LSTM rather than the separate physics component; this is a tentative direction, not a confirmed research result. HTML preview loaded the U-Net and LSTM slides at widths 390 and 1280 without console errors; interactive navigation and the full deck were not rechecked in this pass.

## Explanation revision
User requested removal of the AIS workflow and unused-dataset slides, simpler U-Net and LSTM explanations, and a direct description of the SAR image, manually created source mask, and overlay check. Updated the presentation accordingly; the source research appendix remains for reference.

## Real vessel example — 2026-11-04
User authorized adding the verified full-day NOAA AIS example after the LSTM slide. The chart plots all 1,143 reports for MMSI 368000510 on 1 July 2020 and highlights 04:00–06:00 UTC: 86 reports, 0–0.3 knots, in a USGS-mapped canal/waterway near Matagorda. The full-track maximum report interval is 229 seconds; the five-minute visual threshold is provisional. Source and spatial evidence: `Data/AIS/EXAMPLE-FOR-PRESENTATION.md` and `example-track-2-context.json`. HTML preview rendered the chart at 390 and 1280 pixels with no console errors; arrow-key navigation into and back from the new slide was exercised in preview.

## Preprocessing presentation — 2026-11-04
User supplied completed SAR and AIS preprocessing results and requested a model-first ordering: U-Net and its preprocessing, LSTM and the real chart, AIS preparation, retained dataset-priority and status slides, a framework slide, and a closing thank-you. Removed the illustrative animation and source appendix as requested. The source recovery slide explains the method without candidate counts. Updated the earlier status slide to reflect the newly completed work. Selected slides rendered in HTML preview at 390 and 1280 pixels without console errors after fixing a navigation initialization error caused by removing the animation.
