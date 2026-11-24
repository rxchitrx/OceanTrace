#!/usr/bin/env python3
"""
OceanTrace — DagsHub + MLflow Backfill & Run Logger for SAR Scene Matching
==========================================================================
1. Backfills all completed scene-matching experiments (Prior SIFT, Round 1, Round 2,
   and Full 8,070-patch v2) from SceneMatchingDiagnostic/ into DagsHub MLflow.
2. Also logs any future run folder that contains results.json / summary.md.

Usage (once your SSD is plugged in):
  # Backfill all 4 historical runs to DagsHub:
  python log_oceantrace_mlflow.py --repo-owner YOUR_DAGSHUB_USER --repo-name OceanTrace --backfill

  # Log a single new run going forward:
  python log_oceantrace_mlflow.py --repo-owner YOUR_DAGSHUB_USER --repo-name OceanTrace \
      --log-dir "/Volumes/APFS/Vault/Projects/College projects/OceanTrace/SceneMatchingDiagnostic/full_v3" \
      --run-name "full_8070_v3_mask_chain" --method "mask_chaining_v3"

  # Dry run (prints what would be logged without uploading):
  python log_oceantrace_mlflow.py --backfill --dry-run
"""
import argparse
import json
import os
import statistics

DIAG_ROOT = "/Volumes/APFS/Vault/Projects/College projects/OceanTrace/SceneMatchingDiagnostic"
EXPERIMENT_NAME = "sar-scene-matching"


def summarize_results_json(results_json_path: str):
    """Compute standardized metrics from a results.json file."""
    rows = json.load(open(results_json_path))
    real = [r for r in rows if r.get("split") in ("train", "val")]
    pos_c = [r for r in rows if r.get("split") == "control_pos"]
    neg_c = [r for r in rows if r.get("split") == "control_neg"]

    hi = [r for r in real if r.get("status") == "matched_high_conf"]
    rv = [r for r in real if r.get("status") == "candidate_review"]
    p_all = [r for r in real if r.get("sensor") == "palsar"]
    s_all = [r for r in real if r.get("sensor") == "sentinel"]
    p_hi = [r for r in hi if r.get("sensor") == "palsar"]
    s_hi = [r for r in hi if r.get("sensor") == "sentinel"]
    s_val_all = [r for r in s_all if r.get("split") == "val"]
    s_val_hi = [r for r in s_hi if r.get("split") == "val"]

    sc_split = {}
    for r in hi:
        sc = r.get("scene", "")
        if sc:
            sc_split.setdefault(sc, [0, 0])[0 if r["split"] == "train" else 1] += 1
    shared_scenes = sum(1 for tr_n, va_n in sc_split.values() if tr_n > 0 and va_n > 0)

    metrics = {
        "total_patches": float(len(real)),
        "matched_total": float(len(hi)),
        "review_total": float(len(rv)),
        "match_rate_pct": round(100.0 * len(hi) / max(len(real), 1), 2),
        "palsar_matched": float(len(p_hi)),
        "palsar_match_rate_pct": round(100.0 * len(p_hi) / max(len(p_all), 1), 2),
        "sentinel_matched": float(len(s_hi)),
        "sentinel_match_rate_pct": round(100.0 * len(s_hi) / max(len(s_all), 1), 2),
        "sentinel_val_match_rate_pct": round(100.0 * len(s_val_hi) / max(len(s_val_all), 1), 2),
        "matched_scenes_count": float(len(sc_split)),
        "shared_train_val_scenes": float(shared_scenes),
        "pos_controls_passed": float(sum(1 for r in pos_c if r.get("control_pass"))),
        "neg_controls_false_accepts": float(sum(1 for r in neg_c if not r.get("control_pass"))),
    }
    if hi:
        metrics["median_native_zncc"] = round(statistics.median(r["native_zncc"] for r in hi), 4)
    if p_hi:
        metrics["palsar_median_native_zncc"] = round(statistics.median(r["native_zncc"] for r in p_hi), 4)
    if s_hi:
        metrics["sentinel_median_native_zncc"] = round(statistics.median(r["native_zncc"] for r in s_hi), 4)
    return metrics


