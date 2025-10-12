# tests/test_verify_gpu_vs_cpu.py
import json, pathlib, importlib
import numpy as np
import pytest

# --- petits helpers ---
def has_opencl():
    try:
        import pyopencl as cl  # noqa
        return len(cl.get_platforms()) > 0
    except Exception:
        return False

# On importe la fonction run_backend depuis la CLI (elle n’exécute pas main() à l’import)
axir_run = importlib.import_module("cli.axir_run")
run_backend = axir_run.run_backend

def load_axir_path(name):
    p = pathlib.Path("build") / name
    assert p.exists(), f"AXIR not found: {p}"
    return str(p)

def compare_cpu_opencl(axir_file, dump_name, rtol=1e-6, atol=1e-6):
    # GPU/OpenCL
    res_gpu, _ = run_backend(axir_file, "opencl", dump=dump_name, summary=False, repeat=1, bench=False)
    # CPU
    res_cpu, _ = run_backend(axir_file, "cpu", dump=dump_name, summary=False, repeat=1, bench=False)

    a = np.asarray(res_gpu.get("dump"))
    b = np.asarray(res_cpu.get("dump"))
    assert a is not None and b is not None, "dump manquant"
    assert a.shape == b.shape, f"shapes differ: GPU {a.shape} vs CPU {b.shape}"

    ok = np.allclose(a, b, rtol=rtol, atol=atol)
    if not ok:
        diff = np.max(np.abs(a - b))
        rel  = diff / (np.max(np.abs(b)) + 1e-12)
        pytest.fail(f"not close: diff={diff:.3e}, rel={rel:.3e}, rtol={rtol}, atol={atol}")

# --- tests ---

@pytest.mark.skipif(not has_opencl(), reason="OpenCL not available")
def test_vector_add_small_gpu_matches_cpu():
    ax = load_axir_path("vector_add_small.axir.json")
    compare_cpu_opencl(ax, "hC")

@pytest.mark.skipif(not has_opencl(), reason="OpenCL not available")
def test_reduce_sum_big_gpu_matches_cpu():
    ax = load_axir_path("reduce_sum_big.axir.json")
    compare_cpu_opencl(ax, "hOut", rtol=0, atol=0)  # somme exacte attendue ici

@pytest.mark.skipif(not has_opencl(), reason="OpenCL not available")
def test_matmul_small_gpu_matches_cpu():
    ax = load_axir_path("matmul_small.axir.json")
    # tolérance un peu plus large si kernel tiled/fast-math actif
    compare_cpu_opencl(ax, "hC", rtol=1e-5, atol=1e-5)

# Optionnel : softmax2d_small (résultats normalisés, petite tolérance)
@pytest.mark.skipif(not has_opencl(), reason="OpenCL not available")
def test_softmax2d_small_gpu_matches_cpu():
    ax = load_axir_path("softmax2d_small.axir.json")
    compare_cpu_opencl(ax, "hY", rtol=1e-6, atol=1e-6)
