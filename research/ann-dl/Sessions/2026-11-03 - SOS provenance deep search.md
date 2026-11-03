# 2026-11-03 — SOS provenance deep search

**Role:** Research sub-agent  
**Scope:** Recover a verifiable patch-to-source-scene mapping for the original CBD-Net / Deep-SAR Oil Spill (SOS) dataset; inspect the original paper, official author/repository distribution, public mirrors, Refined SOS Zenodo release, and distinguish SOS from the CERTH/M4D 1,112-image dataset.  
**Constraint:** Read-only research; no bulk dataset download, account creation, author contact, or publication. No overview or ticket edits.

## Finding

**No actual patch-ID → scene-ID crosswalk was found in the public artifacts inspected.** The search did recover a complete *source-scene inventory*: Dong et al. (2023), Table 1, names 14 PALSAR source scenes and 7 Sentinel-1A scene identifiers with dates and center coordinates. The paper does not associate any patch filename/index with any row. Therefore this is useful provenance context, but cannot support assigning a patch to one of the 21 scenes.

The prior ticket’s statement that recovery is “impossible from public artifacts,” and its assertion that the published split is “strictly a random chip-level split,” go beyond the evidence. I found no documented split algorithm or scene-wise split declaration. The evidence supports: **the inspected releases do not expose the crosswalk; whether original train/test membership is scene-disjoint is unknown, and intra-scene overlap cannot be ruled out.** This does not establish that leakage occurred. A hidden crosswalk or another unsearched artifact may still exist.

### What is established

