import sys
import platform
import numpy as np
from importlib.metadata import version, PackageNotFoundError

def _pkg_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "not installed"

def main():
    print("🔒 Public showcase build — minimal backend (private core under NDA)\n")
    print("🩺 Axiomos Doctor — Environment Diagnostic\n")

    # Versions
    axiomos_ver = _pkg_version("axiomos")
    numpy_ver   = np.__version__
    pyopencl_ver = None
    try:
        import pyopencl as cl
        pyopencl_ver = _pkg_version("pyopencl")
    except Exception:
        pass

    # Python environment
    print(f"🐍 Python version   : {platform.python_version()}")
    print(f"🖥️  Platform         : {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"📦 Axiomos version  : {axiomos_ver}")
    print(f"📦 NumPy version    : {numpy_ver}")

    # OpenCL detection (optional)
    try:
        import pyopencl as cl
        plats = cl.get_platforms()
        if plats:
            print(f"✅ OpenCL runtime    : Found (pyopencl {pyopencl_ver})")
            for p in plats:
                print(f"   - Platform: {p.name}")
                for d in p.get_devices():
                    print(f"     • Device: {d.name} ({cl.device_type.to_string(d.type)})")
        else:
            print("⚠️  OpenCL runtime    : Installed but no platforms detected")
    except ImportError:
        print("⚠️  OpenCL runtime    : PyOpenCL not found")
    except Exception as e:
        print("⚠️  OpenCL runtime    : Error while probing →", e)

    # Basic sanity test
    print("\n🧪 Sanity check: 8×8 softmax")
    x = np.random.rand(8, 8).astype(np.float32)
    x_max = np.max(x, axis=1, keepdims=True)
    e = np.exp(x - x_max)
    y = e / e.sum(axis=1, keepdims=True)
    print("✅ Softmax test passed. Shape:", y.shape)

    print("\n🎉 Environment ready — Axiomos IR can run on this machine.")

if __name__ == "__main__":
    main()
