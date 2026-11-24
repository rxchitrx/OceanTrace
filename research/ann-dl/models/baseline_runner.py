"""Shared training, evaluation, and MLflow helpers for train_ofcn.py and train_shaban_cnn_unet.py."""

import argparse
from contextlib import contextmanager
import fcntl
from functools import lru_cache
import hashlib
import json
import math
import os
import random
import time

import cv2
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

from pathlib import Path
from ofcn_and_shaban_models import OFCN, ShabanGate, ShabanUNet, generalized_dice

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'original-palsar'


def pairs(split):
    directory = DATA / split
    images = {p.name.removesuffix('_sat.jpg') for p in directory.glob('*_sat.jpg')}
    masks = {p.name.removesuffix('_mask.png') for p in directory.glob('*_mask.png')}
    return sorted(images & masks, key=int)


def save(state, path):
    temp = path.with_suffix('.tmp')
    torch.save(state, temp)
    temp.replace(path)

SEED = 26143
DATASET = 'sos-original-palsar-v1'
DATASET_SHA256 = '1111cd0b07ef7cc87e62c68e08f34ae259b1d6f50a31bc1b8cab4f06b839b8d7'
EXPERIMENTS = {
    'ofcn': ('OFCN',
             'Bianchi-style OFCN(32) with weighted BCE (oil weight 2). '
             'Trained on native SOS PALSAR patches with paired flips and rotations. '
             'Test masks use eight-view augmentation on each patch.'),
    'shaban': ('Shaban CNN + U-Net',
               'Shaban-style CNN gate with a narrower, padded five-stage U-Net. '
               'Uses nonoverlapping 64x64 crops, generalized Dice, and no Frost filtering. '
               'Both test variants use identical U-Net weights and all held-out pixels.'),
}


@lru_cache(maxsize=128)
def read_image(split, sample, grayscale):
    mode = cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR
    image = cv2.imread(str(DATA / split / f'{sample}_sat.jpg'), mode)
    shape = (256, 256) if grayscale else (256, 256, 3)
    if image is None or image.shape != shape:
        raise ValueError(f'Invalid image for {split}/{sample}')
    return image[..., None] if grayscale else image


def read_mask(split, sample):
    mask = cv2.imread(str(DATA / split / f'{sample}_mask.png'), cv2.IMREAD_GRAYSCALE)
    if mask is None or mask.shape != (256, 256):
        raise ValueError(f'Invalid mask for {split}/{sample}')
    return mask >= 128


def crop64(array, index):
    row, col = divmod(index, 4)
    return array[row * 64:(row + 1) * 64, col * 64:(col + 1) * 64]


def to_tensor(image):
    return torch.from_numpy(np.ascontiguousarray(image.transpose(2, 0, 1))).float() / 255


@lru_cache(maxsize=128)
def training_mask(sample):
    return read_mask('train', sample)


class TrainPatches(Dataset):
    def __init__(self, records, *, ofcn=False, gate=False):
        self.records = records
        self.ofcn = ofcn
        self.gate = gate

    def __len__(self):
        return len(self.records)

    def __getitem__(self, index):
        if self.ofcn:
            sample = self.records[index]
            image = read_image('train', sample, True)
            mask = training_mask(sample)
            rotation = int(torch.randint(4, ()).item())
            image, mask = np.rot90(image, rotation), np.rot90(mask, rotation)
            if torch.rand(()) < 0.5:
                image, mask = np.flip(image, axis=1), np.flip(mask, axis=1)
        else:
            sample, crop_index, label = self.records[index]
            image = crop64(read_image('train', sample, False), crop_index)
            if self.gate:
                return to_tensor(image), label
            mask = crop64(training_mask(sample), crop_index)
        mask_tensor = torch.from_numpy(np.ascontiguousarray(mask[None])).float()
        return to_tensor(image), mask_tensor


def shaban_training_crops(ids):
    groups = [[], []]
    segmentation = []
    for sample in ids:
        mask = read_mask('train', sample)
        for index in range(16):
            oil = crop64(mask, index).mean()
            label = int(oil > 0.01)
            record = (sample, index, label)
            groups[label].append(record)
            if 0.40 <= oil <= 0.60:
                segmentation.append(record)
    count = min(map(len, groups))
    if not count or not segmentation:
        raise ValueError('Need both gate classes and crops with 40–60% oil')
    rng = random.Random(SEED)
    balanced = rng.sample(groups[0], count) + rng.sample(groups[1], count)
    rng.shuffle(balanced)
    rng.shuffle(segmentation)
    return balanced, segmentation


