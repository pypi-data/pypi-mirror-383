#!/usr/bin/env python3
import argparse, subprocess, sys, os

def sh(cmd):
    print("[run]", " ".join(cmd))
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit(r.returncode)

def main():
    ap = argparse.ArgumentParser(description="Run GEMM bench and render HTML")
    ap.add_argument("--sizes", default="256,512,1024", help="Sizes like M,N,K triplets or cubes")
    ap.add_argument("--csv", default="build/axir_gemm_bench.csv")
    ap.add_argument("--md",  default="build/axir_gemm_bench.md")
    ap.add_argument("--html", default=None, help="Output HTML path (default: CSV with .html)")
    args = ap.parse_args()

    # 1) Bench → CSV/MD
    sh(["axir-bench-gemm", "--sizes", args.sizes, "--csv", args.csv, "--md", args.md])

    # 2) CSV → HTML
    html_out = args.html or os.path.splitext(args.csv)[0] + ".html"
    sh(["axir-bench-html", "--csv", args.csv])
    if html_out != os.path.splitext(args.csv)[0] + ".html":
        # move/rename if user requested a different html path
        try:
            os.replace(os.path.splitext(args.csv)[0] + ".html", html_out)
            print(f"[move] -> {html_out}")
        except Exception as e:
            print(f"[warn] could not move html: {e}")

if __name__ == "__main__":
    main()
