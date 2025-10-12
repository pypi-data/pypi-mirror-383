import json, sys, pathlib
p = pathlib.Path(r".\axiomos\candidates\softmax2d_2048_from_export.axir.json")
d = json.loads(p.read_text(encoding="utf-8"))
for op in d.get("ops", []):
    if op.get("op")=="KernelLaunch" and op.get("kernel")=="softmax2d_row":
        args = op.get("args", [])
        if len(args) >= 2:
            if args[0] == "&dX": args[0] = "dX"
            if args[1] == "&dY": args[1] = "dY"
p.write_text(json.dumps(d, indent=2), encoding="utf-8")
print("patched", p)
