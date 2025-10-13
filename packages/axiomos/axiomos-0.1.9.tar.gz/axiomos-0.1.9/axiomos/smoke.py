import time
import numpy as np

def main():
    print("🔥 Axiomos Smoke — tiny benchmark simulation")

    a = np.random.rand(512, 512).astype(np.float32)
    b = np.random.rand(512, 512).astype(np.float32)

    # Warmup
    for _ in range(3):
        _ = a @ b

    # Benchmark
    t0 = time.time()
    for _ in range(5):
        _ = a @ b
    t1 = time.time()

    avg_ms = (t1 - t0) / 5 * 1000
    print(f"✅ Simulated matmul benchmark: {avg_ms:.2f} ms (CPU)")
    print("Note: this is a demo, not the real backend performance.")

if __name__ == "__main__":
    main()
