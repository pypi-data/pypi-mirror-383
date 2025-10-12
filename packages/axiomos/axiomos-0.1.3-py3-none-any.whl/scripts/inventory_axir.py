import json, pathlib, csv, re
ROOT = pathlib.Path(".")
AXIR = list(ROOT.rglob("*.axir.json"))
rows=[]
for p in AXIR:
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        ops = [op.get("op","?") for op in data.get("ops",[])]
        kernels = [op.get("kernel") for op in data.get("ops",[]) if op.get("op")=="KernelLaunch"]
        rows.append({
            "path": str(p),
            "size_bytes": p.stat().st_size,
            "n_ops": len(ops),
            "ops_set": ",".join(sorted(set(ops))),
            "kernels": ",".join(sorted({k for k in kernels if k})),
            "is_backup": int(bool(re.search(r"(bak|backup|fixed)", p.name, re.I))),
        })
    except Exception:
        rows.append({"path": str(p), "size_bytes": p.stat().st_size, "n_ops": -1, "ops_set": "PARSE_ERROR", "kernels":"", "is_backup":1})
outdir = pathlib.Path("axiomos/reports"); outdir.mkdir(parents=True, exist_ok=True)
with open(outdir/"axir_inventory.csv","w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print("Wrote", outdir/"axir_inventory.csv", "(", len(rows), "files)")
