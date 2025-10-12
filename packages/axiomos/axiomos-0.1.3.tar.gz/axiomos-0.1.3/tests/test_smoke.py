import json, pathlib
from backends.cpu_numpy_backend import run as run_cpu

def test_vector_add_small_cpu():
    ax = json.loads(pathlib.Path("build/vector_add_small.axir.json").read_text(encoding="utf-8"))
    r = run_cpu(ax, dump="hC")
    assert "dump" in r
    assert len(r["dump"]) >= 8