def train_stage(model, dataset, loss_fn, work, device, *, config, stage, tracker):
    stage_dir = work / stage
    stage_dir.mkdir(exist_ok=True)
    options = config['stages'][stage]
    optimizer = torch.optim.Adam(model.parameters(), lr=options['lr'])
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, factor=0.5, patience=3)
    loader = DataLoader(dataset, batch_size=options['batch'], shuffle=True)
    latest, best_path = stage_dir / 'latest.pt', stage_dir / 'best.pt'
    start, best, stale = 1, math.inf, 0
    if latest.exists():
        state = torch.load(latest, map_location='cpu', weights_only=True)
        model.load_state_dict(state['model'])
        optimizer.load_state_dict(state['optimizer'])
        scheduler.load_state_dict(state['scheduler'])
        start, best, stale = state['epoch'] + 1, state['best'], state['stale']
        print(f'{stage} resumed after epoch {start - 1}', flush=True)
    for epoch in range(start, options['epochs'] + 1):
        if stale >= 8:
            break
        torch.manual_seed(SEED + epoch)
        model.train()
        started = time.monotonic()
        total, examples = 0.0, 0
        for step, (image, target) in enumerate(loader, 1):
            optimizer.zero_grad(set_to_none=True)
            loss = loss_fn(model(image.to(device)), target.to(device))
            value = loss.item()
            if not math.isfinite(value):
                raise RuntimeError(f'Nonfinite loss in {stage}, epoch {epoch}, batch {step}')
            loss.backward()
            optimizer.step()
            total += value * len(image)
            examples += len(image)
            if step == 1 or step % 50 == 0 or config['smoke_steps']:
                print(f'{stage} epoch {epoch} batch {step}/{len(loader)} loss={value:.6f}',
                      flush=True)
        average = total / examples
        scheduler.step(average)
        improved = average < best
        best, stale = (average, 0) if improved else (best, stale + 1)
        if improved:
            save(model.state_dict(), best_path)
        if not config['smoke_steps']:
            save(dict(epoch=epoch, best=best, stale=stale, model=model.state_dict(),
                      optimizer=optimizer.state_dict(), scheduler=scheduler.state_dict()), latest)
        elapsed = time.monotonic() - started
        print(f'{stage} epoch {epoch} mean_loss={average:.6f} elapsed={elapsed:.1f}s',
              flush=True)
        if tracker:
            tracker.log_metrics({f'{stage}_train_loss': average,
                                 f'{stage}_epoch_seconds': elapsed}, step=epoch)
    model.load_state_dict(torch.load(best_path, map_location='cpu', weights_only=True))
    model.eval()


def count_pixels(prediction, target):
    return np.array([np.count_nonzero(prediction & target),
                     np.count_nonzero(prediction & ~target),
                     np.count_nonzero(~prediction & target),
                     np.count_nonzero(~prediction & ~target)], dtype=np.int64)


def pixel_metrics(counts, test_pairs):
    tp, fp, fn, tn = map(int, counts)
    oil_iou = tp / max(1, tp + fp + fn)
    background_iou = tn / max(1, tn + fp + fn)
    return dict(test_pairs=test_pairs, oil_iou=oil_iou, background_iou=background_iou,
                mean_iou=(oil_iou + background_iou) / 2, oil_dice=2 * tp / max(1, 2 * tp + fp + fn),
                oil_precision=tp / max(1, tp + fp), oil_recall=tp / max(1, tp + fn),
                accuracy=(tp + tn) / max(1, tp + fp + fn + tn),
                counts=dict(tp=tp, fp=fp, fn=fn, tn=tn))


@torch.inference_mode()
def score_ofcn(model, ids, device):
    counts = np.zeros(4, dtype=np.int64)
    views = [(k, dims) for k in (0, 1) for dims in ((), (-2,), (-1,), (-2, -1))]
    for step, sample in enumerate(ids, 1):
        image = to_tensor(read_image('test', sample, True)).to(device)
        stack = torch.stack([image.rot90(k, (-2, -1)).flip(dims) for k, dims in views])
        outputs = torch.cat([model(batch).sigmoid().cpu() for batch in stack.split(4)])
        restored = [pred.flip(dims).rot90(-k, (-2, -1))
                    for pred, (k, dims) in zip(outputs, views)]
        prediction = torch.stack(restored).mean(0)[0].numpy() > 0.5
        counts += count_pixels(prediction, read_mask('test', sample))
        if step % 100 == 0:
            print(f'Evaluated {step}/{len(ids)} test images', flush=True)
    return {'ofcn': pixel_metrics(counts, len(ids))}


