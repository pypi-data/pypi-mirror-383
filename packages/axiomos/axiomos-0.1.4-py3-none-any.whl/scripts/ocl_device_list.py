#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/ocl_device_list.py

Liste les plateformes & devices OpenCL avec indices utilisables par AXIOMOS :
- Plateformes : AXIOMOS_OCL_PLATFORM_INDEX
- Devices     : AXIOMOS_OCL_DEVICE_INDEX  (parmi la plateforme choisie)
- Type        : AXIOMOS_OCL_DEVICE_TYPE = GPU|CPU|ACCEL|DEFAULT|ALL

Usage :
  python scripts/ocl_device_list.py
  python scripts/ocl_device_list.py --short
  python scripts/ocl_device_list.py --json
  python scripts/ocl_device_list.py --filter-type GPU
"""

from __future__ import annotations
import argparse, json, sys

try:
    import pyopencl as cl
except Exception as e:
    print("[ERROR] pyopencl introuvable. Installez-le avec: pip install pyopencl")
    print(f"Cause: {e}")
    sys.exit(1)


def _dev_type_str(dt: int) -> str:
    # Map bitfield -> label le plus “parlant”
    m = []
    if dt & cl.device_type.GPU:     m.append("GPU")
    if dt & cl.device_type.CPU:     m.append("CPU")
    if dt & cl.device_type.ACCELERATOR: m.append("ACCEL")
    if dt & cl.device_type.DEFAULT: m.append("DEFAULT")
    if dt & cl.device_type.CUSTOM:  m.append("CUSTOM")
    return "|".join(m) or f"0x{int(dt):x}"


def _has_fp64(dev) -> bool:
    try:
        # Extension courante côté OpenCL 1.x
        if "cl_khr_fp64" in (dev.extensions or ""):
            return True
    except Exception:
        pass
    try:
        # Si exposé par le driver
        return bool(getattr(dev, "double_fp_config", 0))
    except Exception:
        return False


def _fmt_bytes(n: int) -> str:
    # Affiche lisible (KB/MB/GB)
    s = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if s < 1024.0 or unit == "TB":
            return f"{s:.1f} {unit}"
        s /= 1024.0
    return f"{n} B"


def gather(filter_type: str | None):
    plats = cl.get_platforms()
    out = []
    for pi, p in enumerate(plats):
        try:
            devs = p.get_devices()
        except Exception:
            devs = []
        dev_rows = []
        for di, d in enumerate(devs):
            drow = {
                "p_index": pi,
                "d_index": di,
                "platform_name": p.name,
                "platform_vendor": p.vendor,
                "platform_version": getattr(p, "version", ""),
                "name": d.name,
                "vendor": d.vendor,
                "version": d.version,
                "driver_version": getattr(d, "driver_version", ""),
                "type": _dev_type_str(d.type),
                "max_compute_units": int(getattr(d, "max_compute_units", 0)),
                "max_clock_mhz": int(getattr(d, "max_clock_frequency", 0)),
                "max_work_group_size": int(getattr(d, "max_work_group_size", 0)),
                "local_mem": int(getattr(d, "local_mem_size", 0)),
                "global_mem": int(getattr(d, "global_mem_size", 0)),
                "fp64": _has_fp64(d),
                "extensions_count": len((d.extensions or "").split()),
            }
            if filter_type:
                if filter_type.upper() not in drow["type"].upper():
                    continue
            dev_rows.append(drow)
        out.append({
            "p_index": pi,
            "platform_name": p.name,
            "platform_vendor": p.vendor,
            "platform_version": getattr(p, "version", ""),
            "devices": dev_rows
        })
    return out


def print_human(rows, short=False):
    if not rows:
        print("No OpenCL platforms found.")
        return

    for p in rows:
        print(f"[P{p['p_index']}] {p['platform_name']}  (vendor: {p['platform_vendor']}, version: {p['platform_version']})")
        if not p["devices"]:
            print("   (no devices)")
            continue
        for d in p["devices"]:
            head = f"  [D{d['d_index']}] {d['name']}  <{d['type']}>"
            if short:
                print(head)
                continue
            print(head)
            print(f"     vendor: {d['vendor']}")
            print(f"     version: {d['version']}  | driver: {d['driver_version']}")
            print(f"     compute_units: {d['max_compute_units']}  | clock: {d['max_clock_mhz']} MHz")
            print(f"     workgroup_max: {d['max_work_group_size']}")
            print(f"     local_mem:  {_fmt_bytes(d['local_mem'])}  | global_mem: {_fmt_bytes(d['global_mem'])}")
            print(f"     fp64: {'yes' if d['fp64'] else 'no'}  | extensions: ~{d['extensions_count']}")

    print("\nSelection via variables d’environnement (exemples) :")
    print("  set AXIOMOS_OCL_PLATFORM_INDEX=0")
    print("  set AXIOMOS_OCL_DEVICE_INDEX=1")
    print("  set AXIOMOS_OCL_DEVICE_TYPE=GPU   # prioritaire si les indices ne sont pas définis")
    print("\nPriorité côté backend OpenCL :")
    print("  1) AXIOMOS_OCL_PLATFORM_INDEX + AXIOMOS_OCL_DEVICE_INDEX")
    print("  2) AXIOMOS_OCL_DEVICE_TYPE (GPU|CPU|ACCEL|DEFAULT|ALL)")
    print("  3) Premier device disponible (fallback)")


def main():
    ap = argparse.ArgumentParser(description="Liste les plateformes/devices OpenCL avec indices utilisables par AXIOMOS.")
    ap.add_argument("--short", action="store_true", help="Affichage concis (nom + type).")
    ap.add_argument("--json", action="store_true", help="Sortie JSON.")
    ap.add_argument("--filter-type", choices=["GPU", "CPU", "ACCEL", "DEFAULT"], help="Filtrer par type de device.")
    args = ap.parse_args()

    rows = gather(args.filter_type)

    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        print_human(rows, short=args.short)


if __name__ == "__main__":
    main()
