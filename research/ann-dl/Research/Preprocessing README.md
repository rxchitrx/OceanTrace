# OceanTrace preprocessing evidence

## Completed SAR data preparation

Source: Refined Deep-SAR SOS 2025, https://zenodo.org/records/15298010 ; original CBD-Net paper DOI 10.1109/TGRS.2021.3115492. Pixel labels are supplied annotations with corrections in the refined release, not independently chemically verified spill truth.

- 8,070 image/mask pairs audited and read without errors; every pair has matching dimensions.
- Provided split: 6,455 train / 1,615 validation. These memberships are preserved. Acquisition separation is not established.
- 3,877 PALSAR and 4,193 Sentinel-named patches. All image RGB channels are identical; grayscale conversion preserves values exactly.
- Distinct keys must include split/name: 8,070 pairs but 6,455 bare filenames. Reused filenames are not evidence of duplicate image contents.
- Masks include 4,800 RGB and 3,270 grayscale encodings; their RGB channels are equal. 1,847 masks have intermediate gray values, affecting about 1.154% of all mask pixels.
- Baseline conversion: grayscale mask values >=128 become foreground, lower values background. This is a documented engineering choice, not a user-confirmed physical boundary or a new annotation. Originals are retained. Six low-intensity masks and all empty/full masks remain reviewable; no masks/images were silently dropped.
- Prepared image files are 8-bit grayscale PNG. Prepared mask files use 0/255 for inspection. At load time images become float32 divided by255; targets become float32 values0/1. Shapes are1×256×256.
- Every saved image was compared pixel-for-pixel with the original channel. All8,070 prepared pairs loaded and passed shape/range/binary-target checks.

Evidence in `Data/Preprocessing/`: sos-audit.json, sos-audit.csv, mask-value-followup.json, sos-prepared-summary.json and sos-prepared-manifest.csv. The implementation scripts were retired after these outputs were produced and verified.

## What has not been done

No U-Net/LSTM training. No train-time augmentation, radiometric recalibration of the already-rendered SOS PNGs, or new scene-based split. Full-source scene mapping was retired on 2026-11-06; its outputs are no longer part of the project and are not used here.

## AIS work

The original99-row sample spans98vessels and only7seconds, so it cannot demonstrate trajectory learning. A complete NOAA2020-07-01 daily archive is downloading. A queued ZIP-integrity and continuity audit will extract a bounded northern-Gulf research subset and report actual track lengths and intervals. The5-minute break rule in that audit is provisional; no interpolation, synthetic missing blocks, train/test split or modeltraining is applied yet. See `Data/AIS/acquisition.json` and `Data/AIS/track-audit.json`; the latter proves the audit completed. This2020benchmark is not claimed to be paired with2010/2017SOS scenes.

## Frameworks

Actually used: Python3.12, NumPy, Pillow, OpenCV and rasterio; native source retrieval uses ASF tooling. PyTorch remains the proposed U-Net/LSTM training framework. Model architecture direction is U-Net segmentation, LSTM vessel trajectories and physics-based drift. Do not claim trained neural models or completed integration.

## Short explanation for evaluators

“We acquired the image and annotation datasets, audited their pairing and encodings, and prepared a reproducible single-channel segmentation baseline. The grayscale conversion is lossless because the original RGB channels are identical. We explicitly binarized gray-valued masks, retain originals for review, and normalize image values when loading. Scene provenance is not recovered; the supplied patch split is used, so this is patch-split evaluation. AIS continuity checks and neural model training are separate stages.”

## AIS acquisition update
The daily archive and continuity audit completed:2,228,788clean regional records,3,359vessel IDs,5,673segments satisfying the provisional2-hour/120-report criterion. Movement quality still needs checks; one inspected example shows actual stops and movement, another is mostlystationary. See [AIS evidence](AIS%20README.md). This supersedes the earlier download-pending paragraph; no SAR pairing, resampling or training is claimed.
