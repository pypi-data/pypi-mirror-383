#!/usr/bin/env python3
# axirc.py — CLI de démonstration AXIR (build/run) avec CUDA/OpenCL optionnels
import argparse
import json
import importlib.util
import pathlib
import subprocess
import sys
import textwrap
import time

# Racine du repo (présumé : ce fichier est dans cli/)
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD_DIR = REPO_ROOT / "build"

# Mapping des backends -> chemins de scripts
BACKEND_SCRIPTS = {
    "cpu": REPO_ROOT / "backends" / "cpu_numpy_backend.py",
    "gpu-stub": REPO_ROOT / "backends" / "gpu_stub_backend.py",
    "cuda": REPO_ROOT / "backends" / "cuda_backend.py",            # backend CUDA réel
    "cuda-glue": REPO_ROOT / "backends" / "cuda_glue_backend.py",  # ancien glue (optionnel)
    "hip": REPO_ROOT / "backends" / "hip_glue_backend.py",
    "opencl": REPO_ROOT / "backends" / "opencl_backend.py",
}

# -----------------------------
# Utils d'affichage / d'IO
# -----------------------------
def print_rule(title: str):
    print()
    print(title)
    print("-" * len(title))

def sprint(s: str, n: int = 30) -> str:
    s = s.rstrip("\n")
    lines = s.splitlines()
    if len(lines) > n:
        lines = lines[:n] + ["  ... [truncated] ..."]
    return "\n".join(lines)

def ensure_build_dir():
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

def write_json(p: pathlib.Path, obj):
    p.write_text(json.dumps(obj, indent=2), encoding="utf-8")

def read_json(p: pathlib.Path):
    return json.loads(p.read_text(encoding="utf-8"))

def resolve_backend_script(name: str) -> pathlib.Path:
    path = BACKEND_SCRIPTS.get(name)
    if not path:
        raise SystemExit(f"[axirc] backend inconnu: {name}")
    print(f"[axirc] resolved backend script: {path}")
    return path

def run_backend(label: str, script_path: pathlib.Path, axir_path: pathlib.Path, summary=False, extra_args=None):
    print_rule(f"AXIR → {label}")
    t0 = time.time()
    cmd = [sys.executable, str(script_path), str(axir_path)]
    if summary:
        cmd.append("--summary")
    if extra_args:
        cmd += list(extra_args)

    out = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
    dt_ms = (time.time() - t0) * 1000.0
    print(f"  ({dt_ms:.1f} ms)")
    print("-" * 22)
    if out.stdout:
        print(sprint(out.stdout, 200))
    if out.returncode != 0:
        if out.stderr:
            print(out.stderr)
        print(f"❌ Backend {label} a retourné rc={out.returncode}")
    return out.returncode == 0

# -----------------------------
# Détection CUDA / OpenCL
# -----------------------------
def _cuda_available() -> bool:
    try:
        if importlib.util.find_spec("cupy") is None:
            return False
        import cupy
        return cupy.cuda.runtime.getDeviceCount() > 0
    except Exception:
        return False

def _opencl_available() -> bool:
    try:
        import pyopencl as cl
        return len(cl.get_platforms()) > 0
    except Exception:
        return False

def _opencl_devices():
    try:
        import pyopencl as cl
        out = []
        for p in cl.get_platforms():
            out.append((p.name, [d.name for d in p.get_devices()]))
        return out
    except Exception:
        return []

def _cuda_devices():
    try:
        import cupy
        n = cupy.cuda.runtime.getDeviceCount()
        names = []
        for i in range(n):
            props = cupy.cuda.runtime.getDeviceProperties(i)
            names.append(props["name"].decode() if isinstance(props["name"], bytes) else props["name"])
        return names
    except Exception:
        return []

def cmd_device_list(_args):
    print_rule("AXIR Device List")
    print("CPU        : available")

    ocl = _opencl_devices()
    if ocl:
        for plat, devs in ocl:
            print(f"OpenCL     : {plat} -> {', '.join(devs)}")
    else:
        print("OpenCL     : none")

    cuda = _cuda_devices()
    if cuda:
        print(f"CUDA       : {', '.join(cuda)}")
    else:
        print("CUDA       : none")

