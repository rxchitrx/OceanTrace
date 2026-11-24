"""Train the pinned CBDNet implementation on the original author split."""
import argparse
import hashlib
import json
import math
import os
import random
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import cv2
import numpy as np
import torch

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'original-palsar'
sys.path.insert(0, str(ROOT / 'upstream'))
from data import ImageFolder
from dice_bce_loss import dice_bce_loss
from networks.CBDNet import CBDNet


def pairs(split):
    directory = DATA / split
    images = {p.name.removesuffix('_sat.jpg') for p in directory.glob('*_sat.jpg')}
    masks = {p.name.removesuffix('_mask.png') for p in directory.glob('*_mask.png')}
    return sorted(images & masks, key=int)


def save(state, path):
    temp = path.with_suffix('.tmp')
    torch.save(state, temp)
    temp.replace(path)


def evaluate(model, device, ids):
    """Average the author's eight flips/rotations, then aggregate pixel counts."""
    model.eval()
    tp = fp = fn = tn = 0
    with torch.inference_mode():
        for i, sample in enumerate(ids, 1):
            img = cv2.imread(str(DATA / 'test' / f'{sample}_sat.jpg'))
            target = cv2.imread(str(DATA / 'test' / f'{sample}_mask.png'), cv2.IMREAD_GRAYSCALE) >= 128
            x = torch.from_numpy(img.transpose(2, 0, 1).copy()).to(device, torch.float32)
            x = x / 255 * 3.2 - 1.6
            views = [(k, dims) for k in (0, 1) for dims in ((), (-2,), (-1,), (-2, -1))]
            stacked = torch.stack([x.rot90(k, (-2, -1)).flip(dims) for k, dims in views])
            result = model(stacked).cpu()
            prob = torch.stack([y.flip(dims).rot90(-k, (-2, -1))
                                for y, (k, dims) in zip(result, views)]).mean(0)[0]
            pred = prob.numpy() > 0.5
            tp += int((pred & target).sum())
            fp += int((pred & ~target).sum())
            fn += int((~pred & target).sum())
            tn += int((~pred & ~target).sum())
            if i % 100 == 0:
                print(f'Evaluated {i}/{len(ids)} test images', flush=True)
    oil_iou = tp / max(1, tp + fp + fn)
    background_iou = tn / max(1, tn + fp + fn)
    return dict(test_pairs=len(ids), oil_iou=oil_iou, background_iou=background_iou,
                mean_iou=(oil_iou + background_iou) / 2, oil_dice=2*tp / max(1, 2*tp+fp+fn),
                oil_precision=tp / max(1, tp+fp), oil_recall=tp / max(1, tp+fn),
                accuracy=(tp+tn) / max(1, tp+tn+fp+fn), counts=dict(tp=tp, fp=fp, fn=fn, tn=tn))


