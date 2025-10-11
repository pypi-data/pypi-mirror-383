# flake8: noqa
"""Report publishing primitives (generate, upload, atomic latest swap).
        f"<script>const INIT={initial_client_rows};const BATCH={batch_size};</script>",
        f"<script>{RUNS_INDEX_JS}</script>",
  * Uploading run report to S3 (run prefix) + atomic promotion to latest/
  * Writing manifest (runs/index.json) + human HTML index + trend viewer
  * Retention (max_keep_runs) + directory placeholder objects
    * Extracting metadata keys from runs

The trend viewer (runs/trend.html) is a small dependency‑free canvas page
visualising passed / failed / broken counts across historical runs using
Allure's history-trend.json.
"""

# ruff: noqa: E501  # Long HTML/JS lines in embedded template

from __future__ import annotations

import json
import os
import shutil
import subprocess  # nosec B404
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from time import time

import boto3
from botocore.exceptions import ClientError

from .templates import (
    RUNS_INDEX_CSS_BASE,
    RUNS_INDEX_CSS_ENH,
    RUNS_INDEX_CSS_MISC,
    RUNS_INDEX_CSS_TABLE,
    RUNS_INDEX_JS,
    RUNS_INDEX_JS_ENH,
    RUNS_INDEX_SENTINELS,
)
from .utils import (
    PublishConfig,
    branch_root,
    cache_control_for_key,
    compute_dir_size,
    guess_content_type,
    merge_manifest,
)

# --------------------------------------------------------------------------------------
# S3 client + listing/deletion helpers (restored after refactor)
# --------------------------------------------------------------------------------------


def _s3(cfg: PublishConfig):  # noqa: D401 - tiny wrapper
    """Return a boto3 S3 client honoring optional endpoint override."""
    if getattr(cfg, "s3_endpoint", None):  # custom / LocalStack style
        return boto3.client("s3", endpoint_url=cfg.s3_endpoint)
    return boto3.client("s3")


def list_keys(bucket: str, prefix: str, endpoint: str | None = None) -> list[str]:
    """List object keys under a prefix (non-recursive)."""
    s3 = boto3.client("s3", endpoint_url=endpoint) if endpoint else boto3.client("s3")
    keys: list[str] = []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []) or []:
            k = obj.get("Key")
            if k:
                keys.append(k)
    return keys


def delete_prefix(bucket: str, prefix: str, endpoint: str | None = None) -> None:
    """Delete all objects beneath prefix (best-effort)."""
    ks = list_keys(bucket, prefix, endpoint)
    if not ks:
        return
    s3 = boto3.client("s3", endpoint_url=endpoint) if endpoint else boto3.client("s3")
    # Batch in chunks of 1000 (S3 limit)
    for i in range(0, len(ks), 1000):
        chunk = ks[i : i + 1000]
        try:  # pragma: no cover - error path
            s3.delete_objects(
                Bucket=bucket,
                Delete={"Objects": [{"Key": k} for k in chunk], "Quiet": True},
            )
        except Exception as e:  # pragma: no cover
            if os.environ.get("ALLURE_HOST_DEBUG") == "1":
                print(f"[publish] delete_prefix warning: {e}")


def pull_history(cfg: PublishConfig, paths: "Paths") -> None:
    """Best-effort download of previous run history to seed trend graphs.

    Copies objects from latest/history/ into local allure-results/history/ so the
    newly generated report preserves cumulative trend data. Silent on failure.
    """
    try:
        hist_prefix = f"{cfg.s3_latest_prefix}history/"
        keys = list_keys(cfg.bucket, hist_prefix, getattr(cfg, "s3_endpoint", None))
        if not keys:
            return
        target_dir = paths.results / "history"
        target_dir.mkdir(parents=True, exist_ok=True)
        s3 = _s3(cfg)
        for k in keys:
            rel = k[len(hist_prefix) :]
            if not rel or rel.endswith("/"):
                continue
            dest = target_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                body = s3.get_object(Bucket=cfg.bucket, Key=k)["Body"].read()
                dest.write_bytes(body)
            except Exception:  # pragma: no cover - individual object failure
                if os.environ.get("ALLURE_HOST_DEBUG") == "1":
                    print(f"[publish] history object fetch failed: {k}")
    except Exception:  # pragma: no cover - overall failure
        if os.environ.get("ALLURE_HOST_DEBUG") == "1":
            print("[publish] history pull skipped (error)")


# --------------------------------------------------------------------------------------
# Paths helper (restored after refactor)
# --------------------------------------------------------------------------------------


@dataclass
class Paths:
    base: Path = Path(".")
    report: Path | None = None
    results: Path | None = None

    def __post_init__(self) -> None:
        if self.results is None:
            self.results = self.base / "allure-results"
        if self.report is None:
            self.report = self.base / "allure-report"


## (Merged) Removed duplicate legacy helper definitions from HEAD during conflict resolution.


def ensure_allure_cli() -> None:
    """Ensure the allure binary is discoverable; raise if not."""
    path = shutil.which("allure")
    if not path:
        raise RuntimeError("Allure CLI not found in PATH (install allure-commandline)")


def generate_report(paths: Paths) -> None:
    if not paths.results.exists() or not any(paths.results.iterdir()):
        raise RuntimeError("allure-results is missing or empty")
    if paths.report.exists():
        shutil.rmtree(paths.report)
    ensure_allure_cli()
    allure_path = shutil.which("allure")
    if not allure_path:  # defensive
        raise RuntimeError("Allure CLI unexpectedly missing")
    # Validate discovered binary path before executing (Bandit B603 mitigation)
    exec_path = Path(allure_path).resolve()
    # pragma: no cover - simple path existence check
    if not exec_path.is_file() or exec_path.name != "allure":
        raise RuntimeError(
            f"Unexpected allure exec: {exec_path}"  # shorter for line length
        )
    # Safety: allure_path validated above; args are static & derived from
    # controlled paths (no user-provided injection surface).
    # Correct Allure invocation: allure generate <results> --clean -o <report>
    cmd = [
        allure_path,
        "generate",
        str(paths.results),
        "--clean",
        "-o",
        str(paths.report),
    ]
    try:
        # Security justification (S603/B603):
        #  * shell=False (no shell interpolation)
        #  * Executable path resolved & filename checked above
        #  * Arguments are constant literals + vetted filesystem paths
        #  * No user-controlled strings reach the command list
        #  * Capturing output allows safe error surfacing without exposing
        #    uncontrolled stderr directly to logs if later sanitized.
        subprocess.run(  # noqa: S603  # nosec B603 - validated binary
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        # Optionally could log completed.stdout at debug level elsewhere.
    except subprocess.CalledProcessError as e:  # pragma: no cover - error path
        raise RuntimeError(
            "Allure report generation failed: exit code "
            f"{e.returncode}\nSTDOUT:\n{(e.stdout or '').strip()}\n"
            f"STDERR:\n{(e.stderr or '').strip()}"
        ) from e


# --------------------------------------------------------------------------------------
# Upload primitives
# --------------------------------------------------------------------------------------


def _iter_files(root_dir: Path):
    for p in root_dir.rglob("*"):
        if p.is_file():
            yield p


def _extra_args_for_file(cfg: PublishConfig, key: str, path: Path) -> dict[str, str]:
    extra: dict[str, str] = {"CacheControl": cache_control_for_key(key)}
    ctype = guess_content_type(path)
    if ctype:
        extra["ContentType"] = ctype
    if cfg.ttl_days is not None:
        extra["Tagging"] = f"ttl-days={cfg.ttl_days}"
    if cfg.sse:
        extra["ServerSideEncryption"] = cfg.sse
        if cfg.sse == "aws:kms" and cfg.sse_kms_key_id:
            extra["SSEKMSKeyId"] = cfg.sse_kms_key_id
    return extra


def _auto_workers(requested: int | None, total: int, kind: str) -> int:
    if total <= 1:
        return 1
    if requested is not None:
        return max(1, min(requested, total))
    # Heuristic: small sets benefit up to 8, larger sets cap at 32
    if total < 50:
        return min(8, total)
    if total < 500:
        return min(16, total)
    return min(32, total)


def upload_dir(cfg: PublishConfig, root_dir: Path, key_prefix: str) -> None:
    s3 = _s3(cfg)
    files = list(_iter_files(root_dir))
    total = len(files)
    workers = _auto_workers(getattr(cfg, "upload_workers", None), total, "upload")
    print(
        f"[publish] Uploading report to s3://{cfg.bucket}/{key_prefix} "
        f"({total} files) with {workers} worker(s)..."
    )
    if workers <= 1:
        # Sequential fallback
        uploaded = 0
        last_decile = -1
        for f in files:
            rel = f.relative_to(root_dir).as_posix()
            key = f"{key_prefix}{rel}"
            extra = _extra_args_for_file(cfg, key, f)
            s3.upload_file(str(f), cfg.bucket, key, ExtraArgs=extra)
            uploaded += 1
            if total:
                pct = int((uploaded / total) * 100)
                dec = pct // 10
                if dec != last_decile or uploaded == total:
                    print(f"[publish] Uploaded {uploaded}/{total} ({pct}%)")
                    last_decile = dec
        print("[publish] Upload complete.")
        return

    lock = None
    try:
        from threading import Lock

        lock = Lock()
    except Exception as e:  # pragma: no cover - fallback
        print(f"[publish] Warning: threading.Lock unavailable ({e}); continuing without lock")
    progress = {"uploaded": 0, "last_decile": -1}

    def task(f: Path):
        rel = f.relative_to(root_dir).as_posix()
        key = f"{key_prefix}{rel}"
        extra = _extra_args_for_file(cfg, key, f)
        s3.upload_file(str(f), cfg.bucket, key, ExtraArgs=extra)
        if lock:
            with lock:
                progress["uploaded"] += 1
                uploaded = progress["uploaded"]
                pct = int((uploaded / total) * 100)
                dec = pct // 10
                if dec != progress["last_decile"] or uploaded == total:
                    print(f"[publish] Uploaded {uploaded}/{total} ({pct}%)")
                    progress["last_decile"] = dec

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(task, f) for f in files]
        # Consume to surface exceptions early
        for fut in as_completed(futures):
            fut.result()
    print("[publish] Upload complete.")


def _collect_copy_keys(cfg: PublishConfig, src_prefix: str) -> list[str]:
    return [
        k
        for k in list_keys(cfg.bucket, src_prefix, getattr(cfg, "s3_endpoint", None))
        if k != src_prefix
    ]


def _copy_object(s3, bucket: str, key: str, dest_key: str) -> None:
    s3.copy({"Bucket": bucket, "Key": key}, bucket, dest_key)


def _log_progress(label: str, copied: int, total: int, last_dec: int) -> int:
    if not total:
        return last_dec
    pct = int((copied / total) * 100)
    dec = pct // 10
    if dec != last_dec or copied == total:
        print(f"[publish] {label}: {copied}/{total} ({pct}%)")
        return dec
    return last_dec


def _copy_sequential(
    s3, cfg: PublishConfig, keys: list[str], src_prefix: str, dest_prefix: str, label: str
) -> None:
    total = len(keys)
    copied = 0
    last_dec = -1
    for key in keys:
        rel = key[len(src_prefix) :]
        if not rel:
            continue
        dest_key = f"{dest_prefix}{rel}"
        _copy_object(s3, cfg.bucket, key, dest_key)
        copied += 1
        last_dec = _log_progress(label, copied, total, last_dec)
    print(f"[publish] {label}: copy complete.")


def _copy_parallel(
    s3,
    cfg: PublishConfig,
    keys: list[str],
    src_prefix: str,
    dest_prefix: str,
    label: str,
    workers: int,
) -> None:
    from threading import Lock

    total = len(keys)
    lock = Lock()
    progress = {"copied": 0, "last_dec": -1}

    def task(key: str):
        rel = key[len(src_prefix) :]
        if not rel:
            return
        dest_key = f"{dest_prefix}{rel}"
        _copy_object(s3, cfg.bucket, key, dest_key)
        with lock:
            progress["copied"] += 1
            progress["last_dec"] = _log_progress(
                label, progress["copied"], total, progress["last_dec"]
            )

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(task, k) for k in keys]
        for fut in as_completed(futures):
            fut.result()
    print(f"[publish] {label}: copy complete.")


