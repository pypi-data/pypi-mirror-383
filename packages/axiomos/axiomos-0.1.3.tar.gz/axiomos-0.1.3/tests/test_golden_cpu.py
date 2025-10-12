import subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
VERIFY = "axiomos-verify"  # via console_scripts

def run_ok(args):
    print("Running:", " ".join(args))
    p = subprocess.run(args, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(p.stdout)
    assert p.returncode == 0

def test_add_64k_cpu_cpu():
    run_ok([VERIFY, "AXIR/_golden/add_64k.axir.json", "--backend-a", "cpu", "--backend-b", "cpu", "--buffer", "hA", "--repeat", "2"])

def test_matmul_128_cpu_cpu():
    run_ok([VERIFY, "AXIR/_golden/matmul_128.axir.json", "--backend-a", "cpu", "--backend-b", "cpu", "--buffer", "hC", "--warmup", "1", "--repeat", "3"])
