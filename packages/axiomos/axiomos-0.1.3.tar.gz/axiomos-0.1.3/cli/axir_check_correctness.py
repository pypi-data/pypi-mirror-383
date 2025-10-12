# cli/axir_check_correctness.py
#!/usr/bin/env python3
import numpy as np
from backends.opencl_backend import run as run_ocl

def axir_matmul(M, N, K):
    return {
        "types": {
            "scalars": {"M":{"value":M}, "N":{"value":N}, "K":{"value":K}},
            "buffers": {
                "dA":{"dtype":"f32"}, "dB":{"dtype":"f32"}, "dC":{"dtype":"f32"},
                "hA":{"dtype":"f32"}, "hB":{"dtype":"f32"}, "hC":{"dtype":"f32"},
            }
        },
        "ops": [
            {"op":"DeviceMalloc","dst":"dA","bytes": f"{M*K}*4"},
            {"op":"DeviceMalloc","dst":"dB","bytes": f"{K*N}*4"},
            {"op":"DeviceMalloc","dst":"dC","bytes": f"{M*N}*4"},
            {"op":"Memcpy","kind":"H2D","src":"hA","dst":"dA","bytes": f"{M*K}*4"},
            {"op":"Memcpy","kind":"H2D","src":"hB","dst":"dB","bytes": f"{K*N}*4"},
            {"op":"KernelLaunch","kernel":"matmul","args":["dA","dB","dC","M","N","K"]},
            {"op":"Memcpy","kind":"D2H","src":"dC","dst":"hC","bytes": f"{M*N}*4"},
        ]
    }

def axir_reduce_sum(N):
    return {
        "types": {
            "scalars": {"N":{"value":N}},
            "buffers": {"dA":{"dtype":"f32"}, "hA":{"dtype":"f32"}, "dOut":{"dtype":"f32"}, "hOut":{"dtype":"f32"}}
        },
        "ops": [
            {"op":"DeviceMalloc","dst":"dA","bytes": f"{N}*4"},
            {"op":"Memcpy","kind":"H2D","src":"hA","dst":"dA","bytes": f"{N}*4"},
            {"op":"KernelLaunch","kernel":"reduce_sum","args":["dA","dOut","N"]},
            {"op":"Memcpy","kind":"D2H","src":"dOut","dst":"hOut","bytes": "4"},
        ]
    }

def axir_argmax(N):
    return {
        "types": {
            "scalars": {"N":{"value":N}},
            "buffers": {
                "dA":{"dtype":"f32"}, "hA":{"dtype":"f32"},
                "dOut":{"dtype":"f32"}, "dIdx":{"dtype":"i32"},
                "hOut":{"dtype":"f32"}, "hIdx":{"dtype":"i32"},
            }
        },
        "ops": [
            {"op":"DeviceMalloc","dst":"dA","bytes": f"{N}*4"},
            {"op":"Memcpy","kind":"H2D","src":"hA","dst":"dA","bytes": f"{N}*4"},
            {"op":"KernelLaunch","kernel":"reduce_argmax","args":["dA","dOut","dIdx","N"]},
            {"op":"Memcpy","kind":"D2H","src":"dOut","dst":"hOut","bytes": "4"},
            {"op":"Memcpy","kind":"D2H","src":"dIdx","dst":"hIdx","bytes": "4"},
        ]
    }

def max_abs_rel(a, b, eps=1e-8):
    a = np.asarray(a, dtype=np.float64).ravel()
    b = np.asarray(b, dtype=np.float64).ravel()
    diff = np.abs(a-b)
    rel  = diff / (np.abs(b) + eps)
    return diff.max(initial=0.0), rel.max(initial=0.0)

def test_matmul(M, N, K):
    print(f"[matmul] {M}x{N}x{K}")
    # IMPORTANT: répliquer les init backend (hA = arange, hB = 2*arange)
    A = np.arange(M*K, dtype=np.float32).reshape(M,K)
    B = (2*np.arange(K*N, dtype=np.float32)).reshape(K,N)
    C_ref = A @ B

    ax = axir_matmul(M,N,K)
    # Le backend ignore un dict host externe; on passe par H2D via ops et il génère
    # les buffers hA/hB automatiquement selon le nom (mêmes règles que ci-dessus).
    # Pour s’assurer que le backend reçoit *ces* valeurs, on refait un run pour dump.
    _ = run_ocl(ax, summary=False, dump=None, repeats=1)  # exécute
    C_gpu = run_ocl(ax, summary=False, dump="hC", repeats=1).get("dump").reshape(M,N)

    mad, mrel = max_abs_rel(C_gpu, C_ref)
    print(f"  max|diff|={mad:.3e}   max rel={mrel:.3e}")
    return mad, mrel

def test_reduce_sum(N):
    print(f"[reduce_sum] N={N}")
    hA = np.arange(N, dtype=np.float32)
    ref = np.array([hA.sum(dtype=np.float64)], dtype=np.float32)
    ax = axir_reduce_sum(N)
    _ = run_ocl(ax, summary=False, dump=None, repeats=1)
    out = run_ocl(ax, summary=False, dump="hOut", repeats=1).get("dump")
    mad, mrel = max_abs_rel(out, ref)
    print(f"  out={out[0]:.6e}  ref={ref[0]:.6e}  max|diff|={mad:.3e}  max rel={mrel:.3e}")
    return mad, mrel

def test_argmax(N):
    print(f"[argmax] N={N}")
    # Conformément au backend: hA = arange(N) -> max = N-1, idx = N-1
    ref_val = float(N-1)
    ref_idx = int(N-1)
    ax = axir_argmax(N)
    _ = run_ocl(ax, summary=False, dump=None, repeats=1)
    v = float(run_ocl(ax, summary=False, dump="hOut", repeats=1).get("dump")[0])
    i = int(run_ocl(ax, summary=False, dump="hIdx", repeats=1).get("dump")[0])
    print(f"  value={v:.6e} (ref {ref_val:.6e})  idx={i} (ref {ref_idx})")
    ok = (abs(v-ref_val) < 1e-3) and (i == ref_idx)
    return ok

def main():
    # Pour un test “strict” : AXIR_STRICT=1 et AXIR_FORCE_NAIVE_GEMM=1 dans l’environnement
    sizes = [(64,64,64), (128,128,128), (256,256,256)]
    worst_mad = 0.0
    worst_rel = 0.0
    for (M,N,K) in sizes:
        mad, mrel = test_matmul(M,N,K)
        worst_mad = max(worst_mad, mad)
        worst_rel = max(worst_rel, mrel)
    print(f"\n[matmul] worst max|diff|={worst_mad:.3e}  worst max rel={worst_rel:.3e}\n")

    test_reduce_sum(16)
    test_reduce_sum(10_000_000)

    ok = test_argmax(16)
    print(f"[argmax] status: {'OK' if ok else 'FAIL'}")

if __name__ == "__main__":
    main()