# ------------------------------------------------
# "Frontends" jouets -> génération d'AXIR JSON
# ------------------------------------------------
CUDA_SOURCES = {
    "vector_add": textwrap.dedent("""\
        #include <cuda_runtime.h>

        __global__ void vector_add(const float* A, const float* B, float* C, int N) {
            int i = threadIdx.x;
            if (i < N) C[i] = A[i] + B[i];
        }

        int main() {
            float *dA, *dB, *dC;
            int N = 16;
            cudaMalloc(&dA, N * sizeof(float));
            cudaMalloc(&dB, N * sizeof(float));
            cudaMalloc(&dC, N * sizeof(float));

            float *hA, *hB, *hC; // (hôte)
            cudaMemcpy(dA, hA, N * sizeof(float), cudaMemcpyHostToDevice);
            cudaMemcpy(dB, hB, N * sizeof(float), cudaMemcpyHostToDevice);

            vector_add<<<1, N>>>(dA, dB, dC, N);
            cudaMemcpy(hC, dC, N * sizeof(float), cudaMemcpyDeviceToHost);
            return 0;
        }
    """),
    "saxpy": textwrap.dedent("""\
        #include <cuda_runtime.h>

        __global__ void saxpy(const float* A, const float* B, float* C, float alpha, int N) {
            int i = threadIdx.x;
            if (i < N) C[i] = alpha * A[i] + B[i];
        }

        int main() {
            float *dA, *dB, *dC; float alpha=2.0f; int N=16;
            cudaMalloc(&dA, N*sizeof(float));
            cudaMalloc(&dB, N*sizeof(float));
            cudaMalloc(&dC, N*sizeof(float));
            float *hA, *hB, *hC;
            cudaMemcpy(dA, hA, N*sizeof(float), cudaMemcpyHostToDevice);
            cudaMemcpy(dB, hB, N*sizeof(float), cudaMemcpyHostToDevice);
            saxpy<<<1, N>>>(dA, dB, dC, alpha, N);
            cudaMemcpy(hC, dC, N*sizeof(float), cudaMemcpyDeviceToHost);
            return 0;
        }
    """),
    "reduce_sum": textwrap.dedent("""\
        #include <cuda_runtime.h>
        __global__ void reduce_sum(const float* A, float* Out, int N) { /* demo kernel */ }
        int main() {
            float *dA, *dOut; int N=16;
            cudaMalloc(&dA, N*sizeof(float)); cudaMalloc(&dOut, sizeof(float));
            float *hA, *hOut;
            cudaMemcpy(dA, hA, N*sizeof(float), cudaMemcpyHostToDevice);
            reduce_sum<<<1, N>>>(dA, dOut, N);
            cudaMemcpy(hOut, dOut, sizeof(float), cudaMemcpyDeviceToHost);
            return 0;
        }
    """),
}

HIP_SOURCES = {
    "vector_add": textwrap.dedent("""\
        #include <hip/hip_runtime.h>

        __global__ void vector_add(const float* A, const float* B, float* C, int N) {
            int i = threadIdx.x;
            if (i < N) C[i] = A[i] + B[i];
        }

        int main() {
            float *dA, *dB, *dC;
            int N = 16;
            hipMalloc(&dA, N*sizeof(float));
            hipMalloc(&dB, N*sizeof(float));
            hipMalloc(&dC, N*sizeof(float));
            float *hA, *hB, *hC;
            hipMemcpy(dA, hA, N*sizeof(float), hipMemcpyHostToDevice);
            hipMemcpy(dB, hB, N*sizeof(float), hipMemcpyHostToDevice);
            hipLaunchKernelGGL(vector_add, dim3(1,1,1), dim3(N,1,1), 0, 0, dA, dB, dC, N);
            hipMemcpy(hC, dC, N*sizeof(float), hipMemcpyDeviceToHost);
            return 0;
        }
    """),
    "saxpy": textwrap.dedent("""\
        #include <hip/hip_runtime.h>

        __global__ void saxpy(const float* A, const float* B, float* C, float alpha, int N) {
            int i = threadIdx.x;
            if (i < N) C[i] = alpha * A[i] + B[i];
        }

        int main() {
            float *dA, *dB, *dC; float alpha=2.0f; int N=16;
            hipMalloc(&dA, N*sizeof(float));
            hipMalloc(&dB, N*sizeof(float));
            hipMalloc(&dC, N*sizeof(float));
            float *hA, *hB, *hC;
            hipMemcpy(dA, hA, N*sizeof(float), hipMemcpyHostToDevice);
            hipMemcpy(dB, hB, N*sizeof(float), hipMemcpyHostToDevice);
            hipLaunchKernelGGL(saxpy, dim3(1,1,1), dim3(N,1,1), 0, 0, dA, dB, dC, alpha, N);
            hipMemcpy(hC, dC, N*sizeof(float), hipMemcpyDeviceToHost);
            return 0;
        }
    """),
    "reduce_sum": textwrap.dedent("""\
        #include <hip/hip_runtime.h>
        __global__ void reduce_sum(const float* A, float* Out, int N) { /* see note above */ }
        int main() {
            float *dA, *dOut; int N=16;
            hipMalloc(&dA, N*sizeof(float)); hipMalloc(&dOut, sizeof(float));
            float *hA, *hOut;
            hipMemcpy(dA, hA, N*sizeof(float), hipMemcpyHostToDevice);
            hipLaunchKernelGGL(reduce_sum, dim3(1,1,1), dim3(N,1,1), 0, 0, dA, dOut, N);
            hipMemcpy(hOut, dOut, sizeof(float), hipMemcpyDeviceToHost);
            return 0;
        }
    """),
}

