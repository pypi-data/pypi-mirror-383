import argparse, subprocess, sys, glob, os

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)

def _py(*parts):
    return [sys.executable, os.path.join(REPO, *parts)]

def cmd_verify(args):
    files = []
    for a in args.axir: files.extend(glob.glob(a))
    if not files: 
        print("[ERR] aucun fichier AXIR trouvé"); sys.exit(2)
    for path in files:
        cmd = _py("cli","verify_axir.py") + [
            "--buffer", args.buffer,
            "--backend-a", args.backend_a,
            "--backend-b", args.backend_b,
        ] + (["--time"] if args.time else []) + [path]
        subprocess.check_call(cmd)

def cmd_lint(args):
    files = []
    for a in args.axir: files.extend(glob.glob(a))
    if not files: 
        print("[ERR] aucun fichier AXIR trouvé"); sys.exit(2)
    for path in files:
        subprocess.check_call(_py("scripts","axir_lint.py") + [path])

def main():
    p = argparse.ArgumentParser(prog="axiomos", description="AXIR CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    pv = sub.add_parser("verify", help="Comparer 2 backends sur un AXIR")
    pv.add_argument("axir", nargs="+")
    pv.add_argument("--buffer", default="hC")
    pv.add_argument("--backend-a", default="cpu")
    pv.add_argument("--backend-b", default="opencl")
    pv.add_argument("--time", action="store_true")
    pv.set_defaults(func=cmd_verify)

    pl = sub.add_parser("lint", help="Valider le schéma AXIR")
    pl.add_argument("axir", nargs="+")
    pl.set_defaults(func=cmd_lint)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