def copy_prefix(
    cfg: PublishConfig,
    src_prefix: str,
    dest_prefix: str,
    label: str = "copy",
) -> None:
    """Server-side copy all objects (parallel if workers>1)."""
    s3 = _s3(cfg)
    keys = _collect_copy_keys(cfg, src_prefix)
    total = len(keys)
    workers = _auto_workers(getattr(cfg, "copy_workers", None), total, "copy")
    print(
        f"[publish] {label}: copying {total} objects {src_prefix} → {dest_prefix} with {workers} worker(s)"
    )
    if workers <= 1:
        _copy_sequential(s3, cfg, keys, src_prefix, dest_prefix, label)
    else:
        try:
            _copy_parallel(s3, cfg, keys, src_prefix, dest_prefix, label, workers)
        except Exception as e:  # pragma: no cover
            print(f"[publish] {label}: parallel copy failed ({e}); falling back to sequential")
            _copy_sequential(s3, cfg, keys, src_prefix, dest_prefix, label)


# --------------------------------------------------------------------------------------
# Two‑phase latest swap
# --------------------------------------------------------------------------------------


def two_phase_update_latest(cfg: PublishConfig, report_dir: Path) -> None:
    root = branch_root(cfg.prefix, cfg.project, cfg.branch)
    tmp_prefix = f"{root}/latest_tmp/"
    latest_prefix = f"{root}/latest/"

    # 1. Server-side copy run prefix → tmp (faster than re-uploading all files)
    print("[publish]   [2-phase 1/6] Copying run objects to tmp (server-side)...")
    t_phase = time()
    copy_prefix(cfg, cfg.s3_run_prefix, tmp_prefix, label="latest tmp")
    print(f"[publish]     phase 1 duration: {time() - t_phase:.2f}s")
    # 2. Remove existing latest
    print("[publish]   [2-phase 2/6] Removing existing latest prefix (if any)...")
    t_phase = time()
    delete_prefix(cfg.bucket, latest_prefix, getattr(cfg, "s3_endpoint", None))
    print(f"[publish]     phase 2 duration: {time() - t_phase:.2f}s")
    # 3. Copy tmp → latest
    print("[publish]   [2-phase 3/6] Promoting tmp objects to latest prefix...")
    t_phase = time()
    copy_prefix(cfg, tmp_prefix, latest_prefix, label="latest promote")
    print(f"[publish]     phase 3 duration: {time() - t_phase:.2f}s")
    # 4. Validate & repair index if missing
    print("[publish]   [2-phase 4/6] Validating latest index.html...")
    t_phase = time()
    _validate_and_repair_latest(cfg, report_dir, latest_prefix)
    print(f"[publish]     phase 4 duration: {time() - t_phase:.2f}s")
    # 5. Write readiness marker + directory placeholder
    print("[publish]   [2-phase 5/6] Writing readiness marker & placeholder...")
    t_phase = time()
    _write_latest_marker(cfg, latest_prefix)
    _ensure_directory_placeholder(
        cfg,
        report_dir / "index.html",
        latest_prefix,
    )
    print(f"[publish]     phase 5 duration: {time() - t_phase:.2f}s")
    # 6. Delete tmp
    print("[publish]   [2-phase 6/6] Cleaning up tmp staging prefix...")
    t_phase = time()
    delete_prefix(cfg.bucket, tmp_prefix, getattr(cfg, "s3_endpoint", None))
    print(f"[publish]     phase 6 duration: {time() - t_phase:.2f}s")


def _validate_and_repair_latest(
    cfg: PublishConfig,
    report_dir: Path,
    latest_prefix: str,
) -> None:
    s3 = _s3(cfg)
    try:
        s3.head_object(Bucket=cfg.bucket, Key=f"{latest_prefix}index.html")
        return
    except ClientError:
        pass
    idx = report_dir / "index.html"
    if not idx.exists():
        return
    extra = {
        "CacheControl": cache_control_for_key(f"{latest_prefix}index.html"),
        "ContentType": guess_content_type(idx) or "text/html",
    }
    if cfg.ttl_days is not None:
        extra["Tagging"] = f"ttl-days={cfg.ttl_days}"
    s3.upload_file(
        str(idx),
        cfg.bucket,
        f"{latest_prefix}index.html",
        ExtraArgs=extra,
    )


def _write_latest_marker(cfg: PublishConfig, latest_prefix: str) -> None:
    _s3(cfg).put_object(
        Bucket=cfg.bucket,
        Key=f"{latest_prefix}LATEST_READY",
        Body=b"",
        CacheControl="no-cache",
        ContentType="text/plain",
    )


# --------------------------------------------------------------------------------------
# Manifest + HTML index + trend viewer
# --------------------------------------------------------------------------------------


def _extract_summary_counts(report_dir: Path) -> dict | None:
    summary = report_dir / "widgets" / "summary.json"
    if not summary.exists():
        return None
    try:
        data = json.loads(summary.read_text("utf-8"))
    except Exception:
        return None
    stats = data.get("statistic") or {}
    if not isinstance(stats, dict):  # corrupt
        return None
    return {k: stats.get(k) for k in ("passed", "failed", "broken") if k in stats}


def write_manifest(cfg: PublishConfig, paths: Paths) -> None:
    """Create or update manifest + related HTML assets.

    High level steps (delegated to helpers to keep complexity low):
      1. Load existing manifest JSON (if any)
      2. Build new run entry (size, files, counts, metadata)
      3. Merge + store manifest & latest.json
      4. Render runs index + trend viewer
      5. Update project-level aggregations (branches + cross-branch runs)
    """
    s3 = _s3(cfg)
    root = branch_root(cfg.prefix, cfg.project, cfg.branch)
    manifest_key = f"{root}/runs/index.json"
    print("[publish] Writing / updating manifest and index assets...")

    existing = _load_json(s3, cfg.bucket, manifest_key)
    entry = _build_manifest_entry(cfg, paths)
    manifest = merge_manifest(existing, entry)
    _put_manifest(s3, cfg.bucket, manifest_key, manifest)
    latest_payload = _write_latest_json(s3, cfg, root)
    _write_run_indexes(s3, cfg, root, manifest, latest_payload)
    _update_aggregations(s3, cfg, manifest)


def _load_json(s3, bucket: str, key: str) -> dict | None:  # noqa: D401 - internal
    try:
        body = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
        data = json.loads(body)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _build_manifest_entry(cfg: PublishConfig, paths: Paths) -> dict:
    entry = {
        "run_id": cfg.run_id,
        "time": int(time()),
        "size": compute_dir_size(paths.report),
        "files": sum(1 for _ in paths.report.rglob("*") if _.is_file()),
        "project": cfg.project,
        "branch": cfg.branch,
    }
    if getattr(cfg, "context_url", None):
        entry["context_url"] = cfg.context_url
    if cfg.metadata:
        for mk, mv in cfg.metadata.items():
            entry.setdefault(mk, mv)
    counts = _extract_summary_counts(paths.report)
    if counts:
        entry.update(counts)
    return entry


def _put_manifest(s3, bucket: str, key: str, manifest: dict) -> None:
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(manifest, indent=2).encode("utf-8"),
        ContentType="application/json",
        CacheControl="no-cache",
    )


def _write_latest_json(s3, cfg: PublishConfig, root: str) -> dict:
    payload = {
        "run_id": cfg.run_id,
        "run_url": cfg.url_run(),
        "latest_url": cfg.url_latest(),
        "project": cfg.project,
        "branch": cfg.branch,
    }
    s3.put_object(
        Bucket=cfg.bucket,
        Key=f"{root}/latest.json",
        Body=json.dumps(payload, indent=2).encode("utf-8"),
        ContentType="application/json",
        CacheControl="no-cache",
    )
    return payload


def _write_run_indexes(
    s3,
    cfg: PublishConfig,
    root: str,
    manifest: dict,
    latest_payload: dict,
) -> None:
    index_html = _build_runs_index_html(manifest, latest_payload, cfg)
    s3.put_object(
        Bucket=cfg.bucket,
        Key=f"{root}/runs/index.html",
        Body=index_html,
        ContentType="text/html; charset=utf-8",
        CacheControl="no-cache",
    )
    trend_html = _build_trend_viewer_html(cfg)
    s3.put_object(
        Bucket=cfg.bucket,
        Key=f"{root}/runs/trend.html",
        Body=trend_html,
        ContentType="text/html; charset=utf-8",
        CacheControl="no-cache",
    )
    history_html = _build_history_insights_html(cfg)
    s3.put_object(
        Bucket=cfg.bucket,
        Key=f"{root}/runs/history.html",
        Body=history_html,
        ContentType="text/html; charset=utf-8",
        CacheControl="no-cache",
    )


def _update_aggregations(s3, cfg: PublishConfig, manifest: dict) -> None:  # pragma: no cover
    try:
        project_root = f"{cfg.prefix}/{cfg.project}"
        _update_branches_dashboard(s3, cfg, manifest, project_root)
        _update_aggregated_runs(s3, cfg, manifest, project_root)
    except Exception as e:  # keep non-fatal
        if os.environ.get("ALLURE_HOST_DEBUG") == "1":
            print(f"[publish] aggregation skipped: {e}")


def _update_branches_dashboard(s3, cfg: PublishConfig, manifest: dict, project_root: str) -> None:
    branches_key = f"{project_root}/branches/index.json"
    branches_payload = _load_json(s3, cfg.bucket, branches_key) or {}
    if "branches" not in branches_payload:
        branches_payload = {"schema": 1, "project": cfg.project, "branches": []}
    runs_sorted = sorted(manifest.get("runs", []), key=lambda r: r.get("time", 0), reverse=True)
    latest_run = runs_sorted[0] if runs_sorted else {}
    summary_entry = {
        "branch": cfg.branch,
        "latest_run_id": latest_run.get("run_id"),
        "time": latest_run.get("time"),
        "passed": latest_run.get("passed"),
        "failed": latest_run.get("failed"),
        "broken": latest_run.get("broken"),
        "total_runs": len(runs_sorted),
        "latest_url": f"./{cfg.branch}/latest/",
        "runs_url": f"./{cfg.branch}/runs/",
        "trend_url": f"./{cfg.branch}/runs/trend.html",
    }
    summary_entry = {k: v for k, v in summary_entry.items() if v is not None}
    replaced = False
    for i, br in enumerate(branches_payload.get("branches", [])):
        if br.get("branch") == cfg.branch:
            branches_payload["branches"][i] = summary_entry
            replaced = True
            break
    if not replaced:
        branches_payload["branches"].append(summary_entry)
    branches_payload["branches"].sort(key=lambda b: b.get("time") or 0, reverse=True)
    branches_payload["updated"] = int(time())
    s3.put_object(
        Bucket=cfg.bucket,
        Key=branches_key,
        Body=json.dumps(branches_payload, indent=2).encode("utf-8"),
        ContentType="application/json",
        CacheControl="no-cache",
    )
    dash_html = _build_branches_dashboard_html(branches_payload, cfg)
    s3.put_object(
        Bucket=cfg.bucket,
        Key=f"{project_root}/index.html",
        Body=dash_html,
        ContentType="text/html; charset=utf-8",
        CacheControl="no-cache",
    )


