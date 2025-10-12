# cli/axir_run.py
#!/usr/bin/env python3
import argparse, json, pathlib, time, sys, re, os
import numpy as np

# ========= availability checks =========
def _has_opencl():
    try:
        import pyopencl as cl  # noqa
        return len(cl.get_platforms()) > 0
    except Exception:
        return False

def _has_cuda():
    try:
        import pycuda.driver as cuda  # noqa
        cuda.init()
        return cuda.Device.count() > 0
    except Exception:
        return False

def _has_hip():
    try:
        import hip  # noqa: placeholder
        return True
    except Exception:
        return False

# ========= helpers to read sizes from AXIR =========
def _int_or_none(x):
    try:
        return int(x)
    except Exception:
        return None

def _eval_bytes(expr: str, scalars: dict) -> int | None:
    if not expr:
        return None
    s = str(expr).replace(" ", "")
    s = re.sub(r"sizeof\(\s*float\s*\)?", "4", s, flags=re.IGNORECASE)
    s = re.sub(r"sizeof\(\s*int\s*\)?",   "4", s, flags=re.IGNORECASE)
    for k, v in (scalars or {}).items():
        try:
            s = re.sub(rf"\b{k}\b", str(int(v)), s)
        except Exception:
            pass
    if re.search(r"[A-Za-z_]", s): return None
    if not re.fullmatch(r"[-+*/0-9eE\.()]+", s): return None
    try:
        return int(eval(s, {"__builtins__": {}}))
    except Exception:
        return None

def _collect_scalars(ax):
    out = {}
    for k, meta in (ax.get("types", {}).get("scalars", {}) or {}).items():
        v = meta.get("value")
        iv = _int_or_none(v)
        if iv is not None:
            out[k] = iv
    return out

def _guess_N(ax, scalars):
    if "N" in scalars and scalars["N"] >= 2:
        return scalars["N"]
    max_n, saw_sym = 0, False
    for op in ax.get("ops", []):
        if op.get("op") == "KernelLaunch":
            for key in ("grid", "block"):
                v = (op.get(key) or ["", "", ""])[0]
                if isinstance(v, int):
                    max_n = max(max_n, v)
                elif isinstance(v, str):
                    v = v.strip()
                    if re.fullmatch(r"\d+", v):
                        max_n = max(max_n, int(v))
                    elif "N" in v:
                        saw_sym = True
    for op in ax.get("ops", []):
        if op.get("op") in ("DeviceMalloc", "Memcpy"):
            b = _eval_bytes(str(op.get("bytes", "")), scalars)
            if b and b % 4 == 0:
                elems = b // 4
                if elems >= 8:
                    max_n = max(max_n, elems)
            elif re.search(r"\bN\b", str(op.get("bytes", ""))):
                saw_sym = True
    return max_n if max_n >= 2 else 16

def _detect_workload(ax):
    scalars = _collect_scalars(ax)
    kernels = []
    for op in ax.get("ops", []):
        if op.get("op") == "KernelLaunch":
            kernels.append((op.get("kernel","") or "").lower())
    dims = {"N": _guess_N(ax, scalars), "M": scalars.get("M"), "K": scalars.get("K")}
    return kernels, dims, {"scalars": scalars}

# ========= heuristic policy thresholds =========
TH_ELTWISE   = 1_000_000
TH_REDUCE    = 2_500_000
TH_SMX_W     = 512
TH_SMX_ELEMS = 262_144

# ========= NEW HELPERS =========
def _mnk_from_ax(ax):
    """Récupère (M,N,K) à partir des scalars et, si besoin, des shapes buffers."""
    scalars = _collect_scalars(ax)
    M = scalars.get("M"); N = scalars.get("N"); K = scalars.get("K")
    if all(v is not None for v in (M, N, K)):
        return int(M), int(N), int(K)
    # fallback: méta buffers si présents
    bufs = (ax.get("buffers") or {})
    def _shape(name):
        ent = bufs.get(name) or {}
        sh = ent.get("shape")
        if isinstance(sh, (list, tuple)) and len(sh) in (1,2):
            return tuple(int(x) for x in sh)
        return None
    shA = _shape("hA"); shB = _shape("hB"); shC = _shape("hC")
    m=n=k=None
    if shA and len(shA)==2: m,k = shA
    if shB and len(shB)==2:
        k = k if k is not None else shB[0]
        n = shB[1]
    if shC and len(shC)==2:
        m = m if m is not None else shC[0]
        n = n if n is not None else shC[1]
    if all(v is not None for v in (m,n,k)):
        return int(m), int(n), int(k)
    return None, None, None

