#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AXIR smoke runner: lance des vérifications type "verify" sur un ou plusieurs AXIR JSON
et résume les résultats, avec timing optionnel (run unique ou médiane sur répétitions)
et export de rapport.

Exemples :
  python -m cli.smoke_axir --axir build/matmul_from_hip.axir.json --buffer auto
  python -m cli.smoke_axir --axir "build/*from_*.axir.json" --buffer auto --backend-a cpu --backend-b opencl --strict
  python -m cli.smoke_axir --axir "build/*from_*.axir.json" --buffer auto --backend-a cpu --backend-b opencl ^
      --time --warmup 2 --repeat 5 --quiet ^
      --report-md build/verify_report.md --report-csv build/verify_report.csv
"""

import argparse
import glob
import pathlib
from typing import List, Dict, Optional
import numpy as np

# On réutilise les helpers de verify_axir (plus rapide et pratique pour récupérer les timings)
from cli import verify_axir as V


def maybe_auto_buffer(axir_path: pathlib.Path, buf: str) -> str:
    """Si --buffer=auto, pioche intelligemment un buffer présent dans l’AXIR."""
    if buf and buf.lower() != "auto":
        return buf
    names = V.list_axir_buffers(axir_path)
    if not names:
        raise SystemExit(f"[ERROR] No buffers found in AXIR: {axir_path}")
    preferred = ["hC", "hOut", "out", "output", "result"]
    chosen = next((p for p in preferred if p in names), names[0])
    print(f"[INFO] --buffer auto -> using '{chosen}'")
    return chosen


def _head(x: np.ndarray, k: int = 8) -> str:
    x = np.asarray(x).reshape(-1)
    return np.array2string(x[: min(k, x.size)], precision=6, separator=", ")


def run_one(axir_path: pathlib.Path,
           buffer: str,
           a: str,
           b: str,
           atol: float,
           rtol: float,   # <--- ajouté
           time_flag: bool,
           warmup: int,
           repeat: int,
           quiet: bool,
           inproc: bool) -> Dict[str, str]:
    print("\n========================================")
    print(f"[SMOKE] AXIR: {axir_path.name} | BUFFER: {buffer} | BACKENDS: {a} vs {b}")

    # Résolution du dump effectif (aligne fichiers .npy avec verify_axir)
    ax = V.load_axir(axir_path)
    dump_target = V._resolve_dump_target(ax, buffer)

    # Paths de sortie cohérents avec verify_axir
    out_a = axir_path.parent / f"verify_{a}_{dump_target}.npy"
    out_b = axir_path.parent / f"verify_{b}_{dump_target}.npy"

    # Choix du runner (subprocess vs inproc)
    # IMPORTANT : toujours retourner un temps en **secondes**
    def run_a_once(quiet_flag: bool):
        if inproc:
            _, dt_ms, _ = V.run_backend_inproc(a, axir_path, buffer, quiet=quiet_flag)
            return dt_ms / 1e3  # seconds
        script_a = V.resolve_backend_script(a)
        return V.run_backend(script_a, axir_path, dump_target, out_a, quiet=quiet_flag)  # seconds

    def run_b_once(quiet_flag: bool):
        if inproc:
            _, dt_ms, _ = V.run_backend_inproc(b, axir_path, buffer, quiet=quiet_flag)
            return dt_ms / 1e3  # seconds
        script_b = V.resolve_backend_script(b)
        return V.run_backend(script_b, axir_path, dump_target, out_b, quiet=quiet_flag)  # seconds

    # 1er run (fonctionnel + temps “first”)
    dt_a_first = run_a_once(quiet)
    dt_b_first = run_b_once(quiet)

    # Warmup + timing (médian) — toujours en secondes
    med_a = dt_a_first
    med_b = dt_b_first
    if time_flag and (warmup > 0 or repeat > 1):
        for _ in range(warmup):
            run_a_once(True)
            run_b_once(True)
        times_a = [run_a_once(True) for _ in range(repeat)]
        times_b = [run_b_once(True) for _ in range(repeat)]
        med_a = float(np.median(times_a))
        med_b = float(np.median(times_b))

    # Lecture des sorties (fichiers déjà écrits par les runners)
    a_arr = np.load(out_a)
    b_arr = np.load(out_b)

    # Comparaison (robuste aux différences de shape : on aplatit, puis on tronque au min si tailles différentes)
    print("---- RESULT ----")
    print(f"SHAPES     : {a.upper()}{a_arr.shape} vs {b.upper()}{b_arr.shape}")
    a_flat = a_arr.reshape(-1)
    b_flat = b_arr.reshape(-1)
    if a_flat.size != b_flat.size:
        min_len = min(a_flat.size, b_flat.size)
        print(f"[WARN] shape mismatch -> trimming to {min_len} elements")
        a_flat = a_flat[:min_len]
        b_flat = b_flat[:min_len]

    max_abs_err = float(np.max(np.abs(a_flat - b_flat))) if a_flat.size else 0.0
    allc = bool(np.allclose(a_flat, b_flat, atol=atol, rtol=rtol))
    print(f"max_abs_err: {max_abs_err}")
    print(f"ALLCLOSE   : {allc} (atol={atol}, rtol={rtol})")
    print(f"{a.upper()}(head): {_head(a_flat)}")
    print(f"{b.upper()}(head): {_head(b_flat)}")

    # Affichage timing (converti en ms à l’affichage)
    if time_flag:
        print("---- TIMING ----")
        if warmup > 0 or repeat > 1:
            print(f"Warmup: {warmup}, Repeats: {repeat} (median)")
            print(f"{a.upper():<9}: {med_a*1000:.2f} ms (median)")
            print(f"{b.upper():<9}: {med_b*1000:.2f} ms (median)")
        else:
            print(f"{a.upper():<9}: {dt_a_first*1000:.2f} ms")
            print(f"{b.upper():<9}: {dt_b_first*1000:.2f} ms")

    print("[SMOKE] RESULT:", "PASS" if allc else "FAIL")

    return {
        "file": axir_path.name,
        "buffer": dump_target,
        "backend_a": a,
        "backend_b": b,
        "ok": "true" if allc else "false",
        "dt_a_first_ms": f"{dt_a_first*1000:.2f}" if time_flag else "",
        "dt_b_first_ms": f"{dt_b_first*1000:.2f}" if time_flag else "",
        "med_a_ms": f"{med_a*1000:.2f}" if time_flag and (warmup > 0 or repeat > 1) else "",
        "med_b_ms": f"{med_b*1000:.2f}" if time_flag and (warmup > 0 or repeat > 1) else "",
        "max_abs_err": f"{max_abs_err:.6g}",
    }


def write_reports(rows: List[Dict[str, str]],
                  report_csv: Optional[str],
                  report_md: Optional[str],
                  include_timing: bool) -> None:
    if report_csv:
        p = pathlib.Path(report_csv)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as f:
            if include_timing:
                f.write("file,buffer,backend_a,backend_b,ok,dt_a_first_ms,dt_b_first_ms,med_a_ms,med_b_ms,max_abs_err\n")
            else:
                f.write("file,buffer,backend_a,backend_b,ok,max_abs_err\n")
            for r in rows:
                if include_timing:
                    f.write(",".join([
                        r["file"], r["buffer"], r["backend_a"], r["backend_b"], r["ok"],
                        r["dt_a_first_ms"], r["dt_b_first_ms"], r["med_a_ms"], r["med_b_ms"], r["max_abs_err"]
                    ]) + "\n")
                else:
                    f.write(",".join([
                        r["file"], r["buffer"], r["backend_a"], r["backend_b"], r["ok"], r["max_abs_err"]
                    ]) + "\n")
        print(f"[SMOKE] CSV report written to: {p}")

    if report_md:
        p = pathlib.Path(report_md)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as f:
            f.write("# AXIR Verification Report\n\n")
            if include_timing:
                f.write("| File | Buffer | Backends | Result | max_abs_err | tA_first (ms) | tB_first (ms) | tA_med (ms) | tB_med (ms) |\n")
                f.write("|------|--------|----------|--------|-------------|---------------|---------------|-------------|-------------|\n")
            else:
                f.write("| File | Buffer | Backends | Result | max_abs_err |\n")
                f.write("|------|--------|----------|--------|-------------|\n")
            for r in rows:
                backends = f"{r['backend_a']} vs {r['backend_b']}"
                result = "✅ PASS" if r["ok"] == "true" else "❌ FAIL"
                if include_timing:
                    f.write(f"| {r['file']} | {r['buffer']} | {backends} | {result} | {r['max_abs_err']} | "
                            f"{r['dt_a_first_ms']} | {r['dt_b_first_ms']} | {r['med_a_ms']} | {r['med_b_ms']} |\n")
                else:
                    f.write(f"| {r['file']} | {r['buffer']} | {backends} | {result} | {r['max_abs_err']} |\n")
        print(f"[SMOKE] Markdown report written to: {p}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Run multiple AXIR verifications and summarize results.")
    ap.add_argument("--axir", required=True,
                    help="AXIR file path or glob pattern (e.g., build/*.axir.json)")
    ap.add_argument("--buffer", required=True,
                    help="Buffer name (e.g., hC, hOut) or 'auto' to auto-pick.")
    ap.add_argument("--backend-a", default="cpu",
                    help="Left backend: cpu|opencl|cuda|hip|stub (default: cpu)")
    ap.add_argument("--backend-b", default="opencl",
                    help="Right backend: cpu|opencl|cuda|hip|stub (default: opencl)")
    ap.add_argument("--atol", type=float, default=1e-6,
                    help="Absolute tolerance for np.allclose (default: 1e-6)")
    ap.add_argument("--rtol", type=float, default=1e-5,
                    help="Relative tolerance for np.allclose (default: 1e-5)")
    ap.add_argument("--strict", action="store_true",
                    help="Exit with non-zero code if any verification fails.")
    ap.add_argument("--report-csv", default=None,
                    help="Write a CSV report to this path.")
    ap.add_argument("--report-md", default=None,
                    help="Write a Markdown report to this path.")
    ap.add_argument("--time", action="store_true",
                    help="Measure wall-clock times (single run or with warmup/repeats).")
    ap.add_argument("--warmup", type=int, default=0,
                    help="Warmup iterations per backend before timing (default: 0).")
    ap.add_argument("--repeat", type=int, default=1,
                    help="Timed iterations per backend (median reported if >1; default: 1).")
    ap.add_argument("--quiet", action="store_true",
                    help="Suppress backend stdout (useful with --warmup/--repeat).")

    # --- Option in-process ---
    ap.add_argument("--inproc", action="store_true",
                    help="Exécuter les backends en process courant (pas de subprocess) via verify_axir.run_backend_inproc")

    args = ap.parse_args(argv)

    # Expansion des globs
    paths = [pathlib.Path(p) for p in glob.glob(args.axir)]
    paths = [p for p in paths if p.exists()]
    if not paths:
        raise SystemExit(f"[ERROR] No AXIR files matched: {args.axir}")

    total = len(paths)
    passed = 0
    rows: List[Dict[str, str]] = []

    for p in paths:
        buf = maybe_auto_buffer(p, args.buffer)
        row = run_one(
            axir_path=p,
            buffer=buf,
            a=args.backend_a,
            b=args.backend_b,
            atol=args.atol,
            rtol=args.rtol,        # <--- ajouté
            time_flag=args.time,
            warmup=args.warmup,
            repeat=args.repeat,
            quiet=args.quiet,
            inproc=args.inproc,
        )
        rows.append(row)
        if row["ok"] == "true":
            passed += 1

    print("\n============== SUMMARY =================")
    print(f"Files: {total}, Passed: {passed}, Failed: {total - passed}")
    print("========================================")

    # Exports optionnels
    if args.report_csv or args.report_md:
        write_reports(rows, args.report_csv, args.report_md, include_timing=args.time)

    if args.strict and passed < total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