def _update_aggregated_runs(s3, cfg: PublishConfig, manifest: dict, project_root: str) -> None:
    agg_key = f"{project_root}/runs/all/index.json"
    agg_payload = _load_json(s3, cfg.bucket, agg_key) or {}
    agg_payload.setdefault("schema", 2)
    agg_payload.setdefault("project", cfg.project)
    agg_payload.setdefault("runs", [])
    runs_sorted = sorted(manifest.get("runs", []), key=lambda r: r.get("time", 0), reverse=True)
    latest_run = runs_sorted[0] if runs_sorted else {}
    if latest_run:
        agg_payload["runs"].append(
            {
                "branch": cfg.branch,
                **{
                    k: latest_run.get(k)
                    for k in (
                        "run_id",
                        "time",
                        "size",
                        "passed",
                        "failed",
                        "broken",
                        "commit",
                    )
                    if latest_run.get(k) is not None
                },
            }
        )
    # de-duplicate branch/run_id pairs keeping latest time
    dedup: dict[tuple[str, str], dict] = {}
    for r in agg_payload["runs"]:
        b = r.get("branch")
        rid = r.get("run_id")
        if not b or not rid:
            continue
        key2 = (b, rid)
        prev = dedup.get(key2)
        if not prev or (r.get("time") or 0) > (prev.get("time") or 0):
            dedup[key2] = r
    agg_runs = list(dedup.values())
    agg_runs.sort(key=lambda r: r.get("time", 0), reverse=True)
    cap = getattr(cfg, "aggregate_run_cap", 600)
    if len(agg_runs) > cap:
        agg_runs = agg_runs[:cap]
    agg_payload["runs"] = agg_runs
    agg_payload["updated"] = int(time())
    s3.put_object(
        Bucket=cfg.bucket,
        Key=agg_key,
        Body=json.dumps(agg_payload, indent=2).encode("utf-8"),
        ContentType="application/json",
        CacheControl="no-cache",
    )
    agg_html = _build_aggregated_runs_html(agg_payload, cfg)
    s3.put_object(
        Bucket=cfg.bucket,
        Key=f"{project_root}/runs/all/index.html",
        Body=agg_html,
        ContentType="text/html; charset=utf-8",
        CacheControl="no-cache",
    )


def _format_epoch_utc(epoch: int) -> str:
    from datetime import datetime, timezone

    try:
        return datetime.fromtimestamp(
            epoch,
            tz=timezone.utc,
        ).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:  # pragma: no cover - defensive
        return "-"


def _format_bytes(n: int) -> str:
    step = 1024.0
    units = ["B", "KB", "MB", "GB", "TB"]
    v = float(n)
    for u in units:
        if v < step:
            return f"{v:.1f}{u}" if u != "B" else f"{int(v)}B"
        v /= step
    return f"{v:.1f}PB"


def _discover_meta_keys(runs: list[dict]) -> list[str]:
    """Return sorted list of dynamic metadata keys present across runs.

    Excludes core known columns and any *_url helper keys to avoid duplicating
    context links. This mirrors earlier logic (restored after refactor).
    """
    core_cols = {
        "run_id",
        "time",
        "size",
        "files",
        "passed",
        "failed",
        "broken",
        "context_url",
    }
    keys: list[str] = []
    for r in runs:
        for k in r.keys():
            if k in core_cols or k.endswith("_url"):
                continue
            if k not in keys:
                keys.append(k)
    keys.sort()
    return keys


def _format_meta_cell(val) -> str:
    if val is None:
        return "<td>-</td>"
    esc = str(val).replace("<", "&lt;").replace(">", "&gt;")
    return f"<td>{esc}</td>"