def _is_matmul(kset):
    return any(k.startswith("matmul") or k == "gemm" for k in kset)

def _host_dump_candidates_from_axir(ax: dict) -> list[str]:
    cand: list[str] = []

    def add(x):
        if isinstance(x, str) and x and (x not in cand):
            cand.append(x)

    # 1) Memcpy : repérer les destinations/sources host (souvent 'h*')
    for op in ax.get("ops", []):
        if op.get("op") == "Memcpy":
            src = op.get("src") or op.get("from") or {}
            dst = op.get("dst") or op.get("to") or {}
            if isinstance(src, dict): src = src.get("name") or src.get("var")
            if isinstance(dst, dict): dst = dst.get("name") or dst.get("var")
            if isinstance(dst, str) and dst.startswith("h"): add(dst)
            if isinstance(src, str) and src.startswith("h"): add(src)

    # 2) Buffers déclarés côté host
    bufs = (ax.get("types", {}).get("buffers", {}) or {})
    for name, meta in bufs.items():
        place = str((meta or {}).get("place", "")).lower()
        if name.startswith("h") or "host" in place or "cpu" in place:
            add(name)

    # 3) Fallbacks usuels
    for x in ("hC","hOut","hY","hZ","hRes","C","out","Y","Res","dC"):
        add(x)

    return cand

def _ocl_device_info():
    try:
        import pyopencl as cl
        plats = cl.get_platforms()
        devs = plats[0].get_devices() if plats else []
        if not devs:
            return {}
        d = devs[0]
        name = d.name.lower()
        vendor = d.vendor.lower()
        is_intel_igpu = ("intel" in vendor) and (
            "uhd" in name or "iris" in name or "hd graphics" in name or "graphics" in name
        )
        return {"name": d.name, "vendor": d.vendor, "is_intel_igpu": is_intel_igpu}
    except Exception:
        return {}

# ========= AUTO-DECISION =========
def _decide_auto(ax, why=False):
    have = {"opencl": _has_opencl(), "cuda": _has_cuda(), "hip": _has_hip(), "cpu": True}
    kernels, dims, _ = _detect_workload(ax)
    reasons = []
    kset = set(kernels)

    def pick(pref):
        for t in pref:
            if have.get(t):
                return t
        return "cpu"

    # --- Matmul: nouvelle heuristique (iGPU Intel -> CPU, gros FLOPs -> GPU)
    if _is_matmul(kset):
        # Estimation FLOPs = 2*M*N*K ; fallback ~ N^3 si M/K inconnus
        M = dims.get("M") or dims.get("N") or 256
        N = dims.get("N") or M
        K = dims.get("K") or M
        flops = 2 * int(M) * int(N) * int(K)

        info = _ocl_device_info() if have.get("opencl") else {}
        if info.get("is_intel_igpu"):
            reasons.append("matmul sur iGPU Intel → CPU (overhead OCL + iGPU < MKL/NumPy).")
            return pick(["cpu","opencl","cuda","hip"]), reasons

        if have.get("opencl"):
            # seuil prudent pour dGPU; ajuste si besoin
            if flops >= 5_00_000_000:  # ~5e8 FLOPs
                reasons.append(f"matmul FLOPs≈{flops/1e9:.2f}e9 → GPU.")
                return "opencl", reasons
            reasons.append(f"matmul FLOPs≈{flops/1e9:.2f}e9 → CPU (petit/moyen).")
            return "cpu", reasons

        reasons.append("matmul → pas de GPU dispo → CPU.")
        return "cpu", reasons

    # --- Softmax/Layernorm
    TH_SMX_W     = 512
    TH_SMX_ELEMS = 262_144
    is_softmax  = any(k.startswith("softmax") for k in kset)
    is_laynorm  = any(k.startswith("layernorm") for k in kset)
    if is_softmax or is_laynorm:
        width = (dims.get("N") or 0)
        elems = (dims.get("M") or 0) * (dims.get("N") or 0)
        if width >= TH_SMX_W or elems >= TH_SMX_ELEMS:
            reasons.append("softmax/layernorm larges → GPU.")
            return pick(["opencl","cuda","hip","cpu"]), reasons
        reasons.append("softmax/layernorm petits → CPU.")
        return pick(["cpu","opencl","cuda","hip"]), reasons

    # --- Reductions
    TH_REDUCE = 2_500_000
    is_reduce = any(k.startswith("reduce_") for k in kset)
    N = dims.get("N") or 16
    if is_reduce:
        if N >= TH_REDUCE:
            reasons.append("reduction grande → GPU.")
            return pick(["opencl","cuda","hip","cpu"]), reasons
        reasons.append("reduction petite → CPU.")
        return pick(["cpu","opencl","cuda","hip"]), reasons

    # --- Eltwise
    TH_ELTWISE = 1_000_000
    is_eltwise = any(k.startswith(p) for p in ("vector_add","saxpy","mul","vexp","relu") for k in kset)
    if is_eltwise:
        if N >= TH_ELTWISE:
            reasons.append("eltwise grand → GPU.")
            return pick(["opencl","cuda","hip","cpu"]), reasons
        reasons.append("eltwise petit → CPU.")
        return pick(["cpu","opencl","cuda","hip"]), reasons

    # --- Inconnu
    if N >= TH_ELTWISE and have["opencl"]:
        reasons.append("inconnu mais N grand → OpenCL.")
        return "opencl", reasons

    reasons.append("cas simple/petit → CPU par défaut.")
    return "cpu", reasons

