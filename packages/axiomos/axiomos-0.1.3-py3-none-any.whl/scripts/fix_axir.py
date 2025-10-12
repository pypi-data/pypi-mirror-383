#!/usr/bin/env python3
import os, sys, json, math, copy

CAN_LAYOUT = "rowmajor"

def num(x, default):
    try:
        return float(x)
    except Exception:
        return default

def get_scalars(doc):
    M=N=K=None
    alpha=1.0; beta=0.0
    # 1) types.scalars
    scal = ((doc.get("types") or {}).get("scalars") or {})
    def val(name):
        v = scal.get(name, {}).get("value", None)
        if v is None: return None
        return int(v) if name in ("M","N","K") else float(v)
    M = val("M") or doc.get("M")
    N = val("N") or doc.get("N")
    K = val("K") or doc.get("K")
    a_ = val("alpha")
    b_ = val("beta")
    alpha = a_ if a_ is not None else doc.get("alpha", alpha)
    beta  = b_ if b_ is not None else doc.get("beta",  beta)
    # fallback: try to infer from HostMake shapes if missing
    try:
        ops = doc.get("ops", [])
        shapeA = next((op.get("shape") for op in ops if op.get("op")=="HostMake" and op.get("name")=="hA"), None)
        shapeB = next((op.get("shape") for op in ops if op.get("op")=="HostMake" and op.get("name")=="hB"), None)
        if M is None and isinstance(shapeA, list): M = int(shapeA[0])
        if K is None and isinstance(shapeA, list): K = int(shapeA[1])
        if N is None and isinstance(shapeB, list): N = int(shapeB[1])
    except Exception:
        pass
    if M is None or N is None or K is None:
        raise ValueError("Impossible de déterminer M/N/K")
    return int(M), int(N), int(K), float(alpha), float(beta)

def has_gemm(doc):
    return any(op.get("op")=="GEMM" for op in doc.get("ops", []))

def build_canonical(M,N,K,alpha,beta, layout=CAN_LAYOUT):
    return {
      "version": "0.2",
      "meta": { "source_lang": "AXIR", "layout": layout },
      "types": { "scalars": {
        "M":     { "dtype":"i32",     "value": M },
        "N":     { "dtype":"i32",     "value": N },
        "K":     { "dtype":"i32",     "value": K },
        "alpha": { "dtype":"float32", "value": alpha },
        "beta":  { "dtype":"float32", "value": beta }
      }},
      "buffers": {
        "hA": { "role":"host", "dtype":"float32", "size":"M*K" },
        "hB": { "role":"host", "dtype":"float32", "size":"K*N" },
        "hC": { "role":"host", "dtype":"float32", "size":"M*N" }
      },
      "ops": [
        { "op":"DeviceSelect", "device":"auto" },

        { "op":"HostMake", "name":"hA", "dtype":"float32",
          "shape":["M","K"], "fill":"linspace", "start":1.0, "step":1.0 },

        { "op":"HostMake", "name":"hB", "dtype":"float32",
          "shape":["K","N"], "fill":"linspace", "start":1.0, "step":1.0 },

        { "op":"HostMake", "name":"hC", "dtype":"float32",
          "shape":["M","N"], "fill":"zeros" },

        { "op":"DeviceMallocLike", "dst":"&dA", "like":"hA" },
        { "op":"DeviceMallocLike", "dst":"&dB", "like":"hB" },
        { "op":"DeviceMallocLike", "dst":"&dC", "like":"hC" },

        { "op":"Memcpy", "dst":"dA", "src":"hA", "kind":"H2D" },
        { "op":"Memcpy", "dst":"dB", "src":"hB", "kind":"H2D" },

        # dC H2D seulement si beta != 0.0 (ajouté dynamiquement)

        { "op":"GEMM",
          "A":"dA", "B":"dB", "C":"dC",
          # IMPORTANT: valeurs numériques inlinées (pas de chaînes "M"/"alpha")
          "M": M, "N": N, "K": K,
          "alpha": alpha, "beta": beta,
          "layout": layout, "transA":"N", "transB":"N" },

        { "op":"Memcpy", "dst":"hC", "src":"dC", "kind":"D2H" },

        { "op":"DeviceFree", "ptr":"dA" },
        { "op":"DeviceFree", "ptr":"dB" },
        { "op":"DeviceFree", "ptr":"dC" }
      ]
    }

