import json, codecs, glob

def s(x,p): return isinstance(x,str) and x.startswith(p)

fixed = 0
for path in glob.glob(r".\AXIR\*.axir.json"):
    ax = json.load(codecs.open(path, "r", "utf-8-sig"))
    changed = False
    for op in ax.get("ops", []):
        if op.get("op") == "Memcpy":
            key = "kind" if "kind" in op else ("dir" if "dir" in op else None)
            if not key: 
                continue
            src, dst = str(op.get("src","")), str(op.get("dst",""))
            kind = str(op.get(key,"")).upper()
            # H2D doit être h* -> d*
            if kind == "H2D" and s(src,"d") and s(dst,"h"):
                op[key] = "D2H"; changed = True
            # D2H doit être d* -> h*
            if kind == "D2H" and s(src,"h") and s(dst,"d"):
                op[key] = "H2D"; changed = True
    if changed:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(ax, f, indent=2)
        fixed += 1
print("files_patched", fixed)
