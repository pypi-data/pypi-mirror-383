#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AXIR verifier: compare a given AXIR buffer between two backends.
Default: CPU vs OpenCL.

Usage examples:
  python -m cli.verify_axir build/saxpy_from_cuda.axir.json --list-buffers
  python -m cli.verify_axir build/matmul_from_hip.axir.json --buffer hC
  python -m cli.verify_axir build/matmul_from_hip.axir.json --buffer hC --backend-a cpu --backend-b cuda
  python -m cli.verify_axir build/matmul_from_hip.axir.json --buffer hC --backend-a cpu --backend-b hip --strict
  python -m cli.verify_axir build/saxpy_from_cuda.axir.json --buffer auto --backend-a cpu --backend-b opencl
  python -m cli.verify_axir build/vector_add_from_opencl.axir.json --buffer auto --backend-a cpu --backend-b opencl --time
  python -m cli.verify_axir build/matmul.axir.json --buffer hC --backend-a cpu --backend-b opencl --time --warmup 2 --repeat 5 --inproc

Advanced (opt-in, defaults unchanged):
  --fail-percent X, --nan-policy {propagate,forbid,ignore}, --error-hist K, --dump-mismatch N,
  --ulps, --dtype-tol FILE.json, --check-layout, --check-alias, --json-lines FILE.ndjson
