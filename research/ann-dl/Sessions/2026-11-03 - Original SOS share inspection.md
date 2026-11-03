# Original SOS share inspection

Date: 2026-11-03
Participants: User; Codex parent agent
Source: User authorized inspecting the original SOS manifest and requested a simple image-matching explanation.

## Verified progress
- Followed the official CBD-Net README distribution forms without submitting personal information. Google form configuration points to https://drive.google.com/drive/folders/1KyrtyHkK3IC1_3mUvKA2B2H112uo3J1K ; Baidu points to https://pan.baidu.com/s/1TcbtGt7qp-IL0dALQ9HBlg .
- Original Google root listing exposed test, train, and Readme.pdf (file ID 14bL121jvV0YYXTPD8Ja_aYxboPhpPBEv).
- Inspected both train/test sensor folders. Test has palsar and sentinel, each exposing gt and sat subfolders. Train sensor folders expose interleaved image/mask files directly.
- Train PALSAR first listing: 50 files, 10777_mask.png / 10777_sat.jpg through 10801_mask.png / 10801_sat.jpg. Train Sentinel first listing: 50 files, 20840_mask.png / 20840_sat.jpg through 20864_mask.png / 20864_sat.jpg. These are partial listings, not full folder manifests. Numbers do not establish scene membership.
- Downloaded only original Readme.pdf (234,512 bytes) to /tmp for text extraction with pdftotext. It confirms cropping, rotation, added noise, sensor regions and 3101/776 + 3354/839 split counts, but contains no scene inventory or patch-to-scene table. Its illustrated source locations reference the 2010 Deepwater Horizon and August 2017 Kuwait incidents. Research-only terms require citation.

## Limits
Complete paginated image manifests remain unresolved. No claim that every file in the original share was inspected. No recovered patch-to-scene crosswalk, source imagery download, or image registration was performed. The original README uses train/val in its schematic despite train/test in the Drive tree; neither documents scene separation.

## Image matching proposal (not executed)
1. Obtain full source scenes and reproduce plausible grayscale preprocessing.
2. Search each patch within its sensor-compatible source scenes across scale and rotation, using distinctive structures and local image features or correlation.
3. Verify a candidate with geometric consistency, aligned pixel comparison, and separation from runner-up matches. Smooth sea and noise can make matches ambiguous; keep those unknown.
4. Record patch, scene/product ID, crop position, transform, confidence and validation evidence. Parent-scene assignment enables grouped splits; geographic/AIS joins additionally need georeferenced crop location and acquisition time.

## Next step
Recover a complete paginated original share manifest, preserving any sidecars; if it contains only numeric chips, pilot matching on a few distinctive patches before attempting the full corpus.

Related: [[College projects/OceanTrace/Sessions/2026-11-03 - SOS provenance deep search]]
