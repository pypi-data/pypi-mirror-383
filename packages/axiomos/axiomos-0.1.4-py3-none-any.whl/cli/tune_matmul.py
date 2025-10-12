# cli/tune_matmul.py
import argparse, json, os, time, statistics, csv, sys
from pathlib import Path

def load_axir(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_max_work_group_size_auto():
    """
    Essaie de déterminer automatiquement le MAX_WORK_GROUP_SIZE
    du premier device OpenCL disponible. Retourne un int ou None.
    """
    try:
        import pyopencl as cl
        plats = cl.get_platforms()
        for p in plats:
            devs = p.get_devices()
            if devs:
                return int(devs[0].get_info(cl.device_info.MAX_WORK_GROUP_SIZE))
    except Exception:
        pass
    return None  # inconnu

def run_opencl_once(ax):
    # exécute le backend OCL in-proc et mesure le temps E2E
    from Backends import opencl_backend as ocl
    t0 = time.perf_counter()
    # dump='hC' peut aider au debug/validation côté CLI si besoin
    ocl.run(ax, summary=False, dump="hC", repeats=1)
    return (time.perf_counter() - t0) * 1000.0  # ms

def try_triplet(ax, tm, tn, tk, warmup=1, repeats=3, quiet=False):
    # Fixe les overrides pour le backend
    os.environ["OCL_TM"] = str(tm)
    os.environ["OCL_TN"] = str(tn)
    os.environ["OCL_TK"] = str(tk)

    # Warmup pour amortir build/cache
    for _ in range(max(0, warmup)):
        try:
            run_opencl_once(ax)
        except Exception as e:
            return {"tm": tm, "tn": tn, "tk": tk, "ok": False, "error": str(e)}

    times = []
    for _ in range(max(1, repeats)):
        try:
            dt = run_opencl_once(ax)
            times.append(dt)
        except Exception as e:
            return {"tm": tm, "tn": tn, "tk": tk, "ok": False, "error": str(e)}

    med = statistics.median(times)
    if not quiet:
        runs_s = ", ".join(f"{t:.2f}" for t in times)
        print(f"[{tm:>2},{tn:>2},{tk:>2}] median={med:6.2f} ms  runs={runs_s}")
    return {"tm": tm, "tn": tn, "tk": tk, "ok": True, "median_ms": med, "runs_ms": times}

def main():
    p = argparse.ArgumentParser(description="Tune OpenCL matmul tiled (TM, TN, TK)")
    p.add_argument("axir", help="Chemin du .axir.json (ex: build/matmul_512.axir.json)")
    p.add_argument("--tm", type=int, nargs="+", default=[8,16,32], help="Liste TM")
    p.add_argument("--tn", type=int, nargs="+", default=[8,16,32], help="Liste TN")
    p.add_argument("--tk", type=int, nargs="+", default=[16,32,64], help="Liste TK")
    p.add_argument("--warmup", type=int, default=1)
    p.add_argument("--repeats", type=int, default=3)
    p.add_argument("--csv", type=str, default="build/tune_matmul_results.csv")
    p.add_argument("--max-wg", type=str, default="auto",
                   help="Max work-group size (nombre ou 'auto'). Filtre TM*TN <= max.")
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args()

    axir_path = Path(args.axir)
    if not axir_path.exists():
        print(f"[ERR] AXIR not found: {axir_path}")
        sys.exit(1)
    ax = load_axir(axir_path)

    # Impl tiled + fusions activables (non bloquant si absentes)
    os.environ.setdefault("OCL_IMPL", "tiled")
    os.environ.setdefault("OCL_FUSE_BIAS", "1")
    os.environ.setdefault("OCL_FUSE_RELU", "1")

    # Déterminer max WG
    if args.max_wg.strip().lower() == "auto":
        max_wg = get_max_work_group_size_auto()
    else:
        try:
            max_wg = int(args.max_wg)
        except Exception:
            max_wg = None

    if max_wg:
        print(f"[INFO] max work-group size = {max_wg}")
    else:
        print("[WARN] max work-group size inconnu — aucun filtrage TM*TN", file=sys.stderr)

    # Sweep des triplets
    results = []
    print(f"\n=== TUNING {axir_path.name} (warmup={args.warmup}, repeats={args.repeats}) ===")
    for tm in args.tm:
        for tn in args.tn:
            # Filtrage TM*TN par le max WG
            if max_wg and (tm * tn) > max_wg:
                if not args.quiet:
                    print(f"[SKIP] TM={tm} TN={tn} (TM*TN={tm*tn} > {max_wg})")
                continue
            for tk in args.tk:
                r = try_triplet(ax, tm, tn, tk, warmup=args.warmup, repeats=args.repeats, quiet=args.quiet)
                results.append(r)

    # Tri, affichage
    oks = [r for r in results if r.get("ok")]
    fails = [r for r in results if not r.get("ok")]
    oks.sort(key=lambda r: r["median_ms"])

    print("\n--- TOP 10 (par median_ms) ---")
    for r in oks[:10]:
        print(f"TM={r['tm']:>2} TN={r['tn']:>2} TK={r['tk']:>2}  median={r['median_ms']:6.2f} ms  "
              f"runs={', '.join(f'{t:.2f}' for t in r['runs_ms'])}")

    if fails:
        print("\n--- FAILS ---")
        for r in fails:
            print(f"TM={r['tm']} TN={r['tn']} TK={r['tk']} -> {r.get('error','error')}")

    # Export CSV
    csv_path = Path(args.csv)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["TM", "TN", "TK", "ok", "median_ms", "runs_ms", "error"])
        for r in results:
            w.writerow([
                r.get("tm"), r.get("tn"), r.get("tk"),
                r.get("ok"),
                f"{r.get('median_ms', ''):.4f}" if r.get("median_ms") is not None else "",
                ";".join(f"{t:.4f}" for t in r.get("runs_ms", [])),
                r.get("error", ""),
            ])
    print(f"\n[OK] CSV écrit -> {csv_path.resolve()}")

    # Récap meilleur
    if oks:
        best = oks[0]
        print(f"\n[BEST] TM={best['tm']} TN={best['tn']} TK={best['tk']}  median={best['median_ms']:.2f} ms")

if __name__ == "__main__":
    main()
