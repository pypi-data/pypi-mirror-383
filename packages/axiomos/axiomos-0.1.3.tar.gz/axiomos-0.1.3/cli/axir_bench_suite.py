# cli/axir_bench_suite.py
#!/usr/bin/env python3
import time, numpy as np

from backends.cpu_numpy_backend import run as run_cpu
from backends.opencl_backend import run as run_ocl

# --------------------------------------------------------------------
# AXIR builders (on-the-fly) : H2D once -> kernels -> D2H once
# --------------------------------------------------------------------
def axir_vector_add_pipeline(N, repeats=10):
    # dA,dB <- hA,hB ; (repeats x vector_add) ; hC <- dC
    return {
        "types": {
            "scalars": {"N": {"dtype":"i32","value": int(N)}},
            "buffers": {"hA":{"dtype":"f32"},"hB":{"dtype":"f32"},"hC":{"dtype":"f32"},
                        "dA":{"dtype":"f32"},"dB":{"dtype":"f32"},"dC":{"dtype":"f32"}}
        },
        "ops": (
            [
                {"op":"DeviceMalloc","dst":"dA","bytes":"N*sizeof(float)"},
                {"op":"DeviceMalloc","dst":"dB","bytes":"N*sizeof(float)"},
                {"op":"DeviceMalloc","dst":"dC","bytes":"N*sizeof(float)"},
                {"op":"Memcpy","kind":"H2D","src":"hA","dst":"dA","bytes":"N*sizeof(float)"},
                {"op":"Memcpy","kind":"H2D","src":"hB","dst":"dB","bytes":"N*sizeof(float)"},
            ]
            + [
                {"op":"KernelLaunch","kernel":"vector_add","grid":[str(N), "1", "1"],"block":["1","1","1"],
                 "args":["dA","dB","dC","N"]}
              for _ in range(repeats)
            ]
            + [
                {"op":"Memcpy","kind":"D2H","src":"dC","dst":"hC","bytes":"N*sizeof(float)"}
            ]
        )
    }

def axir_softmax2d_pipeline(M, N, repeats=5):
    # dX <- hX ; (repeats x softmax2d) ; hY <- dY
    return {
        "types": {
            "scalars": {"M":{"dtype":"i32","value":int(M)}, "N":{"dtype":"i32","value":int(N)}},
            "buffers": {"hX":{"dtype":"f32"},"hY":{"dtype":"f32"},
                        "dX":{"dtype":"f32"},"dY":{"dtype":"f32"}}
        },
        "ops": (
            [
                {"op":"DeviceMalloc","dst":"dX","bytes":"M*N*sizeof(float)"},
                {"op":"DeviceMalloc","dst":"dY","bytes":"M*N*sizeof(float)"},
                {"op":"Memcpy","kind":"H2D","src":"hX","dst":"dX","bytes":"M*N*sizeof(float)"},
            ]
            + [
                {"op":"KernelLaunch","kernel":"softmax2d","grid":[str(M),"1","1"],"block":["128","1","1"],
                 "args":["dX","dY","M","N"]}
              for _ in range(repeats)
            ]
            + [
                {"op":"Memcpy","kind":"D2H","src":"dY","dst":"hY","bytes":"M*N*sizeof(float)"}
            ]
        )
    }

def axir_matmul_pipeline(M, N, K):
    # dA <- hA ; dB <- hB ; matmul ; hC <- dC
    return {
        "types": {
            "scalars": {"M":{"dtype":"i32","value":int(M)},
                        "N":{"dtype":"i32","value":int(N)},
                        "K":{"dtype":"i32","value":int(K)}},
            "buffers": {"hC":{"dtype":"f32"},
                        "dA":{"dtype":"f32"},"dB":{"dtype":"f32"},"dC":{"dtype":"f32"}}
        },
        "ops": [
            {"op":"DeviceMalloc","dst":"dA","bytes":"M*K*sizeof(float)"},
            {"op":"DeviceMalloc","dst":"dB","bytes":"K*N*sizeof(float)"},
            {"op":"DeviceMalloc","dst":"dC","bytes":"M*N*sizeof(float)"},
            {"op":"Memcpy","kind":"H2D","src":"hA","dst":"dA","bytes":"M*K*sizeof(float)"},
            {"op":"Memcpy","kind":"H2D","src":"hB","dst":"dB","bytes":"K*N*sizeof(float)"},
            {"op":"KernelLaunch","kernel":"matmul","grid":[str(M),str(N),"1"],"block":["1","1","1"],
             "args":["dA","dB","dC","M","N","K"]},
            {"op":"Memcpy","kind":"D2H","src":"dC","dst":"hC","bytes":"M*N*sizeof(float)"},
        ]
    }

# --------------------------------------------------------------------
def time_ms(fn, *a, **kw):
    t0 = time.perf_counter()
    fn(*a, **kw)
    return (time.perf_counter() - t0) * 1000.0

def bench_case(name, ax, repeat_kernel=1):
    # E2E timings (copies + kernels). On passe repeat_kernel au backend (il répète chaque KernelLaunch).
    cpu_ms = time_ms(run_cpu, ax, summary=False, dump=None, repeats=repeat_kernel)
    ocl_ms = time_ms(run_ocl, ax, summary=False, dump=None, repeats=repeat_kernel)
    return name, cpu_ms, ocl_ms, (cpu_ms / ocl_ms if ocl_ms > 0 else float("nan"))

def main():
    print("=== AXIR pipeline bench (CPU vs OPENCL) ===")
    print("Note: H2D une fois -> kernels -> D2H une fois")

    # 1) vector_add — 10 itérations dans le même pipeline (amortit les copies)
    sizes = [10_000, 100_000, 1_000_000, 10_000_000]
    print("\n(vector_add x10)  N,cpu_ms,ocl_ms,speedup(GPU faster = >1.0)")
    for N in sizes:
        ax = axir_vector_add_pipeline(N, repeats=10)
        name, cpu_ms, ocl_ms, sp = bench_case("vadd10", ax, repeat_kernel=1)
        print(f"{N},{cpu_ms:.1f},{ocl_ms:.1f},{sp:.2f}")

    # 2) softmax 2D — M=2048, N varie, 5 itérations
    Ns = [256, 512, 1024, 2048]
    print("\n(softmax2d x5, M=2048)  N,cpu_ms,ocl_ms,speedup")
    for N in Ns:
        ax = axir_softmax2d_pipeline(M=2048, N=N, repeats=5)
        name, cpu_ms, ocl_ms, sp = bench_case("softmax5", ax, repeat_kernel=1)
        print(f"{N},{cpu_ms:.1f},{ocl_ms:.1f},{sp:.2f}")

    # 3) matmul — tailles carrées croissantes (1 seule passe)
    mats = [ (256,256,256), (512,512,512), (1024,1024,1024) ]
    print("\n(matmul naive)  N,cpu_ms,ocl_ms,speedup")
    for (M,N,K) in mats:
        ax = axir_matmul_pipeline(M,N,K)
        name, cpu_ms, ocl_ms, sp = bench_case("matmul", ax, repeat_kernel=1)
        print(f"{N},{cpu_ms:.1f},{ocl_ms:.1f},{sp:.2f}")

if __name__ == "__main__":
    main()
