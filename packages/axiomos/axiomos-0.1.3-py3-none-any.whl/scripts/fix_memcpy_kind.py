import json, glob, codecs, re

def clean(x):
    return re.sub(r'^[&*]+\s*', '', str(x or '').strip())

fixed = 0
for path in glob.glob(r".\AXIR\*.axir.json"):
    ax = json.load(codecs.open(path, "r", "utf-8-sig"))
    changed = False
    for op in ax.get("ops", []) or []:
        if op.get("op") != "Memcpy":
            continue

        # Normaliser le champ de direction
        if "dir" in op and "kind" not in op:
            op["kind"] = op.pop("dir"); changed = True

        # Nettoyer src/dst (enlever & et *)
        if "src" in op:
            v = clean(op["src"])
            if v != op["src"]: op["src"] = v; changed = True
        if "dst" in op:
            v = clean(op["dst"])
            if v != op["dst"]: op["dst"] = v; changed = True

        # Déduire/forcer la bonne direction d'après les préfixes h*/d*
        k = str(op.get("kind","")).upper()
        s = str(op.get("src",""))
        d = str(op.get("dst",""))
        want = None
        if s.startswith("h") and d.startswith("d"): want = "H2D"
        elif s.startswith("d") and d.startswith("h"): want = "D2H"
        elif s.startswith("h") and d.startswith("h"): want = "H2H"
        elif s.startswith("d") and d.startswith("d"): want = "D2D"
        if want and k != want:
            op["kind"] = want; changed = True

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(ax, f, indent=2)
        fixed += 1

print("fixed_files", fixed)
