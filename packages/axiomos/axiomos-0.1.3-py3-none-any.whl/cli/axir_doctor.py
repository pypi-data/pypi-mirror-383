#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse, json, pathlib, re, sys

# ──────────────────────────────────────────────────────────────────────────────
# Utils
# ──────────────────────────────────────────────────────────────────────────────

def _err(msg): print(f"[doctor] ❌ {msg}")
def _ok(msg):  print(f"[doctor] ✅ {msg}")

def _eval_bytes(expr: str, scalars: dict) -> int | None:
    """Évalue une expression de bytes éventuellement dépendante de scalaires.
    Remplace sizeof(float|int) et injecte les scalaires connus. Retourne None si non résoluble."""
    if not expr:
        return None
    s = str(expr).replace(" ", "")
    s = re.sub(r"sizeof\(\s*float\s*\)?", "4", s, flags=re.I)
    s = re.sub(r"sizeof\(\s*int\s*\)?",   "4", s, flags=re.I)
    for k, v in (scalars or {}).items():
        try:
            s = re.sub(rf"\b{k}\b", str(int(v)), s)
        except Exception:
            pass
    if re.search(r"[A-Za-z_]", s):  # encore des symboles non résolus
        return None
    try:
        return int(eval(s, {"__builtins__": {}}))
    except Exception:
        return None

# ──────────────────────────────────────────────────────────────────────────────
# Doctor ENV (sans argument) : versions + OpenCL
# ──────────────────────────────────────────────────────────────────────────────

def _env_doctor() -> int:
    """Petit check environnement: versions + devices OpenCL. Retourne un code de sortie."""
    import platform, importlib
    def _ver(m):
        try:
            return importlib.import_module(m).__version__
        except Exception:
            return "n/a"

    print("== AXIR Doctor: Environnement ==")
    print(f"- Python   : {platform.python_version()}")
    print(f"- numpy    : {_ver('numpy')}")
    print(f"- pyopencl : {_ver('pyopencl')}")

    # OpenCL inventory (optionnel si lib absente)
    try:
        import pyopencl as cl
        plats = cl.get_platforms()
        if not plats:
            _err("Aucune plateforme OpenCL détectée.")
            print("  Astuce: installez un runtime (pocl, NVIDIA, AMD, Intel) ou utilisez --target cpu.")
            return 2

        print("\nOpenCL devices:")
        for p in plats:
            for d in p.get_devices():
                t = cl.device_type.to_string(d.type)
                local_kb = d.local_mem_size // 1024
                print(f"  - [{p.name.strip()}] {d.name.strip()}  ({t}), local_mem={local_kb} KB, max_wg={d.max_work_group_size}")

        # Heuristiques et conseils actionnables
        warn = 0
        for p in plats:
            for d in p.get_devices():
                try:
                    t = cl.device_type.to_string(d.type)
                    local_kb = d.local_mem_size // 1024
                    max_wg   = d.max_work_group_size
                    exts     = set((d.extensions or "").split())

                    # 1) Mémoire locale faible
                    if local_kb < 32:
                        warn += 1
                        print(f"[doctor] ⚠ Low local memory on '{d.name.strip()}' ({local_kb} KB) — GEMM tiled may be limited. Try smaller tiles (e.g. 8/16).")

                    # 2) Petite taille de work-group
                    if max_wg < 128:
                        warn += 1
                        print(f"[doctor] ⚠ Small max work-group ({max_wg}) — tune work-group to 8x8.")

                    # 3) Extensions intéressantes (non bloquant)
                    needed_any = {"cl_khr_fp16", "cl_khr_fp64", "cl_khr_int64_base_atomics"}
                    missing = [e for e in needed_any if e not in exts]
                    if missing:
                        print(f"[doctor] ℹ Extensions not present: {', '.join(sorted(missing))}. "
                              f"AXIR runs without them, but some precisions/kernels may be slower or unavailable.")
                except Exception:
                    pass

        if warn == 0:
            print("[doctor] ✅ Device capabilities look fine for AXIR.")
        _ok("Environnement OK")
        return 0

    except Exception as e:
        _err(f"OpenCL indisponible: {e}")
        print("  Astuce: vous pouvez quand même utiliser --target cpu (NumPy).")
        return 2

