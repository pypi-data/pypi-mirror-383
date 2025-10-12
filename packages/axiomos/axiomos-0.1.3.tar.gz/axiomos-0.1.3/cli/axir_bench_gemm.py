# cli/axir_bench_gemm.py
#!/usr/bin/env python3
import time, json, pathlib, argparse, csv
import numpy as np

# petite fab AXIR pour un GEMM (option bias)
def make_gemm_axir(M, N, K, with_bias=False):
    ops = [
        {"op":"DeviceMalloc","dst":"dA","bytes": f"{M*K}*sizeof(float)"},
        {"op":"DeviceMalloc","dst":"dB","bytes": f"{K*N}*sizeof(float)"},
        {"op":"DeviceMalloc","dst":"dC","bytes": f"{M*N}*sizeof(float)"},
        # H2D (A,B)
        {"op":"Memcpy","kind":"H2D","src":"hA","dst":"dA","bytes": f"{M*K}*sizeof(float)"},
        {"op":"Memcpy","kind":"H2D","src":"hB","dst":"dB","bytes": f"{K*N}*sizeof(float)"},
    ]
    if with_bias:
        ops += [
            {"op":"DeviceMalloc","dst":"dBias","bytes": f"{N}*sizeof(float)"},
            {"op":"Memcpy","kind":"H2D","src":"hBias","dst":"dBias","bytes": f"{N}*sizeof(float)"},
        ]
    # lancement: “gemm” couvre naive/tiled/2x2 + versions fusionnées si dBias présent
    ops.append({"op":"KernelLaunch","kernel":"gemm","args":["dA","dB","dC","M","N","K"]})
    # D2H pour vérifier (on ne l’exploite pas ici)
    ops.append({"op":"Memcpy","kind":"D2H","src":"dC","dst":"hC","bytes": f"{M*N}*sizeof(float)"})
    ax = {
        "types":{
            "scalars":{"M":{"dtype":"i32","value":M},"N":{"dtype":"i32","value":N},"K":{"dtype":"i32","value":K}},
            "buffers":{"dA":{"dtype":"f32"},"dB":{"dtype":"f32"},"dC":{"dtype":"f32"}}
        },
        "ops": ops
    }
    if with_bias:
        ax["types"]["buffers"]["dBias"]={"dtype":"f32"}
    return ax

def run_one(M,N,K, with_bias=False):
    from backends.opencl_backend import run as run_ocl

    ax = make_gemm_axir(M,N,K, with_bias=with_bias)

    # mur (wall time) mesuré ici
    t0 = time.perf_counter()
    res = run_ocl(ax, bench=True)
    t1 = time.perf_counter()
    wall_ms = (t1 - t0)*1000.0

    # si le backend fournit un nom de kernel (bench) on l’utilise
    kern = "?"
    if isinstance(res, dict) and "bench" in res and isinstance(res["bench"], dict):
        kern = res["bench"].get("kernel") or kern

    # GF/s sur wall-time (pratique et robuste)
    ops = 2.0 * M * N * K
    gflops = ops / (wall_ms/1000.0) / 1e9 if wall_ms > 0 else 0.0

    print(f"{M:5}x{N:4}x{K:4} | kernel={kern:20} | wall={wall_ms:7.1f} ms | {gflops:7.2f} GF/s")
    return {
        "M":M,"N":N,"K":K,
        "kernel":kern,
        "wall_ms":wall_ms,
        "gflops":gflops
    }

def main():
    ap = argparse.ArgumentParser(description="GEMM bench (OpenCL) — wall-time based")
    ap.add_argument("--bias", action="store_true", help="Bench avec Bias (active kernels fusionnés)")
    ap.add_argument("--sizes", default="64,128,256,512", help="Tailles carrées comma-sep (ex: 64,128,256)")
    ap.add_argument("--csv", default="build/axir_gemm_bench.csv", help="Chemin CSV de sortie")
    ap.add_argument("--md",  default="build/axir_gemm_bench.md",  help="Chemin Markdown de sortie")
    args = ap.parse_args()

    sizes = [int(s.strip()) for s in args.sizes.split(",") if s.strip()]

    print("== GEMM bench (OpenCL) ==")
    rows = []
    for n in sizes:
        r = run_one(n,n,n, with_bias=args.bias)
        rows.append(r)

    # CSV
    pathlib.Path(args.csv).parent.mkdir(parents=True, exist_ok=True)
    with open(args.csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["M","N","K","kernel","wall_ms","gflops"])
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # Markdown
    md = ["# AXIR GEMM Bench (OpenCL)\n",
          f"- with_bias: {'yes' if args.bias else 'no'}\n",
          "| M | N | K | kernel | wall_ms | GF/s |",
          "|---:|---:|---:|:--|---:|---:|"]
    for r in rows:
        md.append(f"| {r['M']} | {r['N']} | {r['K']} | {r['kernel']} | {r['wall_ms']:.1f} | {r['gflops']:.2f} |")
    pathlib.Path(args.md).write_text("\n".join(md), encoding="utf-8")

    print(f"[BENCH] results saved to {args.csv} and {args.md}")

if __name__ == "__main__":
    main()
