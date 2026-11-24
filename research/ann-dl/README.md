# OceanTrace — ANN/DL Research Workspace (`research/ann-dl/`)

Oil-spill segmentation, SAR-to-scene provenance reconstruction, and presentation assets for the OceanTrace project.

## Directory Structure

| Folder | Contents |
|---|---|
| `models/` | Single-model training scripts (`train_cbdnet.py`, `train_deeplabv3plus_mobilenetv2.py`, `train_ofcn.py`, `train_shaban_cnn_unet.py`), model definitions (`ofcn_and_shaban_models.py`), shared baseline runner (`baseline_runner.py`), dataset downloader (`download_sos_palsar.py`), manifests, and lockfiles. |
| `scene_matching/` | Full SAR scene-matching & georeferencing pipeline (`scripts/`), verified 3,605-patch WGS84 tables & leak-free `scene_disjoint_split.csv` (`outputs/`), visual spot-checks & forensic sheets (`visuals/`), and `EXPERIMENT_LOG.md`. |
| `presentation/` | Interactive HTML slide decks (`oceantrace-presentation.html`, `index.html`), PowerPoint deck (`ANN_DL_Oil_Slick.pptx`), and SAR/AIS animations (`animations/`). |
| `docs/` | Chronological research notes, AIS coverage audits, and dataset documentation. |
| `Project.md` | High-level research project notes and milestones. |
