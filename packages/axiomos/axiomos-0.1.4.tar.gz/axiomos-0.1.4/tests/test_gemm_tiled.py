import pyopencl as cl
import numpy as np
import time
import csv

TILE = 16

# 👉 Mets ici le peak théorique de ton GPU (GFLOP/s)
# Exemple: Intel Iris Xe ~ 700 GFLOP/s, RTX 3060 ~ 4600 GFLOP/s
GPU_PEAK_GFLOPS = 700.0

def run_gemm(ctx, queue, M, K, N, program):
    A = np.random.rand(M, K).astype(np.float32)
    B = np.random.rand(K, N).astype(np.float32)
    C = np.zeros((M, N), dtype=np.float32)

    mf = cl.mem_flags
    buf_A = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=A)
    buf_B = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=B)
    buf_C = cl.Buffer(ctx, mf.WRITE_ONLY, C.nbytes)

    global_size = (M, N)
    local_size = (TILE, TILE)

    # Warm-up
    program.gemm_tiled(queue, global_size, local_size,
                       buf_A, buf_B, buf_C,
                       np.int32(M), np.int32(N), np.int32(K))
    queue.finish()

    # Mesure temps
    start = time.time()
    program.gemm_tiled(queue, global_size, local_size,
                       buf_A, buf_B, buf_C,
                       np.int32(M), np.int32(N), np.int32(K))
    queue.finish()
    end = time.time()

    cl.enqueue_copy(queue, C, buf_C).wait()
    C_ref = A @ B
    max_err = float(np.max(np.abs(C - C_ref)))

    gflops = (2.0 * M * N * K) / (end - start) / 1e9
    percent_peak = (gflops / GPU_PEAK_GFLOPS) * 100.0

    return end - start, gflops, percent_peak, max_err

if __name__ == "__main__":
    platforms = cl.get_platforms()
    devices = platforms[0].get_devices()
    ctx = cl.Context([devices[0]])
    queue = cl.CommandQueue(ctx)

    with open("Demos/matmul/gemm_tiled.cl") as f:
        kernel_src = f.read()
    program = cl.Program(ctx, kernel_src).build()

    sizes = [128, 256, 512, 1024, 2048]
    results = []

    print(f"{'Size':>8} | {'Time (s)':>9} | {'GFLOP/s':>10} | {'%Peak':>7} | {'Max err':>10}")
    print("-" * 60)

    for n in sizes:
        t, gflops, pct, err = run_gemm(ctx, queue, n, n, n, program)
        results.append((n, t, gflops, pct, err))
        print(f"{n:>8} | {t:9.4f} | {gflops:10.2f} | {pct:7.2f}% | {err:10.2e}")

    # Export CSV
    with open("build/gemm_tiled_bench.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Size", "Time_s", "GFLOP/s", "%Peak", "Max_err"])
        writer.writerows(results)

    # Export Markdown
    with open("build/gemm_tiled_bench.md", "w") as f:
        f.write("| Size | Time (s) | GFLOP/s | %Peak | Max err |\n")
        f.write("|------|----------|---------|-------|---------|\n")
        for n, t, gflops, pct, err in results:
            f.write(f"| {n} | {t:.4f} | {gflops:.2f} | {pct:.2f}% | {err:.2e} |\n")

    print("\nRésultats exportés dans build/gemm_tiled_bench.csv et .md ✅")
