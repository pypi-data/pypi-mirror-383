[![CI](https://github.com/Aidenkuro10/axiomos/actions/workflows/ci.yml/badge.svg)](https://github.com/Aidenkuro10/axiomos/actions/workflows/ci.yml)

# AXIOMOS

**AXIOMOS** is a lightweight playground for describing and running numerical kernels (vector ops, softmax, GEMM…) through a unified IR called **AXIR**, portable across **CPU** and **OpenCL GPU** backends.

- ✅ Runs simple compute graphs described in `.axir.json`
- ✅ Verifies numerical correctness across backends
- ✅ Includes CLI tools, benchmarks, and profiling utilities

---

## 🚀 Quick Start (90 s)

### 1. Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
2. Run environment check
powershell
Copier le code
axiomos-doctor
You should see ✅ if your CPU or OpenCL backend is detected.

3. Try a demo
CPU-only:

powershell
Copier le code
$env:AXIOMOS_OCL_REAL="0"
axiomos-demo
Real OpenCL device:

powershell
Copier le code
$env:AXIOMOS_OCL_REAL="1"
axiomos-demo
4. Verify a computation
Compare CPU vs OpenCL on a buffer:

powershell
Copier le code
axiomos-verify build\matmul_512.axir.json --buffer hC
📚 Full documentation & advanced usage (device selection, environment variables, GEMM tuning, troubleshooting, etc.):
👉 docs/QUICKSTART.md

📁 Project layout
csharp
Copier le code
backends/      # CPU & OpenCL backends
cli/           # Command-line tools (verify, doctor, demo…)
build/         # AXIR fixtures (vector, saxpy, softmax, matmul…)
scripts/       # Utilities (device list, tuning, profiling…)
📜 License
MIT – Early-stage MVP focused on correctness and developer experience. Performance optimizations come next.## 📘 Quickstart

Consultez l’index : [docs/QUICKSTART.md](./docs/QUICKSTART.md)
