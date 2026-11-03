# Cantarell acquisition group verification — OceanTrace

**Date:** 2026-11-03  
**Participants:** User (task owner); Codex research sub-agent  
**Purpose:** Independently verify whether the Cantarell train/validation/test grouping is disjoint at source-image and Sentinel-1 acquisition levels, and check the dataset counts and label semantics.  
**Scope:** Read-only public-source review. No bulk archive download, account creation, or author contact. No shared overview or ticket edited.

## Verdict

**The released split is acquisition-disjoint for the 24 source groups identifiable in the public metadata.** The source tables map each `IMG_XX` to one processed Sentinel-1 source TIFF with a platform, mode, and sensing timestamp. All 24 timestamp/platform/mode prefixes resolve in the Copernicus Data Space catalogue to exactly one non-COG SAFE product; the 24 matched SAFE product identities are distinct. The manifests place every `IMG_XX` group wholly in one split, with no train/validation/test overlap at either the `IMG_XX` or SAFE-product level.

This is a catalogue-backed crosswalk, not a cryptographic provenance proof: the package records processed TIFF filenames and timestamps, not the originating SAFE UUID, checksum, or full SAFE name. The match uses the exact Sentinel-1 platform/mode/acquisition-time prefix in `IMG_FNAME`; the source-to-SAFE lineage is strongly supported but not independently hash-verified.

The headline counts and combined spill/seep mask semantics are accurate in the inspected manifests and metadata. The `385` polygon count means **327 author-labeled oil-spill polygons + 58 author-labeled seepage-slick polygons**; both are collapsed to the same positive `SLICK` mask class. They are not 385 independently verified oil spills.

## What was observed

### Repository and archive identity