@contextmanager
def tracking(args, work, config, start_epoch):
    if not args.mlflow:
        yield None
        return

    import mlflow

    uri = os.environ.get('MLFLOW_TRACKING_URI', 'https://dagshub.com/rxchitrx/OceanTrace.mlflow')
    mlflow.set_tracking_uri(uri)
    reference = work / 'mlflow-run.json'
    if reference.exists():
        saved = json.loads(reference.read_text())
        if saved['tracking_uri'] != uri:
            raise SystemExit('This checkpoint is linked to a different MLflow server.')
        run = mlflow.start_run(run_id=saved['run_id'])
    else:
        mlflow.set_experiment('CBDNet / Original SOS PALSAR')
        run = mlflow.start_run(run_name=f'cbdnet-original-palsar-{args.device}')
    with run:
        if not reference.exists():
            mlflow.log_params({
                **config, 'model': 'CBDNet', 'dataset_version': 'sos-original-palsar-v1',
                'loss': 'Dice+BCE', 'optimizer': 'Adam', 'prediction_threshold': 0.5,
                'test_time_views': 8, 'first_tracked_epoch': start_epoch,
                'dataset_checksums_sha256': hashlib.sha256(
                    (ROOT / 'verified-sha256.txt').read_bytes()
                ).hexdigest(),
            })
            mlflow.log_artifact(str(work / 'config.json'))
            details = (ROOT / 'experiment-notes.md').read_text().strip()
            snapshot = ROOT / 'setup' / 'sos-original-palsar-v1.dagshub.dataset.json'
            fingerprint = hashlib.sha256((ROOT / 'verified-sha256.txt').read_bytes()).hexdigest()
            if snapshot.is_file() and fingerprint == '1111cd0b07ef7cc87e62c68e08f34ae259b1d6f50a31bc1b8cab4f06b839b8d7':
                dataset = json.loads(snapshot.read_text())
                mlflow.log_artifact(str(snapshot))
                mlflow.set_tags({
                    'dagshub.datasets.datasource_id': str(dataset['datasource_id']),
                    'dagshub.datasets.dataset_id': str(dataset['dataset_id']),
                })
                details += f"\n\n[DagsHub dataset snapshot]({dataset['timed_link']}). "
                details += 'Training reads the verified local copy.'
            mlflow.set_tag('mlflow.note.content', details)
            temporary = reference.with_suffix('.tmp')
            temporary.write_text(json.dumps({
                'run_id': run.info.run_id, 'tracking_uri': uri,
            }, indent=2) + '\n')
            temporary.replace(reference)
        print(f'MLflow run: {run.info.run_id}', flush=True)
        yield mlflow


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke-steps', type=int, default=0)
    parser.add_argument('--epochs', type=int, default=80)
    parser.add_argument('--device', choices=('mps', 'cuda', 'cpu'), default='mps')
    parser.add_argument('--mlflow', action='store_true', help='Log this run to MLflow')
    parser.add_argument('--log-checkpoint', action='store_true',
                        help='Upload the best weights as an MLflow artifact after evaluation')
    args = parser.parse_args()
    smoke = args.smoke_steps > 0
    if args.mlflow and smoke:
        parser.error('--mlflow requires a full run')
    if args.log_checkpoint and not args.mlflow:
        parser.error('--log-checkpoint requires --mlflow')
    ids = pairs('train')
    test_ids = pairs('test')
    if smoke:
        ids = ids[:args.smoke_steps * 4]
        if len(ids) < 4:
            raise SystemExit('Need four complete original training pairs')
    else:
        if not (ROOT / 'verified-sha256.txt').is_file() or (len(ids), len(test_ids)) != (3101, 776):
            raise SystemExit('Full training requires the verified 3,101/776 author split')
    seed = 26143
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    cv2.setNumThreads(1)
    device = torch.device(args.device)
    work = ROOT / ('smoke' if smoke else 'run')
    work.mkdir(exist_ok=True)
    config = dict(upstream='ba3aa2e854f8e7ff1fd72fbfd5ce37e864c6d7ad', dataset='Author SOS PALSAR',
                  train_pairs=len(ids), test_pairs=0 if smoke else len(test_ids),
                  device=device.type, seed=seed, torch=torch.__version__, batch=4,
                  initial_lr=2e-4, max_epochs=1 if smoke else args.epochs,
                  manifest_sha256=hashlib.sha256((ROOT / 'setup' / 'drive-manifest.jsonl').read_bytes()).hexdigest())
    (work / 'config.json').write_text(json.dumps(config, indent=2)+'\n')
    print(config, flush=True)
    loader = torch.utils.data.DataLoader(ImageFolder(ids, str(DATA / 'train') + '/'),
                                         batch_size=4, shuffle=False, num_workers=0)
    model = CBDNet().to(device)
    loss_fn = dice_bce_loss()
    optimizer = torch.optim.Adam(model.parameters(), lr=config['initial_lr'])
    print(f'Model parameters: {sum(p.numel() for p in model.parameters()):,}', flush=True)
    best, stale = 100., 0
    start_epoch = 1
    latest = work / 'latest.pt'
    best_path = work / 'best.pt'
    if not smoke and latest.exists():
        state = torch.load(latest, map_location='cpu', weights_only=False)
        if state['config'] != config:
            raise SystemExit('Saved run settings differ. Preserve the existing run before changing settings.')
        model.load_state_dict(state['model'])
        optimizer.load_state_dict(state['optimizer'])
        torch.set_rng_state(state['torch_rng'])
        np.random.set_state(state['numpy_rng'])
        best, stale, start_epoch = state['best'], state['stale'], state['epoch'] + 1
        if state['stop']:
            start_epoch = config['max_epochs'] + 1
    with tracking(args, work, config, start_epoch) as mlflow:
        for epoch in range(start_epoch, config['max_epochs']+1):
            model.train()
            epoch_lr = optimizer.param_groups[0]['lr']
            started = time.monotonic()
            losses = []
            for step, (image, mask) in enumerate(loader, 1):
                optimizer.zero_grad()
                output = model(image.to(device))
                loss = loss_fn(mask.to(device), output)
                value = loss.item()
                if not math.isfinite(value):
                    raise RuntimeError(f'Nonfinite loss at epoch {epoch}, batch {step}')
                loss.backward()
                optimizer.step()
                losses.append(value)
                if step == 1 or step % 50 == 0 or smoke:
                    print(f'Epoch {epoch} batch {step}/{len(loader)} loss={value:.6f} elapsed={time.monotonic()-started:.1f}s', flush=True)
            avg = sum(losses) / len(losses)
            elapsed = time.monotonic()-started
            print(f'Epoch {epoch} mean_loss={avg:.6f} elapsed={elapsed:.1f}s', flush=True)
            stop = False
            if avg < best:
                best, stale = avg, 0
                save(model.state_dict(), best_path)
            else:
                stale += 1
                lr = optimizer.param_groups[0]['lr']
                stop = stale > 6 or (stale > 3 and lr < 5e-7)
                if stale > 3 and not stop:
                    model.load_state_dict(torch.load(best_path, map_location='cpu', weights_only=True))
                    for group in optimizer.param_groups:
                        group['lr'] /= 5
            if not smoke:
                save(dict(epoch=epoch, model=model.state_dict(), optimizer=optimizer.state_dict(),
                          best=best, stale=stale, config=config, stop=stop, torch_rng=torch.get_rng_state(),
                          numpy_rng=np.random.get_state()), latest)
            if mlflow:
                mlflow.log_metrics({'train_loss': avg, 'epoch_seconds': elapsed,
                                    'learning_rate': epoch_lr}, step=epoch)
            if stop:
                break
        model.load_state_dict(torch.load(best_path, map_location='cpu', weights_only=True))
        if smoke:
            print('Smoke test passed: trained and reloaded checkpoint', flush=True)
        else:
            metrics = evaluate(model, device, test_ids)
            (work / 'test-metrics.json').write_text(json.dumps(metrics, indent=2)+'\n')
            print(metrics, flush=True)
            if mlflow:
                mlflow.log_metrics({f'test_{key}': value for key, value in metrics.items()
                                    if key not in ('counts', 'test_pairs')})
                mlflow.log_artifact(str(work / 'test-metrics.json'))
                if args.log_checkpoint:
                    mlflow.log_artifact(str(best_path), artifact_path='checkpoints')


if __name__ == '__main__':
    main()
