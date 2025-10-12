# tests/test_correctness.py
import os, pytest, numpy as np

cpu = pytest.importorskip("backends.cpu_numpy_backend")
try:
    import pyopencl as cl  # noqa
    ocl = __import__("backends.opencl_backend", fromlist=["run"])
    HAVE_OCL = len(cl.get_platforms()) > 0
except Exception:
    HAVE_OCL = False

def axir_vector_add(N=1_000):
    return {
        "types": {
            "scalars": {"N": {"dtype": "i32", "value": N}},
            "buffers": {"hA": {"dtype": "f32"}, "hB": {"dtype": "f32"}, "hC": {"dtype": "f32"}},
        },
        "ops": [
            {"op": "DeviceMalloc", "dst": "dA", "bytes": "N*sizeof(float)"},
            {"op": "DeviceMalloc", "dst": "dB", "bytes": "N*sizeof(float)"},
            {"op": "DeviceMalloc", "dst": "dC", "bytes": "N*sizeof(float)"},
            {"op": "Memcpy", "kind": "H2D", "src": "hA", "dst": "dA", "bytes": "N*sizeof(float)"},
            {"op": "Memcpy", "kind": "H2D", "src": "hB", "dst": "dB", "bytes": "N*sizeof(float)"},
            {"op": "KernelLaunch", "kernel": "vector_add", "args": ["dA","dB","dC","N"]},
            {"op": "Memcpy", "kind": "D2H", "src": "dC", "dst": "hC", "bytes": "N*sizeof(float)"},
        ],
    }

def axir_matmul(M=64, N=64, K=64):
    return {
        "types": {
            "scalars": {"M": {"dtype":"i32","value":M},
                        "N": {"dtype":"i32","value":N},
                        "K": {"dtype":"i32","value":K}},
            "buffers": {"hC": {"dtype":"f32"}},
        },
        "ops": [
            {"op":"DeviceMalloc","dst":"dA","bytes":"M*K*sizeof(float)"},
            {"op":"DeviceMalloc","dst":"dB","bytes":"K*N*sizeof(float)"},
            {"op":"DeviceMalloc","dst":"dC","bytes":"M*N*sizeof(float)"},
            {"op":"KernelLaunch","kernel":"matmul","args":["dA","dB","dC","M","N","K"]},
            {"op":"Memcpy","kind":"D2H","src":"dC","dst":"hC","bytes":"M*N*sizeof(float)"},
        ],
    }

def axir_softmax(M=128, N=256):
    return {
        "types": {
            "scalars": {"M":{"dtype":"i32","value":M}, "N":{"dtype":"i32","value":N}},
            "buffers": {"hY": {"dtype":"f32"}},
        },
        "ops": [
            {"op":"DeviceMalloc","dst":"dX","bytes":"M*N*sizeof(float)"},
            {"op":"DeviceMalloc","dst":"dY","bytes":"M*N*sizeof(float)"},
            {"op":"KernelLaunch","kernel":"softmax2d","args":["dX","dY","M","N"]},
            {"op":"Memcpy","kind":"D2H","src":"dY","dst":"hY","bytes":"M*N*sizeof(float)"},
        ],
    }

@pytest.mark.parametrize("builder,name", [
    (axir_vector_add, "hC"),
    (axir_matmul,     "hC"),
    (axir_softmax,    "hY"),
])
def test_cpu_vs_opencl_allclose(builder, name):
    ax = builder()
    # CPU
    res_cpu = cpu.run(ax, dump=name)
    a_cpu = np.asarray(res_cpu["dump"]).copy()
    # OpenCL (skip si pas dispo)
    if not HAVE_OCL:
        pytest.skip("OpenCL non disponible")
    res_ocl = ocl.run(ax, dump=name)
    a_ocl = np.asarray(res_ocl["dump"]).copy()
    # Si softmax: normaliser forme 2D quand on peut
    scal = ax.get("types",{}).get("scalars",{})
    M = int((scal.get("M",{}) or {}).get("value",0) or 0)
    N = int((scal.get("N",{}) or {}).get("value",0) or 0)
    if name == "hY" and M>0 and N>0 and a_cpu.size==M*N and a_ocl.size==M*N:
        a_cpu = a_cpu.reshape(M,N)
        a_ocl = a_ocl.reshape(M,N)
    np.testing.assert_allclose(a_cpu, a_ocl, rtol=1e-5, atol=1e-5)