@torch.inference_mode()
def score_shaban(gate, unet, ids, device):
    plain = np.zeros(4, dtype=np.int64)
    gated = np.zeros(4, dtype=np.int64)
    gate_counts = np.zeros(4, dtype=np.int64)
    for step, sample in enumerate(ids, 1):
        image = read_image('test', sample, False)
        mask = read_mask('test', sample)
        crops = torch.stack([to_tensor(crop64(image, index)) for index in range(16)]).to(device)
        targets = np.stack([crop64(mask, index) for index in range(16)])
        gate_pass = gate(crops).argmax(dim=1).cpu().numpy() == 1
        prediction = (unet(crops)[:, 0] > 0).cpu().numpy()
        plain += count_pixels(prediction, targets)
        gated += count_pixels(prediction & gate_pass[:, None, None], targets)
        gate_counts += count_pixels(gate_pass, targets.mean(axis=(1, 2)) > 0.01)
        if step % 100 == 0:
            print(f'Evaluated {step}/{len(ids)} test images', flush=True)
    tp, fp, fn, tn = map(int, gate_counts)
    return {
        'unet_only': pixel_metrics(plain, len(ids)),
        'cnn_plus_unet': pixel_metrics(gated, len(ids)),
        'gate': dict(test_crops=16 * len(ids), accepted_crops=tp + fp,
                     rejected_crops=fn + tn, accuracy=(tp + tn) / max(1, tp + fp + fn + tn),
                     precision=tp / max(1, tp + fp), recall=tp / max(1, tp + fn),
                     specificity=tn / max(1, tn + fp),
                     counts=dict(tp=tp, fp=fp, fn=fn, tn=tn)),
    }


@contextmanager
def tracking(enabled, work, config):
    if not enabled:
        yield None
        return

    import mlflow

    tracking_uri = os.environ.get('MLFLOW_TRACKING_URI', 'https://dagshub.com/rxchitrx/OceanTrace.mlflow')
    mlflow.set_tracking_uri(tracking_uri)
    name, description = EXPERIMENTS[config['baseline']]
    reference = work / 'mlflow-run.json'
    existing = reference.is_file()
    if existing:
        saved = json.loads(reference.read_text())
        if saved['tracking_uri'] != tracking_uri:
            raise SystemExit('The checkpoint is linked to a different MLflow server')
        run = mlflow.start_run(run_id=saved['run_id'])
    else:
        mlflow.set_experiment(f'{name} / Original SOS PALSAR')
        run = mlflow.start_run(run_name=f"{config['baseline']}-original-palsar-{config['device']}")
    with run:
        if not existing:
            notes = description
            snapshot = ROOT / f'{DATASET}.dagshub.dataset.json'
            tags = {'dataset_version': DATASET}
            if snapshot.is_file():
                dataset = json.loads(snapshot.read_text())
                if dataset['dataset_name'] != DATASET or dataset['dataset_id'] != 4200:
                    raise ValueError('Unexpected DagsHub dataset snapshot')
                mlflow.log_artifact(str(snapshot))
                tags.update({'dagshub.datasets.dataset_id': str(dataset['dataset_id']),
                             'dagshub.datasets.datasource_id': str(dataset['datasource_id'])})
                notes += f"\n\n[DagsHub dataset snapshot]({dataset['timed_link']})."
            tags['mlflow.note.content'] = notes
            mlflow.set_tags(tags)
            params = {key: value for key, value in config.items() if key != 'stages'}
            for stage, options in config['stages'].items():
                params.update({f'{stage}_{key}': value for key, value in options.items()})
            mlflow.log_params(params)
            mlflow.log_artifact(str(work / 'config.json'))
            write_json(reference, dict(run_id=run.info.run_id, tracking_uri=tracking_uri))
        print(f'MLflow run: {run.info.run_id}', flush=True)
        yield mlflow


def write_json(path, values):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(values, indent=2) + '\n')
    temporary.replace(path)


