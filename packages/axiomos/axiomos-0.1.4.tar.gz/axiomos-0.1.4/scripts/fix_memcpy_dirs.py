import json, codecs, glob, re

def norm(x):
    s = str(x).strip()
    s = re.sub(r'^[&*]+', '', s)  # enlève & et *
    return s

fixed_ops = 0
fixed_files = 0

for path in glob.glob(r".\AXIR\*.axir.json"):
    ax = json.load(codecs.open(path, "r", "utf-8-sig"))
    changed = False
    for op in ax.get("ops", []) or []:
        if op.get("op") != "Memcpy":
            continue
        key = "kind" if "kind" in op else ("dir" if "dir" in op else None)
        if not key:
            continue
        kind = str(op.get(key,"")).upper()
        src  = norm(op.get("src",""))
        dst  = norm(op.get("dst",""))
        # Si la direction ne colle pas aux préfixes (h* = host, d* = device), on flippe
        if kind == "H2D" and src.startswith("d") and dst.startswith("h"):
            op[key] = "D2H"; changed = True; fixed_ops += 1
        elif kind == "D2H" and src.startswith("h") and dst.startswith("d"):
            op[key] = "H2D"; changed = True; fixed_ops += 1
    if changed:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(ax, f, indent=2)
        fixed_files += 1

print("files_fixed", fixed_files, "ops_fixed", fixed_ops)