def log_one_run(run_name: str, params: dict, metrics: dict, artifacts: list, tags: dict, dry_run: bool):
    existing_artifacts = [p for p in artifacts if p and os.path.exists(p)]
    if dry_run:
        print(f"\n[DRY RUN] Run: {run_name}")
        print("  Params:   ", params)
        print("  Metrics:  ", metrics)
        print("  Artifacts:", existing_artifacts)
        return

    import mlflow
    with mlflow.start_run(run_name=run_name):
        mlflow.set_tags(tags)
        mlflow.log_params({k: str(v) for k, v in params.items()})
        mlflow.log_metrics(metrics)
        for ap in existing_artifacts:
            mlflow.log_artifact(ap)
    print(f"Logged run '{run_name}' ({len(metrics)} metrics, {len(existing_artifacts)} artifacts).")


def run_backfill(diag_root: str, dry_run: bool):
    # 1. Prior SIFT 50-patch pilot (baseline reference)
    log_one_run(
        run_name="01_pilot50_sift_baseline",
        params={
            "method": "sift_flann_ransac",
            "dataset_scope": "pilot_50",
            "footprints": "native_whole_scene",
            "orientations": "continuous_sift",
            "device": "cpu",
        },
        metrics={
            "total_patches": 50.0,
            "matched_total": 12.0,
            "match_rate_pct": 24.0,
            "palsar_matched": 12.0,
            "palsar_match_rate_pct": 48.0,
            "sentinel_matched": 0.0,
            "sentinel_match_rate_pct": 0.0,
        },
        artifacts=[],
        tags={"stage": "baseline", "sensor_scope": "palsar+sentinel"},
        dry_run=dry_run,
    )

    # 2. Round 1 Despeckled Coarse-to-Fine ZNCC (50-patch pilot)
    log_one_run(
        run_name="02_pilot50_zncc_v1",
        params={
            "method": "despeckled_zncc_v1",
            "dataset_scope": "pilot_50",
            "palsar_footprints": "256,416,512",
            "sentinel_footprints": "256,416,512,1024",
            "orientations": "D4_8",
            "coarse_ds": "palsar=8,sentinel=16",
            "device": "cpu",
        },
        metrics={
            "total_patches": 50.0,
            "matched_total": 22.0,
            "match_rate_pct": 44.0,
            "palsar_matched": 14.0,
            "palsar_match_rate_pct": 56.0,
            "sentinel_matched": 8.0,
            "sentinel_match_rate_pct": 32.0,
            "pos_controls_passed": 4.0,
            "neg_controls_false_accepts": 0.0,
        },
        artifacts=[os.path.join(diag_root, "run_diagnostic.py")],
        tags={"stage": "round1", "sensor_scope": "palsar+sentinel"},
        dry_run=dry_run,
    )

    # 3. Round 2 Dense-Scale + Multi-Sigma ZNCC (50-patch pilot)
    r2_json = os.path.join(diag_root, "results.json")
    r2_metrics = summarize_results_json(r2_json) if os.path.exists(r2_json) else {
        "total_patches": 50.0, "matched_total": 27.0, "match_rate_pct": 54.0,
        "palsar_matched": 14.0, "palsar_match_rate_pct": 56.0,
        "sentinel_matched": 13.0, "sentinel_match_rate_pct": 52.0,
        "pos_controls_passed": 4.0, "neg_controls_false_accepts": 0.0,
    }
    log_one_run(
        run_name="03_pilot50_zncc_v2_dense_scale",
        params={
            "method": "despeckled_zncc_v2_multi_sigma",
            "dataset_scope": "pilot_50",
            "palsar_footprints": "256,416",
            "sentinel_footprints": "256,268,274,322,416,520",
            "orientations": "rot4",
            "refinement": "sigma4_local_scale_then_sigma1.2",
            "device": "cpu",
        },
        metrics=r2_metrics,
        artifacts=[
            os.path.join(diag_root, "summary.md"),
            os.path.join(diag_root, "results.csv"),
            os.path.join(diag_root, "EXPERIMENT_LOG.md"),
            os.path.join(diag_root, "review.html"),
        ],
        tags={"stage": "round2", "sensor_scope": "palsar+sentinel"},
        dry_run=dry_run,
    )

    # 4. Full 8,070-Patch GPU v2 Run (Apple Silicon MPS)
    full_dir = os.path.join(diag_root, "full_v2")
    full_json = os.path.join(full_dir, "results.json")
    full_metrics = summarize_results_json(full_json) if os.path.exists(full_json) else {
        "total_patches": 8070.0, "matched_total": 2882.0, "review_total": 53.0,
        "match_rate_pct": 35.71, "palsar_matched": 1137.0, "palsar_match_rate_pct": 29.33,
        "sentinel_matched": 1745.0, "sentinel_match_rate_pct": 41.62,
        "sentinel_val_match_rate_pct": 75.57, "matched_scenes_count": 20.0,
        "shared_train_val_scenes": 19.0, "pos_controls_passed": 4.0,
        "neg_controls_false_accepts": 0.0,
    }
    full_metrics["runtime_sec"] = 3064.9
    log_one_run(
        run_name="04_full8070_zncc_v2_mps",
        params={
            "method": "despeckled_zncc_v2_multi_sigma",
            "dataset_scope": "full_8070",
            "palsar_footprints": "256,416",
            "sentinel_footprints": "256,320,416,520 (+-10% refine)",
            "orientations": "rot4",
            "coarse_ds": "palsar=8,sentinel=16",
            "device": "mps",
            "mode": "conv2d",
        },
        metrics=full_metrics,
        artifacts=[
            os.path.join(full_dir, "summary.md"),
            os.path.join(full_dir, "results.csv"),
            os.path.join(full_dir, "review_sample.html"),
            os.path.join(diag_root, "run_full_v2.py"),
            os.path.join(diag_root, "EXPERIMENT_LOG.md"),
        ],
        tags={"stage": "full_corpus", "sensor_scope": "palsar+sentinel"},
        dry_run=dry_run,
    )


