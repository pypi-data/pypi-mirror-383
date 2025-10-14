import numpy as np

try:
    import pyopencl as cl
    _PYOPENCL_OK = True
except Exception:
    _PYOPENCL_OK = False

KERNELS = r"""
__kernel void vec_add(__global const float* A,
                      __global const float* B,
                      __global float* C,
                      const int n) {
    int i = get_global_id(0);
    if (i < n) C[i] = A[i] + B[i];
}

__kernel void softmax_shift_exp(__global const float* X,
                                __global const float* rowmax,
                                __global float* E,
                                const int rows,
                                const int cols) {
    int gid = get_global_id(0);
    if (gid < rows*cols) {
        int r = gid / cols;
        E[gid] = exp(X[gid] - rowmax[r]);
    }
}

__kernel void softmax_normalize(__global const float* E,
                                __global const float* rowsum,
                                __global float* Y,
                                const int rows,
                                const int cols) {
    int gid = get_global_id(0);
    if (gid < rows*cols) {
        int r = gid / cols;
        Y[gid] = E[gid] / rowsum[r];
    }
}
"""

class OpenCLBackend:
    """
    Backend OpenCL minimal :
    - vector_add : 100% device
    - softmax2d  : exp et normalisation sur device, réductions (max/sum) sur host.
    Suffisant pour une démo publique sans dévoiler de logique propriétaire.
    """
    def __init__(self):
        if not _PYOPENCL_OK:
            raise ImportError("PyOpenCL not available")
        plats = cl.get_platforms()
        if not plats:
            raise RuntimeError("No OpenCL platforms")
        devs = plats[0].get_devices()
        if not devs:
            raise RuntimeError("No OpenCL devices")
        self.ctx = cl.Context([devs[0]])
        self.q = cl.CommandQueue(self.ctx)
        self.prg = cl.Program(self.ctx, KERNELS).build()

    def run_ops(self, buffers: dict, ops: list, out_name: str) -> np.ndarray:
        # buffers: name -> np.ndarray (float32)
        # ops: [{"op": "...", ...}]
        b = {k: v.copy() for k, v in buffers.items()}  # work on a copy
        for op in ops:
            kind = op["op"]
            if kind == "vector_add":
                a = b[op["a"]].astype(np.float32, copy=False)
                x = b[op["b"]].astype(np.float32, copy=False)
                n = a.size
                assert x.size == n
                C = np.empty_like(a)

                import pyopencl as cl
                mf = cl.mem_flags
                dA = cl.Buffer(self.ctx, mf.READ_ONLY  | mf.COPY_HOST_PTR, hostbuf=a)
                dB = cl.Buffer(self.ctx, mf.READ_ONLY  | mf.COPY_HOST_PTR, hostbuf=x)
                dC = cl.Buffer(self.ctx, mf.WRITE_ONLY, C.nbytes)
                self.prg.vec_add(self.q, (n,), None, dA, dB, dC, np.int32(n))
                cl.enqueue_copy(self.q, C, dC).wait()
                b[op["out"]] = C

            elif kind == "softmax2d":
                X = b[op["x"]].astype(np.float32, copy=False)
                assert X.ndim == 2
                rows, cols = X.shape
                X_flat = X.reshape(-1)

                # host reductions
                rowmax = np.max(X, axis=1).astype(np.float32)
                E = np.empty_like(X_flat)
                Y = np.empty_like(X_flat)

                import pyopencl as cl
                mf = cl.mem_flags
                dX = cl.Buffer(self.ctx, mf.READ_ONLY  | mf.COPY_HOST_PTR, hostbuf=X_flat)
                dRM= cl.Buffer(self.ctx, mf.READ_ONLY  | mf.COPY_HOST_PTR, hostbuf=rowmax)
                dE = cl.Buffer(self.ctx, mf.READ_WRITE, E.nbytes)
                dY = cl.Buffer(self.ctx, mf.WRITE_ONLY, Y.nbytes)

                # exp(X - rowmax)
                self.prg.softmax_shift_exp(self.q, (rows*cols,), None, dX, dRM, dE, np.int32(rows), np.int32(cols))
                cl.enqueue_copy(self.q, E, dE).wait()

                # host rowsum, then normalize on device
                rowsum = E.reshape(rows, cols).sum(axis=1).astype(np.float32)
                dRS = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=rowsum)
                self.prg.softmax_normalize(self.q, (rows*cols,), None, dE, dRS, dY, np.int32(rows), np.int32(cols))
                cl.enqueue_copy(self.q, Y, dY).wait()
                b[op["out"]] = Y.reshape(rows, cols)
            else:
                raise ValueError(f"Unsupported op for OpenCL backend: {kind}")
        return b[out_name]
