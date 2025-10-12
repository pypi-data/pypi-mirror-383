# cli/torch_export.py
import argparse
from pathlib import Path
from frontends.torch_axir.export import export_saxpy, export_matmul

def main():
    ap = argparse.ArgumentParser("Minimal PyTorch→AXIR exporter (v1)")
    sp = ap.add_subparsers(dest="cmd", required=True)

    sp_sx = sp.add_parser("saxpy")
    sp_sx.add_argument("--N", type=int, required=True)
    sp_sx.add_argument("--alpha", type=float, default=3.0)
    sp_sx.add_argument("--out", required=True)

    sp_mm = sp.add_parser("matmul")
    sp_mm.add_argument("--M", type=int, required=True)
    sp_mm.add_argument("--N", type=int, required=True)
    sp_mm.add_argument("--K", type=int, required=True)
    sp_mm.add_argument("--out", required=True)

    args = ap.parse_args()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)

    if args.cmd == "saxpy":
        export_saxpy(args.N, args.alpha, args.out)
        print(f"WROTE {args.out}")
    else:
        export_matmul(args.M, args.N, args.K, args.out)
        print(f"WROTE {args.out}")

if __name__ == "__main__":
    main()
