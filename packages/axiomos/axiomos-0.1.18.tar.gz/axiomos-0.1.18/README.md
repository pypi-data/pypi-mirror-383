# AXIOMOS — Public Showcase (Minimal)
[PyPI](https://pypi.org/project/axiomos/) • [GitHub](https://github.com/Aidenkuro10/axiomos-vitrine)  
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

> 🔒 Public showcase build — proves the critical path: **AXIR JSON → CPU/OpenCL execution → numeric verification**.  
> The private core (optimizers, scheduler, advanced kernels, **cryptographic trust**) remains **under NDA**.

---

## 🚀 TL;DR — 3-command demo

### Windows (PowerShell)
```powershell
pip install axiomos; or pip install "axiomos>=0.1.18"
axiomos-doctor
axiomos-demo

# optional
axiomos-devices
axiomos-smoke --size 512 --warmup 3 --repeat 30 --seed 0
macOS / Linux (zsh/bash)

pip install "axiomos>=0.1.18"
axiomos-doctor
axiomos-demo

# optional
axiomos-devices
axiomos-smoke --size 512 --warmup 3 --repeat 30 --seed 0

axiomos-doctor prints versions, attempts OpenCL discovery, and runs a softmax 8×8 sanity test.
axiomos-demo creates a tiny AXIR JSON and verifies CPU ↔ OPENCL.
If OpenCL isn’t available, it falls back to OPENCL(cpu-fallback) and still verifies ALLCLOSE (strict parity).


🆘 If a command is “not recognized” (universal fallback)
Use the module form (bypasses PATH issues and mixed Python installs):

Windows (PowerShell)
python -m pip install -U "axiomos>=0.1.18"
python -m axiomos.cli.axir_doctor
python -m axiomos.cli.quick_demo
python -m axiomos.cli.devices
python -m axiomos.smoke --size 512 --warmup 3 --repeat 30 --seed 0

macOS / Linux (zsh/bash)
python3 -m pip install -U "axiomos>=0.1.18"
python3 -m axiomos.cli.axir_doctor
python3 -m axiomos.cli.quick_demo
python3 -m axiomos.cli.devices
python3 -m axiomos.smoke --size 512 --warmup 3 --repeat 30 --seed 0

On Windows, if you use a virtualenv, activate it first:
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install "axiomos>=0.1.18"
axiomos-doctor
axiomos-demo


🎯 What this proves (public)
Portability — the same .axir.json runs on CPU and OpenCL (or a graceful CPU fallback).

Verifiability — strict numeric parity (ALLCLOSE) with shapes, max_abs_err, timings.

Reproducibility — seedable runs, explicit versions printed.

UX — install → run → verify in minutes; no private code exposed.

Not included here (private): optimizer passes, scheduler, advanced kernels, full operator coverage, vendor-tuned implementations, and the full trust pipeline (content-addressed artifacts, Ed25519 signatures, attestations).
➡️ A full private demo is available under NDA.

🔧 Useful commands
List OpenCL devices (if PyOpenCL + drivers are present)

axiomos-devices
# universal fallback:
python -m axiomos.cli.devices
Verify a fixture (example: Softmax 8×8)
python -m axiomos.verify examples/softmax2d_small.axir.json --buffer hY --backend-a cpu --backend-b opencl --seed 0
Output includes: SHAPES, max_abs_err, ALLCLOSE (atol=1e-6, rtol=1e-5), CPU & OPENCL timings.
Note: the public OpenCL path is minimal (not optimized) — correctness, not performance.

Tiny smoke (latency indicator)
axiomos-smoke --size 512 --warmup 3 --repeat 30 --seed 0
# fallback:
python -m axiomos.smoke --size 512 --warmup 3 --repeat 30 --seed 0

🧪 Optional: PyTorch → AXIR mini-export + verify
Install PyTorch (it’s large; keep optional for demos):
pip install torch
Export a tiny model to AXIR JSON:
axiomos-export-torch
# fallback:

This creates:
examples/pytorch_softmax.axir.json
Verify CPU ↔ OPENCL on the exported AXIR:

python -m axiomos.verify examples/pytorch_softmax.axir.json --buffer hY --backend-a cpu --backend-b opencl --seed 0
As with other demos: if OpenCL isn’t available, verification falls back to OPENCL(cpu-fallback) and still checks numeric parity.

🧰 If you cloned the repo (extra fixtures)
Generate fixtures:

python make_fixtures.py
Creates:
examples/
 ├─ vector_add_small.axir.json
 └─ softmax2d_small.axir.json
Verify:

# CPU ↔ CPU (Hello AXIR)
axiomos-verify examples/vector_add_small.axir.json --buffer hC --backend-a cpu --backend-b cpu --seed 0

# CPU ↔ OpenCL (Softmax 8×8)
python -m axiomos.verify examples/softmax2d_small.axir.json --buffer hY --backend-a cpu --backend-b opencl --seed 0

💡 Common errors & fixes
“Command not found” (e.g., axiomos-devices):
Use module form (works everywhere):
python -m axiomos.cli.devices (Windows) or python3 -m axiomos.cli.devices (macOS/Linux).
On Windows, if using a venv, activate it before running commands.

“No matching distribution found for axiomos”
Python is likely too old. Use Python 3.10+. On macOS:
brew install python@3.11
/opt/homebrew/bin/python3.11 -m venv .venv   # Apple Silicon
# or: /usr/local/bin/python3.11 -m venv .venv # Intel
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
python -m pip install -U "axiomos>=0.1.15"

Apple Silicon arch mismatch (Rosetta vs arm64):
usr/bin/arch -arm64 python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -U "axiomos>=0.1.15"
Corporate proxy / SSL errors:
Configure pip to use your proxy or trusted certs, or install inside a VPN/approved network. (Keep the module form.)

PyTorch install is slow:
That’s expected (large wheels). Keep PyTorch optional for the demo.

Why AXIOMOS
AXIR (Axiomos IR) is a universal, hardware-agnostic IR aimed at:

Portability — compile once, run on CPU, GPU, and accelerators.

Determinism & Reproducibility — numerically verifiable parity across backends.

Trust — measured parity today; cryptographic provenance/signatures in the private build.

Longevity — a stable IR beyond today’s frameworks and vendor APIs.

This public showcase is intentionally minimal: it proves AXIR JSON → multi-backend execution → verification without exposing the private core.

License
MIT (public showcase only). The full runtime remains proprietary.