def axir_for_kernel(frontend: str, kernel: str):
    if frontend.lower() == "cuda":
        src = CUDA_SOURCES.get(kernel, "")
        source_lang = "CUDA"
    elif frontend.lower() == "hip":
        src = HIP_SOURCES.get(kernel, "")
        source_lang = "HIP"
    else:
        raise SystemExit(f"[axirc] frontend inconnu: {frontend}")

    # Fabriquer un AXIR jouet cohérent avec nos backends
    if kernel == "vector_add":
        ops = [
            {"op": "DeviceSelect", "device": "auto"},
            {"op": "DeviceMalloc", "dst": "&dA", "bytes": "N * sizeof(float"},
            {"op": "DeviceMalloc", "dst": "&dB", "bytes": "N * sizeof(float"},
            {"op": "DeviceMalloc", "dst": "&dC", "bytes": "N * sizeof(float"},
            {"op": "Memcpy", "dst": "dA", "src": "hA", "bytes": "N * sizeof(float)", "kind": "H2D"},
            {"op": "Memcpy", "dst": "dB", "src": "hB", "bytes": "N * sizeof(float)", "kind": "H2D"},
            {"op": "KernelLaunch", "kernel": "vector_add",
             "grid": ["1", "1", "1"], "block": ["N", "1", "1"], "args": ["dA","dB","dC","N"]},
            {"op": "Memcpy", "dst": "hC", "src": "dC", "bytes": "N * sizeof(float)", "kind": "D2H"},
        ]
        types = {"scalars": {"N": {"value": 16}},
                 "buffers": {"hA":{"dtype":"f32"}, "hB":{"dtype":"f32"}, "hC":{"dtype":"f32"},
                             "dA":{"dtype":"f32"}, "dB":{"dtype":"f32"}, "dC":{"dtype":"f32"}}}
    elif kernel == "saxpy":
        ops = [
            {"op": "DeviceSelect", "device": "auto"},
            {"op": "DeviceMalloc", "dst": "&dA", "bytes": "N*sizeof(float"},
            {"op": "DeviceMalloc", "dst": "&dB", "bytes": "N*sizeof(float"},
            {"op": "DeviceMalloc", "dst": "&dC", "bytes": "N*sizeof(float"},
            {"op": "Memcpy", "dst": "dA", "src": "hA", "bytes": "N*sizeof(float)", "kind": "H2D"},
            {"op": "Memcpy", "dst": "dB", "src": "hB", "bytes": "N*sizeof(float)", "kind": "H2D"},
            {"op": "KernelLaunch", "kernel": "saxpy",
             "grid": ["1","1","1"], "block": ["N","1","1"], "args": ["dA","dB","dC","2.0","N"]},
            {"op": "Memcpy", "dst": "hC", "src": "dC", "bytes": "N*sizeof(float)", "kind": "D2H"},
        ]
        types = {"scalars": {"N": {"value": 16}},
                 "buffers": {"hA":{"dtype":"f32"}, "hB":{"dtype":"f32"}, "hC":{"dtype":"f32"},
                             "dA":{"dtype":"f32"}, "dB":{"dtype":"f32"}, "dC":{"dtype":"f32"}}}
    elif kernel == "reduce_sum":
        ops = [
            {"op": "DeviceSelect", "device": "auto"},
            {"op": "DeviceMalloc", "dst": "&dA", "bytes": "N*sizeof(float"},
            {"op": "DeviceMalloc", "dst": "&dOut", "bytes": "sizeof(float"},
            {"op": "Memcpy", "dst": "dA", "src": "hA", "bytes": "N*sizeof(float)", "kind": "H2D"},
            {"op": "KernelLaunch", "kernel": "reduce_sum",
             "grid": ["1","1","1"], "block": ["N","1","1"], "args": ["dA","dOut","N"]},
            {"op": "Memcpy", "dst": "hOut", "src": "dOut", "bytes": "sizeof(float)", "kind": "D2H"},
        ]
        types = {"scalars": {"N": {"value": 16}},
                 "buffers": {"hA":{"dtype":"f32"}, "hOut":{"dtype":"f32"},
                             "dA":{"dtype":"f32"}, "dOut":{"dtype":"f32"}}}
    elif kernel == "matmul":
        ops = [
            {"op":"DeviceSelect","device":"auto"},
            {"op":"DeviceMalloc","dst":"&dA","bytes":"M*K*4"},
            {"op":"DeviceMalloc","dst":"&dB","bytes":"K*N*4"},
            {"op":"DeviceMalloc","dst":"&dC","bytes":"M*N*4"},
            {"op":"Memcpy","dst":"&dA","src":"&hA","bytes":"M*K*4","kind":"H2D"},
            {"op":"Memcpy","dst":"&dB","src":"&hB","bytes":"K*N*4","kind":"H2D"},
            {"op":"KernelLaunch","kernel":"matmul",
             "grid":["M","N","1"],"block":["1","1","1"],"args":["dA","dB","dC","M","N","K"]},
            {"op":"Memcpy","dst":"&hC","src":"&dC","bytes":"M*N*4","kind":"D2H"},
        ]
        types = {"scalars":{"M":{"value":2},"N":{"value":2},"K":{"value":2}},
                 "buffers":{"hA":{"dtype":"f32"},"hB":{"dtype":"f32"},"hC":{"dtype":"f32"},
                            "dA":{"dtype":"f32"},"dB":{"dtype":"f32"},"dC":{"dtype":"f32"}}}
    else:
        raise SystemExit(f"[axirc] kernel inconnu: {kernel}")

    axir = {"version": "0.2", "meta": {"source_lang": source_lang}, "types": types, "ops": ops}
    return src, axir