def run(args, work, ids, test_ids, fingerprint):
    device = torch.device(args.device)
    smoke = bool(args.smoke_steps)
    if args.baseline == 'ofcn':
        stages = {'ofcn': dict(batch=4, lr=1e-3, epochs=80, loss='weighted_bce',
                              oil_weight=2, base_channels=32)}
        training_sets = {'ofcn': TrainPatches(ids, ofcn=True)}
        descriptions = {'ofcn': (OFCN, nn.BCEWithLogitsLoss(pos_weight=torch.tensor([2.0], device=device)))}
    else:
        gate_crops, unet_crops = shaban_training_crops(ids)
        stages = {'gate': dict(batch=16, lr=5e-5, epochs=40, loss='cross_entropy'),
                  'unet': dict(batch=16, lr=2e-4, epochs=40, loss='generalized_dice',
                               base_channels=16)}
        training_sets = {'gate': TrainPatches(gate_crops, gate=True),
                         'unet': TrainPatches(unet_crops)}
        descriptions = {'gate': (ShabanGate, nn.CrossEntropyLoss()),
                        'unet': (ShabanUNet, generalized_dice)}

    for stage, options in stages.items():
        if smoke:
            options['epochs'] = 1
            dataset = training_sets[stage]
            count = args.smoke_steps * options['batch']
            if len(dataset) < count:
                raise SystemExit(f'{stage} needs {count} training examples for this smoke test')
            dataset.records = dataset.records[:count]
        elif args.epochs:
            options['epochs'] = args.epochs
        options['training_examples'] = len(training_sets[stage])

    config = dict(baseline=args.baseline, device=device.type, seed=SEED,
                  torch=str(torch.__version__), smoke_steps=args.smoke_steps,
                  dataset=DATASET, dataset_checksums_sha256=fingerprint,
                  test_pairs=0 if smoke else len(test_ids),
                  mask_threshold=128, prediction_threshold=0.5,
                  test_views=8 if args.baseline == 'ofcn' else 1,
                  stages=stages)
    config_path = work / 'config.json'
    if not smoke and config_path.is_file() and json.loads(config_path.read_text()) != config:
        raise SystemExit(f'Saved configuration differs in {work}. Resume with the original options.')
    write_json(config_path, config)
    print(json.dumps(config, indent=2), flush=True)
    tracked = args.mlflow or (work / 'mlflow-run.json').exists()
    with tracking(tracked, work, config) as tracker:
        models = {}
        for stage, (build, loss_fn) in descriptions.items():
            torch.manual_seed(SEED)
            model = build().to(device)
            print(f'{stage} parameters: {sum(p.numel() for p in model.parameters()):,}', flush=True)
            train_stage(model, training_sets[stage], loss_fn, work, device,
                        config=config, stage=stage, tracker=tracker)
            models[stage] = model
        if smoke:
            print('Smoke test passed: trained and reloaded all stage checkpoints', flush=True)
            return
        if args.baseline == 'ofcn':
            results = score_ofcn(models['ofcn'], test_ids, device)
        else:
            results = score_shaban(models['gate'], models['unet'], test_ids, device)
        report = work / 'test-metrics.json'
        write_json(report, results)
        if tracker:
            tracker.log_metrics({f'test_{variant}_{key}': value
                                 for variant, metrics in results.items()
                                 for key, value in metrics.items() if key != 'counts'})
            tracker.log_artifact(str(report))
        print(json.dumps(results, indent=2), flush=True)


def run_cli(baseline: str, description: str | None = None):
    parser = argparse.ArgumentParser(description=description or __doc__)
    parser.add_argument('--device', choices=('mps', 'cuda', 'cpu'), default='mps')
    parser.add_argument('--smoke-steps', type=int, default=0, help='Batches per stage in a one-epoch smoke test')
    parser.add_argument('--epochs', type=int, help='Override the full-run epoch cap for each stage')
    parser.add_argument('--mlflow', action='store_true', help='Log to the OceanTrace DagsHub project')
    args = parser.parse_args()
    args.baseline = baseline
    if args.smoke_steps < 0 or (args.epochs is not None and args.epochs < 1):
        parser.error('Invalid epoch or smoke step count')
    if args.smoke_steps and (args.mlflow or args.epochs):
        parser.error('Use --smoke-steps by itself for a local one-epoch check')

    manifest = ROOT / 'verified-sha256.txt'
    fingerprint = hashlib.sha256(manifest.read_bytes()).hexdigest() if manifest.is_file() else None
    ids, test_ids = pairs('train'), pairs('test')
    if fingerprint != DATASET_SHA256 or (len(ids), len(test_ids)) != (3101, 776):
        raise SystemExit('Expected the verified original SOS PALSAR release (3,101 train / 776 test)')
    cv2.setNumThreads(1)
    work = ROOT / f"{'smoke' if args.smoke_steps else 'run'}-{args.baseline}"
    work.mkdir(exist_ok=True)
    with (work / '.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit(f'A trainer is already using {work}') from None
        run(args, work, ids, test_ids, fingerprint)


if __name__ == '__main__':
    raise SystemExit('Run train_ofcn.py or train_shaban_cnn_unet.py directly.')
