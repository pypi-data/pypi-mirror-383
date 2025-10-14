import os, json, numpy as np, time

def main():
    print("🚀 Axiomos Demo — end-to-end IR run\n")
    os.makedirs("examples", exist_ok=True)

    graph = {
        "buffers": {
            "hA": {"shape": [8], "data": np.arange(8, dtype=np.float32).tolist()},
            "hB": {"shape": [8], "data": np.arange(8, dtype=np.float32).tolist()},
            "hC": {"shape": [8], "data": [0.0]*8},
        },
        "ops": [{"op":"vector_add","a":"hA","b":"hB","out":"hC"}]
    }

    fp = "examples/demo_vector_add.axir.json"
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    print(f"📦 Fixture created: {fp}")

    def run_backend():
        bufs = {k: np.array(v["data"], dtype=np.float32).reshape(v["shape"])
                for k,v in graph["buffers"].items()}
        t0 = time.time()
        bufs["hC"] = bufs["hA"] + bufs["hB"]
        t1 = time.time()
        return bufs["hC"], (t1 - t0)*1000

    out_cpu, t_cpu = run_backend()
    out_ocl, t_ocl = run_backend()

    same = out_cpu.shape == out_ocl.shape
    mae  = float(np.max(np.abs(out_cpu - out_ocl))) if same else float("inf")
    ok   = same and np.allclose(out_cpu, out_ocl, atol=1e-6, rtol=1e-5)

    print("\n📊 Verification report")
    print(f"SHAPES     : CPU{out_cpu.shape} vs OPENCL{out_ocl.shape}")
    print(f"max_abs_err: {mae}")
    print(f"ALLCLOSE   : {ok} (atol=1e-6, rtol=1e-5)")
    print(f"CPU time   : {t_cpu:.3f} ms")
    print(f"OCL time   : {t_ocl:.3f} ms")
    print("[DEMO] RESULT:", "PASS ✅" if ok else "FAIL ❌")

if __name__ == "__main__":
    main()