def show_source(title, code):
    print_rule(title)
    print(sprint(textwrap.indent(code, "  "), 40))

def show_axir_excerpt(title, axir_path):
    print_rule(title)
    txt = pathlib.Path(axir_path).read_text(encoding="utf-8")
    print("  " + sprint(txt, 40).replace("\n", "\n  "))

# -----------------------------
# Helpers target -> backend
# -----------------------------
def _target_to_backend(target: str) -> str:
    """
    Mappe un --target (cpu|intel|amd|nvidia|auto) vers un backend concret.
    - intel/amd -> opencl (dans ce PoC)
    - nvidia     -> cuda (si dispo) sinon opencl si dispo sinon cpu
    - auto       -> cuda si dispo sinon opencl si dispo sinon cpu
    """
    t = target.lower()
    if t == "cpu":
        return "cpu"
    if t in ("intel", "amd"):
        return "opencl"
    if t == "nvidia":
        if _cuda_available():
            return "cuda"
        return "opencl" if _opencl_available() else "cpu"
    if t == "auto":
        if _cuda_available():
            return "cuda"
        return "opencl" if _opencl_available() else "cpu"
    # fallback prudent
    return "cpu"

# -----------------------------
# Commandes CLI
# -----------------------------
def cmd_demo(args):
    ensure_build_dir()

    kernel = args.kernel
    frontend = args.frontend

    print_rule("AXIR Demo — Universal IR in action")
    print(f"Kernel: {kernel} | Frontend: {frontend}")
    print(f"Build dir: {BUILD_DIR}")

    # 1) Frontend -> AXIR
    t0 = time.time()
    src, ax = axir_for_kernel(frontend, kernel)
    axir_name = f"{kernel}_from_{frontend}.axir.json"
    axir_path = BUILD_DIR / axir_name
    write_json(axir_path, ax)
    dt_ms = (time.time() - t0) * 1000.0
    print_rule(f"Frontend {frontend} → AXIR  [{kernel}]  ({dt_ms:.1f} ms)")
    print(f"  [OK] AXIR written: {axir_path}")

    # 2) Afficher la source et un extrait AXIR
    show_source(f"Source — {kernel}.{('cu' if frontend=='cuda' else 'hip.cpp')}", src)
    show_axir_excerpt(f"Extrait AXIR JSON — {axir_path.name}", axir_path)

    # 3) Exécuter sur CPU et GPU-stub, toujours
    ok_cpu  = run_backend("cpu", resolve_backend_script("cpu"), axir_path, summary=True)
    ok_stub = run_backend("gpu-stub", resolve_backend_script("gpu-stub"), axir_path, summary=True)

    # 4) Optionnel: OpenCL (GPU réel si dispo)
    ok_ocl = True
    if args.with_opencl:
        ok_ocl = run_backend("opencl", resolve_backend_script("opencl"), axir_path, summary=True)

    # 5) Optionnel: CUDA réel (peut être absent)
    ok_cuda = True  # par défaut True si non demandé
    if args.with_cuda:
        if _cuda_available():
            ok_cuda = run_backend("cuda", resolve_backend_script("cuda"), axir_path, summary=True)
        else:
            if args.allow_missing_cuda:
                print("[axirc] CUDA demandé mais non disponible -> on l'ignore (allow-missing-cuda).")
                ok_cuda = True
            else:
                print("[axirc] CUDA demandé mais non disponible -> on saute le backend CUDA réel")
                ok_cuda = False

    # 6) Conclusion
    success = (
        ok_cpu and ok_stub
        and (not args.with_opencl or ok_ocl)
        and (not args.with_cuda or ok_cuda)
    )

    if success:
        suffix = ["CPU", "GPU-stub"]
        if args.with_opencl: suffix.append("OpenCL")
        if args.with_cuda:
            suffix.append("CUDA" if ok_cuda else "CUDA (absent)")
        print(f"\n✅ Démo réussie (frontend→AXIR→{' & '.join(suffix)}).")
    else:
        print("\n⚠️  Démo partielle (au moins un backend a échoué).")

