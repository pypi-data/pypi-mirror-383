#!/usr/bin/env python3
import subprocess, sys, json, time, pathlib, re

SIZES = [
    ("1e5",   100_000),
    ("1e6", 1_000_000),
    ("1e7",10_000_000),
]

AXIR_TMPL = {
    "types": {"scalars": {"N": {"value": 100000}}},
    "ops": [
        {"op":"DeviceMalloc","dst":"dA","bytes":"N*sizeof(float)"},
        {"op":"Memcpy","kind":"H2D","src":"hA","dst":"dA","bytes":"N*sizeof(float)"},
        {"op":"KernelLaunch","kernel":"reduce_sum","args":["dA","dOut","N"]},
        {"op":"Memcpy","kind":"D2H","src":"dOut","dst":"hOut","bytes":"sizeof(float)"}
    ]
}

BENCH_RE = re.compile(r"\[BENCH\]\s*(\{.*\})")

def run_one(tag, N, kernel_name):
    # build AXIR
    obj = json.loads(json.dumps(AXIR_TMPL))
    obj["types"]["scalars"]["N"]["value"] = N
    obj["ops"][2]["kernel"] = kernel_name
    p = pathlib.Path("build") / f"__reduce_{kernel_name}_{tag}.axir.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj), encoding="utf-8")

    # run
    cmd = [sys.executable, "-m", "cli.axir_run", str(p), "--target", "opencl", "--bench"]
    t0 = time.perf_counter()
    out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
    wall = (time.perf_counter() - t0) * 1000.0

    # parse [BENCH]
    H2D=KER=D2H=E2E=0.0; kern="?"
    m = BENCH_RE.search(out)
    if m:
        d = json.loads(m.group(1))
        kern = d.get("kernel","?")
        H2D  = float(d.get("H2D",0.0))
        KER  = float(d.get("Kernel",0.0))
        D2H  = float(d.get("D2H",0.0))
        E2E  = float(d.get("E2E",0.0))
    print(f"{kernel_name:>12}  N={N:>9} | H2D={H2D:7.1f} ms | KER={KER:7.1f} ms | D2H={D2H:7.1f} ms | E2E={E2E:7.1f} ms | wall={wall:7.1f} ms | selected={kern}")

def main():
    print("== Reduce bench (OpenCL) ==")
    for tag, N in SIZES:
        run_one(tag, N, "reduce_sum")
    for tag, N in SIZES:
        # switch kernel op name
        global AXIR_TMPL
        AXIR_TMPL["ops"][2]["kernel"] = "reduce_max"
        run_one(tag, N, "reduce_max")

if __name__ == "__main__":
    main()
