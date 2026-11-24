# Oil-spill segmentation training

Recreate the OceanTrace CBD-Net, DeepLabv3+, and OFCN baselines, or run the Shaban-style CNN gate and U-Net comparison. All four configurations use the **original SOS ALOS PALSAR split** (3,101 training and 776 held-out image–mask pairs). Each patch is 256 × 256. The Refined SOS release in the repository's DVC snapshot has different masks and is a separate dataset.

## Set up from a Git clone

Run these commands from the OceanTrace repository root. The original runs used Python 3.12.12 on Apple Silicon with Metal (MPS). Install Git and [uv](https://docs.astral.sh/uv/getting-started/installation/) first.

```sh
cd models
uv venv --python 3.12.12 .venv
uv pip sync --python .venv/bin/python setup/requirements.lock
uv venv --python 3.12.12 .venv-deeplab
uv pip sync --python .venv-deeplab/bin/python setup/requirements-deeplab.lock

git clone https://github.com/CUG-URS/Marine-Oil-Spill-Detection-Network-CBDNet.git upstream
git -C upstream checkout --detach ba3aa2e854f8e7ff1fd72fbfd5ce37e864c6d7ad
.venv/bin/python setup/download_sos_palsar.py
```

The trainers reuse the pinned CBD-Net checkout for the model or shared helpers. The downloader retrieves the [authors' original files](https://drive.google.com/drive/folders/1KyrtyHkK3IC1_3mUvKA2B2H112uo3J1K) into `original-palsar/{train,test}/`. It checks each file against the committed SHA-256 listing and verifies its size and image format. Rerun it to resume a partial download. A successful run writes `verified-sha256.txt`. The [DagsHub dataset view](https://dagshub.com/rxchitrx/OceanTrace/datasets/dataset/4200/gallery?query=e30=) indexes the same release. See the [authors' usage terms](https://grzy.cug.edu.cn/zhuqiqi/zh_CN/yjgk/32368/list/index.htm) before using or sharing the data.

The default device is `mps`. Use `--device cpu` or `--device cuda` with a compatible PyTorch build on other systems. The lockfiles record the original macOS environments. Numerical results can vary by hardware. CBD-Net and DeepLabv3+ fetch ImageNet encoder weights on first use.

## Run a smoke test

Run the command for the model you want. Smoke tests use three batches per stage and write to separate `smoke*` directories.

```sh
export PYTORCH_ENABLE_MPS_FALLBACK=1
.venv/bin/python -u train_cbdnet.py --smoke-steps 3
.venv-deeplab/bin/python -u train_deeplabv3plus_mobilenetv2.py --smoke-steps 3
.venv/bin/python -u train_ofcn.py --smoke-steps 3
.venv/bin/python -u train_shaban_cnn_unet.py --smoke-steps 3
```

## Train and evaluate

Run the corresponding command in the same shell after its smoke test passes.

```sh
.venv/bin/python -u train_cbdnet.py
.venv-deeplab/bin/python -u train_deeplabv3plus_mobilenetv2.py
.venv/bin/python -u train_ofcn.py
.venv/bin/python -u train_shaban_cnn_unet.py
```

| Experiment | Configuration | Output |
| --- | --- | --- |
| [CBD-Net](https://doi.org/10.1109/TGRS.2021.3115492) | Authors' architecture, ResNet-34 encoder, Dice+BCE as used in the released trainer, up to 80 epochs. The paper describes a boundary-weighted loss. | `run/` |
| [DeepLabv3+](https://doi.org/10.3390/rs11151762) | MobileNetV2 encoder, binary adaptation on PALSAR, up to 80 epochs. The cited paper used five classes on Sentinel-1. | `run-deeplab/` |
| [Bianchi-style OFCN](https://doi.org/10.3390/rs12142260) | OFCN(32), weighted BCE with oil weight 2, up to 80 epochs. This is a PALSAR reimplementation of the segmentation stage. | `run-ofcn/` |
| [Shaban-style CNN + U-Net](https://doi.org/10.3390/s21072351) | CNN gate and a narrower U-Net trained on 64 × 64 crops, up to 40 epochs per stage. Evaluation compares the same U-Net checkpoint with the gate on and off. | `run-shaban/` |

Each full run saves its settings, checkpoints and final `test-metrics.json`. Report oil IoU, Dice/F1, precision and recall on the held-out split. CBD-Net, DeepLabv3+ and OFCN average eight geometric views. Shaban scores every held-out crop with a single view and treats gate rejections as background. Scene separation within the supplied patch split has not been verified.

## Optional MLflow tracking

Add `--mlflow` to a full training command to log settings and results. By default it uses the [OceanTrace DagsHub experiments](https://dagshub.com/rxchitrx/OceanTrace.mlflow). Supply `MLFLOW_TRACKING_USERNAME` and `MLFLOW_TRACKING_PASSWORD` through your environment if you have write access, or set `MLFLOW_TRACKING_URI` to your own MLflow server. The JSON dataset pointer records the indexed snapshot used in the OceanTrace runs. By default checkpoints are saved locally.

## Files

- `train_cbdnet.py`, `train_deeplabv3plus_mobilenetv2.py`, `train_ofcn.py`, and `train_shaban_cnn_unet.py` are the single-model training entry points.
- `ofcn_and_shaban_models.py` defines OFCN, the Shaban-style CNN gate, and U-Net; `baseline_runner.py` holds their shared training/eval helpers.
- `setup/` holds the dataset downloader (`download_sos_palsar.py`), Drive manifest, SHA-256 checksums, DagsHub dataset pointer, and pinned environment lockfiles (`requirements.lock`, `requirements-deeplab.lock`).