- CBD-Net’s original SOS is the two-region, two-sensor dataset: Gulf of Mexico ALOS/PALSAR and Persian Gulf Sentinel-1A. The official author page and repository report 3,101 train + 776 test samples for Mexico, and 3,354 train + 839 test for Persian Gulf (8,070 total). They do **not** list scene membership per sample. [Official author page (English)](https://grzy.cug.edu.cn/zhuqiqi/en/zhym/32383/list/index.htm), [official CBD-Net repository README](https://github.com/CUG-URS/Marine-Oil-Spill-Detection-Network-CBDNet).
- The author’s public dataset page gives the archive tree as `SOS/train/{gt,images}` and `SOS/val/{gt,images}` and states academic use only / no commercial use. The repository README instead says train/test. Counts are consistent across the two split labels; the intended semantics/name of the held-out folder therefore need care. [Author SOS dataset page](https://grzy.cug.edu.cn/zhuqiqi/zh_CN/zhym/32367/list/index.htm).
- The original journal article is Zhu et al., *Oil Spill Contextual and Boundary-Supervised Detection Network Based on Marine SAR Images*, IEEE TGRS 60 (2022 issue), DOI [10.1109/TGRS.2021.3115492](https://doi.org/10.1109/TGRS.2021.3115492). IEEE’s abstract page identifies SOS as the manually labeled dataset but does not expose a data-supplement link in the browsed record. [IEEE Xplore record](https://ieeexplore.ieee.org/abstract/document/9568691/citations).
- Dong et al. (2023) explicitly describes SOS as derived from 21 full SAR images, with cropping/rotation/noise processing and 8,070 labeled 256×256 images. It says the underlying imagery is split into 14 ALOS PALSAR and 7 Sentinel-1A scenes and publishes the scene inventory below. It does not give a patch-to-scene mapping. [Publisher paper, *Journal of Marine Science and Engineering* 11(8), 1552](https://www.mdpi.com/2077-1312/11/8/1552), DOI [10.3390/jmse11081552](https://doi.org/10.3390/jmse11081552). The publisher HTML fetch was rate-limited during this run; the indexed full-text result exposed Table 1 and the data discussion, and the full text was also available in ResearchGate’s indexed copy. Treat the scene list below as the table’s author-published inventory, not a newly derived mapping.
- A 2024 Frontiers paper independently repeats the 14 PALSAR + 7 Sentinel-1A, 21-scene, 6,456 intermediate crops, then 8,070 final labeled sample description. It also supplies no file crosswalk. [Frontiers paper, DOI 10.3389/fmars.2024.1481028](https://doi.org/10.3389/fmars.2024.1481028).

## Source-scene inventory (not a patch mapping)

Transcribed from Dong et al. (2023), Table 1, “The composition of the SOS dataset.” The first coordinate is the table’s latitude and the second longitude. Identifiers are preserved as printed; apparent irregularities are flagged below.

| Sensor subset | Scene identifier as printed | Capture date | Center latitude | Center longitude |
|---|---|---:|---:|---:|
| PALSAR | `ALPSRP230200560` | 2010-05-21 | 28.734 | -90.707 |
| PALSAR | `ALPSRP231220540` | 2010-05-28 | 27.739 | -87.821 |
| PALSAR | `ALPSRP231220560` | 2010-05-28 | 28.728 | -88.026 |
| PALSAR | `ALPSRP231220580` | 2010-05-28 | 29.723 | -88.229 |
| PALSAR | `ALPSRP232970570` | 2010-06-09 | 29.224 | -87.056 |
| PALSAR | `ALPSRP232970580` | 2010-06-09 | 29.721 | -87.155 |
| PALSAR | `ALPSRS233043050` | 2010-06-09 | 28.389 | -88.302 |
| PALSAR | `ALPSRP235450560` | 2010-06-26 | 28.728 | -87.488 |
| PALSAR | `ALPSRP237930550` | 2010-07-13 | 28.233 | -87.926 |
| PALSAR | `ALPSRP237930560` | 2010-07-13 | 28.728 | -88.024 |
| PALSAR | `ALPSRP238660500` | 2010-07-18 | 25.758 | -89.029 |
| PALSAR | `ALPSRP238660550` | 2010-07-18 | 28.237 | -89.535 |
| PALSAR | `ALPSRS239753100` | 2010-07-25 | 25.719 | -88.871 |
| PALSAR | `ALPSRP241870520` | 2010-08-09 | 26.749 | -91.371 |
| Sentinel-1A | `IW_GRDH_1SDV_017782_01DCBB_DE28` | 2017-08-05 | 27.311 | 50.597 |
| Sentinel-1A | `IW_GRDH_1SDV_017848_01DEC1_EC32` | 2017-08-09 | 28.495 | 48.995 |
| Sentinel-1A | `IW_GRDH_1SDV_017848_01DEC1_C09A` | 2017-08-09 | 29.002 | 48.660 |
| Sentinel-1A | `IW_GRDH_1SDV_017855_01DEF7_F48C` | 2017-08-10 | 29.439 | 47.535 |
| Sentinel-1A | `IW_GRDH_1SDV_017884_01DFD8_8F93` | 2017-08-12 | 27.014 | 52.812 |
| Sentinel-1A | `IW_GRDH_1SDV_017884_01DFD8_6CAE` | 2017-08-12 | 25.505 | 52.485 |
| Sentinel-1A | `IW_GRDH_1SDV_017921_01EOED DB39` | 2017-08-14 | 28.706 | 46.893 |

**Identifier caveats:** The table has two PALSAR strings beginning `ALPSRS` rather than `ALPSRP`, and a space before `DB39` in the last Sentinel identifier. The Sentinel strings are shortened/nonstandard compared with full Sentinel-1 SAFE product names. Do not silently normalize them or treat the table as a complete product manifest without checking source metadata.

## Patch ID and filename evidence

- **Official author/CBD-Net distribution:** the official page describes pixel-level labels and the split tree/counts, and links the Google Drive and Baidu Drive shares. It does not document a source-scene column or crosswalk. The official code repo has 12 commits (from 2023-12-03 to 2024-04-14) and code/README/log files only; its recursive repository tree contains no dataset, filename manifest, or scene map. The current repository has no release assets. [GitHub commit history](https://github.com/CUG-URS/Marine-Oil-Spill-Detection-Network-CBDNet/commits/master/).
- **Original share manifests:** the CUG page’s Google link resolves to a public `SOS_dataset` Drive folder; static folder metadata showed a nested `test` folder but did not expose a usable full file manifest. The corresponding Baidu form resolves to a share URL; direct Baidu access reset the connection here. The share links are real and currently published, so this audit does **not** count their inaccessible/partial listings as proof that no metadata is present in the complete archives. [Author’s Chinese SOS page](https://grzy.cug.edu.cn/zhuqiqi/zh_CN/zhym/32367/list/index.htm).
- **Official 2023 analysis gives example filenames, not scene IDs:** its PALSAR illustrations refer to files such as `10,777_sat.jpg`, `11,019_sat.jpg`, `11,253_sat.jpg`, `12,037_sat.jpg`, and `33,165_sat.jpg` / `33,291_sat.jpg`; mask-quality examples include `33,282_mask.png` and `33,259_mask.png`. No cited example is joined to one of the 14 scene rows. The numbering is not a safe scene key; inferring group membership from sequential/index-like numbers would be unsupported.
- **Refined SOS on Zenodo:** the record calls itself an improved version of the original SOS and says masks were manually revised. [Zenodo record 15298010](https://zenodo.org/records/15298010), DOI [10.5281/zenodo.15298010](https://doi.org/10.5281/zenodo.15298010). I queried the Zenodo API and range-read only the ZIP central directory (about 1.8 MB from the 1.148 GB image archive; no image payload bulk download). It lists 8,070 PNG chips in `images/train` and `images/val` plus macOS metadata entries; image names are of the form `sentinel_<index>.png` and `palsar_<index>.png`. The central directory contained no source scene/product IDs or acquisition metadata. This verifies absence from the **published image archive’s file paths/names**, not from every pixel, every archive byte, or the authors’ private records.
- **Kaggle mirrors:** search located a “Deep SAR Oil Spill Segmentation Refined” copy whose dataset description points to Refined SOS and repeats its train/val chip counts, and a separate SOS Kaggle dataset card. These are mirrors/cards, not evidence of added provenance; no searchable manifest with a scene crosswalk surfaced. [Refined SOS Kaggle card](https://www.kaggle.com/datasets/bakhtiyar2222/deep-sar-oil-spill-segmentation-refined), [SOS Kaggle card](https://www.kaggle.com/bitsandlayers/sar-oil-spill-segmentation-dataset-sos/discussion).
- **Baidu AI Studio mirror:** the listing identifies itself as “Deep-SAR Oil Spill Dataset (SOS)” and its HTML metadata describes SOS and points back to the CUG page. Its direct page was reachable, but it did not expose a human-readable file manifest through the indexed browser result. It does not establish patch ancestry. [Baidu AI Studio listing](https://aistudio.baidu.com/datasetdetail/145599).
- **Dong et al. correction repo:** [MOSD_LSAR](https://github.com/dongxr2/MOSD_LSAR) README states the project suspended its SOS-label correction because it could not obtain original SAR imagery with copyright permission. It links a Drive archive of data used for its work but gives no patch-to-scene table. This is a separate derivative/correction effort, not the CERTH dataset.

## SOS is not CERTH / M4D (1,112 images)

These are separate datasets with different source collections, time/region, class schema, and file scale:

- **SOS / CBD-Net:** 8,070 256×256 chips, 21 source scenes, ALOS PALSAR Gulf of Mexico Deepwater Horizon period (2010) plus Sentinel-1A Persian Gulf (2017); oil/background pixel masks; research-only distribution stated by CUG.
- **CERTH/M4D Oil Spill Detection Dataset:** approximately 1,112 Sentinel-1 images (the official page rounds to “around 1000” train + 110 test), 1,250×650, 2015-09-28 through 2017-10-31; five pixel classes (sea, oil, look-alike, ship, land) and EMSA CleanSeaNet event context. Official M4D page says about 400 MB and requires an institution-email request with a supervisor for student access. Its terms prohibit redistribution and restrict use to non-commercial academic work. [Official M4D dataset page](https://m4d.iti.gr/oil-spill-detection-dataset/), [official terms](https://mklab.iti.gr/files/oli-spill-detection-terms.pdf), original paper [Krestenitis et al. 2019, DOI 10.3390/rs11151762](https://doi.org/10.3390/rs11151762).
- The 1,112 figure belongs to the CERTH 2019 corpus; SOS papers and CUG pages describe their separate 8,070-chip corpus. Differences in later papers’ image counts (e.g. 1,110) appear to be reporting variation; no evidence found that CERTH’s 1,112 files are SOS chips, or that SOS was derived from CERTH.
- M4D sample filenames/IDs were not inspectable without obtaining the gated data; the official page does not publish a manifest. Do not mix M4D naming, geography, split, or event metadata with SOS.

## Defensible conclusion and use

1. We have a **verified scene inventory**, not a mapping. The 21 scene rows above can support a candidate-scene catalogue for later visual/geospatial matching, but cannot assign even one chip without independent join evidence.
2. The refined archive filenames and central directory preserve sensor family + per-family index + train/val membership, not parent scene IDs. Original CUG page preserves sensor/region split counts and a train/val folder description; code README instead says train/test. Neither source documents scene-disjoint membership.
3. Correct current split claim: **“Scene-level train/test separation is undocumented in the public descriptions inspected, and source scene for each patch is unavailable in the inspected archive names; intra-scene overlap cannot be ruled out.”** Avoid saying the split is proven random or that leakage definitely exists.
4. To move from inventory toward a real patch mapping without inventing one, the remaining viable routes are: (a) inspect the full original Drive/Baidu archive manifest after a compatible access path is available; (b) find an original annotation/export artifact or repository history omitted from the current code tree; or (c) explicitly perform geospatial/pixel registration of individual chips against the 21 original scene products. Route (c) requires acquiring those source products and documenting matching tolerances; no such matching was attempted in this research pass.

## Search and inspection record

Completed in this pass:

- Read the vault `AGENTS.md`, `SOUL.md`, index, OceanTrace `Project.md`, both assigned Wayfinding tickets, dataset profile, and the linked ANN-DL spec plus its two relevant dated Wayfinding sessions.
- Browsed official CUG author pages in English and Chinese; the official GitHub CBD-Net README, full repository tree, and 12-commit history; IEEE publisher record; 2023 publisher-paper indexed content and Table 1; 2024 Frontiers paper; Zenodo landing record and API; Kaggle search results/cards; Baidu AI Studio listing; CERTH official dataset page, terms, email template, and 2019 source paper metadata.
- Inspected the original Google Drive public folder HTML metadata and the Baidu share redirect form fields. Baidu direct access was blocked by connection reset; the Drive static page did not yield a complete file listing. No login, account, or access request was made.
- Range-read the Refined SOS image ZIP central directory only; did not download image payloads, masks, or full archives.
- Searched exact example filenames and known scene IDs across indexed web sources. No public filename-to-source-scene join surfaced.

### Unresolved access gaps

- Whether the complete original CUG archive or Baidu share contains a sidecar/metadata file not exposed by its public webpage/static Drive listing.
- Whether there are IEEE supplemental files available to authenticated subscribers or omitted from the public record; none was linked in the browsed publisher record.
- Whether the full original source imagery can be redistributed/re-downloaded for chip registration; CUG says SOS is for academic use only and the 2023 correction authors report difficulty obtaining original SAR imagery copyright permission.
- Whether original train/test groups were assigned randomly, by acquisition, or by some other design. No source inspected states this.

## Sources

- Zhu et al., CBD-Net / SOS original paper, IEEE Xplore: https://doi.org/10.1109/TGRS.2021.3115492
- CUG URSmart official SOS pages: https://grzy.cug.edu.cn/zhuqiqi/en/zhym/32383/list/index.htm · https://grzy.cug.edu.cn/zhuqiqi/zh_CN/zhym/32367/list/index.htm
- CUG official CBD-Net code and downloads: https://github.com/CUG-URS/Marine-Oil-Spill-Detection-Network-CBDNet
- Dong et al. 2023, scene inventory and analysis: https://doi.org/10.3390/jmse11081552
- Shi et al. 2024, repeated SOS composition: https://doi.org/10.3389/fmars.2024.1481028
- Refined SOS Zenodo: https://doi.org/10.5281/zenodo.15298010 · API: https://zenodo.org/api/records/15298010
- Dong et al. SOS correction project: https://github.com/dongxr2/MOSD_LSAR
- CERTH/M4D official page / terms: https://m4d.iti.gr/oil-spill-detection-dataset/ · https://mklab.iti.gr/files/oli-spill-detection-terms.pdf
- CERTH/M4D paper: https://doi.org/10.3390/rs11151762