# ========= loader AXIR ou source =========
def _load_axir_or_translate(path_str: str) -> dict:
    p = pathlib.Path(path_str)
    ext = p.suffix.lower()
    if ext == ".json":
        return json.loads(p.read_text(encoding="utf-8-sig"))
    # sources: .cu/.cl/.c/.cpp + suffixes .hip.cpp/.sycl.cpp
    if ext in (".cu",".cl",".c",".cpp") or p.name.endswith(".hip.cpp") or p.name.endswith(".sycl.cpp"):
        try:
            from frontends.frontend_light import translate_file_to_axir
        except Exception as e:
            raise SystemExit(f"[axir_run] Frontend léger indisponible: {e}")
        return translate_file_to_axir(p)
    raise SystemExit(f"[axir_run] Format non supporté: {p.name}")

# --- infer-sizes helper -------------------------------------------------
def _parse_infer_sizes(s: str):
    """
    '1000000'       -> ('N',   (1000000,))
    '512,512,512'   -> ('MNK', (512,512,512))
    """
    raw = s.strip()
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if len(parts) == 1:
        try:
            N = int(parts[0])
            return "N", (N,)
        except:
            raise SystemExit(f"[--infer-sizes] invalide: {s}")
    if len(parts) == 3:
        try:
            M, N, K = map(int, parts)
            return "MNK", (M, N, K)
        except:
            raise SystemExit(f"[--infer-sizes] invalide: {s}")
    raise SystemExit(f"[--infer-sizes] format attendu: 'N' ou 'M,N,K' (reçu: {s})")