def merge_preserve_c_fill(orig_doc, new_doc):
    # préserve le 'fill' de hC si présent (utile quand beta != 0)
    try:
        for op in orig_doc.get("ops", []):
            if op.get("op")=="HostMake" and op.get("name")=="hC":
                fill_c = op.get("fill")
                start  = op.get("start")
                step   = op.get("step")
                if fill_c is not None:
                    for nop in new_doc["ops"]:
                        if nop.get("op")=="HostMake" and nop.get("name")=="hC":
                            nop["fill"] = fill_c
                            if start is not None: nop["start"]=start
                            if step  is not None: nop["step"]=step
    except Exception:
        pass

def maybe_insert_dc_h2d(new_doc, beta):
    if abs(beta) < 1e-12:
        return
    # insérer Memcpy dC H2D après dB H2D
    ops = new_doc["ops"]
    insert_after = -1
    for i,op in enumerate(ops):
        if op.get("op")=="Memcpy" and op.get("dst")=="dB" and op.get("kind")=="H2D":
            insert_after = i
            break
    if insert_after >= 0:
        ops.insert(insert_after+1, { "op":"Memcpy", "dst":"dC", "src":"hC", "kind":"H2D" })

def find_op(ops, kind):
    for i,o in enumerate(ops):
        if o.get("op")==kind:
            return i,o
    return -1,None

def canonicalize(path, outdir):
    # lecture tolérante au BOM
    with open(path, "r", encoding="utf-8-sig") as f:
        orig = json.load(f)

    if not has_gemm(orig):
        return False, "skip (no GEMM)"
    M,N,K,alpha,beta = get_scalars(orig)
    doc = build_canonical(M,N,K,alpha,beta)

    # garde transA/B/layout si l’original en avait
    try:
        orig_gemm = next(op for op in orig.get("ops",[]) if op.get("op")=="GEMM")
        gi, new_gemm = find_op(doc["ops"], "GEMM")
        if gi >= 0 and new_gemm is not None:
            if "transA" in orig_gemm: new_gemm["transA"] = orig_gemm["transA"]
            if "transB" in orig_gemm: new_gemm["transB"] = orig_gemm["transB"]
            if "layout" in orig_gemm: new_gemm["layout"] = orig_gemm["layout"]
    except Exception:
        pass

    # layout global si existant
    meta = orig.get("meta") or {}
    if "layout" in meta: doc["meta"]["layout"] = meta["layout"]

    merge_preserve_c_fill(orig, doc)
    maybe_insert_dc_h2d(doc, beta)

    # compare JSON canonique vs original (en tant que texte minifié)
    changed = json.dumps(orig, sort_keys=True) != json.dumps(doc, sort_keys=True)

    out_path = os.path.join(outdir, os.path.basename(path))
    os.makedirs(outdir, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
    return changed, out_path

def main():
    if len(sys.argv) < 3:
        print("Usage: python fix_axir.py <in_dir> <out_dir>")
        sys.exit(1)
    in_dir, out_dir = sys.argv[1], sys.argv[2]
    total = 0; changed = 0; skipped = 0
    for root, _, files in os.walk(in_dir):
        for fn in files:
            if not fn.endswith(".json"): continue
            if "matmul" not in fn: continue
            p = os.path.join(root, fn)
            total += 1
            try:
                chg, outp = canonicalize(p, out_dir)
                if chg: changed += 1
            except Exception as e:
                skipped += 1
                print(f"!! {fn}: {e}")
    print(f"Done. total={total}, changed={changed}, skipped={skipped}, out='{out_dir}'")

if __name__ == "__main__":
    main()
