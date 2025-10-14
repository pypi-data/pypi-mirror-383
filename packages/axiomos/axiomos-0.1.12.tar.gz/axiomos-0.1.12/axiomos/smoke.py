import argparse, time, numpy as np
from importlib.metadata import version, PackageNotFoundError

def _pkg_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "not installed"

def main():
    p = argparse.ArgumentParser(description="Tiny latency smoke test (public showcase).")
    p.add_argument("--size", type=int, default=512, help="Matrix size N for NxN matmul (default: 512)")
    p.add_argument("--warmup", type=int, default=3, help="Warmup iterations (default: 3)")
    p.add_argument("--repeat", type=int, default=30, help="Timed iterations (default: 30)")
    p.add_argument("--seed", type=int, default=0, help="RNG seed for reproducibility (default: 0)")
    args = p.parse_args()

    print("🔒 Public showcase build — minimal backend (private core under NDA)")
    print("🔥 Axiomos Smoke — tiny benchmark simulation\n")
    print(f"🧾 Versions: axiomos {_pkg_version('axiomos')} | numpy {np.__version__}\n")

    np.random.seed(args.seed)
    N = args.size
    a = np.random.rand(N, N).astype(np.float32)
    b = np.random.rand(N, N).astype(np.float32)

    # Warmup
    for _ in range(args.warmup):
        _ = a @ b

    # Timed runs
    times_ms = []
    for _ in range(args.repeat):
        t0 = time.perf_counter()
        _ = a @ b
        t1 = time.perf_counter()
        times_ms.append((t1 - t0) * 1000)

    times = np.array(times_ms, dtype=np.float64)
    p50, p95 = np.percentile(times, [50, 95])
    mean, best = times.mean(), times.min()
    # Rough FLOPs: 2*N^3 for GEMM
    gflops_p50 = (2 * (N**3)) / ((p50/1000.0) * 1e9)

    print(f"Size       : {N} x {N}")
    print(f"Warmup     : {args.warmup}  |  Repeat: {args.repeat}")
    print(f"Latency    : p50={p50:.3f} ms  p95={p95:.3f} ms  mean={mean:.3f} ms  best={best:.3f} ms")
    print(f"Throughput : ~{gflops_p50:.2f} GFLOP/s (p50, CPU numpy)")
    print("\nNote: indicative only — public minimal path, not optimized.\n")

if __name__ == "__main__":
    main()
