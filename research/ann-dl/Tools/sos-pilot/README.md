# SOS provenance pilot

This is an acquisition/matching experiment, not a model-training pipeline.
It is authorized for exactly **50 real SOS patches**, never all 8,070.

## Current artifacts

- `../../Data/SOS/Browse-50.html`: offline browser of the selected images and masks.
- `../../Data/SOS/previews/21-scenes-contact-sheet.jpg`: catalogue previews only.
- `../../Data/SOS/pilot/selected_50.json`: fixed selection of 25 PALSAR and 25 Sentinel patches, spanning five mask-coverage quantiles per sensor.
- `../../Data/SOS/metadata/scenes.json`: 21 source catalogue matches, original published identifiers retained, access URLs and preview provenance.
- `../../Data/SOS/pilot/status.json`: actual matching status. Missing source rasters produce an explicit block, not fabricated matches.

The previews are not full original rasters. Full archives are downloaded to
`Data/SOS/archives/scenes/` and preserved. Their detected HH (PALSAR) / VV
(Sentinel-1) band is exported losslessly to `Data/SOS/scenes/` after download.
The original SOS preprocessing and polarization are not proven; a downloaded
product is a candidate source until registration succeeds. Other polarizations
remain available in the preserved archives for a later agreed experiment.

## Run

Python 3.12 environment: `.venv312/bin/python`. Dependencies are pinned in
`requirements.txt`. From the project root:

```sh
Tools/sos-pilot/.venv312/bin/python Tools/sos-pilot/fetch_pilot.py
Tools/sos-pilot/.venv312/bin/python Tools/sos-pilot/match.py --controls
Tools/sos-pilot/.venv312/bin/python Tools/sos-pilot/match.py
```

`run.py` acquires both full collections, exports rasters, builds
`Data/SOS/Browse.html` for all 8,070 patches, and runs the 50-patch pilot.
Authentication takes private username/password file paths as arguments;
never put credentials in this folder or shell command text. It resumes completed
patch chunks and scene `.part` files. Do not launch duplicate pipelines.

## Checks and limits

Patch ZIP MD5 is verified against Zenodo before full extraction. The separately
fetched 50 ZIP members are checked with each member's CRC and uncompressed size.
Source archive ZIP CRCs are verified before extraction. Safe extraction checks
prevent archive paths leaving their destination.

The matching method uses SIFT descriptors, robust affine estimation, alignment
correlation and feature spread. Scene pyramids allow different scales; SIFT can
handle rotation. Strong candidates still require review: thresholds are diagnostic
heuristics, not calibrated probabilities. No automatic ancestry assignment is made.
The six passing synthetic checks cover four rotations and rejection of blank and
unrelated patches. They do not establish accuracy on real SAR chips.

Original processing (calibration, terrain correction, speckle filtering, contrast,
rotation, noise) may differ. Smooth sea and repeated textures can be unmatchable.
Unknowns must remain unknown. Once real results exist, inspect aligned crop evidence
before using a recovered scene assignment for grouped evaluation.

## Learning scope

The user wants hands-on preprocessing and explanations they can defend to
evaluators. The current download/50-patch pilot is authorized. Broader preprocessing,
full-dataset matching, training, and dataset-merging choices are not authorized by
this pilot. Work through those later with explanations and small user-led steps.