# ──────────────────────────────────────────────────────────────────────────────
# Doctor AXIR (avec fichier) : validation de l’AXIR JSON
# ──────────────────────────────────────────────────────────────────────────────

def _axir_file_doctor(axir_path: pathlib.Path, fix: bool) -> int:
    if not axir_path.exists():
        _err(f"Fichier introuvable: {axir_path}")
        return 1
    try:
        ax = json.loads(axir_path.read_text(encoding="utf-8"))
    except Exception as e:
        _err(f"JSON invalide: {e}")
        return 1

    problems = 0
    types = ax.get("types") or {}
    bufs  = types.get("buffers") or {}
    scal  = types.get("scalars") or {}
    ops   = ax.get("ops") or []

    # (1) Dimensions requises selon le kernel
    need_dims = set()
    if any(op.get("op")=="KernelLaunch" and str(op.get("kernel","")).lower().startswith("matmul") for op in ops):
        need_dims |= {"M","N","K"}
    if any(op.get("op")=="KernelLaunch" and str(op.get("kernel","")).lower().startswith("softmax") for op in ops):
        need_dims |= {"M","N"}

    for nm in sorted(need_dims):
        if nm not in scal or "value" not in scal[nm]:
            problems += 1
            _err(f"Scalaire '{nm}' manquant (ex: ajouter \"{nm}\":{{\"dtype\":\"i32\",\"value\":128}}).")

    # (2) Buffers présents ?
    if not bufs:
        problems += 1
        _err("Aucun buffer déclaré dans types.buffers")

    # (3) Consistance bytes dans DeviceMalloc / Memcpy
    solv_scal = {k:int(v.get("value")) for k,v in scal.items() if isinstance(v,dict) and "value" in v}
    for i, op in enumerate(ops):
        if op.get("op") == "DeviceMalloc":
            expr = op.get("bytes")
            b = _eval_bytes(expr, solv_scal)
            if b is None or b <= 0:
                problems += 1
                _err(f"DeviceMalloc op#{i}: bytes='{expr}' non résolu → vérifier scalars/expr.")
        if op.get("op") == "Memcpy":
            kind, expr = op.get("kind"), op.get("bytes")
            b = _eval_bytes(expr, solv_scal)
            if b is None or b <= 0:
                problems += 1
                _err(f"Memcpy({kind}) op#{i}: bytes='{expr}' non résolu.")

    # (4) KernelLaunch: kernel & args
    for i, op in enumerate(ops):
        if op.get("op") == "KernelLaunch":
            k = (op.get("kernel","") or "").lower()
            args = op.get("args") or []
            if not k:
                problems += 1
                _err(f"KernelLaunch op#{i}: champ 'kernel' manquant.")
            if not args:
                problems += 1
                _err(f"KernelLaunch '{k or '?'}' op#{i}: liste 'args' manquante.")

    if problems == 0:
        _ok("AXIR semble cohérent ✅")
        return 0
    else:
        print(f"[doctor] → Problèmes détectés: {problems}")
        if fix:
            print("[doctor] Suggestions génériques:")
            if "M" in need_dims and ("M" not in scal or "value" not in scal.get("M",{})):
                print('  - Ajouter: "M":{"dtype":"i32","value":256}')
            if "N" in need_dims and ("N" not in scal or "value" not in scal.get("N",{})):
                print('  - Ajouter: "N":{"dtype":"i32","value":256}')
            if "K" in need_dims and ("K" not in scal or "value" not in scal.get("K",{})):
                print('  - Ajouter: "K":{"dtype":"i32","value":256}')
        return 2

# ──────────────────────────────────────────────────────────────────────────────
# Entrée CLI
# ──────────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description="AXIR Doctor — vérifie l'environnement (sans argument) ou un AXIR JSON (avec fichier)."
    )
    p.add_argument("axir", nargs="?", help="Chemin du fichier .axir.json (optionnel)")
    p.add_argument("--fix", action="store_true", help="Affiche des suggestions de valeurs par défaut")
    return p.parse_args()

def main():
    args = parse_args()
    if not args.axir:
        # Mode environnement (aucun argument positionnel)
        code = _env_doctor()
        sys.exit(code)
    else:
        # Mode validation de fichier AXIR
        code = _axir_file_doctor(pathlib.Path(args.axir), args.fix)
        sys.exit(code)

if __name__ == "__main__":
    main()
