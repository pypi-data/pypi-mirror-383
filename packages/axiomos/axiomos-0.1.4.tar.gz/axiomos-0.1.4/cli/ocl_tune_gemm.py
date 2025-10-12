# cli/ocl_tune_gemm.py
import os, re, json, subprocess, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
AXIR_DEFAULT = ROOT / "build" / "matmul_512.axir.json"  # tu peux changer si besoin

COMBOS = [
    (16,16,16),
    (16,16,8),
    (32,8,8),
    (8,32,8),
    (8,8,32),
]

def run_once(axir_path, TM, TN, TK, fastmath=False):
    env = os.environ.copy()
    env["AXIOMOS_OCL_REAL"] = "1"
    env["AXIOMOS_OCL_GEMM_IMPL"] = "tiled"
    env["AXIOMOS_OCL_TM"] = str(TM)
    env["AXIOMOS_OCL_TN"] = str(TN)
    env["AXIOMOS_OCL_TK"] = str(TK)
    if fastmath:
        env["AXIOMOS_OCL_FASTMATH"] = "1"
    else:
        env.pop("AXIOMOS_OCL_FASTMATH", None)

    cmd = [
        sys.executable, "-B", "-m", "cli.verify_axir", str(axir_path),
        "--buffer", "hC",
        "--backend-a", "cpu", "--backend-b", "opencl",
        "--time", "--warmup", "1", "--repeat", "3",
        "--rtol", "1e-3", "--atol", "1e-1", "--quiet"
    ]
    cp = subprocess.run(cmd, capture_output=True, text=True, env=env)
    out = cp.stdout + "\n" + cp.stderr

    # device
    mdev = re.search(r"choose device '([^']+)'", out)
    device = mdev.group(1) if mdev else "UNKNOWN_DEVICE"

    # median ms (OPENCL)
    m = re.search(r"OPENCL\s*:\s*([0-9.]+)\s*ms\s*\(median\)", out)
    ms = float(m.group(1)) if m else float("inf")
    return device, ms, out

def main():
    axir = AXIR_DEFAULT
    if not axir.exists():
        print(f"[ERROR] AXIR not found: {axir}")
        sys.exit(1)

    results = []
    for TM,TN,TK in COMBOS:
        for fast in (False, True):
            device, ms, _ = run_once(axir, TM,TN,TK, fastmath=fast)
            results.append({
                "TM": TM, "TN": TN, "TK": TK,
                "fastmath": fast, "median_ms": ms,
                "device": device
            })
            fm = "fast" if fast else "precise"
            print(f"[{device}] TM={TM} TN={TN} TK={TK} {fm} -> {ms:.2f} ms")

    # pick best
    results = [r for r in results if r["median_ms"] != float("inf")]
    if not results:
        print("[ERROR] no valid timings")
        sys.exit(2)
    best = min(results, key=lambda r: r["median_ms"])
    print("\n=== BEST ===")
    print(best)

    # write cache
    cache_path = ROOT / "build" / "ocl_tuning_cache.json"
    cache = {}
    if cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            cache = {}
    cache[best["device"]] = {
        "TM": best["TM"], "TN": best["TN"], "TK": best["TK"],
        "fastmath": best["fastmath"]
    }
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    print(f"[OK] cache updated -> {cache_path}")

if __name__ == "__main__":
    main()