def cmd_run(args):
    """Exécuter un AXIR existant sur un target logique + (optionnel) vérifier CPU vs target."""
    axir_path = pathlib.Path(args.axir).resolve()
    if not axir_path.exists():
        raise SystemExit(f"[axirc] introuvable: {axir_path}")

    target = args.target.lower()
    backend = _target_to_backend(target)

    print_rule("AXIR Run")
    print(f"Fichier : {axir_path.name}")
    print(f"Target  : {target}  -> backend: {backend}")

    # Avertissements utiles
    if backend == "cuda" and not _cuda_available():
        print("[axirc] Attention: CUDA demandé mais non disponible sur cette machine. Fallback impossible pour --run.")
    if backend == "opencl" and not _opencl_available():
        print("[axirc] Attention: OpenCL indisponible. Fallback impossible pour --run.")

    be_path = resolve_backend_script(backend)
    ok = run_backend(backend, be_path, axir_path, summary=args.summary)

    if not ok:
        print(f"\n❌ Run {backend} échec.")
        return

    print(f"\n✅ Run {backend} OK.")

    # --verify : comparer CPU vs target (pour OpenCL c'est natif via verify_axir.py)
    if args.verify:
        # Heuristique du buffer si non précisé
        buffer_name = args.buffer
        if not buffer_name:
            # détection simple à partir du nom de fichier
            name = axir_path.name.lower()
            buffer_name = "hOut" if "reduce_sum" in name else "hC"

        if backend == "opencl":
            # réutilise le script de vérification existant (CPU vs OCL)
            script = REPO_ROOT / "cli" / "verify_axir.py"
            if script.exists():
                print_rule("VERIFY (CPU vs OpenCL)")
                cmd = [sys.executable, str(script), str(axir_path), "--buffer", buffer_name]
                out = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
                if out.stdout:
                    print(out.stdout)
                if out.returncode != 0:
                    if out.stderr: print(out.stderr)
                    print("❌ VERIFY a échoué.")
                else:
                    print("✅ VERIFY OK.")
            else:
                print("[axirc] verify_axir.py introuvable, vérification sautée.")
        elif backend == "cuda":
            # placeholder simple : on relance CPU + affiche un message (PoC)
            print_rule("VERIFY (simplifié)")
            print("Pour CUDA réel, ajoute un verify dédié CPU vs CUDA. (PoC : non implémenté ici)")
        else:
            print_rule("VERIFY")
            print("Vérification CPU vs CPU inutile (même backend).")

