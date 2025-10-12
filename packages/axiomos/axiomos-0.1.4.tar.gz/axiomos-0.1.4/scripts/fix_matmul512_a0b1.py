import json, codecs

p = r".\AXIR\matmul_512_alpha0_beta1.axir.json"
ax = json.load(codecs.open(p, "r", "utf-8-sig"))
chg = 0
for op in ax.get("ops", []):
    if op.get("op")=="Memcpy" and op.get("kind")=="H2D":
        if str(op.get("src","")).startswith("d") and str(op.get("dst","")).startswith("h"):
            op["kind"] = "D2H"; chg += 1
if chg:
    with open(p, "w", encoding="utf-8") as f: json.dump(ax, f, indent=2)
print("patched", chg, "Memcpy")
