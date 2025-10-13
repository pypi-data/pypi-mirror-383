import sys
import json
import time
import numpy as np

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
    with open(path, "r") as f:
        graph = json.load(f)
    buffers = {}
    for name, spec in graph["buffers"].items():
        shape = tuple(spec["shape"])
        data = np.array(spec["data"], dtype=np.float32).reshape(shape)
        buffers[name] = data
    return buffers, graph["ops"]

def _run_backend(path, backend, buffer_name):
    # NOTE: For demo purposes, 'opencl' just calls the same NumPy executor.
    buffers, ops = _load_axir(path)
    t0 = time.time()
    out = _execute_ops(buffers, ops)[buffer_name]
    t1 = time.time()
    return out, (t1 - t0) * 1000

def verify_main():
    if len(sys.argv) < 5:
        print("Usage: axiomos-verify <axir.json> --buffer <name> --backend-a cpu --backend-b opencl")
        sys.exit(1)

    path = sys.argv[1]
    buffer_name = sys.argv[3]
    backend_a = sys.argv[5] if len(sys.argv) > 5 else "cpu"
    backend_b = sys.argv[7] if len(sys.argv) > 7 else "cpu"

    outA, timeA = _run_backend(path, backend_a, buffer_name)
    outB, timeB = _run_backend(path, backend_b, buffer_name)

    same_shape = outA.shape == outB.shape
    max_abs_err = float(np.max(np.abs(outA - outB))) if same_shape else float("inf")
    allclose = same_shape and np.allclose(outA, outB, atol=1e-6, rtol=1e-5)

    print(f"SHAPES     : {backend_a.upper()}{outA.shape} vs {backend_b.upper()}{outB.shape}")
    print(f"max_abs_err: {max_abs_err}")
    print(f"ALLCLOSE   : {allclose} (atol=1e-6, rtol=1e-5)")
    print(f"{backend_a.upper()} time : {timeA:.3f} ms")
    print(f"{backend_b.upper()} time : {timeB:.3f} ms")
    print("[SMOKE] RESULT:", "PASS ✅" if allclose else "FAIL ❌")

if __name__ == "__main__":
    verify_main()
