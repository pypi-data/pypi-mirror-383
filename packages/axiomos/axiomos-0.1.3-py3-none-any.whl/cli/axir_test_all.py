import numpy as np
import sys
import importlib

# Liste des backends à tester
BACKENDS = [
    "Backends.cpu_numpy_backend",
    "Backends.cuda_backend",
    "Backends.hip_glue_backend",
    "Backends.opencl_backend",
    "Backends.gpu_stub_backend",
]

# Liste des kernels et tailles de test
KERNELS = {
    "vector_add": (np.random.rand(1024).astype(np.float32), 
                   np.random.rand(1024).astype(np.float32)),
    "saxpy": (2.0, 
              np.random.rand(1024).astype(np.float32), 
              np.random.rand(1024).astype(np.float32)),
    "reduce_sum": (np.random.rand(1024).astype(np.float32),),
    "matmul": (np.random.rand(64, 64).astype(np.float32), 
               np.random.rand(64, 64).astype(np.float32)),
}

def run_reference(kernel, args):
    if kernel == "vector_add":
        return args[0] + args[1]
    elif kernel == "saxpy":
        return args[0] * args[1] + args[2]
    elif kernel == "reduce_sum":
        return np.sum(args[0])
    elif kernel == "matmul":
        return np.matmul(args[0], args[1])
    else:
        raise ValueError(f"Référence inconnue pour {kernel}")

def main():
    for backend_name in BACKENDS:
        try:
            backend = importlib.import_module(backend_name)
        except ImportError:
            print(f"[WARN] Backend {backend_name} introuvable")
            continue

        print(f"\n=== Test backend: {backend_name} ===")
        for kernel, args in KERNELS.items():
            try:
                # Résultat de référence (NumPy)
                ref = run_reference(kernel, args)

                # Appel kernel via backend (pseudo-API à adapter)
                func = getattr(backend, kernel, None)
                if func is None:
                    print(f"  {kernel}: ✗ (non implémenté)")
                    continue

                out = func(*args)

                # Comparaison tolérante
                if np.allclose(out, ref, atol=1e-5):
                    print(f"  {kernel}: ✓")
                else:
                    print(f"  {kernel}: ✗ (mauvais résultat)")

            except Exception as e:
                print(f"  {kernel}: ✗ ({e})")

if __name__ == "__main__":
    main()
