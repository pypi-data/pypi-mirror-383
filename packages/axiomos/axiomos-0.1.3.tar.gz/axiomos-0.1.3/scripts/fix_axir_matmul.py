import json, sys

src, dst = sys.argv[1], sys.argv[2]
with open(src, "r", encoding="utf-8") as f:
    d = json.load(f)

# ---- ensure root fields
d.setdefault("version", "0.1.1")
d.setdefault("meta", {"source_lang": "AXIR"})
d.setdefault("types", {})
d["types"].setdefault("scalars", {})
sc = d["types"]["scalars"]

def ensure_scalar(name, val):
    sc[name] = {"dtype": "i32", "value": int(val)}

M = int(sc.get("M", {}).get("value", 512))
N = int(sc.get("N", {}).get("value", 512))
K = int(sc.get("K", {}).get("value", 512))
ensure_scalar("M", M); ensure_scalar("N", N); ensure_scalar("K", K)

# ---- buffers
d.setdefault("buffers", {})
buf = d["buffers"]
buf.setdefault("hA", {"role": "host", "dtype": "float32", "size": "M*K"})
buf.setdefault("hB", {"role": "host", "dtype": "float32", "size": "K*N"})
buf.setdefault("hC", {"role": "host", "dtype": "float32", "size": "M*N"})

ops = d.setdefault("ops", [])

def has_op(ops_list, op_type, **kv):
    for op in ops_list:
        if op.get("op") == op_type and all(op.get(k) == v for k, v in kv.items()):
            return True
    return False

prepend = []

# HostMake (if missing)
if not any(op.get("op") == "HostMake" and op.get("name") == "hA" for op in ops):
    prepend.append({"op": "HostMake", "name": "hA", "dtype": "float32", "shape": ["M","K"], "fill": "ones"})
if not any(op.get("op") == "HostMake" and op.get("name") == "hB" for op in ops):
    prepend.append({"op": "HostMake", "name": "hB", "dtype": "float32", "shape": ["K","N"], "fill": "ones"})
if not any(op.get("op") == "HostMake" and op.get("name") == "hC" for op in ops):
    prepend.append({"op": "HostMake", "name": "hC", "dtype": "float32", "shape": ["M","N"], "fill": "zeros"})

# DeviceMallocLike for dA/dB/dC (if missing)
if not has_op(ops, "DeviceMallocLike", dst="&dA"):
    prepend.append({"op": "DeviceMallocLike", "dst": "&dA", "like": "hA"})
if not has_op(ops, "DeviceMallocLike", dst="&dB"):
    prepend.append({"op": "DeviceMallocLike", "dst": "&dB", "like": "hB"})
if not has_op(ops, "DeviceMallocLike", dst="&dC"):
    prepend.append({"op": "DeviceMallocLike", "dst": "&dC", "like": "hC"})

# New ordered ops: prepend + existing
new_ops = prepend + ops

# Ensure Memcpy H2D for dA/dB (before KernelLaunch)
if not has_op(new_ops, "Memcpy", dst="dA", kind="H2D"):
    new_ops.insert(len(prepend), {"op": "Memcpy", "dst": "dA", "src": "hA", "kind": "H2D"})
if not has_op(new_ops, "Memcpy", dst="dB", kind="H2D"):
    new_ops.insert(len(prepend)+1, {"op": "Memcpy", "dst": "dB", "src": "hB", "kind": "H2D"})

# Ensure Memcpy D2H for hC at the end
if not has_op(new_ops, "Memcpy", dst="hC", kind="D2H"):
    new_ops.append({"op": "Memcpy", "dst": "hC", "src": "dC", "kind": "D2H"})

d["ops"] = new_ops

with open(dst, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2)
print("fixed ->", dst)
