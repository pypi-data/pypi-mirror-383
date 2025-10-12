import json, pathlib, itertools

def load(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))

A = load(r".\axiomos\canonical\softmax2d_2048.axir.json")
B = load(r".\axiomos\candidates\softmax2d_2048_from_export.axir.json")

def show(title, d):
    print(f"\n=== {title} ===")
    print("buffers:")
    for k,v in d.get("buffers",{}).items():
        print(f"  {k}: role={v.get('role')} dtype={v.get('dtype')} size={v.get('size')}")
    print("ops[0:8]:")
    for i,op in enumerate(itertools.islice(d.get('ops',[]), 8)):
        line = f"  [{i}] {op.get('op')}"
        if op.get('op')=='HostMake':
            line += f" name={op.get('name')} dtype={op.get('dtype')} shape={op.get('shape')} fill={op.get('fill')}"
        elif op.get('op')=='DeviceMallocLike':
            line += f" dst={op.get('dst')} like={op.get('like')}"
        elif op.get('op')=='Memcpy':
            line += f" dst={op.get('dst')} src={op.get('src')} kind={op.get('kind')}"
        elif op.get('op')=='KernelLaunch':
            line += f" kernel={op.get('kernel')} grid={op.get('grid')} block={op.get('block')} args={op.get('args')}"
        print(line)

show("CANONICAL", A)
show("EXPORT",    B)
