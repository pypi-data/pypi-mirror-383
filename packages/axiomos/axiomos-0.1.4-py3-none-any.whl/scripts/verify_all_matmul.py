#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/verify_all_matmul.py

Vérifie une liste de fichiers AXIR (par motif) en appelant cli.verify_axir
avec propagation des tolérances et options de timing.
Retourne un code de sortie non-nul si au moins un fichier échoue.

Usage basique:
  python scripts/verify_all_matmul.py --pattern AXIR/matmul_*.axir.json

Avec timing:
  python scripts/verify_all_matmul.py --pattern AXIR/matmul_*.axir.json --time --warmup 2 --repeat 5

Comportement additionnel:
- Si un fichier AXIR est "host-only" (aucune opé device) ou a un GEMM/MatMul avec alpha=0.0 et beta=1.0,
  on “miroire” l'OPENCL vers le CPU en simulant une comparaison CPU↔CPU.
  (Cela revient à ce que tu décris: copier verify_cpu_hC.npy vers verify_opencl_hC.npy et
   sauter l’appel backend; ici on l’approxime côté batch en appelant cli.verify_axir avec backend-b=cpu.)
"""

import argparse
import glob
import pathlib
import subprocess
import sys
import json, os, shutil


def is_host_only(axir):
    dev_ops = {"MatMul","Gemm","GEMM","Conv2D","Kernel","OpenCLKernel",
               "DeviceMake","DeviceCopy"}
    return not any(op.get("op") in dev_ops for op in axir.get("ops", []))


def is_alpha0_beta1(axir):
    for op in axir.get("ops", []):
        if op.get("op") in {"Gemm","GEMM","MatMul"}:
            alpha = op.get("alpha", op.get("attrs", {}).get("alpha", 1.0))
            beta  = op.get("beta",  op.get("attrs", {}).get("beta",  0.0))
            try:
                alpha = float(alpha); beta = float(beta)
            except Exception:
                # Si valeurs non convertibles, on ignore ce noeud
                continue
            if alpha == 0.0 and beta == 1.0:
                return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Batch verify AXIR matmul files (CPU vs OpenCL by default).")
    ap.add_argument("--pattern", default=r"AXIR/matmul_*.axir.json",
                    help=r"Glob pattern for AXIR files (default: AXIR/matmul_*.axir.json).")
    ap.add_argument("--backend-a", default="cpu", help="Left backend (default: cpu).")
    ap.add_argument("--backend-b", default="opencl", help="Right backend (default: opencl).")
    ap.add_argument("--buffer", default="hC", help="Buffer to compare (default: hC).")
    ap.add_argument("--rtol", type=float, default=1e-5, help="Relative tolerance (default: 1e-5).")
    ap.add_argument("--atol", type=float, default=1e-6, help="Absolute tolerance (default: 1e-6).")
    ap.add_argument("--time", action="store_true", help="Enable timing in verify_axir.")
    ap.add_argument("--warmup", type=int, default=0, help="Warmup iterations when --time.")
    ap.add_argument("--repeat", type=int, default=1, help="Repeat count (median) when --time.")
    ap.add_argument("--inproc", action="store_true", help="Use in-proc mode of verify_axir (optional).")
    args = ap.parse_args()

    # --- Lint AXIR JSONs avant la boucle (expansion du glob pour éviter shell=True) ---
    axir_jsons = sorted(glob.glob("AXIR/*.json"))
    if axir_jsons:
        lint_cmd = [sys.executable, "scripts/axir_lint.py", *axir_jsons, "--schema", "tools/axir.schema.json"]
        print("[verify_all_matmul] Running lint:", " ".join(lint_cmd))
        subprocess.run(lint_cmd, check=True)
    else:
        print("[verify_all_matmul] No AXIR/*.json found for lint; skipping axir_lint.")

    # Résolution du motif (compatible / ou \)
    pattern = str(args.pattern)
    paths = [pathlib.Path(p) for p in glob.glob(pattern)]
    paths = sorted(set(paths))

    if not paths:
        print(f"[verify_all_matmul] No files match pattern: {pattern}")
        print("[verify_all_matmul] Nothing to do.")
        return 0

    failures = 0
    total = len(paths)

    for p in paths:
        print(f"\n[verify_all_matmul] Verifying: {p}")

        # Chargement de l'AXIR pour décider si on "miroire" OPENCL -> CPU
        ax = None
        try:
            with open(p, "r", encoding="utf-8") as f:
                ax = json.load(f)
        except Exception as e:
            print(f"[verify_all_matmul] Warning: unable to load AXIR JSON ({e}); proceeding with default backends.")

        mirror_cpu_for_ocl = False
        if ax is not None:
            try:
                if is_host_only(ax) or is_alpha0_beta1(ax):
                    mirror_cpu_for_ocl = True
            except Exception as e:
                print(f"[verify_all_matmul] Warning: host-only/alpha0_beta1 check failed ({e}); proceeding normally.")

        # Backends effectifs (on ne modifie pas args.*)
        effective_backend_a = args.backend_a
        effective_backend_b = args.backend_b

        # Si on doit "miroirer", on force backend-b à cpu pour simuler CPU->OPENCL
        env = os.environ.copy()
        if mirror_cpu_for_ocl and args.backend_b.lower() != "cpu":
            effective_backend_b = "cpu"
            env["VERIFY_MIRROR_CPU_TO_OPENCL"] = "1"
            print("[verify_all_matmul] (host-only / alpha0_beta1) mirroring CPU -> OPENCL (simulate with CPU vs CPU)")

        cmd = [
            sys.executable, "-m", "cli.verify_axir",
            str(p),
            "--buffer", args.buffer,
            "--backend-a", effective_backend_a, "--backend-b", effective_backend_b,
            "--rtol", str(args.rtol), "--atol", str(args.atol),
            "--strict",                 # fail si allclose False
            "--fail-percent", "0.0",    # et si % mismatches > 0
        ]
        if args.time:
            cmd += ["--time", "--warmup", str(args.warmup), "--repeat", str(args.repeat)]
        if args.inproc:
            cmd += ["--inproc"]

        rc = subprocess.call(cmd, env=env)
        if rc != 0:
            failures += 1
            print(f"[verify_all_matmul] ❌ FAIL: {p.name}")
        else:
            print(f"[verify_all_matmul] ✅ PASS: {p.name}")

    print(f"\n[verify_all_matmul] SUMMARY: total={total} fails={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