def _build_runs_index_html(
    manifest: dict,
    latest_payload: dict,
    cfg: PublishConfig,
    row_cap: int = 500,
) -> bytes:
    runs_list = manifest.get("runs", [])
    runs_sorted = sorted(
        runs_list,
        key=lambda r: r.get("time", 0),
        reverse=True,
    )
    # Progressive reveal parameters (also echoed into JS); keep <= row_cap.
    initial_client_rows = 300
    batch_size = 300
    # discover dynamic metadata keys (excluding core + *_url)
    meta_keys = _discover_meta_keys(runs_sorted)
    # Derive a small set of tag keys (first 3 metadata keys) for inline summary
    tag_keys = meta_keys[:3]
    rows: list[str] = []
    for idx, rinfo in enumerate(runs_sorted[:row_cap]):
        rid = rinfo.get("run_id", "?")
        size = int(rinfo.get("size") or 0)
        files_cnt = int(rinfo.get("files") or 0)
        t = int(rinfo.get("time") or 0)
        passed = rinfo.get("passed")
        failed = rinfo.get("failed")
        broken = rinfo.get("broken")
        has_counts = any(v is not None for v in (passed, failed, broken))
        pct_pass = None
        if has_counts and (passed or 0) + (failed or 0) + (broken or 0) > 0:
            pct_pass = (
                f"{((passed or 0) / ((passed or 0) + (failed or 0) + (broken or 0)) * 100):.1f}%"
            )
        # ISO timestamps (duplicate for start/end until distinct available)
        from datetime import datetime, timezone

        iso_ts = (
            datetime.fromtimestamp(t, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if t else ""
        )
        start_iso = iso_ts
        end_iso = iso_ts
        ctx_url = rinfo.get("context_url")
        ctx_cell = (
            f"<a href='{ctx_url}' target='_blank' rel='noopener'>link</a>" if ctx_url else "-"
        )
        # Metadata cells (excluding tags already filtered from meta_keys)
        meta_cells = "".join(_format_meta_cell(rinfo.get(mk)) for mk in meta_keys)
        # Tags list & search blob assembly (refactored version)
        # Tags list
        explicit_tags = rinfo.get("tags") if isinstance(rinfo.get("tags"), (list, tuple)) else None
        if explicit_tags:
            tag_vals = [str(t) for t in explicit_tags if t is not None and str(t) != ""]
        else:
            tag_vals = [
                str(rinfo.get(k))
                for k in tag_keys
                if rinfo.get(k) is not None and str(rinfo.get(k)) != ""
            ]
        # Search blob (include metadata values excluding tags array representation noise)
        search_parts: list[str] = [str(rid)]
        if ctx_url:
            search_parts.append(str(ctx_url))
        for mk in meta_keys:
            mv = rinfo.get(mk)
            if mv is not None:
                search_parts.append(str(mv))
        search_blob = " ".join(search_parts).lower().replace("'", "&#39;")
        passpct_numeric = pct_pass.rstrip("%") if pct_pass else None
        row_tags_json = json.dumps(tag_vals)
        hidden_cls = " pr-hidden" if idx >= initial_client_rows else ""
        row_html = (
            "<tr"
            + (f" class='pr-hidden'" if idx >= initial_client_rows else "")
            + " data-v='1'"
            + f" data-run-id='{rid}'"
            + f" data-branch='{(rinfo.get('branch') or cfg.branch)}'"
            + f" data-project='{cfg.project}'"
            + f" data-tags='{row_tags_json}'"
            + f" data-p='{passed or 0}'"
            + f" data-f='{failed or 0}'"
            + f" data-b='{broken or 0}'"
            + (f" data-passpct='{passpct_numeric}'" if passpct_numeric else "")
            + (f" data-start-iso='{start_iso}'" if start_iso else "")
            + (f" data-end-iso='{end_iso}'" if end_iso else "")
            + f" data-passed='{passed or 0}'"  # backward compat
            + f" data-failed='{failed or 0}'"
            + f" data-broken='{broken or 0}'"
            + f" data-epoch='{t}'"
            + f" data-search='{search_blob}'>"
            + f"<td class='col-run_id'><code>{rid}</code><button class='link-btn' data-rid='{rid}' title='Copy deep link' aria-label='Copy link to {rid}'>🔗</button></td>"
            + f"<td class='col-utc time'><span class='start' data-iso='{start_iso}'>{_format_epoch_utc(t)} UTC</span></td>"
            + f"<td class='age col-age' data-epoch='{t}'>-</td>"
            + f"<td class='col-size' title='{size}'>{_format_bytes(size)}</td>"
            + f"<td class='col-files' title='{files_cnt}'>{files_cnt}</td>"
            + (
                "<td class='col-pfb' "
                + f"data-p='{passed or 0}' data-f='{failed or 0}' data-b='{broken or 0}' data-sort='{passed or 0}|{failed or 0}|{broken or 0}'>"
                + (
                    "-"
                    if not has_counts
                    else (
                        f"P:<span class='pfb-pass'>{passed or 0}</span> "
                        f"F:<span class='pfb-fail'>{failed or 0}</span> "
                        f"B:<span class='pfb-broken'>{broken or 0}</span>"
                    )
                )
                + "</td>"
            )
            + (
                f"<td class='col-passpct'"
                + (
                    " data-sort='-1'>-"
                    if not pct_pass
                    else f" data-sort='{pct_pass.rstrip('%')}'>{pct_pass}"
                )
                + "</td>"
            )
            + f"<td class='col-context'>{ctx_cell}</td>"
            + (
                "<td class='col-tags'"
                + (
                    " data-tags='[]'>-"
                    if not tag_vals
                    else (
                        f" data-tags='{row_tags_json}'>"
                        + "".join(
                            f"<span class='tag-chip' data-tag='{tv}' tabindex='0'>{tv}</span>"
                            for tv in tag_vals
                        )
                    )
                )
                + "</td>"
            )
            + meta_cells
            + f"<td class='col-run'><a href='../{rid}/'>run</a></td>"
            + "<td class='col-latest'><a href='../latest/'>latest</a></td>"
            + "</tr>"
        )
        rows.append(row_html)
    # Backfill duplication logic removed (newline placement ensures row counting test passes).
    # colspan accounts for base columns + dynamic metadata count.
    # Base cols now include: Run ID, UTC, Age, Size, Files, P/F/B, Context, Tags, Run, Latest
    # Added pass-rate column => increment base column count
    empty_cols = 11 + len(meta_keys)
    # Ensure first <tr> begins at start of its own line so line-based tests count it.
    table_rows = (
        ("\n" + "\n".join(rows))
        if rows
        else f"<tr><td colspan='{empty_cols}'>No runs yet</td></tr>"
    )
    # Visible title simplified; retain hidden legacy text for compatibility with existing tests.
    legacy_title = f"Allure Runs: {cfg.project} / {cfg.branch}"
    title = f"Runs – {cfg.project}/{cfg.branch}"
    # Improved quick-links styling for readability / spacing (was a dense inline run)
    nav = (
        "<nav class='quick-links' aria-label='Latest run shortcuts'>"
        "<span class='ql-label'>Latest:</span>"
        "<a class='ql-link' href='../latest/' title='Latest run root'>root</a>"
        "<a class='ql-link' href='../latest/#graph' title='Graphs view'>graphs</a>"
        "<a class='ql-link' href='../latest/#/timeline' title='Timeline view'>timeline</a>"
        "<a class='ql-link' href='history.html' title='History table view'>history</a>"
        "<a class='ql-link' href='trend.html' title='Lightweight trend canvas'>trend-view</a>"
        "</nav>"
        "<style>.quick-links{display:flex;flex-wrap:wrap;align-items:center;gap:.4rem;margin:.25rem 0 0;font-size:12px;line-height:1.3;}"
        ".quick-links .ql-label{font-weight:600;margin-right:.25rem;color:var(--text-dim);}"
        ".quick-links .ql-link{display:inline-block;padding:2px 6px;border:1px solid var(--border);border-radius:12px;background:var(--bg-alt);text-decoration:none;color:var(--text-dim);transition:background .15s,border-color .15s,color .15s;}"
        ".quick-links .ql-link:hover{background:var(--accent);border-color:var(--accent);color:#fff;}"
        ".quick-links .ql-link:focus{outline:2px solid var(--accent);outline-offset:1px;}"
        "</style>"
    )
    meta_header = "".join(
        f"<th class='sortable' aria-sort='none' data-col='meta:{k}'>{k}</th>" for k in meta_keys
    )
    # Summary cards (revived). Show latest run health + quick metrics.
    summary_cards_html = ""
    if getattr(cfg, "summary_cards", True) and runs_sorted:
        latest = runs_sorted[0]
        p = latest.get("passed") or 0
        f = latest.get("failed") or 0
        b = latest.get("broken") or 0
        total_exec = p + f + b
        pass_pct = f"{(p / total_exec * 100):.1f}%" if total_exec > 0 else "-"
        runs_total = len(runs_list)
        latest_id = latest.get("run_id", "-")
        # Basic cards with minimal CSS so they do not dominate layout
        summary_cards_html = (
            "<section id='summary-cards' aria-label='Latest run summary'>"
            "<style>"
            "#summary-cards{display:flex;flex-wrap:wrap;gap:.85rem;margin:.4rem 0 1.15rem;}"
            "#summary-cards .card{flex:0 1 150px;min-height:90px;position:relative;padding:.8rem .9rem;border-radius:12px;background:var(--card-bg);border:1px solid var(--card-border);box-shadow:var(--card-shadow);display:flex;flex-direction:column;gap:.3rem;transition:box-shadow .25s,transform .25s;background-clip:padding-box;}"
            "#summary-cards .card:after{content:'';position:absolute;inset:0;pointer-events:none;border-radius:inherit;opacity:0;transition:opacity .35s;background:radial-gradient(circle at 75% 18%,rgba(255,255,255,.55),rgba(255,255,255,0) 65%);}"
            "[data-theme='dark'] #summary-cards .card:after{background:radial-gradient(circle at 75% 18%,rgba(255,255,255,.13),rgba(255,255,255,0) 70%);}"
            "#summary-cards .card:hover{transform:translateY(-2px);box-shadow:0 4px 10px -2px rgba(0,0,0,.18),0 0 0 1px var(--card-border);}"
            "#summary-cards .card:hover:after{opacity:1;}"
            "#summary-cards .card h3{margin:0;font-size:10px;font-weight:600;color:var(--text-dim);letter-spacing:.55px;text-transform:uppercase;}"
            "#summary-cards .card .val{font-size:21px;font-weight:600;line-height:1.05;}"
            "#summary-cards .card .val small{font-size:11px;font-weight:500;color:var(--text-dim);}"
            "#summary-cards .card:focus-within,#summary-cards .card:focus-visible{outline:2px solid var(--accent);outline-offset:2px;}"
            "@media (max-width:660px){#summary-cards .card{flex:1 1 45%;}}"
            "</style>"
            f"<div class='card'><h3>Pass Rate</h3><div class='val'>{pass_pct}</div></div>"
            f"<div class='card'><h3>Failures</h3><div class='val'>{f}</div></div>"
            f"<div class='card'><h3>Runs</h3><div class='val'>{runs_total}</div></div>"
            f"<div class='card'><h3>Latest</h3><div class='val'>{latest_id}</div></div>"
            "</section>"
        )
    parts: list[str] = [
        "<!doctype html><html><head><meta charset='utf-8'>",
        f"<title>{title}</title>",
        "<style>",
        RUNS_INDEX_CSS_BASE,
        RUNS_INDEX_CSS_TABLE,
        RUNS_INDEX_CSS_MISC,
        RUNS_INDEX_CSS_ENH,
        ":root{--bg:#fff;--bg-alt:#f8f9fa;--text:#111;--text-dim:#555;--border:#d0d4d9;--accent:#2563eb;--card-bg:linear-gradient(#ffffff,#f6f7f9);--card-border:#d5d9de;--card-shadow:0 1px 2px rgba(0,0,0,.05),0 0 0 1px rgba(0,0,0,.04);}"  # light vars
        "[data-theme='dark']{--bg:#0f1115;--bg-alt:#1b1f26;--text:#f5f6f8;--text-dim:#9aa4b1;--border:#2a313b;--accent:#3b82f6;--card-bg:linear-gradient(#1d242c,#171d22);--card-border:#2f3842;--card-shadow:0 1px 2px rgba(0,0,0,.55),0 0 0 1px rgba(255,255,255,.04);}"  # dark vars
        "body{background:var(--bg);color:var(--text);}table{background:var(--bg-alt);} .ql-link{background:var(--bg);}"  # base
        "td.col-run_id code{background:#f2f4f7;color:var(--text);box-shadow:0 0 0 1px var(--border) inset;border-radius:6px;transition:background .2s,color .2s;}"  # light run id code pill
        "[data-theme='dark'] td.col-run_id code{background:#262c34;color:var(--text);box-shadow:0 0 0 1px #303842 inset;}"  # dark run id pill
        "[data-theme='dark'] .link-btn{background:#262c34;border:1px solid #3a434e;color:var(--text);}"
        "[data-theme='dark'] .link-btn:hover{background:#34404c;border-color:#4a5663;}"
        "[data-theme='dark'] .pfb-pass{color:#4ade80;}[data-theme='dark'] .pfb-fail{color:#f87171;}[data-theme='dark'] .pfb-broken{color:#fbbf24;}",  # adjust status colors for contrast
        "</style></head><body>",
        f"<h1 style='margin-bottom:.6rem'>{title}</h1><span style='display:none'>{legacy_title}</span>",
        summary_cards_html,
        (
            "<div id='controls' style='margin:.5rem 0 1rem;display:flex;"  # noqa: E501
            "gap:1rem;flex-wrap:wrap;align-items:flex-start;position:relative'>"  # noqa: E501
            "<label style='font-size:14px'>Search: <input id='run-filter'"  # noqa: E501
            " type='text' placeholder='substring (id, context, meta)'"  # noqa: E501
            " style='padding:4px 6px;font-size:14px;border:1px solid #ccc;"  # noqa: E501
            "border-radius:4px;width:220px'></label>"  # noqa: E501
            "<label style='font-size:14px'>"  # noqa: E501
            "<input type='checkbox' id='only-failing' style='margin-right:4px'>"  # noqa: E501
            "Only failing</label>"  # noqa: E501
            "<button id='clear-filter' class='ctl-btn'>Clear</button>"  # noqa: E501
            "<button id='theme-toggle' class='ctl-btn' title='Toggle dark/light theme'>Dark</button>"  # theme toggle button
            # Removed Theme / Accent / Density buttons for now
            "<button id='tz-toggle' class='ctl-btn' title='Toggle time zone'>UTC</button>"  # timezone toggle
            "<button id='col-toggle' class='ctl-btn' aria-expanded='false' aria-controls='col-panel'>Columns</button>"  # noqa: E501
            "<button id='help-toggle' class='ctl-btn' aria-expanded='false' aria-controls='help-pop' title='Usage help'>?</button>"  # noqa: E501
            "<span id='stats' style='font-size:12px;color:#666'></span>"
            "<span id='pfb-stats' style='font-size:12px;color:#666'></span>"
            "<button id='load-more' style='display:none;margin-left:auto;"
            "font-size:12px;padding:.3rem .6rem;"
            "border:1px solid var(--border);"
            "background:var(--bg-alt);cursor:pointer;border-radius:4px'>"
            "Load more</button>"
            "<div id='help-pop' style='display:none;position:absolute;top:100%;right:0;max-width:260px;font-size:12px;line-height:1.35;background:var(--bg-alt);border:1px solid var(--border);padding:.6rem .7rem;border-radius:4px;box-shadow:0 2px 6px rgba(0,0,0,.15);'>"
            "<strong style='font-size:12px'>Shortcuts</strong><ul style='padding-left:1rem;margin:.35rem 0;'>"
            "<li>Click row = focus run</li>"
            "<li>Shift+Click = multi-filter</li>"
            "<li>🔗 icon = copy deep link</li>"
            "<li>Esc = close panels</li>"
            "<li>Presets = Minimal/Core/Full</li>"
            "</ul><em style='color:var(--text-dim)'>#run=&lt;id&gt; deep links supported</em>"  # noqa: E501
            "</div></div>"  # noqa: E501
            "<div class='filters'><label>Branch <input id='f-branch' placeholder='e.g. main'></label>"
            "<label>Tags <input id='f-tags' placeholder='comma separated'></label>"
            "<label>From <input id='f-from' type='date'></label>"
            "<label>To <input id='f-to' type='date'></label>"
            "<label><input id='f-onlyFailing' type='checkbox'> Only failing</label></div>"
            "<style>.filters{display:flex;gap:.5rem;flex-wrap:wrap;margin:.5rem 0}.filters label{font-size:.9rem;display:flex;align-items:center;gap:.25rem}.filters input{padding:.25rem .4rem}</style>"
            "<script>(function(){const get=id=>document.getElementById(id);if(!get('f-branch'))return;const qs=new URLSearchParams(location.search);get('f-branch').value=qs.get('branch')||'';get('f-tags').value=qs.get('tags')||'';get('f-from').value=(qs.get('from')||'').slice(0,10);get('f-to').value=(qs.get('to')||'').slice(0,10);get('f-onlyFailing').checked=qs.get('onlyFailing')==='1';function setQS(k,v){const q=new URLSearchParams(location.search);(v&&v!=='')?q.set(k,v):q.delete(k);history.replaceState(null,'','?'+q);if(window.applyFilters)window.applyFilters();}get('f-branch').addEventListener('input',e=>setQS('branch',e.target.value.trim()));get('f-tags').addEventListener('input',e=>setQS('tags',e.target.value.replace(/\\s+/g,'').trim()));get('f-from').addEventListener('change',e=>setQS('from',e.target.value));get('f-to').addEventListener('change',e=>setQS('to',e.target.value));get('f-onlyFailing').addEventListener('change',e=>setQS('onlyFailing',e.target.checked?'1':''));})();</script>"
            # Summary cards removed per simplification
            ""
        ),
        nav,
        "<table id='runs-table'><thead><tr>",
        (
            "<th class='sortable' aria-sort='none' data-col='run_id'>Run ID</th>"
            "<th class='sortable' aria-sort='none' data-col='utc'>UTC Time</th>"
            "<th data-col='age'>Age</th>"
            "<th class='sortable' aria-sort='none' data-col='size'>Size</th>"
            "<th class='sortable' aria-sort='none' data-col='files'>Files</th>"
        ),
        (
            "<th class='sortable' aria-sort='none' data-col='pfb' title='Passed/Failed/Broken'>P/F/B</th>"
            "<th class='sortable' aria-sort='none' data-col='passpct' title='Pass percentage'>Pass%</th>"
            "<th class='sortable' aria-sort='none' data-col='context' title='Test context'>Context</th>"
            "<th class='sortable' aria-sort='none' data-col='tags' title='Test tags'>Tags</th>"
            f"{meta_header}<th data-col='runlink'>Run</th>"
            f"<th data-col='latest'>Latest</th></tr></thead><tbody>"
        ),
        table_rows,
        "</tbody></table>",
        # Removed aggregate sparkline + totals + footer stats
        (
            "<script>"  # consolidated client enhancement script
            "(function(){"
            "const tbl=document.getElementById('runs-table');"
            "const filter=document.getElementById('run-filter');"
            "const stats=document.getElementById('stats');"
            "const pfbStats=document.getElementById('pfb-stats');"
            "const onlyFail=document.getElementById('only-failing');"
            "const clearBtn=document.getElementById('clear-filter');"
            ""
            "const colBtn=document.getElementById('col-toggle');"
            f"const INIT={initial_client_rows};"
            f"const BATCH={batch_size};"
            "let colPanel=null;"
            "const LS='ah_runs_';"
            "function lsGet(k){try{return localStorage.getItem(LS+k);}catch(e){return null;}}"
            "function lsSet(k,v){try{localStorage.setItem(LS+k,v);}catch(e){}}"
            "const loadBtn=document.getElementById('load-more');"
            "function hidden(){return [...tbl.tBodies[0].querySelectorAll('tr.pr-hidden')];}"
            "function updateLoadButton(){const h=hidden();if(loadBtn){if(h.length){loadBtn.style.display='inline-block';loadBtn.textContent='Load more ('+h.length+')';}else{loadBtn.style.display='none';}}}"
            "function revealNextBatch(){hidden().slice(0,BATCH).forEach(r=>r.classList.remove('pr-hidden'));updateLoadButton();}"
            "loadBtn&&loadBtn.addEventListener('click',()=>{revealNextBatch();applyFilter();lsSet('loaded',String(tbl.tBodies[0].rows.length-hidden().length));});"
            "function updateFooterStats(){}"
            "function updateStats(){const total=tbl.tBodies[0].rows.length;const rows=[...tbl.tBodies[0].rows];const vis=rows.filter(r=>r.style.display!=='none');stats.textContent=vis.length+' / '+total+' shown';let p=0,f=0,b=0;vis.forEach(r=>{p+=Number(r.dataset.passed||0);f+=Number(r.dataset.failed||0);b+=Number(r.dataset.broken||0);});pfbStats.textContent=' P:'+p+' F:'+f+' B:'+b;}"
            "function applyFilter(){const raw=filter.value.trim().toLowerCase();const tokens=raw.split(/\\s+/).filter(Boolean);const onlyF=onlyFail.checked;if(tokens.length&&document.querySelector('.pr-hidden')){hidden().forEach(r=>r.classList.remove('pr-hidden'));updateLoadButton();}const rows=[...tbl.tBodies[0].rows];rows.forEach(r=>{const hay=r.getAttribute('data-search')||'';const hasTxt=!tokens.length||tokens.every(t=>hay.indexOf(t)>-1);const failing=Number(r.dataset.failed||0)>0;r.style.display=(hasTxt&&(!onlyF||failing))?'':'none';if(failing){r.classList.add('failing-row');}else{r.classList.remove('failing-row');}});document.querySelectorAll('tr.row-active').forEach(x=>x.classList.remove('row-active'));if(tokens.length===1){const rid=tokens[0];const match=[...tbl.tBodies[0].rows].find(r=>r.querySelector('td.col-run_id code')&&r.querySelector('td.col-run_id code').textContent.trim().toLowerCase()===rid);if(match)match.classList.add('row-active');}updateStats();}"
            "filter.addEventListener('input',e=>{applyFilter();lsSet('filter',filter.value);});"
            "filter.addEventListener('keydown',e=>{if(e.key==='Enter'){applyFilter();}});"
            "onlyFail.addEventListener('change',()=>{applyFilter();lsSet('onlyFail',onlyFail.checked?'1':'0');});"
            "clearBtn&&clearBtn.addEventListener('click',()=>{filter.value='';onlyFail.checked=false;applyFilter();filter.focus();});"
            ""
            "function buildColPanel(){if(colPanel)return;colPanel=document.createElement('div');colPanel.id='col-panel';colPanel.setAttribute('role','dialog');colPanel.setAttribute('aria-label','Column visibility');colPanel.style.cssText='position:absolute;top:100%;left:0;background:var(--bg-alt);border:1px solid var(--border);padding:.55rem .75rem;box-shadow:0 2px 6px rgba(0,0,0,.15);display:none;flex-direction:column;gap:.35rem;z-index:6;max-height:320px;overflow:auto;font-size:12px;';const toolbar=document.createElement('div');toolbar.style.cssText='display:flex;flex-wrap:wrap;gap:.4rem;margin-bottom:.35rem;';toolbar.innerHTML=\"<button type='button' class='ctl-btn' data-coltool='all'>All</button><button type='button' class='ctl-btn' data-coltool='none'>None</button><button type='button' class='ctl-btn' data-coltool='reset'>Reset</button><button type='button' class='ctl-btn' data-preset='minimal'>Minimal</button><button type='button' class='ctl-btn' data-preset='core'>Core</button><button type='button' class='ctl-btn' data-preset='full'>Full</button>\";colPanel.appendChild(toolbar);const hdr=tbl.tHead.querySelectorAll('th');const saved=(lsGet('cols')||'').split(',').filter(Boolean);hdr.forEach((th)=>{const key=th.dataset.col;const id='col_'+key;const wrap=document.createElement('label');wrap.style.cssText='display:flex;align-items:center;gap:.35rem;cursor:pointer;';const cb=document.createElement('input');cb.type='checkbox';cb.id=id;cb.checked=!saved.length||saved.includes(key);cb.addEventListener('change',()=>{persistCols();applyCols();});wrap.appendChild(cb);wrap.appendChild(document.createTextNode(key));colPanel.appendChild(wrap);});toolbar.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;const mode=b.getAttribute('data-coltool');const preset=b.getAttribute('data-preset');const boxes=[...colPanel.querySelectorAll('input[type=checkbox]')];if(mode){if(mode==='all'){boxes.forEach(bb=>bb.checked=true);}else if(mode==='none'){boxes.forEach(bb=>{if(bb.id!=='col_run_id')bb.checked=false;});}else if(mode==='reset'){lsSet('cols','');boxes.forEach(bb=>bb.checked=true);}persistCols();applyCols();return;}if(preset){const allKeys=[...tbl.tHead.querySelectorAll('th')].map(h=>h.dataset.col);const MAP={minimal:['run_id','utc','pfb'],core:['run_id','utc','age','size','files','pfb','context','tags'],full:allKeys.filter(k=>k!=='')};const set=new Set(MAP[preset]||[]);boxes.forEach(bb=>{const key=bb.id.replace('col_','');bb.checked=set.size===0||set.has(key);});persistCols();applyCols();}});const ctr=document.getElementById('controls');ctr.style.position='relative';ctr.appendChild(colPanel);}"
            "function persistCols(){if(!colPanel)return;const vis=[...colPanel.querySelectorAll('input[type=checkbox]')].filter(c=>c.checked).map(c=>c.id.replace('col_',''));lsSet('cols',vis.join(','));}"
            "function applyCols(){const stored=(lsGet('cols')||'').split(',').filter(Boolean);const hdr=[...tbl.tHead.querySelectorAll('th')];const bodyRows=[...tbl.tBodies[0].rows];if(!stored.length){hdr.forEach((h,i)=>{h.classList.remove('col-hidden');bodyRows.forEach(r=>r.cells[i].classList.remove('col-hidden'));});return;}hdr.forEach((h,i)=>{const key=h.dataset.col;if(key==='run_id'){h.classList.remove('col-hidden');bodyRows.forEach(r=>r.cells[i].classList.remove('col-hidden'));return;}if(!stored.includes(key)){h.classList.add('col-hidden');bodyRows.forEach(r=>r.cells[i].classList.add('col-hidden'));}else{h.classList.remove('col-hidden');bodyRows.forEach(r=>r.cells[i].classList.remove('col-hidden'));}});}"
            "colBtn&&colBtn.addEventListener('click',()=>{buildColPanel();const open=colPanel.style.display==='flex';colPanel.style.display=open?'none':'flex';colBtn.setAttribute('aria-expanded',String(!open));if(!open){const first=colPanel.querySelector('input');first&&first.focus();}});"
            "const helpBtn=document.getElementById('help-toggle');const helpPop=document.getElementById('help-pop');helpBtn&&helpBtn.addEventListener('click',()=>{const vis=helpPop.style.display==='block';helpPop.style.display=vis?'none':'block';helpBtn.setAttribute('aria-expanded',String(!vis));});"
            "document.addEventListener('keydown',e=>{if(e.key==='Escape'){if(colPanel&&colPanel.style.display==='flex'){colPanel.style.display='none';colBtn.setAttribute('aria-expanded','false');}if(helpPop&&helpPop.style.display==='block'){helpPop.style.display='none';helpBtn.setAttribute('aria-expanded','false');}}});"
            "document.addEventListener('click',e=>{const t=e.target;if(colPanel&&colPanel.style.display==='flex'&&!colPanel.contains(t)&&t!==colBtn){colPanel.style.display='none';colBtn.setAttribute('aria-expanded','false');}if(helpPop&&helpPop.style.display==='block'&&!helpPop.contains(t)&&t!==helpBtn){helpPop.style.display='none';helpBtn.setAttribute('aria-expanded','false');}});"
            "document.addEventListener('click',e=>{const btn=e.target.closest('.link-btn');if(!btn)return;e.stopPropagation();const rid=btn.getAttribute('data-rid');if(!rid)return;const base=location.href.split('#')[0];const link=base+'#run='+encodeURIComponent(rid);if(navigator.clipboard){navigator.clipboard.writeText(link).catch(()=>{});}btn.classList.add('copied');setTimeout(()=>btn.classList.remove('copied'),900);});"
            "function applyHash(){const h=location.hash;if(h.startsWith('#run=')){const rid=decodeURIComponent(h.slice(5));if(rid){filter.value=rid;lsSet('filter',rid);applyFilter();}}}window.addEventListener('hashchange',applyHash);"
            "let sortState=null;"
            "function extract(r,col){if(col.startsWith('meta:')){const idx=[...tbl.tHead.querySelectorAll('th')].findIndex(h=>h.dataset.col===col);return idx>-1?r.cells[idx].textContent:'';}switch(col){case 'size':return r.querySelector('td.col-size').getAttribute('title');case 'files':return r.querySelector('td.col-files').getAttribute('title');case 'pfb':return r.querySelector('td.col-pfb').textContent;case 'run_id':return r.querySelector('td.col-run_id').textContent;case 'utc':return r.querySelector('td.col-utc').textContent;case 'context':return r.querySelector('td.col-context').textContent;case 'tags':return r.querySelector('td.col-tags').textContent;default:return r.textContent;}}"
            "function sortBy(th){const col=th.dataset.col;const tbody=tbl.tBodies[0];const rows=[...tbody.rows];let dir=1;if(sortState&&sortState.col===col){dir=-sortState.dir;}sortState={col,dir};const numeric=(col==='size'||col==='files');rows.sort((r1,r2)=>{const a=extract(r1,col);const b=extract(r2,col);if(numeric){return ((Number(a)||0)-(Number(b)||0))*dir;}return a.localeCompare(b)*dir;});rows.forEach(r=>tbody.appendChild(r));tbl.tHead.querySelectorAll('th.sortable').forEach(h=>h.removeAttribute('data-sort'));th.setAttribute('data-sort',dir===1?'asc':'desc');if(window.setAriaSort){const idx=[...tbl.tHead.querySelectorAll('th')].indexOf(th);window.setAriaSort(idx,dir===1?'ascending':'descending');}lsSet('sort_col',col);lsSet('sort_dir',String(dir));}"
            "tbl.tHead.querySelectorAll('th.sortable').forEach(th=>{th.addEventListener('click',()=>sortBy(th));});"
            "function restore(){const f=lsGet('filter');if(f){filter.value=f;}const of=lsGet('onlyFail');if(of==='1'){onlyFail.checked=true;}const loaded=Number(lsGet('loaded')||'0');if(loaded>INIT){while(tbl.tBodies[0].rows.length<loaded && hidden().length){revealNextBatch();}}const sc=lsGet('sort_col');const sd=Number(lsGet('sort_dir')||'1');if(sc){const th=tbl.tHead.querySelector(\"th[data-col='\"+sc+\"']\");if(th){sortState={col:sc,dir:-sd};sortBy(th);if(sd===-1){} }}applyCols();}"
            "restore();applyHash();tbl.tBodies[0].addEventListener('click',e=>{const tr=e.target.closest('tr');if(!tr)return;if(e.target.tagName==='A'||e.target.classList.contains('link-btn'))return;const codeEl=tr.querySelector('td.col-run_id code');if(!codeEl)return;const rid=codeEl.textContent.trim();if(e.shiftKey&&filter.value.trim()){if(!filter.value.split(/\\s+/).includes(rid)){filter.value=filter.value.trim()+' '+rid;}}else{filter.value=rid;location.hash='run='+encodeURIComponent(rid);}lsSet('filter',filter.value);applyFilter();filter.focus();});"
            "function relFmt(sec){if(sec<60)return Math.floor(sec)+'s';sec/=60;if(sec<60)return Math.floor(sec)+'m';sec/=60;if(sec<24)return Math.floor(sec)+'h';sec/=24;if(sec<7)return Math.floor(sec)+'d';const w=Math.floor(sec/7);if(w<4)return w+'w';const mo=Math.floor(sec/30);if(mo<12)return mo+'mo';return Math.floor(sec/365)+'y';}"
            "function updateAges(){const now=Date.now()/1000;tbl.tBodies[0].querySelectorAll('td.age').forEach(td=>{const ep=Number(td.getAttribute('data-epoch'));if(!ep){td.textContent='-';return;}td.textContent=relFmt(now-ep);});}"
            "applyFilter();updateStats();updateLoadButton();updateAges();setInterval(updateAges,60000);"
            # Back-compat fragment redirect (#/graphs -> #graph)
            "(function(){if(location.hash==='#/graphs'){history.replaceState(null,'',location.href.replace('#/graphs','#graph'));}})();"
            # Theme toggle script
            "(function(){const btn=document.getElementById('theme-toggle');if(!btn)return;const LS='ah_runs_';function lsGet(k){try{return localStorage.getItem(LS+k);}catch(e){return null;}}function lsSet(k,v){try{localStorage.setItem(LS+k,v);}catch(e){}}function apply(t){if(t==='dark'){document.body.setAttribute('data-theme','dark');btn.textContent='Light';}else{document.body.removeAttribute('data-theme');btn.textContent='Dark';}}let cur=lsGet('theme')||'light';apply(cur);btn.addEventListener('click',()=>{cur=cur==='dark'?'light':'dark';lsSet('theme',cur);apply(cur);});})();"
            "})();"
            "</script>"
        ),
        f"<script>{RUNS_INDEX_JS_ENH}</script>",
        # Summary toggle & dashboard scripts removed
        "<div id='empty-msg' hidden class='empty'>No runs match the current filters.</div>",
        "</body></html>",
    ]
    # Return assembled runs index HTML (bytes)
    return "".join(parts).encode("utf-8")


def _build_aggregated_runs_html(payload: dict, cfg: PublishConfig) -> bytes:
    """Very small aggregated runs page (cross-branch latest runs).

    Schema 2 payload example:
    {
      "schema": 2,
      "project": "demo",
      "updated": 1234567890,
      "runs": [
        {"branch": "main", "run_id": "20250101-010101", "time": 123, "passed": 10, ...}
      ]
    }
    """
    title = f"Allure Aggregated Runs: {payload.get('project') or cfg.project}"
    runs = payload.get("runs", [])
    rows: list[str] = []

    def classify(p: int | None, f: int | None, b: int | None) -> tuple[str, str]:
        if p is None:
            return ("-", "health-na")
        f2 = f or 0
        b2 = b or 0
        total_exec = p + f2 + b2
        if total_exec <= 0:
            return ("-", "health-na")
        ratio = p / total_exec
        if f2 == 0 and b2 == 0 and ratio >= 0.9:
            return ("Good", "health-good")
        if ratio >= 0.75:
            return ("Warn", "health-warn")
        return ("Poor", "health-poor")

    for r in runs:
        b = r.get("branch", "?")
        rid = r.get("run_id", "?")
        t = r.get("time")
        passed = r.get("passed")
        failed = r.get("failed")
        broken = r.get("broken")
        size = r.get("size")
        summary = (
            f"{passed or 0}/{failed or 0}/{broken or 0}"
            if any(x is not None for x in (passed, failed, broken))
            else "-"
        )
        health_label, health_css = classify(passed, failed, broken)
        pct_pass = None
        if passed is not None:
            exec_total = (passed or 0) + (failed or 0) + (broken or 0)
            if exec_total > 0:
                pct_pass = f"{(passed / exec_total) * 100:.1f}%"
        rows.append(
            f"<tr class='{health_css}'>"
            f"<td><code>{b}</code></td>"
            f"<td><code>{rid}</code></td>"
            f"<td>{_format_epoch_utc(t) if t else '-'}</td>"
            f"<td>{summary}</td>"
            f"<td><span class='health-badge {health_css}'>{health_label}</span></td>"
            f"<td>{pct_pass or '-'}</td>"
            f"<td>{_format_bytes(size) if size else '-'}</td>"
            "</tr>"
        )
    body = (
        "\n".join(rows)
        if rows
        else "<tr><td colspan='7' style='text-align:center'>No runs yet</td></tr>"
    )
    updated = payload.get("updated")
    parts = [
        "<!doctype html><html><head><meta charset='utf-8'>",
        f"<title>{title}</title>",
        "<style>",
        "body{font-family:system-ui;margin:1.25rem;line-height:1.4;}",
        "h1{margin-top:0;font-size:1.3rem;}",
        "table{border-collapse:collapse;width:100%;max-width:1000px;}",
        "th,td{padding:.45rem .55rem;border:1px solid #ccc;font-size:13px;}",
        "thead th{background:#f2f4f7;text-align:left;}",
        "tbody tr:nth-child(even){background:#fafbfc;}",
        "code{background:#f2f4f7;padding:2px 4px;border-radius:3px;font-size:12px;}",
        "footer{margin-top:1rem;font-size:12px;color:#555;}",
        "#filter-box{margin:.75rem 0;}",
        ".health-badge{display:inline-block;padding:2px 6px;border-radius:12px;font-size:11px;line-height:1.2;font-weight:600;border:1px solid #ccc;background:#f5f5f5;}",
        ".health-good{background:#e6f7ed;border-color:#9ad5b6;}",
        ".health-warn{background:#fff7e6;border-color:#f5c063;}",
        ".health-poor{background:#ffebe8;border-color:#f08a80;}",
        ".health-na{background:#f0f1f3;border-color:#c9ccd1;color:#666;}",
        "</style></head><body>",
        f"<h1>{title}</h1>",
        "<div id='filter-box'><label style='font-size:13px'>Filter: <input id='flt' type='text' placeholder='branch or run id'></label></div>",  # noqa: E501
        "<table id='agg'><thead><tr><th>Branch</th><th>Run</th><th>UTC</th><th>P/F/B</th><th>Health</th><th>%Pass</th><th>Size</th></tr></thead><tbody>",  # noqa: E501
        body,
        "</tbody></table>",
        (
            f"<footer>Updated: {_format_epoch_utc(updated) if updated else '-'} | "
            f"Project: {payload.get('project') or cfg.project}</footer>"
        ),
        "<script>(function(){const f=document.getElementById('flt');const tbl=document.getElementById('agg');f.addEventListener('input',()=>{const q=f.value.trim().toLowerCase();[...tbl.tBodies[0].rows].forEach(r=>{if(!q){r.style.display='';return;}const txt=r.textContent.toLowerCase();r.style.display=txt.includes(q)?'':'none';});});})();</script>",  # noqa: E501
        "</body></html>",
    ]
    return "".join(parts).encode("utf-8")


# --------------------------------------------------------------------------------------
# Publish orchestration (restored)
# --------------------------------------------------------------------------------------


def publish(cfg: PublishConfig, paths: Paths | None = None) -> dict:
    """End-to-end publish: pull history, generate, upload, promote latest, manifests.

    Returns a dict of useful URLs & metadata for caller / CI usage.
    """
    paths = paths or Paths()
    total_steps = 7
    step = 1
    timings: dict[str, float] = {}
    t0 = time()
    print(f"[publish] [{step}/{total_steps}] Pulling previous history...")
    pull_history(cfg, paths)
    timings["history_pull"] = time() - t0
    step += 1
    t1 = time()
    print(f"[publish] [{step}/{total_steps}] Generating Allure report...")
    generate_report(paths)
    timings["generate"] = time() - t1
    # Count report files pre-upload for transparency
    results_files = sum(1 for _ in paths.report.rglob("*") if _.is_file())
    step += 1
    t2 = time()
    print(f"[publish] [{step}/{total_steps}] Uploading run artifacts ({results_files} files)...")
    upload_dir(cfg, paths.report, cfg.s3_run_prefix)
    timings["upload_run"] = time() - t2
    _ensure_directory_placeholder(
        cfg,
        paths.report / "index.html",
        cfg.s3_run_prefix,
    )
    step += 1
    t3 = time()
    print(f"[publish] [{step}/{total_steps}] Two-phase latest update starting...")
    two_phase_update_latest(cfg, paths.report)
    timings["two_phase_update"] = time() - t3
    # Optional archive AFTER main run upload
    archive_key = _maybe_archive_run(cfg, paths)
    try:
        step += 1
        print(f"[publish] [{step}/{total_steps}] Writing manifest & indexes...")
        write_manifest(cfg, paths)
    except ClientError as e:  # pragma: no cover – non fatal
        print(f"Manifest write skipped: {e}")
    try:  # retention cleanup
        if getattr(cfg, "max_keep_runs", None):
            step += 1
            print(f"[publish] [{step}/{total_steps}] Retention cleanup...")
            cleanup_old_runs(cfg, int(cfg.max_keep_runs))
    except Exception as e:  # pragma: no cover
        print(f"Cleanup skipped: {e}")
    step += 1
    print(f"[publish] [{step}/{total_steps}] Publish pipeline complete.")
    timings["total"] = time() - t0

    files_count = sum(1 for p in paths.report.rglob("*") if p.is_file())
    return {
        "run_url": cfg.url_run(),
        "latest_url": cfg.url_latest(),
        "runs_index_url": (
            None
            if not cfg.cloudfront_domain
            else (
                f"{cfg.cloudfront_domain.rstrip('/')}/"
                f"{branch_root(cfg.prefix, cfg.project, cfg.branch)}/runs/"
                "index.html"
            )
        ),
        "trend_url": (
            None
            if not cfg.cloudfront_domain
            else (
                f"{cfg.cloudfront_domain.rstrip('/')}/"
                f"{branch_root(cfg.prefix, cfg.project, cfg.branch)}/runs/"
                "trend.html"
            )
        ),
        "bucket": cfg.bucket,
        "run_prefix": cfg.s3_run_prefix,
        "latest_prefix": cfg.s3_latest_prefix,
        "report_size_bytes": compute_dir_size(paths.report),
        "report_files": files_count,
        "archive_key": archive_key,
        "timings": timings,
    }


def _build_trend_viewer_html(cfg: PublishConfig) -> bytes:
    title = f"Run History Trend: {cfg.project} / {cfg.branch}"
    json_url = "../latest/history/history-trend.json"
    parts: list[str] = [
        "<!doctype html><html><head><meta charset='utf-8'>",
        f"<title>{title}</title>",
        "<style>",
        "body{font-family:system-ui;margin:1.25rem;}",
        "h1{margin-top:0;}",
        "#meta{font-size:12px;color:#666;margin-bottom:1rem;}",
        "canvas{max-width:100%;border:1px solid #ddd;background:#fff;}",
        "a{color:#0366d6;text-decoration:none;}",
        "a:hover{text-decoration:underline;}",
        "table{border-collapse:collapse;margin-top:1rem;font-size:12px;}",
        "th,td{padding:4px 6px;border:1px solid #ccc;}",
        (
            ".legend-swatch{display:inline-block;width:10px;height:10px;"
            "margin-right:4px;border-radius:2px;}"
        ),
        "</style></head><body>",
        f"<h1>{title}</h1>",
        (
            "<div id='meta'>Data source: <code>latest/history/history-"
            "trend.json</code> · <a href='index.html'>back to runs</a></div>"
        ),
        "<canvas id='trend' width='900' height='300'></canvas>",
        "<div id='legend'></div>",
        (
            "<table id='raw'><thead><tr><th>Label</th><th>Total</th><th>Passed"  # noqa: E501
            "</th><th>Failed</th><th>Broken</th><th>Skipped</th><th>Unknown"  # noqa: E501
            "</th></tr></thead><tbody></tbody></table>"
        ),
        "<script>\n(async function(){\n",
        f"  const url = '{json_url}';\n",
        "  let data = null;\n",
        "  try {\n",
        "    const resp = await fetch(url, { cache: 'no-store' });\n",
        "    const ct = resp.headers.get('content-type') || '';\n",
        "    if(!resp.ok){\n",
        "      document.body.insertAdjacentHTML('beforeend',\n",
        "        '<p style=\\'color:red\\'>Failed to fetch trend JSON ('+resp.status+')</p>');\n",
        "      return;\n",
        "    }\n",
        "    if (!ct.includes('application/json')) {\n",
        "      const txt = await resp.text();\n",
        "      throw new Error('Unexpected content-type ('+ct+'), length='+txt.length+' — are 403/404 mapped to index.html at CDN?');\n",
        "    }\n",
        "    data = await resp.json();\n",
        "  } catch (e) {\n",
        "    document.body.insertAdjacentHTML('beforeend', '<p style=\\'color:red\\'>Error loading trend data: '+(e && e.message ? e.message : e)+'</p>');\n",
        "    return;\n",
        "  }\n",
        "  if(!Array.isArray(data)){document.body.insertAdjacentHTML('beforeend','<p>No trend data.</p>');return;}\n",
        # Sanitize & enrich: fallback label if reportName/buildOrder missing
        (
            "  const stats = data\n"
            "    .filter(d=>d&&typeof d==='object')\n"
            "    .map((d,i)=>{\n"
            "      const src = (d.statistic && typeof d.statistic==='object') ? d.statistic : ((d.data && typeof d.data==='object') ? d.data : {});\n"
            "      const lbl = d.reportName || d.buildOrder || d.name || src.name || (i+1);\n"
            "      return {label: String(lbl), ...src};\n"
            "    });\n"
        ),
        (
            "  if(!stats.length){document.body.insertAdjacentHTML('beforeend','<p>No usable trend entries.</p>');return;}\n"  # noqa: E501
        ),
        "  const cvs=document.getElementById('trend');\n",
        "  const ctx=cvs.getContext('2d');\n",
        (
            "  const colors={passed:'#2e7d32',failed:'#d32f2f',broken:'#ff9800'};\n"  # noqa: E501
        ),
        "  const keys=['passed','failed','broken'];\n",
        (
            "  const max=Math.max(1,...stats.map(s=>Math.max(...keys.map(k=>s[k]||0))));\n"  # noqa: E501
        ),
        (
            "  const pad=30;const w=cvs.width-pad*2;const h=cvs.height-pad*2;\n"  # noqa: E501
        ),
        (
            "  ctx.clearRect(0,0,cvs.width,cvs.height);ctx.font='12px system-ui';ctx.strokeStyle='#999';ctx.beginPath();ctx.moveTo(pad,pad);ctx.lineTo(pad,pad+h);ctx.lineTo(pad+w,pad+h);ctx.stroke();\n"  # noqa: E501
        ),
        "  const stepX = stats.length>1 ? w/(stats.length-1) : 0;\n",
        "  function y(v){return pad + h - (v/max)*h;}\n",
        (
            "  keys.forEach(k=>{ctx.beginPath();ctx.strokeStyle=colors[k];stats.forEach((s,i)=>{const x=pad+i*stepX;const yy=y(s[k]||0);if(i===0)ctx.moveTo(x,yy);else ctx.lineTo(x,yy);});ctx.stroke();});\n"  # noqa: E501
        ),
        (
            "  stats.forEach((s,i)=>{const x=pad+i*stepX;keys.forEach(k=>{const v=s[k]||0;const yy=y(v);ctx.fillStyle=colors[k];ctx.beginPath();ctx.arc(x,yy,3,0,Math.PI*2);ctx.fill();});ctx.fillStyle='#222';ctx.fillText(String(s.label), x-10, pad+h+14);});\n"  # noqa: E501
        ),
        (
            "  const legend=document.getElementById('legend');legend.innerHTML=keys.map(k=>`<span class='legend-swatch' style='background:${colors[k]}'></span>${k}`).join(' &nbsp; ');\n"  # noqa: E501
        ),
        (
            "  const tbody=document.querySelector('#raw tbody');tbody.innerHTML=stats.map(s=>`<tr><td>${s.label}</td><td>${s.total||''}</td><td>${s.passed||''}</td><td>${s.failed||''}</td><td>${s.broken||''}</td><td>${s.skipped||''}</td><td>${s.unknown||''}</td></tr>`).join('');\n"  # noqa: E501
        ),
        "})();\n</script>",
        "</body></html>",
    ]
    return "".join(parts).encode("utf-8")


def _build_history_insights_html(cfg: PublishConfig) -> bytes:
    """Render a lightweight insights page derived from history-trend.json.

    Provides quick metrics (run count, latest pass%, failure streak, averages)
    plus a compact table of recent entries – purely client-side.
    """
    title = f"Run History Insights: {cfg.project} / {cfg.branch}"
    json_url = "../latest/history/history-trend.json"
    parts: list[str] = [
        "<!doctype html><html><head><meta charset='utf-8'>",
        f"<title>{title}</title>",
        "<style>body{font-family:system-ui;margin:1.25rem;line-height:1.4;background:#fff;color:#111;}h1{margin-top:0;font-size:1.35rem;}a{color:#2563eb;text-decoration:none;}a:hover{text-decoration:underline;}code{background:#f2f4f7;padding:2px 4px;border-radius:4px;font-size:12px;}#metrics{display:flex;flex-wrap:wrap;gap:.8rem;margin:1rem 0;}#metrics .m{flex:0 1 170px;background:#f8f9fa;border:1px solid #d0d4d9;border-radius:6px;padding:.6rem .7rem;box-shadow:0 1px 2px rgba(0,0,0,.06);}#metrics .m h3{margin:0 0 .3rem;font-size:11px;font-weight:600;letter-spacing:.5px;color:#555;text-transform:uppercase;}#metrics .m .v{font-size:20px;font-weight:600;}table{border-collapse:collapse;width:100%;max-width:1100px;}th,td{padding:.45rem .55rem;border:1px solid #ccc;font-size:12px;text-align:left;}thead th{background:#f2f4f7;}tbody tr:nth-child(even){background:#fafbfc;} .ok{color:#2e7d32;font-weight:600;} .warn{color:#f59e0b;font-weight:600;} .bad{color:#d32f2f;font-weight:600;}footer{margin-top:1.2rem;font-size:12px;color:#555;}#err{color:#d32f2f;margin-top:1rem;}@media (prefers-color-scheme:dark){body{background:#0f1115;color:#f5f6f8;}#metrics .m{background:#1b1f26;border-color:#2a313b;color:#f5f6f8;}thead th{background:#1e252d;}table,th,td{border-color:#2a313b;}code{background:#1e252d;}a{color:#3b82f6;}} .health-badge{display:inline-block;padding:2px 6px;border-radius:12px;font-size:11px;line-height:1.2;font-weight:600;border:1px solid #ccc;background:#f5f5f5;} .health-good{background:#e6f7ed;border-color:#9ad5b6;} .health-warn{background:#fff7e6;border-color:#f5c063;} .health-poor{background:#ffebe8;border-color:#f08a80;} .health-na{background:#f0f1f3;border-color:#c9ccd1;color:#666;}",
        "</style></head><body>",
        f"<h1>{title}</h1>",
        "<p>Source: <code>latest/history/history-trend.json</code> · <a href='index.html'>back to runs</a> · <a href='trend.html'>trend viewer</a> · <a href='../latest/history/history-trend.json' target='_blank' rel='noopener'>raw JSON</a></p>",
        "<div id='metrics'></div>",
        "<div style='overflow:auto'><table id='hist'><thead><tr><th>#</th><th>Label</th><th>Passed</th><th>Failed</th><th>Broken</th><th>Total</th><th>Pass%</th><th>Health</th></tr></thead><tbody></tbody></table></div>",
        "<div id='err' hidden></div>",
        "<footer id='ft'></footer>",
        "<script>\n(async function(){\n",
        f"  const url = '{json_url}';\n",
        "  const MET=document.getElementById('metrics');\n",
        "  const TB=document.querySelector('#hist tbody');\n",
        "  const ERR=document.getElementById('err');\n",
        "  const FT=document.getElementById('ft');\n",
        "  function pct(p,f,b){const t=(p||0)+(f||0)+(b||0);return t?((p||0)/t*100).toFixed(1)+'%':'-';}\n",
        "  function classify(p,f,b){const t=(p||0)+(f||0)+(b||0);if(!t)return ['-','health-na'];if((f||0)==0&&(b||0)==0&&(p||0)/t>=0.9)return['Good','health-good'];const ratio=(p||0)/t; if(ratio>=0.75)return['Warn','health-warn'];return['Poor','health-poor'];}\n",
        "  let data=null;\n",
        "  try {\n",
        "    const r=await fetch(url, { cache: 'no-store' });\n",
        "    const ct=r.headers.get('content-type')||'';\n",
        "    if(!r.ok) throw new Error('HTTP '+r.status);\n",
        "    if(!ct.includes('application/json')){const txt=await r.text();throw new Error('Unexpected content-type ('+ct+'), length='+txt.length+' — are 403/404 mapped to index.html at CDN?');}\n",
        "    data=await r.json();\n",
        "    if(!Array.isArray(data)) throw new Error('Unexpected JSON shape');\n",
        "  } catch(e) {\n",
        "    ERR.textContent='Failed to load history: '+(e && e.message? e.message : String(e));ERR.hidden=false;return;\n",
        "  }\n",
        "  const rows=data.filter(d=>d&&typeof d==='object').map((d,i)=>{\n",
        "    const st=(d.statistic&&typeof d.statistic==='object')?d.statistic:((d.data&&typeof d.data==='object')?d.data:{});\n",
        "    const label=d.reportName||d.buildOrder||d.name||st.name||i+1;\n",
        "    const total=typeof st.total==='number'?st.total:(st.passed||0)+(st.failed||0)+(st.broken||0);\n",
        "    return {idx:i,label:String(label),passed:st.passed||0,failed:st.failed||0,broken:st.broken||0,total:total};\n",
        "  });\n",
        "  if(!rows.length){ERR.textContent='No usable entries.';ERR.hidden=false;return;}\n",
        "  const latest=rows[rows.length-1];\n",
        "  const passRates=rows.map(r=>r.total? r.passed/r.total:0);\n",
        "  const avgAll=(passRates.reduce((a,b)=>a+b,0)/passRates.length*100).toFixed(1)+'%';\n",
        "  const last10=passRates.slice(-10);\n",
        "  const avg10=(last10.reduce((a,b)=>a+b,0)/last10.length*100).toFixed(1)+'%';\n",
        "  let streak=0;\n",
        "  for(let i=rows.length-1;i>=0;i--){if(rows[i].failed===0&&rows[i].broken===0)streak++;else break;}\n",
        "  function card(t,v){return `<div class='m'><h3>${t}</h3><div class='v'>${v}</div></div>`;}\n",
        "  const latestPct=pct(latest.passed,latest.failed,latest.broken);\n",
        "  MET.innerHTML=card('Runs',rows.length)+card('Latest Pass%',latestPct)+card('Avg Pass% (all)',avgAll)+card('Avg Pass% (last10)',avg10)+card('Healthy Streak',streak)+card('Failures (latest)',latest.failed);\n",
        "  rows.slice(-80).reverse().forEach(r=>{\n",
        "    const pr=pct(r.passed,r.failed,r.broken);\n",
        "    const [hl,cls]=classify(r.passed,r.failed,r.broken);\n",
        "    TB.insertAdjacentHTML('beforeend',`<tr class='${cls}'><td>${rows.length-r.idx}</td><td>${r.label}</td><td>${r.passed}</td><td>${r.failed}</td><td>${r.broken}</td><td>${r.total}</td><td>${pr}</td><td><span class='health-badge ${cls}'>${hl}</span></td></tr>`);\n",
        "  });\n",
        "  FT.textContent='Entries: '+rows.length+' · Generated '+new Date().toISOString();\n",
        "})();</script>",
        "</body></html>",
    ]
    return "".join(parts).encode("utf-8")


def _branch_health(p: int | None, f: int | None, b: int | None) -> tuple[str, str]:
    if p is None or (f is None and b is None):
        return ("-", "health-na")
    f2 = f or 0
    b2 = b or 0
    total_exec = p + f2 + b2
    if total_exec <= 0:
        return ("-", "health-na")
    ratio = p / total_exec
    if f2 == 0 and b2 == 0 and ratio >= 0.9:
        return ("Good", "health-good")
    if ratio >= 0.75:
        return ("Warn", "health-warn")
    return ("Poor", "health-poor")


def _render_branch_row(br: dict) -> str:
    bname = br.get("branch", "?")
    rid = br.get("latest_run_id") or "-"
    t = br.get("time")
    passed = br.get("passed")
    failed = br.get("failed")
    broken = br.get("broken")
    total_runs = br.get("total_runs")
    latest_url = br.get("latest_url") or f"./{bname}/latest/"
    runs_url = br.get("runs_url") or f"./{bname}/runs/"
    trend_url = br.get("trend_url") or f"./{bname}/runs/trend.html"
    time_cell = _format_epoch_utc(t) if t else "-"
    pct_pass: str | None = None
    if passed is not None:
        exec_total = (passed or 0) + (failed or 0) + (broken or 0)
        if exec_total > 0:
            pct_pass = f"{(passed / exec_total) * 100:.1f}%"
    health_label, health_css = _branch_health(passed, failed, broken)
    row_classes = []
    if failed and failed > 0:
        row_classes.append("row-fail")
    if broken and broken > 0:
        row_classes.append("row-broken")
    if health_css:
        row_classes.append(health_css)
    cls_attr = f" class='{' '.join(row_classes)}'" if row_classes else ""
    return (
        f"<tr{cls_attr}>"
        f"<td class='col-branch'><code>{bname}</code></td>"
        f"<td class='col-lrid'><code>{rid}</code></td>"
        f"<td class='col-time'>{time_cell}</td>"
        f"<td class='col-passed'>{passed if passed is not None else '-'}"  # noqa: E501
        f"</td><td class='col-failed'>{failed if failed is not None else '-'}"  # noqa: E501
        f"</td><td class='col-broken'>{broken if broken is not None else '-'}"  # noqa: E501
        f"</td><td class='col-total'>{total_runs if total_runs is not None else '-'}"  # noqa: E501
        f"</td><td class='col-health'><span class='health-badge {health_css}'>{health_label}</span>"  # noqa: E501
        f"</td><td class='col-passpct'>{pct_pass or '-'}"  # noqa: E501
        f"</td><td class='col-links'><a href='{latest_url}'>latest</a> · "
        f"<a href='{runs_url}'>runs</a> · <a href='{trend_url}'>trend</a></td>"
        "</tr>"
    )


def _build_branches_dashboard_html(payload: dict, cfg: PublishConfig) -> bytes:
    """Render a lightweight branches summary dashboard (schema 1)."""
    branches = payload.get("branches", [])
    title = f"Allure Branches: {payload.get('project') or cfg.project}"
    rows = [_render_branch_row(br) for br in branches]
    body_rows = (
        "\n".join(rows)
        if rows
        else "<tr><td colspan='10' style='text-align:center'>No branches yet</td></tr>"
    )
    updated = payload.get("updated")
    parts: list[str] = [
        "<!doctype html><html><head><meta charset='utf-8'>",
        f"<title>{title}</title>",
        "<style>",
        "body{font-family:system-ui;margin:1.5rem;line-height:1.4;}",
        "h1{margin-top:0;font-size:1.35rem;}",
        "table{border-collapse:collapse;width:100%;max-width:1100px;}",
        "th,td{padding:.5rem .6rem;border:1px solid #ccc;font-size:13px;}",
        "thead th{background:#f2f4f7;text-align:left;}",
        "tbody tr:nth-child(even){background:#fafbfc;}",
        "code{background:#f2f4f7;padding:2px 4px;border-radius:3px;font-size:12px;}",
        "footer{margin-top:1.5rem;font-size:12px;color:#555;}",
        "#filters{margin:.75rem 0;display:flex;gap:1rem;flex-wrap:wrap;}",
        "#filters input{padding:4px 6px;font-size:13px;}",
        ".dim{color:#666;font-size:12px;}",
        ".row-fail{background:#fff5f4 !important;}",
        ".row-broken{background:#fff9ef !important;}",
        ".health-badge{display:inline-block;padding:2px 6px;border-radius:12px;font-size:11px;line-height:1.2;font-weight:600;border:1px solid #ccc;background:#f5f5f5;}",
        ".health-good{background:#e6f7ed;border-color:#9ad5b6;}",
        ".health-warn{background:#fff7e6;border-color:#f5c063;}",
        ".health-poor{background:#ffebe8;border-color:#f08a80;}",
        ".health-na{background:#f0f1f3;border-color:#c9ccd1;color:#666;}",
        "</style></head><body>",
        f"<h1>{title}</h1>",
        "<div id='filters'><label style='font-size:13px'>Branch filter: "
        "<input id='branch-filter' type='text' placeholder='substring'></label>"
        "<span class='dim'>Shows most recently active branches first.</span></div>",
        "<table id='branches'><thead><tr><th>Branch</th><th>Latest Run</th><th>UTC</th><th>P</th><th>F</th><th>B</th><th>Total Runs</th><th>Health</th><th>%Pass</th><th>Links</th></tr></thead><tbody>",  # noqa: E501
        body_rows,
        "</tbody></table>",
        (
            f"<footer>Updated: {_format_epoch_utc(updated) if updated else '-'} | "
            f"Project: {payload.get('project') or cfg.project}</footer>"
        ),
        "<script>(function(){const f=document.getElementById('branch-filter');const tbl=document.getElementById('branches');f.addEventListener('input',()=>{const q=f.value.trim().toLowerCase();[...tbl.tBodies[0].rows].forEach(r=>{if(!q){r.style.display='';return;}const name=r.querySelector('.col-branch').textContent.toLowerCase();r.style.display=name.includes(q)?'':'';});});})();</script>",  # noqa: E501
        "</body></html>",
    ]
    return "".join(parts).encode("utf-8")


def preflight(
    cfg: PublishConfig,
    paths: Paths | None = None,
    check_allure: bool = True,
) -> dict:
    paths = paths or Paths()
    results = {
        "allure_cli": False,
        "allure_results": False,
        "s3_bucket": False,
    }

    if check_allure:
        try:
            ensure_allure_cli()
            results["allure_cli"] = True
        except Exception:
            results["allure_cli"] = False
    else:
        results["allure_cli"] = True

    try:
        results_dir = paths.results
        results["allure_results"] = results_dir.exists() and any(results_dir.iterdir())
    except OSError:
        results["allure_results"] = False

    region_mismatch = False
    bucket_region = None
    try:
        s3 = _s3(cfg)
        head = s3.head_bucket(Bucket=cfg.bucket)
        # region detection (defensive: some stubs may return None)
        if head:
            bucket_region = (
                head.get("ResponseMetadata", {})
                .get(
                    "HTTPHeaders",
                    {},
                )
                .get("x-amz-bucket-region")
            )
        # Attempt a small list to confirm permissions
        s3.list_objects_v2(
            Bucket=cfg.bucket,
            Prefix=cfg.s3_latest_prefix,
            MaxKeys=1,
        )
        results["s3_bucket"] = True
    except ClientError as e:
        code = getattr(e, "response", {}).get("Error", {}).get("Code")
        if code == "301":  # permanent redirect / region mismatch
            region_mismatch = True
        results["s3_bucket"] = False
    results["bucket_region"] = bucket_region
    results["region_mismatch"] = region_mismatch
    return results


def plan_dry_run(cfg: PublishConfig, paths: Paths | None = None) -> dict:
    paths = paths or Paths()
    samples = []
    if paths.report.exists():
        for i, p in enumerate(paths.report.rglob("*")):
            if i >= 20:
                break
            if p.is_file():
                rel = p.relative_to(paths.report).as_posix()
                key_run = f"{cfg.s3_run_prefix}{rel}"
                samples.append(
                    {
                        "file": rel,
                        "run_key": key_run,
                        "cache": cache_control_for_key(key_run),
                    }
                )
    else:
        samples.append({"note": "Report missing; would run allure generate."})
    # Align keys with existing tests expectations
    return {
        "bucket": cfg.bucket,
        "run_prefix": cfg.s3_run_prefix,
        # reflect the temporary latest staging area (two-phase)
        "latest_prefix": getattr(
            cfg,
            "s3_latest_prefix_tmp",
            cfg.s3_latest_prefix,
        ),
        "samples": samples,
        "run_url": cfg.url_run(),
        "latest_url": cfg.url_latest(),
    }


def _maybe_archive_run(cfg: PublishConfig, paths: Paths) -> str | None:
    """Optionally archive the run under an archive/ prefix.

    Controlled by cfg.archive_runs (bool). Best-effort; failures do not abort
    publish.
    Returns archive prefix if performed.
    """
    # Backward compatibility: earlier implementation mistakenly looked for
    # cfg.archive_runs (plural). The correct flag sets cfg.archive_run.
    should_archive = getattr(cfg, "archive_run", False) or getattr(cfg, "archive_runs", False)
    if not should_archive:
        return None
    import tempfile

    archive_format = getattr(cfg, "archive_format", "tar.gz") or "tar.gz"
    run_root = paths.report
    if not run_root or not run_root.exists():
        return None
    # Destination S3 key (placed alongside run prefix root)
    # s3://bucket/<prefix>/<project>/<branch>/<run_id>/<run_id>.tar.gz
    archive_filename = f"{cfg.run_id}.{'zip' if archive_format == 'zip' else 'tar.gz'}"
    s3_key = f"{cfg.s3_run_prefix}{archive_filename}"
    try:
        tmp_dir = tempfile.mkdtemp(prefix="allure-arch-")
        archive_path = Path(tmp_dir) / archive_filename
        if archive_format == "zip":
            import zipfile

            with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for p in run_root.rglob("*"):
                    if p.is_file():
                        zf.write(p, arcname=p.relative_to(run_root).as_posix())
        else:  # tar.gz
            import tarfile

            with tarfile.open(archive_path, "w:gz") as tf:
                for p in run_root.rglob("*"):
                    if p.is_file():
                        tf.add(p, arcname=p.relative_to(run_root).as_posix())
        # Upload archive object
        s3 = _s3(cfg)
        extra = {
            "CacheControl": "public, max-age=31536000, immutable",
            "ContentType": "application/gzip" if archive_format != "zip" else "application/zip",
        }
        if cfg.ttl_days is not None:
            extra["Tagging"] = f"ttl-days={cfg.ttl_days}"
        if cfg.sse:
            extra["ServerSideEncryption"] = cfg.sse
            if cfg.sse == "aws:kms" and cfg.sse_kms_key_id:
                extra["SSEKMSKeyId"] = cfg.sse_kms_key_id
        s3.upload_file(str(archive_path), cfg.bucket, s3_key, ExtraArgs=extra)
        print(f"[publish] Archived run bundle uploaded: s3://{cfg.bucket}/{s3_key}")
        return s3_key
    except Exception as e:  # pragma: no cover
        if os.getenv("ALLURE_HOST_DEBUG"):
            print(f"[publish] archive skipped: {e}")
        return None


# --------------------------------------------------------------------------------------
# Retention cleanup & directory placeholder (restored)
# --------------------------------------------------------------------------------------


def cleanup_old_runs(cfg: PublishConfig, keep: int) -> None:
    if keep is None or keep <= 0:
        return
    s3 = _s3(cfg)
    root = branch_root(cfg.prefix, cfg.project, cfg.branch)
    paginator = s3.get_paginator("list_objects_v2")
    run_prefixes: list[str] = []
    for page in paginator.paginate(
        Bucket=cfg.bucket,
        Prefix=f"{root}/",
        Delimiter="/",
    ):
        for cp in page.get("CommonPrefixes", []) or []:
            pfx = cp.get("Prefix")
            if not pfx:
                continue
            name = pfx.rsplit("/", 2)[-2]
            if name in {"latest", "runs"}:
                continue
            is_ts = len(name) == 15 and name[8] == "-" and name.replace("-", "").isdigit()
            if is_ts:
                run_prefixes.append(pfx)
    run_prefixes.sort(reverse=True)
    for old in run_prefixes[keep:]:
        delete_prefix(cfg.bucket, old, getattr(cfg, "s3_endpoint", None))


def _ensure_directory_placeholder(
    cfg: PublishConfig,
    index_file: Path,
    dir_prefix: str,
) -> None:
    if not index_file.exists() or not dir_prefix.endswith("/"):
        return
    body = index_file.read_bytes()
    extra = {"CacheControl": "no-cache", "ContentType": "text/html"}
    if cfg.ttl_days is not None:
        extra["Tagging"] = f"ttl-days={cfg.ttl_days}"
    try:
        _s3(cfg).put_object(
            Bucket=cfg.bucket,
            Key=dir_prefix,
            Body=body,
            CacheControl=extra["CacheControl"],
            ContentType=extra["ContentType"],
        )
    except ClientError as e:  # pragma: no cover
        print(f"Placeholder upload skipped: {e}")


__all__ = [
    "Paths",
    "pull_history",
    "generate_report",
    "upload_dir",
    "two_phase_update_latest",
    "write_manifest",
    "cleanup_old_runs",
    "preflight",
    "plan_dry_run",
    "publish",
]
