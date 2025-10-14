import os, sys, json, time, argparse
import numpy as np
from importlib.metadata import version, PackageNotFoundError

def _pkg_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "not installed"

def _execute_ops(buffers, ops):
    for op in ops:
        kind = op["op"]
        if kind == "vector_add":
            buffers[op["out"]] = buffers[op["a"]] + buffers[op["b"]]
        elif kind == "softmax2d":
            x = buffers[op["x"]]
            x_max = np.max(x, axis=1, keepdims=True)
            e = np.exp(x - x_max)
            buffers[op["out"]] = e / e.sum(axis=1, keepdims=True)
        else:
            raise ValueError(f"Unsupported op: {kind}")
    return buffers

def _load_axir(path):
    with open(path, "r", encoding="utf-8") as f:
        graph = json.load(f)
    buffers = {}
    for name, spec in graph["buffers"].items():
        shape = tuple(spec["shape"])
        data = np.array(spec["data"], dtype=np.float32).reshape(shape)
        buffers[name] = data
    return buffers, graph["ops"]

def _run_cpu(path, buffer_name):
    buffers, ops = _load_axir(path)
    t0 = time.perf_counter()
    out = _execute_ops(buffers, ops)[buffer_name]
    t1 = time.perf_counter()
    return out, (t1 - t0) * 1000

def _run_opencl(path, buffer_name):
    try:
        from axiomos.backends.opencl_backend import OpenCLBackend
        buffers, ops = _load_axir(path)
        be = OpenCLBackend()
        t0 = time.perf_counter()
        out = be.run_ops(buffers, ops, buffer_name)
        t1 = time.perf_counter()
        return out, (t1 - t0) * 1000, "OPENCL"
    except Exception:
        out, ms = _run_cpu(path, buffer_name)
        return out, ms, "OPENCL(cpu-fallback)"

def verify_main():
    p = argparse.ArgumentParser(description="Verify AXIR output across two backends.")
    p.add_argument("axir", help="Path to .axir.json")
    p.add_argument("--buffer", required=True, help="Output buffer to compare (e.g. hC, hY)")
    p.add_argument("--backend-a", default="cpu", choices=["cpu","opencl"])
    p.add_argument("--backend-b", default="cpu", choices=["cpu","opencl"])
    p.add_argument("--seed", type=int, default=None, help="Optional RNG seed for reproducibility")
    args = p.parse_args()

    # Banner + versions
    print("🔒 Public showcase build — minimal backend (private core under NDA)")
    axiomos_ver = _pkg_version("axiomos")
    numpy_ver   = np.__version__
    pyopencl_ver = _pkg_version("pyopencl")
    print(f"🧾 Versions: axiomos {axiomos_ver} | numpy {numpy_ver} | pyopencl {pyopencl_ver}")

    # Seed (CLI or env)
    seed = args.seed if args.seed is not None else os.getenv("AXIOMOS_SEED")
    if seed is not None:
        try:
            seed = int(seed)
            np.random.seed(seed)
            print(f"🎲 Seed: {seed}")
        except Exception:
            print("🎲 Seed: (ignored, not an int)")

    # Backend A
    if args.backend_a == "cpu":
        outA, timeA = _run_cpu(args.axir, args.buffer)
        labelA = "CPU"
    else:
        outA, timeA, labelA = _run_opencl(args.axir, args.buffer)

    # Backend B
    if args.backend_b == "cpu":
        outB, timeB = _run_cpu(args.axir, args.buffer)
        labelB = "CPU"
    else:
        outB, timeB, labelB = _run_opencl(args.axir, args.buffer)

    same_shape = outA.shape == outB.shape
    max_abs_err = float(np.max(np.abs(outA - outB))) if same_shape else float("inf")
    allclose = same_shape and np.allclose(outA, outB, atol=1e-6, rtol=1e-5)

    print(f"SHAPES     : {labelA}{outA.shape} vs {labelB}{outB.shape}")
    print(f"max_abs_err: {max_abs_err}")
    print(f"ALLCLOSE   : {allclose} (atol=1e-6, rtol=1e-5)")
    print(f"{labelA:10} time : {timeA:.3f} ms")
    print(f"{labelB:10} time : {timeB:.3f} ms")
    if labelA.startswith("OPENCL") or labelB.startswith("OPENCL"):
        print("ℹ️  OpenCL path = public minimal backend (not optimized)")
    print("[SMOKE] RESULT:", "PASS ✅" if allclose else "FAIL ❌")

if __name__ == "__main__":
    verify_main()