# ========= dispatch to real backends =========
def run_backend(axir_json_path: str, target: str, dump: str|None,
                summary: bool, repeat: int, bench: bool,
                infer_sizes: str | None = None):
    # charge AXIR ou traduit la source
    ax = _load_axir_or_translate(axir_json_path)

    # override tailles si demandé
    if infer_sizes:
        kind, vals = _parse_infer_sizes(infer_sizes)
        ax.setdefault("types", {}).setdefault("scalars", {})
        scal = ax["types"]["scalars"]
        if kind == "N":
            N, = vals
            scal["N"] = {"dtype":"i32","value": int(N)}
        else:
            M, N, K = vals
            scal["M"] = {"dtype":"i32","value": int(M)}
            scal["N"] = {"dtype":"i32","value": int(N)}
            scal["K"] = {"dtype":"i32","value": int(K)}

    decision_reasons = None
    if target == "auto":
        target, decision_reasons = _decide_auto(ax, why=True)

    t0 = time.perf_counter()
    if target == "cpu":
        # CPU: Backends vs backends
        try:
            from Backends.cpu_numpy_backend import run as run_cpu
        except ImportError:
            from backends.cpu_numpy_backend import run as run_cpu
        print("Running on CPU...")
        res = run_cpu(ax, summary=summary, dump=dump, repeats=repeat)
        dt = (time.perf_counter() - t0) * 1000
        print(f"Running on CPU... OK ({dt:.1f} ms)")
        return res, decision_reasons

    if target == "opencl":
        # OpenCL: Backends vs backends
        try:
            try:
                from Backends.opencl_backend import run as run_ocl
            except ImportError:
                from backends.opencl_backend import run as run_ocl
        except Exception as e:
            print(f"[ERROR] OpenCL backend not available: {e}", file=sys.stderr)
            sys.exit(1)
        print("Running on OPENCL...")
        # utilise profile (pas bench) ; le backend affichera ses lignes [OCL][PROFILE] ...
        res = run_ocl(ax, summary=summary, dump=dump, repeats=repeat, profile=bench)
        dt = (time.perf_counter() - t0) * 1000
        print(f"Running on OPENCL... OK ({dt:.1f} ms)")
        # On garde uniquement le feedback natif du backend ([OCL][PROFILE] ...).
        return res, decision_reasons

    if target == "cuda":
        try:
            try:
                from Backends.cuda_backend import run as run_cuda
            except ImportError:
                from backends.cuda_backend import run as run_cuda
        except Exception as e:
            print(f"[ERROR] CUDA backend not available: {e}", file=sys.stderr)
            sys.exit(1)
        print("Running on CUDA...")
        res = run_cuda(ax, summary=summary, dump=dump, repeats=repeat)
        dt = (time.perf_counter() - t0) * 1000
        print(f"Running on CUDA... OK ({dt:.1f} ms)")
        return res, decision_reasons

    if target == "hip":
        try:
            try:
                from Backends.hip_backend import run as run_hip
            except ImportError:
                from backends.hip_backend import run as run_hip
        except Exception as e:
            print(f"[ERROR] HIP backend not available: {e}", file=sys.stderr)
            sys.exit(1)
        print("Running on HIP...")
        res = run_hip(ax, summary=summary, dump=dump, repeats=repeat)
        dt = (time.perf_counter() - t0) * 1000
        print(f"Running on HIP... OK ({dt:.1f} ms)")
        return res, decision_reasons

    print(f"[ERROR] Unknown target: {target}", file=sys.stderr)
    sys.exit(2)

