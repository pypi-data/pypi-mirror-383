#!/usr/bin/env python3
import csv, pathlib
import numpy as np
from backends.opencl_backend import run as run_ocl

def axir_reduce_sum(N):
    return {
        "types":{"scalars":{"N":{"value":N}},"buffers":{"dA":{},"hA":{},"dOut":{},"hOut":{}}},
        "ops":[
            {"op":"DeviceMalloc","dst":"dA","bytes": f"{N}*4"},
            {"op":"Memcpy","kind":"H2D","src":"hA","dst":"dA","bytes": f"{N}*4"},
            {"op":"KernelLaunch","kernel":"reduce_sum","args":["dA","dOut","N"]},
            {"op":"Memcpy","kind":"D2H","src":"dOut","dst":"hOut","bytes":"4"},
        ]
    }

def axir_softmax(M,N):
    return {
        "types":{"scalars":{"M":{"value":M},"N":{"value":N}},
                 "buffers":{"dX":{},"dY":{},"hX":{},"hY":{}}},
        "ops":[
            {"op":"DeviceMalloc","dst":"dX","bytes": f"{M*N}*4"},
            {"op":"DeviceMalloc","dst":"dY","bytes": f"{M*N}*4"},
            {"op":"Memcpy","kind":"H2D","src":"hX","dst":"dX","bytes": f"{M*N}*4"},
            {"op":"KernelLaunch","kernel":"softmax2d","args":["dX","dY","M","N","1"]},
            {"op":"Memcpy","kind":"D2H","src":"dY","dst":"hY","bytes": f"{M*N}*4"},
        ]
    }

def bench_reduce():
    sizes=[100_000, 1_000_000, 10_000_000]
    rows=[]
    for N in sizes:
        ax = axir_reduce_sum(N)
        r = run_ocl(ax, bench=True)
        rows.append({"op":"reduce_sum","N":N, **r})
    return rows

def bench_softmax():
    sizes=[(1024,512),(2048,1024)]
    rows=[]
    for (M,N) in sizes:
        ax = axir_softmax(M,N)
        r = run_ocl(ax, bench=True)
        rows.append({"op":"softmax2d","M":M,"N":N, **r})
    return rows

def main():
    out = pathlib.Path("build/axir_bench_suite.csv")
    out_md = pathlib.Path("build/axir_bench_suite.md")
    out.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    rows += bench_reduce()
    rows += bench_softmax()

    # CSV
    with out.open("w", newline="") as f:
        if rows:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)

    # MD
    with out_md.open("w", encoding="utf-8") as f:
        f.write("# AXIR Bench Suite (OpenCL)\n\n")
        for r in rows:
            if r["op"]=="reduce_sum":
                f.write(f"- reduce_sum N={r['N']}: kernel={r['kernel']} KER={r['Kernel']:.1f}ms E2E={r['E2E']:.1f}ms\n")
            else:
                f.write(f"- softmax2d M={r['M']} N={r['N']}: kernel={r['kernel']} KER={r['Kernel']:.1f}ms E2E={r['E2E']:.1f}ms\n")
    print(f"[SUITE] saved to {out} and {out_md}")

if __name__ == "__main__":
    main()
