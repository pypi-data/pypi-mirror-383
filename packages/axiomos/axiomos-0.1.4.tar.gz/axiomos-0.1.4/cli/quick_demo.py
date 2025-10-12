# -*- coding: utf-8 -*-
"""
cli.quick_demo : mini démo utilisable en 1 commande.
- Compare 2 fixtures (vector_add, softmax2d) entre CPU et OpenCL (si activé).
- Affiche PASS/FAIL + gère les shapes (flatten si même taille).
"""
from __future__ import annotations
import os, pathlib, sys, traceback
from typing import List
import numpy as np
from cli import verify_axir as V

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"

def _run_case(axir_name: str, buffer: str, a: str, b: str) -> bool:
    axir = BUILD / axir_name
    if not axir.exists():
        print(f"[DEMO] missing fixture: {axir}")
        return False
    print("\n========================================")
    print(f"[DEMO] {axir.name} | BUFFER: {buffer} | BACKENDS: {a} vs {b}")
    try:
        V.run_backend(V.resolve_backend_script(b), axir, buffer, axir.parent / f"verify_{b}_{buffer}.npy", quiet=False)
        V.run_backend(V.resolve_backend_script(a), axir, buffer, axir.parent / f"verify_{a}_{buffer}.npy", quiet=True)
        a_arr = np.load(axir.parent / f"verify_{a}_{buffer}.npy")
        b_arr = np.load(axir.parent / f"verify_{b}_{buffer}.npy")
        if a_arr.shape != b_arr.shape:
            if a_arr.size == b_arr.size:
                a_arr = a_arr.reshape(-1)
                b_arr = b_arr.reshape(-1)
                print(f"[DEMO] note: flattened for comparison (sizes match: {a_arr.size})")
            else:
                print(f"[DEMO] shape mismatch: {a_arr.shape} vs {b_arr.shape}")
                return False
        ok = bool(np.allclose(a_arr, b_arr, atol=1e-6, rtol=0.0))
        print(f"[DEMO] RESULT: {'PASS' if ok else 'FAIL'}")
        return ok
    except Exception:
        traceback.print_exc()
        return False

def main(argv: List[str] | None = None) -> int:
    print("=== AXIOMOS DEMO ===")
    real = (os.getenv("AXIOMOS_OCL_REAL", "0") == "1")
    b = "opencl" if real else "cpu"
    print(f"[info] AXIOMOS_OCL_REAL={'1' if real else '0'}  → right backend: {b}")
    ok1 = _run_case("vector_add_small.axir.json", "hC", "cpu", b)
    ok2 = _run_case("softmax2d_small.axir.json", "hY", "cpu", b)
    ok = ok1 and ok2
    print("\n[DEMO] SUMMARY:", "ALL PASS ✅" if ok else "Some FAIL ❌")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))