"""

import argparse
import json
import pathlib
import subprocess
import sys
import re
import io
import time
import statistics
from time import perf_counter
import numpy as np
from importlib import import_module
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]

# global args (read by helpers for --silence)
_global_args = argparse.Namespace(silence=False)

# -------------------------------
# Backend import (robust fallback with detailed logging)
# -------------------------------

_BACKEND_ALIASES = {
    "cpu":    ["Backends.cpu_numpy_backend", "Backends.cpu_backend", "Backends.cpu"],
    "opencl": ["Backends.opencl_backend", "Backends.ocl_backend", "Backends.opencl"],
    "ocl":    ["Backends.opencl_backend", "Backends.ocl_backend", "Backends.opencl"],
}

def _import_backend(name: str, quiet: bool = False):
    """Try multiple module paths for a backend name and log each attempt."""
    key = (name or "").lower()
    tried = _BACKEND_ALIASES.get(key, [name, f"Backends.{key}_backend"]) or []
    last_exc = None
    for modpath in tried:
        try:
            mod = import_module(modpath)
            if (not quiet) and (not _global_args.silence):
                print(f"[verify] backend '{name}' -> imported '{modpath}'")
            return mod, modpath
        except Exception as e:
            if (not quiet) and (not _global_args.silence):
                print(f"[verify] import failed '{modpath}': {type(e).__name__}: {e}")
            last_exc = e
    raise ModuleNotFoundError(
        f"Could not import backend '{name}'. Tried: {tried}"
    ) from last_exc


# -------------------------------
# Backend script resolution (subprocess)
# -------------------------------

def resolve_backend_script(name: str) -> pathlib.Path:
    """Map a backend short name to its script path."""
    name = name.lower()
    mapping = {
        "cpu": ROOT / "Backends" / "cpu_numpy_backend.py",
        "opencl": ROOT / "cli" / "entry_opencl_backend.py",
        "cuda": ROOT / "Backends" / "cuda_backend.py",
        "hip": ROOT / "Backends" / "hip_glue_backend.py",
        "stub": ROOT / "Backends" / "gpu_stub_backend.py",
    }
    if name not in mapping:
        raise SystemExit(f"[ERROR] Unknown backend: {name}")
    p = mapping[name]
    if not p.exists():
        raise SystemExit(f"[ERROR] Backend script not found: {p}")
    return p


# -------------------------------
# Runner (subprocess; supports both CLI styles)
# -------------------------------

def _is_entry_style(script_path: pathlib.Path) -> bool:
    """Heuristic: our new 'entry_*' wrappers take --axir/--buffer/--out."""
    return script_path.name.startswith("entry_") or "entry_" in str(script_path).replace("\\", "/")

def run_backend(script_path: pathlib.Path,
                axir_path: pathlib.Path,
                dump_name: str,
                out_path: pathlib.Path,
                quiet: bool = False) -> float:
    """Run a backend script that dumps a specific buffer to a .npy file.
    Returns the wall-clock duration in seconds."""
    if _is_entry_style(script_path):
        cmd = [sys.executable, str(script_path),
               "--axir", str(axir_path),
               "--buffer", dump_name,
               "--out", str(out_path)]
    else:
        cmd = [sys.executable, str(script_path),
               str(axir_path),
               "--dump", dump_name,
               "--out", str(out_path)]
    t0 = perf_counter()
    cp = subprocess.run(cmd, capture_output=True, text=True)
    dt = perf_counter() - t0
    if cp.returncode != 0:
        if cp.stdout and not _global_args.silence:
            print(cp.stdout, end="")
        if cp.stderr and not _global_args.silence:
            print(cp.stderr, file=sys.stderr, end="")
        raise SystemExit(f"[ERROR] Backend script failed: {script_path.name} (rc={cp.returncode})")
    if (not quiet) and cp.stdout and not _global_args.silence:
        print(cp.stdout, end="")
    return dt


# -------------------------------
# AXIR helpers
# -------------------------------

def load_axir(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def list_axir_buffers(axir_path: pathlib.Path):
    """Liste propre des buffers AXIR. Préfère la section 'buffers' si présente,
    sinon tente une détection prudente dans les ops."""
    data = load_axir(axir_path)

    # 1) Section "buffers"
    if isinstance(data.get("buffers"), dict) and data["buffers"]:
        names = list(data["buffers"].keys())
        preferred_order = ["hC", "hOut", "out", "output", "result", "C", "Y"]
        ordered = [p for p in preferred_order if p in names] + [n for n in names if n not in preferred_order]
        seen, unique = set(), []
        for n in ordered:
            if n not in seen:
                seen.add(n)
                unique.append(n)
        return unique

    # 2) Fallback : heuristique depuis les ops
    names = []
    def may_add(x: str):
        if isinstance(x, str) and re.match(r"^[A-Za-z]\w{0,63}$", x):
            if x not in names:
                names.append(x)
    try:
        ops = data.get("ops", []) or []
        for op in ops:
            for key in ("name", "dst", "src", "ptr", "A", "B", "C", "out", "output"):
                v = op.get(key)
                if isinstance(v, str):
                    may_add(v)
    except Exception:
        pass

    preferred_order = ["hC", "hOut", "out", "output", "result", "C", "Y"]
    ordered = [p for p in preferred_order if p in names] + [n for n in names if n not in preferred_order]
    seen, unique = set(), []
    for n in ordered:
        if n not in seen:
            seen.add(n)
            unique.append(n)
    return unique


# -------------------------------
# OpenCL profile parsing & GEMM FLOPs helpers
# -------------------------------

_PROFILE_RE = re.compile(r"\[OCL\]\[PROFILE\].*TOTAL=([0-9.]+)\s*ms")

def _extract_ocl_profile_total(stdout_text: str):
    matches = _PROFILE_RE.findall(stdout_text or "")
    return float(matches[-1]) if matches else None

def _read_scalar(ax: dict, name: str):
    try:
        v = ((ax.get("types", {}) or {}).get("scalars", {}) or {}).get(name, {}).get("value")
        if v is not None:
            return int(v)
    except Exception:
        pass
    try:
        v = ((ax.get("scalars", {}) or {}).get(name, {}) or {}).get("value")
        if v is not None:
            return int(v)
    except Exception:
        pass
    try:
        if name in ax:
            return int(ax[name])
    except Exception:
        pass
    return None

def _gemm_flops(ax):
    M = _read_scalar(ax, "M")
    N = _read_scalar(ax, "N")
    K = _read_scalar(ax, "K")
    if not (M and N and K):
        return None, None, None, None
    return 2.0 * M * N * K, M, N, K


# -------------------------------
# Dump target resolution (only one buffer)
# -------------------------------

def _resolve_dump_target(ax: dict, arg: str) -> str:
    if not arg:
        return "hC"
    s = arg.strip()
    if s.lower() == "auto":
        try:
            ops = ax.get("ops", []) or []
            for op in reversed(ops):
                out = op.get("out") or op.get("dst") or op.get("output")
                if isinstance(out, str) and out:
                    return out
        except Exception:
            pass
        return "hC"
    if "," in s:
        return s.split(",", 1)[0].strip()
    return s


# -------------------------------
# In-proc runner (captures [OCL][PROFILE] TOTAL)
# -------------------------------

def run_backend_inproc(backend: str, axir_path: pathlib.Path, buffer_arg: str, quiet: bool = False):
    from contextlib import redirect_stdout

    ax = load_axir(axir_path)
    dump_target = _resolve_dump_target(ax, buffer_arg)

    mod, resolved = _import_backend(backend, quiet=quiet)
    if not quiet and not _global_args.silence:
        print(f"[verify] backend '{backend}' -> imported '{resolved}'")
        print(f"[INFO] --buffer {buffer_arg} -> using '{dump_target}'")

    t0 = time.perf_counter()
    buf = io.StringIO()
    with redirect_stdout(buf):
        try:
            out = mod.run(ax, summary=False, dump=dump_target, repeats=1, profile=True)
        except TypeError:
            out = mod.run(ax, summary=False, dump=dump_target, repeats=1)
    captured = buf.getvalue()
    if captured and not quiet and not _global_args.silence:
        print(captured, end="")

    if isinstance(out, dict) and "dump" in out:
        arr = np.asarray(out["dump"])
    else:
        arr = np.asarray(out)

    dt_ms = (time.perf_counter() - t0) * 1e3
    profile_used = False

    if backend.lower() in ("opencl", "ocl"):
        tot = _extract_ocl_profile_total(captured)
        if tot is not None:
            dt_ms = float(tot)
            profile_used = True

    out_path = axir_path.parent / f"verify_{backend}_{dump_target}.npy"
    np.save(out_path, arr.reshape(-1))

    if not quiet and not _global_args.silence:
        shape = (arr.size,)
        print(f"[inproc] {backend}: saved {out_path.name} shape={shape} in {dt_ms:.2f} ms")

    return arr, dt_ms, profile_used


# -------------------------------
# Orchestrator for in-proc timing/median/GFLOP/s
# -------------------------------

def run_one_inproc(axir_path: pathlib.Path, buffer: str, a_backend: str, b_backend: str, warmup: int = 0, repeats: int = 1, quiet: bool = False):
    for _ in range(max(0, warmup)):
        run_backend_inproc(a_backend, axir_path, buffer, quiet=True)
        run_backend_inproc(b_backend, axir_path, buffer, quiet=True)

    times_a, times_b = [], []
    prof_a_used, prof_b_used = False, False
    last_a, last_b = None, None

    for _ in range(max(1, repeats)):
        last_a, dt_a, used_a = run_backend_inproc(a_backend, axir_path, buffer, quiet=True)
        times_a.append(dt_a); prof_a_used |= used_a
        last_b, dt_b, used_b = run_backend_inproc(b_backend, axir_path, buffer, quiet=True)
        times_b.append(dt_b); prof_b_used |= used_b

    med_a = statistics.median(times_a)
    med_b = statistics.median(times_b)

    ax = load_axir(axir_path)
    flops, M, N, K = _gemm_flops(ax)
    if flops is not None and med_a > 0 and med_b > 0:
        gflops_a = (flops / (med_a / 1e3)) / 1e9
        gflops_b = (flops / (med_b / 1e3)) / 1e9
    else:
        gflops_a = gflops_b = None

    if not _global_args.silence:
        print("---- TIMING ----")
        print(f"Warmup: {warmup}, Repeats: {repeats} (median)")
        line_a = f"{a_backend.upper():8}: {med_a:.2f} ms (median)"
        line_b = f"{b_backend.upper():8}: {med_b:.2f} ms (median)"
        if gflops_a is not None:
            line_a += f" | {gflops_a:.2f} GFLOP/s"
            line_b += f" | {gflops_b:.2f} GFLOP/s"
        if prof_a_used:
            line_a += " | source=[PROFILE]"
        if prof_b_used:
            line_b += " | source=[PROFILE]"
        print(line_a)
        print(line_b)

    return {
        "med_a_ms": med_a, "med_b_ms": med_b,
        "gflops_a": gflops_a, "gflops_b": gflops_b,
        "profile_a": prof_a_used, "profile_b": prof_b_used,
        "M": M, "N": N, "K": K,
        "last_a": last_a, "last_b": last_b,
    }


# -------------------------------
# Aux: dtype tolerances, ULPs, JSON/CSV writers
# -------------------------------

def _normalize_dtype_key(dt: np.dtype) -> str:
    d = np.dtype(dt).name  # e.g., 'float32'
    aliases = {
        "float16": "float16", "f2": "float16", "half": "float16",
        "float32": "float32", "f4": "float32", "single": "float32",
        "float64": "float64", "f8": "float64", "double": "float64",
    }
    return aliases.get(d, d)

def _apply_dtype_tolerances(a_dtype, b_dtype, base_atol, base_rtol, tol_profile):
    """Return (atol, rtol) possibly overridden by dtype profile (by b's dtype)."""
    if not tol_profile:
        return base_atol, base_rtol
    try:
        key = _normalize_dtype_key(np.dtype(b_dtype))
        prof = tol_profile.get(key) or tol_profile.get(key.upper()) or tol_profile.get(key.lower())
        if prof:
            atol = float(prof.get("atol", base_atol))
            rtol = float(prof.get("rtol", base_rtol))
            return atol, rtol
    except Exception:
        pass
    return base_atol, base_rtol

def _float_to_ordered_int(arr: np.ndarray):
    """Map IEEE754 floats to monotonic signed integers for ULP distance.
    Works for float16/32/64."""
    if not np.issubdtype(arr.dtype, np.floating):
        return None
    itemsize = arr.dtype.itemsize
    if itemsize == 2:
        itype = np.int16
    elif itemsize == 4:
        itype = np.int32
    elif itemsize == 8:
        itype = np.int64
    else:
        return None
    i = arr.view(itype).astype(np.int64)
    bias = np.int64(1) << (itemsize * 8 - 1)
    ordered = np.where(i < 0, bias - i, i + bias).astype(np.int64)
    return ordered

def _ulps_stats(a: np.ndarray, b: np.ndarray):
    """Return dict with max/median/p99 ULPs (only for float arrays)."""
    if not (np.issubdtype(a.dtype, np.floating) and np.issubdtype(b.dtype, np.floating)):
        return None
    ao = _float_to_ordered_int(a)
    bo = _float_to_ordered_int(b)
    if ao is None or bo is None:
        return None
    ulps = np.abs(ao - bo).astype(np.int64)
    if ulps.size == 0:
        return {"max": 0, "median": 0, "p99": 0}
    return {
        "max": int(np.max(ulps)),
        "median": float(np.median(ulps)),
        "p99": float(np.quantile(ulps.astype(np.float64), 0.99)),
    }

def _maybe_write_outputs(args, row_dict):
    if args.csv:
        _write_csv(args.csv, row_dict)
    if args.json:
        _write_json_array(args.json, row_dict)
    if args.json_lines:
        _write_json_lines(args.json_lines, row_dict)

def _write_csv(path, row_dict):
    import csv
    p = pathlib.Path(path)
    fieldnames = [
        "timestamp", "axir", "buffer",
        "backend_a", "backend_b",
        "size", "mismatches", "percent",
        "max_abs_err", "worst_idx", "a_worst", "b_worst",
        "atol", "rtol", "allclose",
        "med_a_ms", "med_b_ms", "gflops_a", "gflops_b",
        "profile_a", "profile_b",
        "nan_a", "nan_b", "inf_a", "inf_b",
        "fail_percent", "nan_policy",
    ]
    write_header = not p.exists()
    with p.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            w.writeheader()
        row = {k: row_dict.get(k, "") for k in fieldnames}
        w.writerow(row)

def _write_json_array(path, row_dict):
    """Append to JSON array (create if missing)."""
    p = pathlib.Path(path)
    data = []
    if p.exists():
        try:
            with p.open("r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, list):
                    data = loaded
                elif isinstance(loaded, dict):
                    data = [loaded]
        except Exception:
            pass
    data.append(row_dict)
    tmp = p.with_suffix(p.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    tmp.replace(p)

def _write_json_lines(path, row_dict):
    """Append one JSON object per line (NDJSON)."""
    p = pathlib.Path(path)
    with p.open("a", encoding="utf-8") as f:
        json.dump(row_dict, f, ensure_ascii=False)
        f.write("\n")


# -------------------------------
# Main
# -------------------------------

def main(argv=None):
    global _global_args
    ap = argparse.ArgumentParser(description="Verify one AXIR buffer between two backends (default: CPU vs OpenCL).")
    ap.add_argument("axir", help="Path to the AXIR JSON")
    ap.add_argument("--buffer", help="Buffer name to compare (e.g., hC, hOut) or 'auto'")
    ap.add_argument("--backend-a", default="cpu", help="Left backend: cpu|opencl|cuda|hip|stub (default: cpu)")
    ap.add_argument("--backend-b", default="opencl", help="Right backend: cpu|opencl|cuda|hip|stub (default: opencl)")
    ap.add_argument("--atol", type=float, default=1e-6, help="Absolute tolerance for np.allclose")
    ap.add_argument("--rtol", type=float, default=1e-5, help="Relative tolerance for np.allclose (default: 1e-5)")
    ap.add_argument("--list-buffers", action="store_true",
                    help="List available buffers in the AXIR file and exit.")
    ap.add_argument("--head-k", type=int, default=8,
                    help="How many elements to show in head previews (default: 8).")
    ap.add_argument("--strict", action="store_true", help="Exit with non-zero code if verification fails.")
    ap.add_argument("--time", action="store_true", help="Measure wall-clock or profiled time (median if repeats>1).")
    ap.add_argument("--warmup", type=int, default=0, help="Warmup iterations per backend before timing (default: 0).")
    ap.add_argument("--repeat", type=int, default=1, help="Timed iterations per backend (median reported if >1).")
    ap.add_argument("--quiet", action="store_true", help="Suppress backend stdout (useful with --warmup/--repeat).")
    ap.add_argument("--inproc", action="store_true", help="Run backends in-proc and align SMOKE with [PROFILE] TOTAL when available.")
    # Outputs & UX
    ap.add_argument("--percent", action="store_true",
                    help="Only print mismatch percentage in RESULT block.")
    ap.add_argument("--csv", type=str, default=None,
                    help="Write/append a CSV summary to this path.")
    ap.add_argument("--json", type=str, default=None,
                    help="Write/append a JSON summary (array of runs) to this path.")
    ap.add_argument("--json-lines", type=str, default=None,
                    help="Write/append NDJSON (one JSON object per line).")
    ap.add_argument("--silence", action="store_true",
                    help="Suppress banners/logs; only RESULT (or percent) is printed.")
    # New controls (opt-in)
    ap.add_argument("--fail-percent", type=float, default=None,
                    help="Exit non-zero if mismatch percentage exceeds this threshold.")
    ap.add_argument("--nan-policy", choices=["propagate", "forbid", "ignore"], default="propagate",
                    help="How to handle NaN/Inf in comparison and checks (default: propagate).")
    ap.add_argument("--error-hist", type=int, default=None,
                    help="If set, print an absolute-error histogram with K bins.")
    ap.add_argument("--dump-mismatch", type=int, default=None,
                    help="If set, print top-N worst mismatches (idx, a, b, tol, err).")
    ap.add_argument("--ulps", action="store_true",
                    help="If set, report ULPs error stats (float dtypes).")
    ap.add_argument("--dtype-tol", type=str, default=None,
                    help="JSON file with per-dtype tolerances e.g. {'float16':{'rtol':1e-3,'atol':1e-3}}")
    ap.add_argument("--check-layout", action="store_true",
                    help="Check declared buffer shape/strides from AXIR (best-effort).")
    ap.add_argument("--check-alias", action="store_true",
                    help="If AXIR declares alias_of for the buffer, verify equality when dumps exist.")
    _global_args = ap.parse_args(argv)
    args = _global_args

    # Load tolerances profile if any
    tol_profile = None
    if args.dtype_tol:
        try:
            with open(args.dtype_tol, "r", encoding="utf-8") as f:
                tol_profile = json.load(f)
        except Exception as e:
            print(f"[WARN] failed to load --dtype-tol '{args.dtype_tol}': {e}")

    axir_path = pathlib.Path(args.axir).resolve()
    if not axir_path.exists():
        raise SystemExit(f"[ERROR] AXIR file not found: {axir_path}")

    if args.list_buffers:
        names = list_axir_buffers(axir_path)
        if not args.silence:
            print("---- AXIR BUFFERS ----")
        if names:
            for n in names:
                print(n)
            raise SystemExit(0)
        else:
            raise SystemExit("[ERROR] No buffers found in AXIR.")

    if args.buffer and args.buffer.lower() == "auto" and not args.silence:
        print(f"[INFO] --buffer auto -> will resolve from ops or fallback 'hC'")

    if not args.buffer:
        raise SystemExit("[ERROR] --buffer is required (or use --list-buffers or --buffer auto).")

    ax = load_axir(axir_path)
    dump_target = _resolve_dump_target(ax, args.buffer)

    # Optional checks with AXIR metadata
    if args.check_layout:
        try:
            bufmeta = (ax.get("buffers", {}) or {}).get(dump_target)
            if bufmeta:
                shp = bufmeta.get("shape") or bufmeta.get("dims")
                strides = bufmeta.get("strides")
                layout = bufmeta.get("layout")
                if not args.silence:
                    print(f"[layout] buffer='{dump_target}' shape={shp} strides={strides} layout={layout}")
        except Exception:
            pass

    build_dir = axir_path.parent
    out_a = build_dir / f"verify_{args.backend_a}_{dump_target}.npy"
    out_b = build_dir / f"verify_{args.backend_b}_{dump_target}.npy"

    if not args.silence:
        print("---- AXIR VERIFY ----")
        print(f"AXIR       : {axir_path}")
        print(f"BUFFER     : {args.buffer} -> '{dump_target}'")
        print(f"BACKENDS   : {args.backend_a} vs {args.backend_b}")

    # collect timing stats (for outputs) if available
    med_a_ms = None
    med_b_ms = None
    gflops_a = None
    gflops_b = None
    profile_a = None
    profile_b = None

    if args.inproc:
        stats = run_one_inproc(
            axir_path,
            args.buffer,
            args.backend_a,
            args.backend_b,
            warmup=args.warmup if args.time else 0,
            repeats=args.repeat if args.time else 1,
            quiet=args.quiet
        )
        med_a_ms = stats["med_a_ms"]
        med_b_ms = stats["med_b_ms"]
        gflops_a = stats["gflops_a"]
        gflops_b = stats["gflops_b"]
        profile_a = stats["profile_a"]
        profile_b = stats["profile_b"]

        a = np.load(out_a, allow_pickle=False)
        b = np.load(out_b, allow_pickle=False)
    else:
        script_a = resolve_backend_script(args.backend_a)
        script_b = resolve_backend_script(args.backend_b)

        dt_a_first = run_backend(script_a, axir_path, dump_target, out_a, quiet=args.quiet)  # seconds
        dt_b_first = run_backend(script_b, axir_path, dump_target, out_b, quiet=args.quiet)
        # seconds -> ms
        med_a_ms = dt_a_first * 1000.0
        med_b_ms = dt_b_first * 1000.0

        if args.time and (args.warmup > 0 or args.repeat > 1):
            for _ in range(args.warmup):
                run_backend(script_a, axir_path, dump_target, out_a, quiet=True)
                run_backend(script_b, axir_path, dump_target, out_b, quiet=True)
            times_a = [run_backend(script_a, axir_path, dump_target, out_a, quiet=True) for _ in range(args.repeat)]
            times_b = [run_backend(script_b, axir_path, dump_target, out_b, quiet=True) for _ in range(args.repeat)]
            med_a = float(np.median(times_a))  # seconds
            med_b = float(np.median(times_b))  # seconds
            med_a_ms = med_a * 1000.0
            med_b_ms = med_b * 1000.0

            if not args.silence:
                print("---- TIMING ----")
                print(f"Warmup: {args.warmup}, Repeats: {args.repeat} (median)")
            flops, M, N, K = _gemm_flops(load_axir(axir_path))
            if flops is not None:
                gflops_a = (flops / med_a) / 1e9
                gflops_b = (flops / med_b) / 1e9
                if not args.silence:
                    print(f"{args.backend_a.upper():8}: {med_a_ms:.2f} ms (median) | {gflops_a:.2f} GFLOP/s")
                    print(f"{args.backend_b.upper():8}: {med_b_ms:.2f} ms (median) | {gflops_b:.2f} GFLOP/s")
            else:
                if not args.silence:
                    print(f"{args.backend_a.upper():8}: {med_a_ms:.2f} ms (median)")
                    print(f"{args.backend_b.upper():8}: {med_b_ms:.2f} ms (median)")

        a = np.load(out_a, allow_pickle=False)
        b = np.load(out_b, allow_pickle=False)

    # ---- RESULT ----
    if not args.silence:
        print("---- RESULT ----")
        print(f"SHAPES     : {args.backend_a.upper()}{a.shape} vs {args.backend_b.upper()}{b.shape}")

    # Always flatten before comparison (avoid 2D vs 1D mismatches)
    a = np.asarray(a).reshape(-1)
    b = np.asarray(b).reshape(-1)

    if a.size != b.size:
        min_len = min(a.size, b.size)
        if not args.silence:
            print(f"[WARN] shape mismatch -> trimming to {min_len} elements")
        a = a[:min_len]
        b = b[:min_len]

    # Edge case: nothing to compare
    if a.size == 0:
        percent = 0.0
        allc = bool(np.allclose(a, b, atol=args.atol, rtol=args.rtol))
        if args.percent:
            print(f"{percent:.6f}")
            if args.strict and not allc:
                raise SystemExit(1)
            _maybe_write_outputs(args, {
                "timestamp": datetime.utcnow().isoformat(),
                "axir": str(axir_path),
                "buffer": str(dump_target),
                "backend_a": args.backend_a,
                "backend_b": args.backend_b,
                "size": 0,
                "mismatches": 0,
                "percent": percent,
                "max_abs_err": 0.0,
                "worst_idx": -1,
                "a_worst": None,
                "b_worst": None,
                "atol": args.atol,
                "rtol": args.rtol,
                "allclose": allc,
                "med_a_ms": med_a_ms,
                "med_b_ms": med_b_ms,
                "gflops_a": gflops_a,
                "gflops_b": gflops_b,
                "profile_a": profile_a,
                "profile_b": profile_b,
                "nan_a": 0, "nan_b": 0, "inf_a": 0, "inf_b": 0,
                "fail_percent": args.fail_percent,
                "nan_policy": args.nan_policy,
            })
            return
        if not args.silence:
            print("[WARN] empty arrays after trimming; nothing to compare.")
            print("max_abs_err: 0.0")
            print(f"ALLCLOSE   : {allc} (atol={args.atol}, rtol={args.rtol})")
            print(f"{args.backend_a.upper()}(head): []")
            print(f"{args.backend_b.upper()}(head): []")
            print("mismatches : 0/0")
        _maybe_write_outputs(args, {
            "timestamp": datetime.utcnow().isoformat(),
            "axir": str(axir_path),
            "buffer": str(dump_target),
            "backend_a": args.backend_a,
            "backend_b": args.backend_b,
            "size": 0,
            "mismatches": 0,
            "percent": 0.0,
            "max_abs_err": 0.0,
            "worst_idx": -1,
            "a_worst": None,
            "b_worst": None,
            "atol": args.atol,
            "rtol": args.rtol,
            "allclose": allc,
            "med_a_ms": med_a_ms,
            "med_b_ms": med_b_ms,
            "gflops_a": gflops_a,
            "gflops_b": gflops_b,
            "profile_a": profile_a,
            "profile_b": profile_b,
            "nan_a": 0, "nan_b": 0, "inf_a": 0, "inf_b": 0,
            "fail_percent": args.fail_percent,
            "nan_policy": args.nan_policy,
        })
        if args.strict and not allc:
            raise SystemExit(1)
        return

    # dtype-driven tolerances (opt-in)
    eff_atol, eff_rtol = _apply_dtype_tolerances(a.dtype, b.dtype, args.atol, args.rtol, tol_profile)

    # NaN/Inf handling
    nan_a = int(np.isnan(a).sum())
    nan_b = int(np.isnan(b).sum())
    inf_a = int(np.isinf(a).sum())
    inf_b = int(np.isinf(b).sum())
    if args.nan_policy == "forbid" and (nan_a or nan_b or inf_a or inf_b):
        if not args.silence:
            print(f"[ERROR] NaN/Inf detected (nan_a={nan_a}, nan_b={nan_b}, inf_a={inf_a}, inf_b={inf_b}) with --nan-policy=forbid")
        # still compute minimal outputs for csv/json
        percent = 100.0  # force fail-percent if set
        _maybe_write_outputs(args, {
            "timestamp": datetime.utcnow().isoformat(),
            "axir": str(axir_path),
            "buffer": str(dump_target),
            "backend_a": args.backend_a,
            "backend_b": args.backend_b,
            "size": int(a.size),
            "mismatches": int(a.size),
            "percent": percent,
            "max_abs_err": float("nan"),
            "worst_idx": -1,
            "a_worst": None,
            "b_worst": None,
            "atol": eff_atol,
            "rtol": eff_rtol,
            "allclose": False,
            "med_a_ms": med_a_ms,
            "med_b_ms": med_b_ms,
            "gflops_a": gflops_a,
            "gflops_b": gflops_b,
            "profile_a": profile_a,
            "profile_b": profile_b,
            "nan_a": nan_a, "nan_b": nan_b, "inf_a": inf_a, "inf_b": inf_b,
            "fail_percent": args.fail_percent,
            "nan_policy": args.nan_policy,
        })
        raise SystemExit(1)

    # diff & metrics
    diff = a - b
    abs_diff = np.abs(diff)
    max_abs_err = float(np.max(abs_diff))
    imax = int(np.argmax(abs_diff))

    # allclose (optionally equal_nan)
    allc = bool(np.allclose(a, b, atol=eff_atol, rtol=eff_rtol, equal_nan=(args.nan_policy == "ignore")))

    # Mismatch stats with per-element tolerance
    tol_vec = eff_atol + eff_rtol * np.abs(b)
    # if ignore NaN: positions where both NaN are not mismatches
    if args.nan_policy == "ignore":
        both_nan = np.isnan(a) & np.isnan(b)
        mismatch_mask = (abs_diff > tol_vec) & (~both_nan)
    else:
        mismatch_mask = abs_diff > tol_vec

    mismatch = int(np.count_nonzero(mismatch_mask))
    percent = (100.0 * mismatch / a.size) if a.size > 0 else 0.0

    # Optional ULPs
    ulps_stats = _ulps_stats(a, b) if args.ulps else None

    # Optional error histogram
    error_hist = None
    if args.error_hist and args.error_hist > 0 and abs_diff.size > 0:
        hist, edges = np.histogram(abs_diff.astype(np.float64), bins=int(args.error_hist))
        error_hist = {"bins": int(args.error_hist),
                      "counts": hist.astype(int).tolist(),
                      "edges": [float(x) for x in edges.tolist()]}

    # Optional top mismatches
    top_mismatches = None
    if args.dump_mismatch and args.dump_mismatch > 0 and abs_diff.size > 0:
        k = int(min(args.dump_mismatch, abs_diff.size))
        # argsort descending
        worst_idx = np.argpartition(-abs_diff, range(k))[:k]
        # stable order by err desc
        worst_idx = worst_idx[np.argsort(-abs_diff[worst_idx])]
        top_mismatches = []
        for idx in worst_idx:
            top_mismatches.append({
                "idx": int(idx),
                "a": float(a[idx]),
                "b": float(b[idx]),
                "tol": float(tol_vec[idx]),
                "err": float(abs_diff[idx]),
            })

    # If --percent: print only the percentage (RESULT-minimal mode)
    if args.percent:
        print(f"{percent:.6f}")
        _maybe_write_outputs(args, {
            "timestamp": datetime.utcnow().isoformat(),
            "axir": str(axir_path),
            "buffer": str(dump_target),
            "backend_a": args.backend_a,
            "backend_b": args.backend_b,
            "size": int(a.size),
            "mismatches": mismatch,
            "percent": percent,
            "max_abs_err": max_abs_err,
            "worst_idx": imax,
            "a_worst": float(a[imax]) if a.size else None,
            "b_worst": float(b[imax]) if b.size else None,
            "atol": eff_atol,
            "rtol": eff_rtol,
            "allclose": allc,
            "med_a_ms": med_a_ms,
            "med_b_ms": med_b_ms,
            "gflops_a": gflops_a,
            "gflops_b": gflops_b,
            "profile_a": profile_a,
            "profile_b": profile_b,
            "nan_a": nan_a, "nan_b": nan_b, "inf_a": inf_a, "inf_b": inf_b,
            "fail_percent": args.fail_percent,
            "nan_policy": args.nan_policy,
            "ulps": ulps_stats,
            "error_hist": error_hist,
            "top_mismatches": top_mismatches,
        })
        # fail-percent applies even in percent mode
        if args.fail_percent is not None and percent > args.fail_percent:
            raise SystemExit(1)
        if args.strict and not allc:
            raise SystemExit(1)
        return

    # Verbose RESULT (default)
    if not args.silence:
        print(f"max_abs_err: {max_abs_err}")
        print(f"ALLCLOSE   : {allc} (atol={eff_atol}, rtol={eff_rtol})")
        tol_worst = float(eff_atol + eff_rtol * np.abs(b[imax]))
        print(f"tolerance@worst_idx: {tol_worst}  (formula: |a-b| <= atol + rtol*|b|)")

        head_k = max(0, int(args.head_k))
        def head(x, k=head_k):
            x = np.asarray(x).reshape(-1)
            return np.array2string(x[: min(k, x.size)], precision=6, separator=", ")

        print(f"{args.backend_a.upper()}(head):", head(a))
        print(f"{args.backend_b.upper()}(head):", head(b))

        print(
            f"worst_idx  : {imax} "
            f"{args.backend_a.upper()}={float(a[imax])} "
            f"{args.backend_b.upper()}={float(b[imax])} "
            f"diff={float(abs_diff[imax])}"
        )
        print(f"mismatches : {mismatch}/{a.size} ({percent:.4f}%)")

        if ulps_stats is not None:
            print(f"ULPs       : max={ulps_stats['max']}  p99={ulps_stats['p99']:.2f}  median={ulps_stats['median']:.2f}")

        if error_hist is not None:
            print("[error-hist] counts:", error_hist["counts"])
            print("[error-hist] edges :", error_hist["edges"])

        if top_mismatches:
            print(f"[top-{len(top_mismatches)} mismatches] idx,a,b,tol,err")
            for t in top_mismatches:
                print(f"{t['idx']},{t['a']},{t['b']},{t['tol']},{t['err']}")
    else:
        # silence mode: print minimal parseable output when not --percent
        print(f"{percent:.6f}")

    # CSV/JSON/NDJSON output if requested
    _maybe_write_outputs(args, {
        "timestamp": datetime.utcnow().isoformat(),
        "axir": str(axir_path),
        "buffer": str(dump_target),
        "backend_a": args.backend_a,
        "backend_b": args.backend_b,
        "size": int(a.size),
        "mismatches": mismatch,
        "percent": percent,
        "max_abs_err": max_abs_err,
        "worst_idx": imax,
        "a_worst": float(a[imax]),
        "b_worst": float(b[imax]),
        "atol": eff_atol,
        "rtol": eff_rtol,
        "allclose": allc,
        "med_a_ms": med_a_ms,
        "med_b_ms": med_b_ms,
        "gflops_a": gflops_a,
        "gflops_b": gflops_b,
        "profile_a": profile_a,
        "profile_b": profile_b,
        "nan_a": nan_a, "nan_b": nan_b, "inf_a": inf_a, "inf_b": inf_b,
        "fail_percent": args.fail_percent,
        "nan_policy": args.nan_policy,
        "ulps": ulps_stats,
        "error_hist": error_hist,
        "top_mismatches": top_mismatches,
    })

    # Optional alias check (best effort): if alias_of exists and dumps also exist, compare quickly
    if args.check_alias:
        try:
            bufmeta = (ax.get("buffers", {}) or {}).get(dump_target)
            alias = bufmeta.get("alias_of") if bufmeta else None
            if alias:
                alias_a = build_dir / f"verify_{args.backend_a}_{alias}.npy"
                alias_b = build_dir / f"verify_{args.backend_b}_{alias}.npy"
                if alias_a.exists() and alias_b.exists():
                    la = np.load(alias_a, allow_pickle=False).reshape(-1)
                    lb = np.load(alias_b, allow_pickle=False).reshape(-1)
                    if la.size != a.size or lb.size != b.size:
                        if not args.silence:
                            print(f"[WARN] alias '{alias}' size mismatch vs '{dump_target}' (skipping alias check)")
                    else:
                        ok_a = bool(np.allclose(a, la, atol=eff_atol, rtol=eff_rtol))
                        ok_b = bool(np.allclose(b, lb, atol=eff_atol, rtol=eff_rtol))
                        if not args.silence:
                            print(f"[alias] {dump_target}↔{alias} A={ok_a} B={ok_b}")
                else:
                    if not args.silence:
                        print(f"[alias] '{alias}' dumps not found for quick check (expected {alias_a.name}, {alias_b.name})")
        except Exception:
            pass

    # Enforce fail-percent / strict after outputs
    if args.fail_percent is not None and percent > args.fail_percent:
        raise SystemExit(1)
    if args.strict and not allc:
        raise SystemExit(1)


def verify_main():
    return main()


if __name__ == "__main__":
    verify_main()