# ========= CLI =========
def main():
    # Defaults for verify tolerances from environment (overridable by CLI)
    env_rtol = float(os.getenv("AXIOMOS_VERIFY_RTOL", "1e-6"))
    env_atol = float(os.getenv("AXIOMOS_VERIFY_ATOL", "1e-6"))

    p = argparse.ArgumentParser(description="AXIR runner — auto-selects backend unless --target is set")
    p.add_argument("axir", help="Path to AXIR JSON or source (.json/.cu/.cl/.cpp/...)")
    p.add_argument("--target", default="auto", choices=["auto","cpu","opencl","cuda","hip"])
    p.add_argument("--print", dest="dump", help="Buffer to fetch (e.g., hC, dC, hOut, dOut, hY, hIdx)")
    p.add_argument("--out", help="If set, saves --print buffer to this .npy file")
    p.add_argument("--summary", action="store_true")
    p.add_argument("--repeat", type=int, default=1)
    p.add_argument("--why", action="store_true")
    p.add_argument("--bench", action="store_true",
                   help="Enable backend profiling (OpenCL shows [OCL][PROFILE] lines)")
    p.add_argument(
        "--verify",
        action="store_true",
        help="Rejoue sur CPU et compare le buffer --print (tolérances via --rtol/--atol ; défaut 1e-6 ou variables d'env).",
    )
    p.add_argument("--infer-sizes", help="Override tailles (ex: 'N' ou 'M,N,K', p.ex. 1000000 ou 256,512,256)")
    # tolérances personnalisables (défaut depuis env)
    p.add_argument("--rtol", type=float, default=env_rtol, help="Relative tolerance for --verify (FP32)")
    p.add_argument("--atol", type=float, default=env_atol, help="Absolute tolerance for --verify")
    p.add_argument("--tolerant", action="store_true", help="Shortcut: --rtol 3e-6 --atol 1e-6")
    p.add_argument("--strict",   action="store_true", help="Shortcut: --rtol 1e-6 --atol 1e-6 (default)")
    # OpenCL env helpers
    p.add_argument("--ocl-autotune", choices=["0","1","force"], help="Set AXIOMOS_OCL_AUTOTUNE")
    p.add_argument("--ocl-fastmath", action="store_true", help="Set AXIOMOS_OCL_FASTMATH=1")
    args = p.parse_args()

    # presets tolérance
    if args.tolerant:
        args.rtol, args.atol = 3e-6, 1e-6
    if args.strict:
        args.rtol, args.atol = 1e-6, 1e-6

    # env OpenCL facultatifs
    if args.ocl_autotune:
        os.environ["AXIOMOS_OCL_AUTOTUNE"] = args.ocl_autotune
    if args.ocl_fastmath:
        os.environ["AXIOMOS_OCL_FASTMATH"] = "1"

    # run principal
    res, reasons = run_backend(
        args.axir, args.target, dump=args.dump, summary=args.summary,
        repeat=args.repeat, bench=args.bench, infer_sizes=args.infer_sizes
    )
    # normalisation si --print est demandé et que le backend renvoie un array brut
    if args.dump and not isinstance(res, dict):
        res = {"dump": res}

    # explication auto-select
    if args.why and args.target == "auto":
        print("\n[why] auto-selection rationale:")
        if reasons:
            for r in reasons:
                print(" -", r)
        else:
            print(" - no extra info")

    # impression / sauvegarde du buffer
    if args.dump:
        arr = res.get("dump")
        if arr is None:
            print(f"[ERROR] dump target not found: {args.dump}", file=sys.stderr)
            sys.exit(3)
        if args.out:
            np.save(args.out, arr)
            print(f"[OK] saved {args.dump} -> {args.out} shape={np.asarray(arr).shape}")
        else:
            np.set_printoptions(suppress=True, linewidth=200)
            print(f"{args.dump}:", np.asarray(arr)[:16])

    # --- verification GPU vs CPU ---
    if args.verify:
        # 1) Exécuter le CPU SANS 'dump' pour éviter "dump target not found"
        res_cpu, _ = run_backend(args.axir, "cpu", dump=None, summary=False, repeat=1, bench=False)

        # 2) Récupération "intelligente" d'un tableau côté GPU/CPU
        def _pick_array(res, preferred=None):
            import numpy as _np
            # si array brut
            try:
                arr = _np.asarray(res)
                if not isinstance(res, dict):
                    return arr
            except Exception:
                pass
            # si dict: clé demandée sinon premier gros tableau numérique
            if isinstance(res, dict):
                if preferred and preferred in res:
                    try: return _np.asarray(res[preferred])
                    except Exception: pass
                best = None
                for v in res.values():
                    try:
                        a = _np.asarray(v)
                        if a.dtype.kind in "fi" and a.size > 0:
                            if best is None or a.size > best.size:
                                best = a
                    except Exception:
                        pass
                return best
            return None

        a = _pick_array(res, args.dump)       # GPU
        b = _pick_array(res_cpu, args.dump)   # CPU

        if a is None or b is None:
            print("[verify] ⚠️ Rien à comparer (pas de buffer exploitable).", file=sys.stderr)
            sys.exit(5)
        if a.shape != b.shape:
            print(f"[verify] ❌ Shapes différents: GPU {a.shape} vs CPU {b.shape}", file=sys.stderr)
            sys.exit(6)
        if np.allclose(a, b, rtol=args.rtol, atol=args.atol):
            print(f"[verify] ✅ GPU ≈ CPU (rtol={args.rtol:g}, atol={args.atol:g})")
        else:
            diff = float(np.max(np.abs(a - b)))
            rel  = float(diff / (np.max(np.abs(b)) + 1e-12))
            print(f"[verify] ❌ Diff max = {diff:.3e}  (rel ≈ {rel:.3e}, tol={args.rtol:g})", file=sys.stderr)
            sys.exit(7)

    print("Done.")

if __name__ == "__main__":
    main()
