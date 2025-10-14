import sys
import platform

def main():
    print("🔎 AXIOMOS Devices — OpenCL enumeration\n")
    try:
        import pyopencl as cl
    except ImportError:
        print("PyOpenCL not found. Install with: pip install \"axiomos[opencl]\"")
        sys.exit(1)
    except Exception as e:
        print("OpenCL probe error:", e)
        sys.exit(2)

    try:
        platforms = cl.get_platforms()
    except Exception as e:
        print("No OpenCL platforms detected or probe failed:", e)
        sys.exit(3)

    if not platforms:
        print("No OpenCL platforms detected.")
        sys.exit(4)

    for p in platforms:
        print(f"• Platform: {p.name}")
        for d in p.get_devices():
            dtype = cl.device_type.to_string(d.type)
            print(f"  - Device: {d.name} ({dtype})")

if __name__ == "__main__":
    main()