def cmd_demo_prebaked(args):
    """Démos à partir d’AXIR déjà fourni (ex: matmul.axir.json)."""
    ensure_build_dir()
    kernel = args.kernel
    src_title = f"{kernel}.axir.json"
    # Fichier AXIR "pré-baked" attendu dans repo/assets ou build
    prebaked = REPO_ROOT / "assets" / f"{kernel}.axir.json"
    if not prebaked.exists():
        prebaked = REPO_ROOT / "build" / f"{kernel}.axir.json"
    if not prebaked.exists():
        raise SystemExit(f"[axirc] AXIR prebaked introuvable: {prebaked}")

    print_rule("AXIR Demo (prebaked) — AXIR → backends")
    print(f"Kernel: {kernel} | From: axir")

    show_axir_excerpt(f"Extrait AXIR JSON — {src_title}", prebaked)

    ok_cpu  = run_backend("cpu", resolve_backend_script("cpu"), prebaked, summary=True)
    ok_stub = run_backend("gpu-stub", resolve_backend_script("gpu-stub"), prebaked, summary=True)

    ok_cuda = True
    if args.with_cuda:
        if _cuda_available():
            ok_cuda = run_backend("cuda", resolve_backend_script("cuda"), prebaked, summary=True)
        else:
            print("[axirc] CUDA demandé mais non disponible -> on saute le backend CUDA réel")
            ok_cuda = False

    ok_ocl = True
    if args.with_opencl:
        ok_ocl = run_backend("opencl", resolve_backend_script("opencl"), prebaked, summary=True)

    success = (
        ok_cpu and ok_stub
        and (not args.with_cuda or ok_cuda)
        and (not args.with_opencl or ok_ocl)
    )

    suffix = ["CPU", "GPU-stub"]
    if args.with_cuda and ok_cuda:
        suffix.append("CUDA")
    if args.with_opencl and ok_ocl:
        suffix.append("OpenCL")

    if success:
        print(f"\n✅ Démo prébaked réussie (AXIR→{' & '.join(suffix)}).")
    else:
        print("\n⚠️  Démo prébaked partielle.")

# -----------------------------
# Entrée principale
# -----------------------------
def main():
    ap = argparse.ArgumentParser(prog="axirc", description="AXIR CLI — demos & runs")
    sp = ap.add_subparsers(dest="cmd")

    # device-list
    p_list = sp.add_parser("device-list", help="Liste les devices détectés (CPU/OpenCL/CUDA)")
    p_list.set_defaults(func=cmd_device_list)

    # demo
    p_demo = sp.add_parser("demo", help="Génère AXIR depuis un frontend jouet et exécute les backends")
    p_demo.add_argument("--kernel", required=True, choices=["vector_add", "saxpy", "reduce_sum", "matmul"])
    p_demo.add_argument("--frontend", required=True, choices=["cuda", "hip"])
    p_demo.add_argument("--summary", action="store_true")
    p_demo.add_argument("--with-opencl", action="store_true", help="Exécuter aussi le backend OpenCL réel")
    p_demo.add_argument("--with-cuda", action="store_true", help="Exécuter aussi le backend CUDA réel (si device dispo)")
    p_demo.add_argument("--allow-missing-cuda", action="store_true",
                        help="Ne pas échouer si CUDA est demandé mais indisponible")
    p_demo.set_defaults(func=cmd_demo)

    # demo-prebaked
    p_pre = sp.add_parser("demo-prebaked", help="Exécute des AXIR déjà fournis (ex: matmul)")
    p_pre.add_argument("--kernel", required=True, choices=["matmul", "vector_add", "saxpy", "reduce_sum"])
    p_pre.add_argument("--summary", action="store_true")
    p_pre.add_argument("--with-opencl", action="store_true")
    p_pre.add_argument("--with-cuda", action="store_true")
    p_pre.set_defaults(func=cmd_demo_prebaked)

    # run
    p_run = sp.add_parser("run", help="Exécute un AXIR existant sur une cible et (optionnel) vérifie")
    p_run.add_argument("--axir", required=True, help="Chemin vers le JSON AXIR")
    p_run.add_argument("--target", required=True, choices=["cpu","intel","amd","nvidia","auto"],
                       help="Cible logique (cpu|intel|amd|nvidia|auto)")
    p_run.add_argument("--summary", action="store_true")
    p_run.add_argument("--verify", action="store_true", help="Compare CPU vs target (OpenCL supporté via verify_axir.py)")
    p_run.add_argument("--buffer", help="Nom du buffer à comparer (défaut: hC, ou hOut si reduce_sum)")
    p_run.set_defaults(func=cmd_run)

    args = ap.parse_args()
    if not hasattr(args, "func"):
        ap.print_help()
        sys.exit(1)
    args.func(args)

if __name__ == "__main__":
    main()