- Inspected repository at main commit [`1b9a62c30a9da9698eb470562aa976f9bd1e8fc3`](https://github.com/Garcia-INPE/oilspill-detection-dataset/commit/1b9a62c30a9da9698eb470562aa976f9bd1e8fc3), dated 2026-09-12; repository history has 9 commits.
- Zenodo concept ID `22214144` resolves through the API to current record/version `22728926`, DOI `10.5281/zenodo.22728926`, version `0.2.1`, license `CC BY 4.0`. The record lists one ZIP (`oilspill-detection-dataset_20260912-1b9a62c.zip`, 428,775,653 bytes). The archive was not downloaded.
- The repository tree lists 173 input PNG paths, 173 single-channel mask PNG paths, and 173 RGB mask PNG paths. Image/TIFF/GeoJSON binary paths are Git LFS pointers in the GitHub tree (e.g. representative PNG pointer declares 389,068 bytes); the large files are in the Zenodo ZIP. Therefore the GitHub file listing verifies inventory and names, not image pixel values or dimensions.
- Current repo card and README report 800×600 triplets. I did not inspect archive raster headers or image pixels, so the dimensions remain an author assertion in this pass.

### Manifests and source-image metadata

Inspected all three CSV manifests and both 8-bit/16-bit feature tables directly from the pinned repository commit.

- Manifests contain 108 train, 43 validation, and 22 test rows: **173 distinct samples** overall; no duplicate `sample_id`s. The `classe` and `subclasse` fields are blank in every manifest row.
- Filename-prefix grouping yields 16 train source groups, 4 validation groups, and 4 test groups. Pairwise group intersections are empty.
- Each stats table has 385 rows and 67 semicolon-delimited columns. Both tables contain 24 distinct `IMG_XX` groups; every group has exactly one corresponding source filename. The 8-bit and 16-bit filenames differ in processing suffix (`_8b.tif` vs `_NR_Orb_Cal_TC.tif`) but agree on platform, acquisition mode, and timestamp for all 24 groups.
- Every manifest group appears in the source table, and no source-table group is absent from the manifests.
- Across both stats tables, class counts are identical: `OIL SPILL` 327 and `SEEPAGE SLICK` 58.
- The card states mask values `0=SEA`, `1=SLICK`; its source-vector class distinction is retained in the feature table, but binary masks and manifest labels collapse spill and seepage. Thus training/evaluation on the released binary masks cannot measure spill-vs-seep discrimination.

### Acquisition-level checks

For every group, queried the official [Copernicus Data Space OData Products API](https://catalogue.dataspace.copernicus.eu/odata/v1/Products) using `contains(Name, '<platform>_IW_GRDH_1SDV_<timestamp>')`, requesting `Id`, `Name`, and `ContentDate`. Each query returned a standard SAFE and a COG SAFE representation for the same acquisition time. I retained the standard (non-COG) SAFE product name below. All queries matched one standard SAFE record per `IMG_XX`; the 24 full SAFE product names are distinct.

| Group | Split | Matched SAFE product ID | Catalogue sensing start (UTC) |
|---|---|---|---|
| IMG_01 | train | `S1A_IW_GRDH_1SDV_20200117T001541_20200117T001606_030833_03899B_5AEE.SAFE` | 2020-01-17 00:15:41.076 |
| IMG_02 | train | `S1A_IW_GRDH_1SDV_20200210T001540_20200210T001605_031183_0395DE_D14C.SAFE` | 2020-02-10 00:15:40.402 |
| IMG_04 | train | `S1A_IW_GRDH_1SDV_20200609T001544_20200609T001609_032933_03D092_DDFD.SAFE` | 2020-06-09 00:15:44.031 |
| IMG_05 | train | `S1A_IW_GRDH_1SDV_20200621T001544_20200621T001609_033108_03D5E1_330F.SAFE` | 2020-06-21 00:15:44.762 |
| IMG_06 | train | `S1A_IW_GRDH_1SDV_20200715T001545_20200715T001610_033458_03E085_0A22.SAFE` | 2020-07-15 00:15:45.988 |
| IMG_07 | test | `S1A_IW_GRDH_1SDV_20200727T001546_20200727T001611_033633_03E5E3_9C78.SAFE` | 2020-07-27 00:15:46.977 |
| IMG_08 | train | `S1A_IW_GRDH_1SDV_20200808T001547_20200808T001612_033808_03EB6D_9935.SAFE` | 2020-08-08 00:15:47.521 |
| IMG_09 | train | `S1A_IW_GRDH_1SDV_20200820T001548_20200820T001613_033983_03F18E_09C7.SAFE` | 2020-08-20 00:15:48.118 |
| IMG_10 | train | `S1A_IW_GRDH_1SDV_20200901T001548_20200901T001613_034158_03F7BC_A128.SAFE` | 2020-09-01 00:15:48.928 |
| IMG_11 | train | `S1B_IW_GRDH_1SDV_20200320T120027_20200320T120056_020775_027650_1467.SAFE` | 2020-03-20 12:00:27.061 |
| IMG_12 | val | `S1B_IW_GRDH_1SDV_20200425T120028_20200425T120057_021300_0286E8_BC4C.SAFE` | 2020-04-25 12:00:28.170 |
| IMG_13 | val | `S1B_IW_GRDH_1SDV_20200519T120029_20200519T120058_021650_02919F_C9C8.SAFE` | 2020-05-19 12:00:29.310 |
| IMG_14 | train | `S1B_IW_GRDH_1SDV_20200612T120030_20200612T120059_022000_029C10_08E2.SAFE` | 2020-06-12 12:00:30.930 |
| IMG_15 | val | `S1B_IW_GRDH_1SDV_20200624T120031_20200624T120100_022175_02A164_74FC.SAFE` | 2020-06-24 12:00:31.500 |
| IMG_16 | train | `S1B_IW_GRDH_1SDV_20200706T120032_20200706T120101_022350_02A6BC_9CE5.SAFE` | 2020-07-06 12:00:32.166 |
| IMG_17 | test | `S1B_IW_GRDH_1SDV_20200709T001514_20200709T001539_022387_02A7D4_FC7A.SAFE` | 2020-07-09 00:15:14.721 |
| IMG_18 | train | `S1B_IW_GRDH_1SDV_20200718T120032_20200718T120101_022525_02AC08_6314.SAFE` | 2020-07-18 12:00:32.845 |
| IMG_19 | val | `S1B_IW_GRDH_1SDV_20200721T001515_20200721T001540_022562_02AD25_A143.SAFE` | 2020-07-21 00:15:15.379 |
| IMG_20 | test | `S1B_IW_GRDH_1SDV_20200730T120033_20200730T120102_022700_02B15C_9155.SAFE` | 2020-07-30 12:00:33.745 |
| IMG_21 | train | `S1B_IW_GRDH_1SDV_20200802T001516_20200802T001541_022737_02B271_B17F.SAFE` | 2020-08-02 00:15:16.279 |
| IMG_22 | train | `S1B_IW_GRDH_1SDV_20200811T120034_20200811T120103_022875_02B6C6_3E8C.SAFE` | 2020-08-11 12:00:34.431 |
| IMG_23 | train | `S1B_IW_GRDH_1SDV_20200823T120035_20200823T120104_023050_02BC43_2F2A.SAFE` | 2020-08-23 12:00:35.062 |
| IMG_25 | train | `S1B_IW_GRDH_1SDV_20200904T120035_20200904T120104_023225_02C1B5_8D30.SAFE` | 2020-09-04 12:00:35.664 |
| IMG_26 | test | `S1B_IW_GRDH_1SDV_20200907T001518_20200907T001543_023262_02C2CE_E67A.SAFE` | 2020-09-07 00:15:18.168 |

## Reproducible checks

### File evidence and split checks

Sources pinned to the repository commit above:

- [Dataset card](https://github.com/Garcia-INPE/oilspill-detection-dataset/blob/1b9a62c30a9da9698eb470562aa976f9bd1e8fc3/DATASET_CARD.md)
- [Train manifest](https://github.com/Garcia-INPE/oilspill-detection-dataset/blob/1b9a62c30a9da9698eb470562aa976f9bd1e8fc3/splits/train.csv), [validation manifest](https://github.com/Garcia-INPE/oilspill-detection-dataset/blob/1b9a62c30a9da9698eb470562aa976f9bd1e8fc3/splits/val.csv), [test manifest](https://github.com/Garcia-INPE/oilspill-detection-dataset/blob/1b9a62c30a9da9698eb470562aa976f9bd1e8fc3/splits/test.csv)
- [8-bit feature table](https://github.com/Garcia-INPE/oilspill-detection-dataset/blob/1b9a62c30a9da9698eb470562aa976f9bd1e8fc3/CSV/Oil_Stats_manual_windows_8bits_800x600.csv), [16-bit feature table](https://github.com/Garcia-INPE/oilspill-detection-dataset/blob/1b9a62c30a9da9698eb470562aa976f9bd1e8fc3/CSV/Oil_Stats_manual_windows_16bits_800x600.csv)
- [Zenodo concept](https://zenodo.org/records/22214144), [current version](https://zenodo.org/records/22728926)

Both feature tables are semicolon-delimited. For each row, the source-image group is the two-digit prefix in `IMG_FNAME` and the acquisition key is the remaining Sentinel product platform/mode/time prefix before `_8b.tif` or `_NR_Orb_Cal_TC.tif`. Each key was matched against Copernicus OData using `contains(Name, '<key>')`.

Pseudocode used for the overlap audit:

```python
for split in (train, val, test):
    groups[split] = {row.sample_id.split("_TILE_")[0] for row in split}
    products[split] = {crosswalk[group].safe_product_name for group in groups[split]}

for a, b in ((train, val), (train, test), (val, test)):
    assert groups[a].isdisjoint(groups[b])
    assert products[a].isdisjoint(products[b])
```

Observed results: all 173 sample IDs are unique; group intersections are empty for train/val, train/test, and val/test; the catalogue provides exactly one standard SAFE match per each of the 24 groups; 24 distinct SAFE products total; product intersections are empty for all three split pairs (train 16, validation 4, test 4 products).

## Evidence versus author assertions

**Directly checked in files/API:** manifest row counts and group membership; 173 unique sample IDs; both 385-row/67-column tables; 24 source groups and one source filename per group; shared acquisition timestamp/platform/mode keys across bit-depth tables; 327/58 class counts; empty manifest class fields; Git LFS pointer behavior; Zenodo current version/license/archive size; Copernicus product-name and sensing-time matches; no split overlap at source-group and matched SAFE identity level.

**Author-stated, not pixel/archive-verified here:** 800×600 image dimensions; how source TIFFs were generated from the SAFE products; manual interpretation/validation quality and the accuracy of polygon boundaries; precise mask construction and raster alignment; geographic extraction details. The dataset card/record call the groups “source image/acquisition” groups, consistent with the inspected filenames and the recovered catalogue crosswalk, but they do not supply SAFE UUIDs or checksums.

**Paper/supplement:** No paper DOI, supplement, or related-identifier entry was present in the inspected repository `CITATION.cff`, Zenodo record metadata, or repository tree. This release appears documented by its dataset card, README, feature tables, manifests, and benchmark code rather than a linked paper supplement. I did not find a paper supplement to inspect in this pass.

## Conclusion for OceanTrace

The previous open question can be closed with a qualified positive result: **the public Cantarell split is acquisition-disjoint across the currently released 24 `IMG_XX` source groups, based on exact acquisition-time/platform matching to Copernicus SAFE records.** The 173 count and 108/43/22 counts are consistent. The binary task deliberately combines oil-spill and seepage-slick positives; preserve the 327/58 source-label distinction when possible and do not describe the combined mask as verified anthropogenic oil only.

Remaining narrow provenance limitation: the files do not embed original SAFE identifiers, UUIDs, or checksums, so archive-to-product pixel lineage is not proven by source-package metadata alone. The acquisition split conclusion is well-supported by the crosswalk but should be described as “catalogue-matched acquisition-disjoint,” with that limitation available if strict provenance is discussed.
