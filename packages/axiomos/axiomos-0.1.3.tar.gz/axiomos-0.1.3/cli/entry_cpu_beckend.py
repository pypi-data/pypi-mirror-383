#!/usr/bin/env python3
# entry_cpu_backend.py — mince wrapper CLI pour Backends.cpu_numpy_backend.run
import argparse, json, pathlib, numpy as np

def main():
    ap = argparse.ArgumentParser(description="CPU entry — run AXIR and dump a buffer")
    ap.add_argument("--axir", required=True)
    ap.add_argument("--buffer", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--repeat", type=int, default=1)
    args = ap.parse_args()

    ax = json.loads(pathlib.Path(args.axir).read_text(encoding="utf-8-sig"))
    try:
        from Backends.cpu_numpy_backend import run as run_cpu
    except ImportError:
        from backends.cpu_numpy_backend import run as run_cpu

    out = run_cpu(ax, summary=args.summary, dump=args.buffer, repeats=args.repeat)

    if isinstance(out, dict) and "dump" in out:
        arr = np.asarray(out["dump"])
    else:
        arr = np.asarray(out)

    np.save(args.out, arr.reshape(-1))
    print(f"[entry_cpu] saved {args.out} shape={arr.shape}")

if __name__ == "__main__":
    main()
