import argparse, json, pathlib, sys
from math import prod

OK, FAIL, WARN = 0, 0, 0

def as_int(x):
    try:
        return int(x)
    except Exception:
        return None

def as_float(x):
    try:
        return float(x)
    except Exception:
        return None

def shape_of(buf):
    shp = buf.get("shape")
    if isinstance(shp, list) and all(isinstance(d,(int,str)) for d in shp):
        dims = []
        for d in shp:
            if isinstance(d,int): dims.append(d)
            else:
                vi = as_int(d)
                if vi is not None: dims.append(vi)
                else: return None
        return tuple(dims)
    return None

def check_gemm(ax, fn):
    global FAIL, WARN, OK
    bufs = ax.get("buffers", {})
    okfile = True
    for op in ax.get("ops", []):
        if op.get("op") != "GEMM":
            continue
        M,N,K = as_int(op.get("M")), as_int(op.get("N")), as_int(op.get("K"))
        if None in (M,N,K):
            print(f"[FAIL] {fn}: GEMM M/N/K non entiers -> M={op.get('M')} N={op.get('N')} K={op.get('K')}")
            FAIL+=1; okfile=False; continue
        tA, tB = bool(op.get("transA", False)), bool(op.get("transB", False))
        A,B,C = op.get("A","A"), op.get("B","B"), op.get("C","C")
        a,b,c = bufs.get(A,{}), bufs.get(B,{}), bufs.get(C,{})

        sa, sb, sc = shape_of(a), shape_of(b), shape_of(c)
        # Shapes optionnelles : si absentes on “warn” seulement.
        if sa is not None:
            expA = (K,M) if tA else (M,K)
            if sa != expA:
                print(f"[FAIL] {fn}: shape(A)={sa} attendu={expA} (transA={tA})"); FAIL+=1; okfile=False
        else:
            print(f"[WARN] {fn}: shape(A) absent -> skipping vérif"); WARN+=1

        if sb is not None:
            expB = (N,K) if tB else (K,N)
            if sb != expB:
                print(f"[FAIL] {fn}: shape(B)={sb} attendu={expB} (transB={tB})"); FAIL+=1; okfile=False
        else:
            print(f"[WARN] {fn}: shape(B) absent -> skipping vérif"); WARN+=1

        if sc is not None:
            expC = (M,N)
            if sc != expC:
                print(f"[FAIL] {fn}: shape(C)={sc} attendu={expC}"); FAIL+=1; okfile=False
        else:
            print(f"[WARN] {fn}: shape(C) absent -> skipping vérif"); WARN+=1

        af, bf = as_float(op.get("alpha",1.0)), as_float(op.get("beta",0.0))
        if af is None or bf is None:
            print(f"[FAIL] {fn}: alpha/beta non numériques -> alpha={op.get('alpha')} beta={op.get('beta')}")
            FAIL+=1; okfile=False
    if okfile:
        print(f"[OK ] {fn}")
        OK+=1

def check_memcpy(ax, fn):
    global WARN
    for op in ax.get("ops", []):
        if op.get("op") == "Memcpy":
            k = op.get("kind")
            src, dst = op.get("src",""), op.get("dst","")
            if k == "H2D" and not (src.startswith("h") and dst.startswith("d")):
                print(f"[WARN] {fn}: Memcpy H2D noms atypiques src={src} dst={dst}"); WARN+=1
            if k == "D2H" and not (src.startswith("d") and dst.startswith("h")):
                print(f"[WARN] {fn}: Memcpy D2H noms atypiques src={src} dst={dst}"); WARN+=1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    args = ap.parse_args()
    files = []
    for s in args.paths:
        p = pathlib.Path(s)
        if p.is_dir(): files += sorted(p.rglob("*.axir.json"))
        elif p.exists(): files.append(p)
    if not files:
        print("[ERR] aucun fichier"); sys.exit(2)

    for f in files:
        try:
            ax = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[FAIL] {f.name}: JSON invalide ({e})"); globals()["FAIL"]+=1; continue
        check_memcpy(ax, f.name)
        check_gemm(ax, f.name)

    print(f"\nRésumé: OK={OK}  WARN={WARN}  FAIL={FAIL}")
    sys.exit(1 if FAIL>0 else 0)

if __name__ == "__main__":
    main()
