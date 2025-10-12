import argparse, json, sys, pathlib, shutil

OP_SYNONYMS = {
    "gemm":"GEMM", "Gemm":"GEMM", "matmul":"GEMM", "MatMul":"GEMM",
    "Add":"Add", "Sub":"Sub", "Mul":"Mul",
    "Memcpy":"Memcpy", "HostMake":"HostMake", "DeviceMallocLike":"DeviceMallocLike", "KernelLaunch":"KernelLaunch",
}

def _to_bool_trans(v):
    if isinstance(v, bool): return v
    if isinstance(v, str): return v.upper() == "T"
    return bool(v)

def _num(v, kind=float):
    try:
        return kind(v)
    except Exception:
        return v

def fix_one(p, write=False):
    raw = p.read_text(encoding="utf-8-sig")
    try:
        ax = json.loads(raw)
    except Exception as e:
        print(f"[SKIP] {p.name}: JSON invalide ({e})")
        return False

    changed = False
    # version
    if "version" not in ax or ax["version"] != "0.1.1":
        ax["version"] = "0.1.1"; changed = True

    # ops
    ops = ax.get("ops", [])
    new_ops = []
    for op in ops:
        op = dict(op)  # copy
        name = op.get("op")
        if name in OP_SYNONYMS:
            if OP_SYNONYMS[name] != name:
                op["op"] = OP_SYNONYMS[name]; changed = True
        # Memcpy: dir -> kind, et purge des champs hors schéma
        if op.get("op") == "Memcpy":
            if "dir" in op and "kind" not in op:
                op["kind"] = op.pop("dir"); changed = True
            # garder uniquement {op,kind,src,dst}
            keep = {"op","kind","src","dst"}
            if any(k not in keep for k in op.keys()):
                op = {k:v for k,v in op.items() if k in keep}; changed = True

        # GEMM: coercions + purges
        if op.get("op") == "GEMM":
            # numeros
            for k in ("M","N","K"):
                if k in op:
                    v = op[k]
                    op[k] = _num(v, int) if isinstance(v,(int,str)) else v
            for k in ("alpha","beta"):
                if k in op:
                    op[k] = _num(op[k], float)
            # transA/transB acceptent "N"/"T"
            if "transA" in op: op["transA"] = _to_bool_trans(op["transA"]); changed = True
            if "transB" in op: op["transB"] = _to_bool_trans(op["transB"]); changed = True
            # retirer champs non prévus par le schéma minimal
            for k in ("layout",):
                if k in op: del op[k]; changed = True
        new_ops.append(op)

    if new_ops != ops:
        ax["ops"] = new_ops; changed = True

    if not changed:
        print(f"[OK ] {p.name} (aucun changement)")
        return False

    if write:
        bak = p.with_suffix(p.suffix + ".bak")
        try: shutil.copy2(p, bak)
        except Exception: pass
        p.write_text(json.dumps(ax, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[FIX] {p.name} (écrit, backup: {bak.name})")
    else:
        print(f"[DRY] {p.name} (changement détecté, utilisez --write)")
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="Dossiers ou fichiers .axir.json")
    ap.add_argument("--write", action="store_true", help="Écrire les corrections (sinon dry-run)")
    args = ap.parse_args()

    files = []
    for s in args.paths:
        p = pathlib.Path(s)
        if p.is_dir():
            files += sorted(p.rglob("*.axir.json"))
        elif p.suffixes[-2:] == [".axir",".json"]:
            files.append(p)
    if not files:
        print("[ERR] Aucun fichier AXIR trouvé"); sys.exit(2)

    changed = 0
    for f in files:
        changed += 1 if fix_one(f, write=args.write) else 0
    print(f"Résumé: modifiés={changed} / total={len(files)}")
if __name__ == "__main__":
    main()
