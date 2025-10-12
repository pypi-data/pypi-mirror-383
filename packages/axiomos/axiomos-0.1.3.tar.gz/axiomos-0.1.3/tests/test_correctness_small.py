import json, pathlib, numpy as np
from backends.cpu_numpy_backend import run as run_cpu
from backends.opencl_backend import run as run_ocl

def _cmp(ax_path, buf, rtol=1e-6, atol=1e-6):
    ax = json.loads(pathlib.Path(ax_path).read_text(encoding="utf-8"))
    rc = run_cpu(ax, dump=buf); ro = run_ocl(ax, dump=buf)
    a, b = np.asarray(rc["dump"]), np.asarray(ro["dump"])
    assert a.shape == b.shape
    assert np.allclose(a, b, rtol=rtol, atol=atol)

def test_matmul_small():
    _cmp("build/matmul_small.axir.json", "hC")

def test_reduce_sum_small():
    _cmp("build/reduce_sum_from_hip.axir.json", "hOut")
