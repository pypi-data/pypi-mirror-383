# scripts/make_big_axir.py
#!/usr/bin/env python3
import argparse, json, pathlib

def main():
    ap = argparse.ArgumentParser(description="Set scalars.{N,M,K} in an AXIR JSON and write a new file.")
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--N", type=int)
    ap.add_argument("--M", type=int)
    ap.add_argument("--K", type=int)
    args = ap.parse_args()

    src = pathlib.Path(args.src)
    dst = pathlib.Path(args.dst)

    ax = json.loads(src.read_text(encoding="utf-8"))
    scal = ax.setdefault("types", {}).setdefault("scalars", {})
    for key, val in (("N", args.N), ("M", args.M), ("K", args.K)):
        if val is not None:
            scal.setdefault(key, {})["value"] = val

    dst.write_text(json.dumps(ax, indent=2), encoding="utf-8")
    print(f"[OK] wrote {dst} with "
          + ", ".join([f"{k}={scal[k]['value']}" for k in scal if k in ("N","M","K") and 'value' in scal[k]]))

if __name__ == "__main__":
    main()