def main():
    ap = argparse.ArgumentParser(description="Log OceanTrace SAR scene-matching runs to DagsHub + MLflow")
    ap.add_argument("--repo-owner", default=os.environ.get("DAGSHUB_USER", "rxchitrx"), help="DagsHub username")
    ap.add_argument("--repo-name", default=os.environ.get("DAGSHUB_REPO", "OceanTrace"), help="DagsHub repo name")
    ap.add_argument("--experiment", default=EXPERIMENT_NAME, help="MLflow experiment name")
    ap.add_argument("--diag-root", default=DIAG_ROOT, help="Path to SceneMatchingDiagnostic/")
    ap.add_argument("--backfill", action="store_true", help="Backfill all 4 historical runs")
    ap.add_argument("--log-dir", default=None, help="Log a single new run directory containing results.json")
    ap.add_argument("--run-name", default="scene_matching_run", help="MLflow run name when using --log-dir")
    ap.add_argument("--method", default="custom", help="Method tag when using --log-dir")
    ap.add_argument("--local-only", action="store_true", help="Log to local ./mlruns instead of DagsHub")
    ap.add_argument("--dry-run", action="store_true", help="Print metrics/artifacts without logging")
    args = ap.parse_args()

    if not args.backfill and not args.log_dir:
        ap.error("Pass --backfill to log past runs, or --log-dir <folder> to log a new run.")

    if not args.dry_run:
        if args.local_only:
            os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"
            import mlflow
            mlruns_dir = os.path.join(args.diag_root, "mlruns")
            os.makedirs(mlruns_dir, exist_ok=True)
            mlflow.set_tracking_uri(f"file://{mlruns_dir}")
        else:
            import mlflow
            try:
                import dagshub
                dagshub.init(repo_owner=args.repo_owner, repo_name=args.repo_name, mlflow=True)
            except ImportError:
                mlflow.set_tracking_uri(f"https://dagshub.com/{args.repo_owner}/{args.repo_name}.mlflow")
        mlflow.set_experiment(args.experiment)

    if args.backfill:
        run_backfill(args.diag_root, args.dry_run)

    if args.log_dir:
        r_json = os.path.join(args.log_dir, "results.json")
        if not os.path.exists(r_json):
            raise FileNotFoundError(f"Missing {r_json}")
        metrics = summarize_results_json(r_json)
        artifacts = [
            os.path.join(args.log_dir, fn)
            for fn in ("summary.md", "results.csv", "review_sample.html", "review.html")
        ]
        log_one_run(
            run_name=args.run_name,
            params={"method": args.method, "log_dir": os.path.basename(args.log_dir.rstrip("/"))},
            metrics=metrics,
            artifacts=artifacts,
            tags={"stage": "new_experiment"},
            dry_run=args.dry_run,
        )


if __name__ == "__main__":
    main()
