#!/usr/bin/env python3
# Générateur d’AXIR pour GEMM (+Bias optionnel) avec activation (relu/gelu/none)
# Le backend OpenCL choisira auto le kernel (tiled, 2x2_v4, fused bias/act) selon tailles/env.
import argparse, json, pathlib

TEMPLATE = {
  "types": {
    "scalars": {
      "M": {"value": 128},
      "N": {"value": 128},
      "K": {"value": 128}
    },
    "buffers": {
      "dA": {"dtype": "f32"},
      "dB": {"dtype": "f32"},
      "dC": {"dtype": "f32"}
    }
  },
  "ops": []
}

def build_axir(M:int,N:int,K:int, with_bias:bool):
    ax = json.loads(json.dumps(TEMPLATE))
    ax["types"]["scalars"]["M"]["value"]=M
    ax["types"]["scalars"]["N"]["value"]=N
    ax["types"]["scalars"]["K"]["value"]=K

    if with_bias:
        ax["types"]["buffers"]["dBias"]={"dtype":"f32"}

    ops = []

    # Mallocs
    ops += [
      {"op":"DeviceMalloc","dst":"dA","bytes":f"{M*K}*sizeof(float)"},
      {"op":"DeviceMalloc","dst":"dB","bytes":f"{K*N}*sizeof(float)"},
      {"op":"DeviceMalloc","dst":"dC","bytes":f"{M*N}*sizeof(float)"},
    ]
    if with_bias:
        ops.append({"op":"DeviceMalloc","dst":"dBias","bytes":f"{N}*sizeof(float)"})

    # H2D (démo: remplit hA/hB/hBias côté backend si absents, mais on ajoute les copies pour clarté)
    ops += [
      {"op":"Memcpy","kind":"H2D","src":"hA","dst":"dA","bytes":f"{M*K}*sizeof(float)"},
      {"op":"Memcpy","kind":"H2D","src":"hB","dst":"dB","bytes":f"{K*N}*sizeof(float)"},
    ]
    if with_bias:
        ops.append({"op":"Memcpy","kind":"H2D","src":"hBias","dst":"dBias","bytes":f"{N}*sizeof(float)"})

    # KernelLaunch — IMPORTANT: on garde 'matmul' pour que le backend fasse le dispatch + fusion auto si Bias présent
    ops.append({
      "op":"KernelLaunch",
      "kernel":"matmul",
      "args":["dA","dB","dC","M","N","K"],
      # (grid/block peuvent rester vides; le backend ignore pour OpenCL)
      "grid":  ["M","N","1"],
      "block": ["1","1","1"]
    })

    # D2H
    ops.append({"op":"Memcpy","kind":"D2H","src":"dC","dst":"hC","bytes":f"{M*N}*sizeof(float)"})

    ax["ops"]=ops
    return ax

def main():
    ap = argparse.ArgumentParser(description="Génère un AXIR GEMM (+Bias optionnel)")
    ap.add_argument("--M", type=int, default=128)
    ap.add_argument("--N", type=int, default=128)
    ap.add_argument("--K", type=int, default=128)
    ap.add_argument("--bias", action="store_true", help="Inclure un Bias (longueur N) — permettra la fusion")
    ap.add_argument("-o","--out", required=True, help="Chemin de sortie .axir.json")
    ap.add_argument("--act", choices=["none","relu","gelu"], default="none",
                    help="Activation fusionnée désirée (le choix se fait côté backend via AXIR_GEMM_ACT)")
    args = ap.parse_args()

    ax = build_axir(args.M, args.N, args.K, args.bias)
    # L’activation est contrôlée par variable d’env côté backend; on ajoute une note dans axir pour traçabilité
    ax.setdefault("meta",{})["suggested_activation"]=args.act

    out = pathlib.Path(args.out)
    out.write_text(json.dumps(ax, indent=2), encoding="utf-8")
    print(f"[make_gemm_bias] écrit -> {out}")
    print("Astuce backend:")
    print("  set AXIR_GEMM_ACT=%s   (none|relu|gelu)" % args.act)
    print("  set AXIR_GEMM_TILE=16  (ou 32)")
    print("  python -m cli.axir_run %s --target opencl --why --summary" % str(out))

if __name__ == "__main__":
    main()
