# Reproduce published SOS baselines

Date: 2026-11-23. Participants: Rachit and Codex. Source: direct project conversation.

Rachit asked to train published models and examine their outcomes before training OceanTrace's proposed solution. No paper results have been reproduced yet.

Recommended first experiment: CBDNet on the original authors' PALSAR split, using the authors' training and evaluation code. The documented split is 3,101 train and 776 test, with Dice+BCE and an initial learning rate of 2e-4 in the example. Confirm the full settings against the code and paper. Follow with the separate Sentinel-1A experiment. DAENet and its U-Net and DeepLabv3 comparisons are candidates for a second paper, subject to reproducibility checks.

Original SOS and the hosted Refined SOS are distinct releases. A run on Refined SOS can serve as a comparative baseline, but matching split counts do not establish equivalence to the paper's experiment. Record the source revision, data hashes, settings, metrics, and deviations for each run.

Next: verify access to the original PALSAR images and labels and freeze the first experiment's recipe before a short training smoke run.

Sources: [CBDNet author repository](https://github.com/CUG-URS/Marine-Oil-Spill-Detection-Network-CBDNet), [DAENet paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC9601461/).

## Access check and presentation priorities

- The [official SOS Drive](https://drive.google.com/drive/folders/1KyrtyHkK3IC1_3mUvKA2B2H112uo3J1K) served eight 256×256 PALSAR JPEG/PNG pairs from train and eight from test without authentication. Full pagination, acquisition and count verification are still pending.
- Compared original train IDs 10777–10784 and test IDs 10001–10008 to Refined PALSAR indices 0–7 in train and val respectively. The 16 decoded grayscale images and the 16 masks binarized at 128 matched pixel for pixel. This contiguous sample establishes correspondence only for those files. Both local Refined archives matched the [Zenodo checksums](https://zenodo.org/records/15298010). Zenodo reports edits to roughly 38% of train and 50% of validation masks overall.
- Pinned upstream CBDNet revision `ba3aa2e854f8e7ff1fd72fbfd5ce37e864c6d7ad` for recipe inspection. The public code uses Adam, Dice+BCE, initial LR 2e-4, batch size four per CUDA GPU, and up to 80 epochs with early stopping. It also uses image/mask augmentation and separate test-time augmentation. Treat these as code defaults pending comparison against the paper settings. Training has not started.
- User clarified that paper selection should primarily follow the teacher-facing deck. Slides 3–6 of [[College projects/OceanTrace/ANN_DL  Oil Slick (1).pptx|ANN/DL presentation]] cite CBDNet, Krestenitis, Bianchi OFCN, Shaban CNN + U-Net, Chen & Wang Attention U-Net, OSDA-SAM, and Capobianco trajectory forecasting. Prioritize CBDNet first, then verify original code/data access for the deck's segmentation papers. Keep Capobianco in a separate AIS track. DAENet remains optional.

## 2026-11-23 execution and paper reviews

The complete original PALSAR file listing was obtained through Drive pagination: 6,202 train files and 776 images plus 776 masks in the test folders. The listing pairs 3,101 / 776 unique numeric IDs by split. A resumable downloader checks each file's size and image decoding and writes SHA-256 checksums only on full completion. Local working directory: `/Volumes/APFS/Scratch/oceantrace-cbdnet`. No DagsHub upload authorized for these original files.

CBDNet port passed a three-batch, 12-pair MPS smoke test and reloaded its checkpoint. The released script uses Dice+BCE, whereas the paper describes boundary-weighted joint loss. Treat the first experiment as a reproduction of the released code, with the hardware and loader changes documented in the run README. No held-out scoring in the smoke test. The full training command is gated on verified download completion.

### What the teacher-facing papers can support

| Paper | Original experiment | Adapted training for OceanTrace |
|---|---|---|
| [Krestenitis 2019](https://doi.org/10.3390/rs11151762) | Five-class Sentinel-1 collection, 1,002 train and 110 test. CERTH offers institutional access. Exact training implementation unverified. | Binary DeepLabv3+ with MobileNetV2 on Refined SOS. |
| [Bianchi OFCN](https://www.mdpi.com/2072-4292/12/14/2260) | KSAT expert masks and full-scene evaluation. No public exact split, annotations or training code verified. | Reimplement the OFCN segmentor. SOS does not provide the attributes for the separate event categorizer. |
| [Shaban 2021](https://www.mdpi.com/1424-8220/21/7/2351) | Specific Sentinel-1 subset, crop selection and folds unavailable. | Train both the CNN gate and U-Net from 64×64 crops and oil-pixel fractions derived from SOS masks. Compare against U-Net alone on all held-out crops. |
| [Chen and Wang 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9564763/) | Eight-channel polarimetry and wind inputs unavailable as prepared patches. | Compare a grayscale Attention U-Net to a matched U-Net to isolate the gates. |
| [OSDA-SAM](https://doi.org/10.3390/rs18121948) | Custom Sentinel-1 patch collection and author implementation unverified. | Later SAM transfer run. Use the SOS Sentinel subset, single segmentation stage, fixed prompt and optionally derived texture inputs. |
| [Capobianco 2021](https://arxiv.org/abs/2101.02486) | Danish AIS archives reachable. Processed trajectory and fold manifests unavailable. | Separate position-only encoder-decoder benchmark on NOAA AIS with vessel-disjoint splits. |

Use published results for context. Compare adapted segmentors against one another on the same Refined SOS split and foreground metrics. Record any pipeline or input changes. Do not use the SOS labels to infer ship attribution or named look-alike classes. No other paper model was trained in this session.

### Full PALSAR download verified

All 7,754 files (3,101 train pairs and 776 test pairs) were downloaded from the source listings. Byte sizes and decoded dimensions/formats passed, then all 7,754 SHA-256 readback checks passed. Local source files: `/Volumes/APFS/Scratch/oceantrace-cbdnet/original-palsar`.

Full PALSAR release comparison: all 3,877 decoded grayscale images matched their same-split Refined counterparts pixel-for-pixel. At the binary threshold of 128, 1,069/3,101 training masks and 361/776 test masks differ. The report is `/Volumes/APFS/Scratch/oceantrace-cbdnet/original-vs-refined.json`. This comparison covers PALSAR only.

Full CBDNet training started on MPS after the verified download. The released training code's Dice+BCE differs from the boundary-aware joint loss described in the paper. Keep this modeled as the released-code run and log any later paper-loss run separately. The full run writes checkpoints and final scores under `/Volumes/APFS/Scratch/oceantrace-cbdnet/run`.

Epoch 1 completed in 191.9 seconds with mean training loss 0.613965. Best and resumable checkpoints were written before epoch 2 began. No final test metrics yet. Exact decoded grayscale duplicates across the original train/test partitions: zero. Source-scene independence is still unverified.
