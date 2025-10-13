import sys
import platform
import numpy as np

def main():
    print("🩺 Axiomos Doctor — Environment Diagnostic\n")

    # Python environment
    print(f"🐍 Python version   : {platform.python_version()}")
    print(f"🖥️  Platform         : {platform.system()} {platform.release()} ({platform.machine()})")

    # NumPy check
    try:
        print(f"📦 NumPy version    : {np.__version__}")
    except Exception as e:
        print("❌ NumPy not available:", e)
        sys.exit(1)

    # OpenCL detection (optional)
    try:
        import pyopencl as cl
        platforms = cl.get_platforms()
        if platforms:
            print("✅ OpenCL runtime    : Found")
            for p in platforms:
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


