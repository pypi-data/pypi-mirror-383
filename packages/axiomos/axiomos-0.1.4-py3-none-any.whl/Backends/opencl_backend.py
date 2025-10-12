#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
"""
OpenCL backend (GEMM-focused) with caching, profiling, pinned staging, and
AXIR-aligned host inputs. Kernel is tiled in local memory and accumulates across
the full K range. Program caches cl.Program and cl.Kernel objects, and reuses
device buffers across runs.

Public API: `run(ax, summary=False, dump=None, repeats=1, profile=False)`
Returns the output buffer (hC) as a NumPy array (for matmul path). For non-matmul
quick kernels, returns {"dump": ...} or {"ok": True} selon le dispatch demandé.
"""

from __future__ import annotations

# =======================
# Imports + flags (ajout)
# =======================
import os
import json, re, ast, operator
from typing import Optional, Dict, Any
import numpy as np
import pyopencl as cl

# -------- Cache contexte & queue (global, unique) --------
_CTX = None
_QUEUE = None

def _get_ctx_queue():
    global _CTX, _QUEUE
    if _CTX is None:
        # Sélection simple: première plateforme / premier device
        plat = cl.get_platforms()[0]
        dev = plat.get_devices()[0]
        _CTX = cl.Context([dev])
        _QUEUE = cl.CommandQueue(
            _CTX, properties=cl.command_queue_properties.PROFILING_ENABLE
        )
    return _CTX, _QUEUE
# ---------------------------------------------------------

# ---------- Caches globaux (programme & kernel) ----------
# (utilisés pour Softmax2D et réutilisés par SAXPY si besoin)
_OCL_CTX = None
_OCL_QUEUE = None
_OCL_PRG_CACHE: Dict[Any, cl.Program] = {}
_OCL_KERN_CACHE: Dict[Any, cl.Kernel] = {}
# ---------------------------------------------------------

# ---------- AJOUT (haut de fichier) : cache/softmax2d minimal ----------
_PRG_CACHE = {}
SOFTMAX2D_SRC = r"""
// --- Scalar (1 thread / row) reference kernel ---
__kernel void softmax2d_row_scalar(__global const float* X,
                                   __global float* Y,
                                   const int M, const int N)
{
    int row = get_global_id(0);
    if (row >= M) return;
    int base = row * N;
    float m = X[base];
    for (int j = 1; j < N; ++j) m = fmax(m, X[base + j]);
    float s = 0.0f;
    for (int j = 0; j < N; ++j) s += exp(X[base + j] - m);
    float invs = 1.0f / s;
    for (int j = 0; j < N; ++j)
        Y[base + j] = exp(X[base + j] - m) * invs;
}

// WG par défaut si non fourni via l'env AXIOMOS_OCL_SOFTMAX_WG
#ifndef WG
#define WG 256
#endif

__attribute__((reqd_work_group_size(WG,1,1)))
__kernel void softmax2d_row(__global const float* restrict X,
                            __global float* restrict Y,
                            const int M, const int N)
{
    const int row = get_group_id(0);
    if (row >= M) return;

    const int lid = get_local_id(0);
    const int lsz = get_local_size(0);

    __local float lmax[WG];
    __local float lsum[WG];

    // 1) Max sur la ligne (maské: on ne lit que j < N)
    float m = -INFINITY;
    for (int j = lid; j < N; j += lsz) {
        float v = X[row * N + j];
        m = fmax(m, v);
    }
    lmax[lid] = m;
    barrier(CLK_LOCAL_MEM_FENCE);
    // réduction locale max
    for (int off = lsz >> 1; off > 0; off >>= 1) {
        if (lid < off) lmax[lid] = fmax(lmax[lid], lmax[lid + off]);
        barrier(CLK_LOCAL_MEM_FENCE);
    }
    m = lmax[0];
    barrier(CLK_LOCAL_MEM_FENCE);

    // 2) Somme des exp (maskée)
    float s = 0.0f;
    for (int j = lid; j < N; j += lsz) {
        s += exp(X[row * N + j] - m);
    }
    lsum[lid] = s;
    barrier(CLK_LOCAL_MEM_FENCE);
    // réduction locale somme
    for (int off = lsz >> 1; off > 0; off >>= 1) {
        if (lid < off) lsum[lid] += lsum[lid + off];
        barrier(CLK_LOCAL_MEM_FENCE);
    }
    s = lsum[0];
    barrier(CLK_LOCAL_MEM_FENCE);

    // 3) Écriture normalisée (maskée)
    for (int j = lid; j < N; j += lsz) {
        Y[row * N + j] = exp(X[row * N + j] - m) / s;
    }
}

// --- Softmax 2D row-wise, tiled ---
// Un work-group par ligne, LOCAL_SIZE threads (128/256 recommandé).
#ifndef LOCAL_SIZE
#define LOCAL_SIZE 256
#endif

__attribute__((reqd_work_group_size(LOCAL_SIZE,1,1)))
__kernel void softmax2d_row_tiled(__global const float* X,
                                  __global float* Y,
                                  const int M, const int N)
{
    const int row = get_group_id(0);
    const int lid = get_local_id(0);
    if (row >= M) return;

    const int base = row * N;
    __local float sdata[LOCAL_SIZE];

    // 1) Max par ligne (réduction locale)
    float vmax = -INFINITY;
    for (int c = lid; c < N; c += LOCAL_SIZE) {
        float v = X[base + c];
        vmax = fmax(vmax, v);
    }
    sdata[lid] = vmax;
    barrier(CLK_LOCAL_MEM_FENCE);
    for (int ofs = LOCAL_SIZE >> 1; ofs > 0; ofs >>= 1) {
        if (lid < ofs) sdata[lid] = fmax(sdata[lid], sdata[lid + ofs]);
        barrier(CLK_LOCAL_MEM_FENCE);
    }
    const float m = sdata[0];

    // 2) exp-shift + somme (réduction locale)
    float lsum = 0.0f;
    for (int c = lid; c < N; c += LOCAL_SIZE) {
        float e = exp(X[base + c] - m);
        Y[base + c] = e;   // on stocke temporairement e dans Y
        lsum += e;
    }
    sdata[lid] = lsum;
    barrier(CLK_LOCAL_MEM_FENCE);
    for (int ofs = LOCAL_SIZE >> 1; ofs > 0; ofs >>= 1) {
        if (lid < ofs) sdata[lid] += sdata[lid + ofs];
        barrier(CLK_LOCAL_MEM_FENCE);
    }
    const float s = sdata[0];

    // 3) normalisation
    for (int c = lid; c < N; c += LOCAL_SIZE) {
        Y[base + c] = Y[base + c] / s;
    }
}
"""

def _get_or_build(ctx, key, src):
    prg = _PRG_CACHE.get(key)
    if prg is None:
        prg = cl.Program(ctx, src).build()
        _PRG_CACHE[key] = prg
    return prg

# ----------- Kernel cache pour éviter RepeatedKernelRetrieval -----------
_KERNEL_CACHE: Dict[Any, cl.Kernel] = {}

def _get_kernel(prg: cl.Program, name: str) -> cl.Kernel:
    """Return a cached cl.Kernel for (program,name). Avoids repeated retrieval warnings."""
    key = (id(prg), name)
    kn = _KERNEL_CACHE.get(key)
    if kn is None:
        kn = cl.Kernel(prg, name)
        _KERNEL_CACHE[key] = kn
    return kn
# -----------------------------------------------------------------------

# ----- AJOUT : helpers Softmax OCL -----

def _resolve_MN(ax, op):
    """Resolve (M, N) robustly, preferring buffer shapes over scalars/op args.
    This avoids swapped M/N when ops list arguments are ordered as (N, M)."""
    # 1) Prefer explicit buffer metadata (most reliable)
    bufs = (ax.get("buffers", {}) or {})
    for nm in ("hX", "X", "hY", "Y", "hC", "C"):
        sh = (bufs.get(nm, {}) or {}).get("shape")
        if isinstance(sh, (list, tuple)) and len(sh) == 2:
            try:
                M = int(sh[0]); N = int(sh[1])
                return M, N
            except Exception:
                pass

    # 2) Scalars from AXIR (types.scalars)
    def get_scalar(name):
        try:
            return int(((ax.get("types", {}) or {}).get("scalars", {}) or {}).get(name, {}).get("value"))
        except Exception:
            return None
    M = get_scalar("M"); N = get_scalar("N")
    if M is not None and N is not None:
        return int(M), int(N)

    # 3) Fallback: try to parse op args, resolving symbolic names via scalars
    ints = []
    scalars = (ax.get("types", {}) or {}).get("scalars", {}) or {}
    for a in (op.get("args", []) or []):
        if isinstance(a, int):
            ints.append(int(a))
        elif isinstance(a, str):
            # symbolic like "M"/"N"
            s = scalars.get(a, {})
            val = s.get("value") if isinstance(s, dict) else None
            if val is not None:
                try:
                    ints.append(int(val)); continue
                except Exception:
                    pass
            # literal integer in string
            if a.isdigit():
                ints.append(int(a))
    if len(ints) >= 2:
        return int(ints[0]), int(ints[1])

    raise RuntimeError("softmax2d: M/N introuvables")


def _run_softmax2d(ax, host, device, dev_sizes, op):
    # Compile une seule fois et profile H2D/KRN/D2H, avec kernel réutilisé via cache
    ctx, queue = _get_ctx_queue()

    # Résoudre M, N (robuste)
    M, N = _resolve_MN(ax, op)

    # Source hôte
    if "hX" in host:
        hX = np.asarray(host["hX"], dtype=np.float32).reshape(M * N)
    else:
        hX = np.arange(M * N, dtype=np.float32)

    # Buffers device + copies profilées
    dX = cl.Buffer(ctx, cl.mem_flags.READ_ONLY, size=4 * M * N)
    dY = cl.Buffer(ctx, cl.mem_flags.WRITE_ONLY, size=4 * M * N)
    evt_h2d = cl.enqueue_copy(queue, dX, hX)

    # ----- Sélection kernel : seuil N>=256 -> tiled, sinon scalar (1 thread/row) -----
    use_tiled = (int(N) >= 256)
    if use_tiled:
        WG = int(os.getenv("AXIOMOS_OCL_SOFTMAX_WG", "256"))
        build_opts = f"-cl-fast-relaxed-math -cl-mad-enable -DLOCAL_SIZE={WG}"
        src_key = ("softmax2d_src", build_opts)
        prg = _OCL_PRG_CACHE.get(src_key)
        if prg is None:
            prg = cl.Program(ctx, SOFTMAX2D_SRC).build(options=build_opts.split())
            _OCL_PRG_CACHE[src_key] = prg
        kern = _get_kernel(prg, "softmax2d_row_tiled")
        evt_k = kern(queue, (int(M) * WG,), (WG,), dX, dY, np.int32(M), np.int32(N))
    else:
        build_opts = "-cl-fast-relaxed-math -cl-mad-enable"
        src_key = ("softmax2d_src", build_opts)
        prg = _OCL_PRG_CACHE.get(src_key)
        if prg is None:
            prg = cl.Program(ctx, SOFTMAX2D_SRC).build(options=build_opts.split())
            _OCL_PRG_CACHE[src_key] = prg
        kern = _get_kernel(prg, "softmax2d_row_scalar")
        evt_k = kern(queue, (int(M),), None, dX, dY, np.int32(M), np.int32(N))

    hY = np.empty(M * N, dtype=np.float32)
    evt_d2h = cl.enqueue_copy(queue, hY, dY)

    evt_d2h.wait()
    to_ms = lambda e: (e.profile.end - e.profile.start) * 1e-6
    print(f"[OCL][PROFILE] H2D={to_ms(evt_h2d):.2f} ms  KRN={to_ms(evt_k):.2f} ms  D2H={to_ms(evt_d2h):.2f} ms  TOTAL={(to_ms(evt_h2d)+to_ms(evt_k)+to_ms(evt_d2h)):.2f} ms")

    host["hY"] = hY.reshape(M, N)
    host["hC"] = host["hY"]  # pour verify --buffer hC
# ---------------------------------------------------------------

AXIOMOS_OCL_PINNED   = os.getenv("AXIOMOS_OCL_PINNED", "1") == "1"
AXIOMOS_OCL_FASTMATH = os.getenv("AXIOMOS_OCL_FASTMATH", "0") == "1"
AXIOMOS_OCL_DEBUG    = os.getenv("AXIOMOS_OCL_DEBUG", "0") == "1"

# Avoid PyOpenCL cache encoding warning on Windows (cp1252)
os.environ.setdefault("PYOPENCL_NO_CACHE", "1")

# =======================
# Helpers scalars/shapes
# =======================

def _get_scalar(ax, name: str):
    try:
        return int(((ax.get("types", {}) or {}).get("scalars", {}) or {}).get(name, {}).get("value"))
    except Exception:
        return None

# ---- float scalar resolver ----

def _get_fscalar(ax, name: str):
    try:
        v = ((ax.get("types", {}) or {}).get("scalars", {}) or {}).get(name, {}).get("value")
        if v is None:
            return None
        return float(v)
    except Exception:
        return None
# ---------------------------------------------------


def _resolve_shape(ax, shape_list):
    out = []
    for d in (shape_list or []):
        if isinstance(d, (int, float)):
            out.append(int(d))
        elif isinstance(d, str):
            v = _get_scalar(ax, d)  # "N" -> valeur dans types.scalars
            if v is not None:
                out.append(int(v))
            else:
                try:
                    out.append(int(d))  # ex: "65536"
                except Exception:
                    raise ValueError(f"Unresolvable shape extent: {d!r}")
        else:
            raise ValueError(f"Unsupported shape extent type: {type(d)}")
    return out

# ====================================
# Kernel SAXPY (source)
# ====================================
SAXPY_SRC = r"""
__kernel void saxpy(const int n, const float alpha,
                    __global const float* a,
                    __global const float* b,
                    __global float* c) {
  int i = get_global_id(0);
  if (i < n) {
    // FMA via mad() si l'option -cl-mad-enable est activée
    c[i] = mad(alpha, a[i], b[i]);
  }
}
"""

# Cache de programme & kernel pour SAXPY: clé = (platform, device, fastmath)
# (réutilise les caches globaux si déjà définis)
try:
    _OCL_PROG_CACHE
except NameError:
    _OCL_PROG_CACHE: Dict[Any, cl.Program] = {}
try:
    _OCL_KERN_CACHE
except NameError:
    _OCL_KERN_CACHE: Dict[Any, cl.Kernel] = {}


def _get_saxpy_program(ctx, fastmath: bool = False):
    dev = ctx.devices[0]; plat = dev.platform
    key = (plat.name, dev.name, bool(fastmath))
    prg = _OCL_PROG_CACHE.get(key)
    if prg is not None:
        return prg
    opts = ["-cl-std=CL1.2"]
    if fastmath:
        opts += ["-cl-fast-relaxed-math", "-cl-mad-enable"]
    prg = cl.Program(ctx, SAXPY_SRC).build(options=" ".join(opts))
    _OCL_PROG_CACHE[key] = prg
    return prg


def _get_saxpy_kernel(ctx, fastmath: bool = False):
    prg = _get_saxpy_program(ctx, fastmath)
    kkey = (id(prg), "saxpy")  # kernel cache key harmonisé
    kern = _OCL_KERN_CACHE.get(kkey)
    if kern is None:
        kern = cl.Kernel(prg, "saxpy")
        _OCL_KERN_CACHE[kkey] = kern
    return kern

# ================================================================
# Helpers ajoutés (avant fonctions existantes)
# ================================================================

# ---------------- ctx/queue ----------------

def _mk_ctx_queue(profile: bool = False):
    ctx = cl.create_some_context(interactive=False)
    props = cl.command_queue_properties.PROFILING_ENABLE if profile else 0
    queue = cl.CommandQueue(ctx, properties=props)
    return ctx, queue

# ---------------- petits kernels “rapides” ----------------
KERNELS = {
"vector_add": r"""
__kernel void vadd(__global const float* A, __global const float* B, __global float* C, int N){
  int i = get_global_id(0);
  if (i < N) C[i] = A[i] + B[i];
}""",
# (on conserve ce saxpy "rapide" pour compat, même si la voie SAXPY_SRC est prioritaire)
"saxpy": r"""
__kernel void saxpy(float alpha, __global const float* A, __global const float* B, __global float* C, int N){
  int i = get_global_id(0);
  if (i < N) C[i] = alpha*A[i] + B[i];
}""",
"relu": r"""
__kernel void relu(__global const float* A, __global float* C, int N){
  int i = get_global_id(0);
  if (i < N) C[i] = fmax(A[i], 0.0f);
}""",
"mul": r"""
__kernel void vmul(__global const float* A, __global const float* B, __global float* C, int N){
  int i = get_global_id(0);
  if (i < N) C[i] = A[i]*B[i];
}""",
"vexp": r"""
__kernel void vexp(__global const float* A, __global float* C, int N){
  int i = get_global_id(0);
  if (i < N) C[i] = exp(A[i]);
}""",
"reduce_sum": r"""
__kernel void reduce_sum(__global const float* A, __global float* out, int N){
  float s = 0.0f;
  for (int i=0;i<N;++i) s += A[i];
  out[0] = s;
}""",
"reduce_max": r"""
__kernel void reduce_max(__global const float* A, __global float* out, int N){
  float m = A[0];
  for (int i=1;i<N;++i){ float v=A[i]; if (v>m) m=v; }
  out[0] = m;
}""",
"reduce_argmax": r"""
__kernel void reduce_argmax(__global const float* A, __global float* out_val, __global int* out_idx, int N){
  float m = A[0]; int idx = 0;
  for (int i=1;i<N;++i){ float v=A[i]; if (v>m){ m=v; idx=i; } }
  out_val[0] = m; out_idx[0] = idx;
}""",
"softmax2d": r"""
__kernel void softmax2d(__global const float* X, __global float* Y, int M, int N){
  int r = get_global_id(0);
  if (r >= M) return;
  float mx = X[r*N];
  for (int j=1;j<N;++j){ float v=X[r*N+j]; if (v>mx) mx=v; }
  float s = 0.0f;
  for (int j=0;j<N;++j){ float e = exp(X[r*N+j]-mx); Y[r*N+j]=e; s+=e; }
  for (int j=0;j<N;++j){ Y[r*N+j] = Y[r*N+j]/s; }
}""",
"layernorm2d": r"""
__kernel void layernorm2d(__global const float* X, __global const float* G, __global const float* B,
                          __global float* Y, int M, int N, float eps){
  int r = get_global_id(0);
  if (r >= M) return;
  float mu = 0.0f;
  for (int j=0;j<N;++j) mu += X[r*N+j];
  mu /= (float)N;
  float var = 0.0f;
  for (int j=0;j<N;++j){ float d=X[r*N+j]-mu; var += d*d; }
  var /= (float)N;
  float inv = rsqrt(var + eps);
  for (int j=0;j<N;++j){
    float z = (X[r*N+j]-mu) * inv;
    Y[r*N+j] = z * G[j] + B[j];
  }
}""",
}

# Utilise un cache séparé pour éviter d’écraser celui du GEMM
_PROG_CACHE_MISC: Dict[Any, cl.Program] = {}

def _get_prog(ctx, name, fastmath: bool = False):
    key = (int(ctx.int_ptr), name, bool(fastmath))
    prg = _PROG_CACHE_MISC.get(key)
    if prg is None:
        opts = ["-cl-fast-relaxed-math"] if fastmath else []
        prg = cl.Program(ctx, KERNELS[name]).build(" ".join(opts) or None)
        _PROG_CACHE_MISC[key] = prg
    return prg

# ----- small guesses (compat CPU backend) -----

def _scalar(ax, name, default=None):
    try:
        return int(ax.get("types", {}).get("scalars", {}).get(name, {}).get("value"))
    except Exception:
        return default


def _guess_N(ax, default=1 << 16):
    v = _scalar(ax, "N", None)
    return v if isinstance(v, int) and v > 0 else default


def _guess_MN(ax, default=(128, 128)):
    M = _scalar(ax, "M", None)
    N = _scalar(ax, "N", None)
    if isinstance(M, int) and isinstance(N, int) and M > 0 and N > 0:
        return M, N
    return default

# ---------- runners (sans AXIR memgraph complet) ----------

def _ocl_vadd(N, repeats=1, fastmath=False, profile=False):
    ctx, q = _mk_ctx_queue(profile)
    A = np.arange(N, dtype=np.float32)
    B = np.arange(N, dtype=np.float32)
    C = np.empty_like(A)
    mf = cl.mem_flags
    dA = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=A)
    dB = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=B)
    dC = cl.Buffer(ctx, mf.WRITE_ONLY, size=C.nbytes)
    prg = _get_prog(ctx, "vector_add", fastmath)
    kn = prg.vadd
    ls = (256,)
    gs = ((N + ls[0] - 1) // ls[0] * ls[0],)
    for _ in range(max(1, int(repeats))):
        kn(q, gs, ls, dA, dB, dC, np.int32(N))
    cl.enqueue_copy(q, C, dC).wait()
    return C


def _ocl_relu(N, repeats=1, fastmath=False, profile=False):
    ctx, q = _mk_ctx_queue(profile)
    A = np.arange(N, dtype=np.float32)
    C = np.empty_like(A)
    mf = cl.mem_flags
    dA = cl.Buffer(ctx, mf.Read_ONLY | mf.COPY_HOST_PTR, hostbuf=A) if hasattr(mf,'Read_ONLY') else cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=A)
    dC = cl.Buffer(ctx, mf.WRITE_ONLY, size=C.nbytes)
    prg = _get_prog(ctx, "relu", fastmath)
    kn = prg.relu
    ls = (256,)
    gs = ((N + ls[0] - 1) // ls[0] * ls[0],)
    for _ in range(max(1, int(repeats))):
        kn(q, gs, ls, dA, dC, np.int32(N))
    cl.enqueue_copy(q, C, dC).wait()
    return C


def _ocl_mul(N, repeats=1, fastmath=False, profile=False):
    ctx, q = _mk_ctx_queue(profile)
    A = np.arange(N, dtype=np.float32)
    B = np.arange(N, dtype=np.float32)
    C = np.empty_like(A)
    mf = cl.mem_flags
    dA = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=A)
    dB = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=B)
    dC = cl.Buffer(ctx, mf.WRITE_ONLY, size=C.nbytes)
    prg = _get_prog(ctx, "mul", fastmath)
    kn = prg.vmul
    ls = (256,)
    gs = ((N + ls[0] - 1) // ls[0] * ls[0],)
    for _ in range(max(1, int(repeats))):
        kn(q, gs, ls, dA, dB, dC, np.int32(N))
    cl.enqueue_copy(q, C, dC).wait()
    return C


def _ocl_vexp(N, repeats=1, fastmath=False, profile=False):
    ctx, q = _mk_ctx_queue(profile)
    A = np.arange(N, dtype=np.float32)
    C = np.empty_like(A)
    mf = cl.mem_flags
    dA = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=A)
    dC = cl.Buffer(ctx, mf.WRITE_ONLY, size=C.nbytes)
    prg = _get_prog(ctx, "vexp", fastmath)
    kn = prg.vexp
    ls = (256,)
    gs = ((N + ls[0] - 1) // ls[0] * ls[0],)
    for _ in range(max(1, int(repeats))):
        kn(q, gs, ls, dA, dC, np.int32(N))
    cl.enqueue_copy(q, C, dC).wait()
    return C


def _ocl_reduce_sum(N, repeats=1, fastmath=False, profile=False):
    ctx, q = _mk_ctx_queue(profile)
    A = np.arange(N, dtype=np.float32)
    out = np.zeros(1, dtype=np.float32)
    mf = cl.mem_flags
    dA = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=A)
    dO = cl.Buffer(ctx, mf.WRITE_ONLY, size=out.nbytes)
    prg = _get_prog(ctx, "reduce_sum", fastmath)
    kn = prg.reduce_sum
    for _ in range(max(1, int(repeats))):
        kn(q, (1,), None, dA, dO, np.int32(N))
    cl.enqueue_copy(q, out, dO).wait()
    return float(out[0])


def _ocl_reduce_max(N, repeats=1, fastmath=False, profile=False):
    ctx, q = _mk_ctx_queue(profile)
    A = np.arange(N, dtype=np.float32)
    out = np.zeros(1, dtype=np.float32)
    mf = cl.mem_flags
    dA = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=A)
    dO = cl.Buffer(ctx, mf.WRITE_ONLY, size=out.nbytes)
    prg = _get_prog(ctx, "reduce_max", fastmath)
    kn = prg.reduce_max
    for _ in range(max(1, int(repeats))):
        kn(q, (1,), None, dA, dO, np.int32(N))
    cl.enqueue_copy(q, out, dO).wait()
    return float(out[0])


def _ocl_reduce_argmax(N, repeats=1, fastmath=False, profile=False):
    ctx, q = _mk_ctx_queue(profile)
    A = np.arange(N, dtype=np.float32)
    outv = np.zeros(1, dtype=np.float32)
    outi = np.zeros(1, dtype=np.int32)
    mf = cl.mem_flags
    dA = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=A)
    dV = cl.Buffer(ctx, mf.WRITE_ONLY, size=outv.nbytes)
    dIx = cl.Buffer(ctx, mf.WRITE_ONLY, size=outi.nbytes)
    prg = _get_prog(ctx, "reduce_argmax", fastmath)
    kn = prg.reduce_argmax
    for _ in range(max(1, int(repeats))):
        kn(q, (1,), None, dA, dV, dIx, np.int32(N))
    cl.enqueue_copy(q, outv, dV)
    cl.enqueue_copy(q, outi, dIx).wait()
    return float(outv[0]), int(outi[0])


def _ocl_softmax2d(M, N, repeats=1, fastmath=False, profile=False):
    ctx, q = _mk_ctx_queue(profile)
    X = np.arange(M * N, dtype=np.float32).reshape(M, N)
    Y = np.empty_like(X)
    mf = cl.mem_flags
    dX = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=X)
    dY = cl.Buffer(ctx, mf.WRITE_ONLY, size=Y.nbytes)
    prg = _get_prog(ctx, "softmax2d", fastmath)
    kn = prg.softmax2d
    ls = None
    gs = (M,)
    for _ in range(max(1, int(repeats))):
        kn(q, gs, ls, dX, dY, np.int32(M), np.int32(N))
    cl.enqueue_copy(q, Y, dY).wait()
    return Y


def _ocl_layernorm2d(M, N, repeats=1, fastmath=False, profile=False, eps=1e-5):
    ctx, q = _mk_ctx_queue(profile)
    X = np.arange(M * N, dtype=np.float32).reshape(M, N)
    G = np.ones(N, dtype=np.float32)
    B = np.zeros(N, dtype=np.float32)
    Y = np.empty_like(X)
    mf = cl.mem_flags
    dX = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=X)
    dG = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=G)
    dB = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=B)
    dY = cl.Buffer(ctx, mf.WRITE_ONLY, size=Y.nbytes)
    prg = _get_prog(ctx, "layernorm2d", fastmath)
    kn = prg.layernorm2d
    ls = None
    gs = (M,)
    for _ in range(max(1, int(repeats))):
        kn(q, gs, ls, dX, dG, dB, dY, np.int32(M), np.int32(N), np.float32(eps))
    cl.enqueue_copy(q, Y, dY).wait()
    return Y

# ================================================================
# Helper d’exécution SAXPY (avec cache + profilage)
# ================================================================

def _run_saxpy_ocl(ctx, queue, dA, dB, dC, N, alpha, fastmath: bool = False, debug: bool = False):
    import numpy as _np
    if debug and not (queue.properties & cl.command_queue_properties.PROFILING_ENABLE):
        queue = cl.CommandQueue(ctx, properties=cl.command_queue_properties.PROFILING_ENABLE)

    wgs = min(256, queue.device.max_work_group_size)
    gsz = ((N + wgs - 1) // wgs) * wgs

    kern = _get_saxpy_kernel(ctx, fastmath=fastmath)
    kern.set_args(_np.int32(N), _np.float32(alpha), dA, dB, dC)
    evt = cl.enqueue_nd_range_kernel(queue, kern, (gsz,), (wgs,))
    evt.wait()

    if debug and (queue.properties & cl.command_queue_properties.PROFILING_ENABLE):
        t = (evt.profile.end - evt.profile.start) * 1e-6
        print(f"[OCL][PROFILE] SAXPY KRN={t:.2f} ms")
    return evt

# ================================================================
# (Suite : code existant du backend GEMM)
# ================================================================

# ================================================================
# Context / Queue cache
# ================================================================
_CTXQ = None


def _device_type_from_env():
    s = (os.getenv("AXIOMOS_OCL_DEVICE_TYPE", "") or "").strip().upper()
    if s == "GPU":
        return cl.device_type.GPU
    if s == "CPU":
        return cl.device_type.CPU
    return None


def _parse_int_env(name: str):
    v = os.getenv(name, "").strip()
    if not v:
        return None
    try:
        return int(v)
    except Exception:
        return None


def _select_platform_device():
    """
    Respecte (optionnellement) AXIOMOS_OCL_PLATFORM_INDEX, AXIOMOS_OCL_DEVICE_INDEX,
    AXIOMOS_OCL_DEVICE_TYPE. Fallback: première plateforme / premier device.
    Jamais d'exception bloquante : en cas d'indices invalides, on retombe
    sur le comportement historique.
    """
    try:
        plats = cl.get_platforms()
        if not plats:
            raise RuntimeError("No OpenCL platforms")

        want_pidx = _parse_int_env("AXIOMOS_OCL_PLATFORM_INDEX")
        want_didx = _parse_int_env("AXIOMOS_OCL_DEVICE_INDEX")
        want_dtype = _device_type_from_env()

        plat = None
        dev = None

        # Sélection plateforme
        if want_pidx is not None and 0 <= want_pidx < len(plats):
            plat = plats[want_pidx]
        elif want_dtype is not None:
            for p in plats:
                try:
                    ds = p.get_devices(device_type=want_dtype)
                    if ds:
                        plat = p
                        break
                except Exception:
                    pass
        if plat is None:
            plat = plats[0]

        # Sélection device
        try:
            devs = plat.get_devices(device_type=want_dtype) if want_dtype is not None else plat.get_devices()
            if not devs:
                devs = plat.get_devices()
        except Exception:
            devs = plat.get_devices()

        if want_didx is not None and 0 <= want_didx < len(devs):
            dev = devs[want_didx]
        else:
            dev = devs[0]

        return plat, dev
    except Exception:
        plats = cl.get_platforms()
        plat = plats[0]
        dev = plat.get_devices()[0]
        return plat, dev

# -------------------- PATCH INSERT: _choose_device + new _ctx_queue --------------------

def _choose_device():
    plats = cl.get_platforms()
    # 1) indices explicites
    pi = os.getenv("AXIOMOS_OCL_PLATFORM_INDEX")
    di = os.getenv("AXIOMOS_OCL_DEVICE_INDEX")
    if pi is not None and di is not None:
        try:
            p = plats[int(pi)]
            d = p.get_devices()[int(di)]
            return p, d
        except Exception:
            pass

    # 2) type explicite
    dtype_env = (os.getenv("AXIOMOS_OCL_DEVICE_TYPE") or "").upper()
    type_map = {
        "GPU": cl.device_type.GPU,
        "CPU": cl.device_type.CPU,
        "ACCEL": cl.device_type.ACCELERATOR,
        "DEFAULT": cl.device_type.DEFAULT,
        "ALL": cl.device_type.ALL,
    }
    if dtype_env in type_map:
        want = type_map[dtype_env]
        for p in plats:
            for d in p.get_devices(device_type=want):
                return p, d

    # 3) fallback: premier device dispo
    p0 = plats[0]
    d0 = p0.get_devices()[0]
    return p0, d0


def _ctx_queue(profile: bool = True):
    """Context/queue cache with env-driven device selection (non-breaking)."""
    global _CTXQ
    if _CTXQ is not None:
        ctx, q = _CTXQ
        want_props = cl.command_queue_properties.PROFILING_ENABLE if profile else 0
        if bool(q.properties & cl.command_queue_properties.PROFILING_ENABLE) != bool(want_props):
            q = cl.CommandQueue(ctx, properties=want_props)
            _CTXQ = (ctx, q)
        return _CTXQ

    plat, dev = _choose_device()
    props = cl.command_queue_properties.PROFILING_ENABLE if profile else 0
    ctx = cl.Context([dev])
    q = cl.CommandQueue(ctx, properties=props)
    print(f"[OCL] platform '{plat.name}' -> device '{dev.name}'")
    _CTXQ = (ctx, q)
    return _CTXQ
# ------------------ END PATCH INSERT --------------------

# ================================================================
# Device/Program/Kernel/Buffer caches
# ================================================================
_PROG_CACHE: dict = {}
_BUF_CACHE: dict = {}

# ================================================================
# Helpers
# ================================================================

def _ctx_key(ctx: cl.Context):
    try:
        return int(ctx.int_ptr)
    except Exception:
        d = ctx.devices[0]
        return hash((d.platform.name, d.name))

# Pinned host buffers: suivre le flag global demandé
_PINNED = AXIOMOS_OCL_PINNED
_PINNED_CACHE = {}


def _ensure_pinned_host_buf(ctx: cl.Context, role: str, nbytes: int):
    if not _PINNED:
        return None
    key = (_ctx_key(ctx), role)
    ent = _PINNED_CACHE.get(key)
    if ent is None or int(ent.get("size", 0)) < int(nbytes):
        buf = cl.Buffer(ctx, cl.mem_flags.ALLOC_HOST_PTR | cl.mem_flags.READ_WRITE, int(nbytes))
        _PINNED_CACHE[key] = {"size": int(nbytes), "buf": buf}
        print(f"[OCL][PINNED] {role} {nbytes/1024:.1f} KB")
        return buf
    return ent["buf"]


def _safe_unmap(mapped, q: cl.CommandQueue):
    base = getattr(mapped, "base", None)
    if base is None:
        return None
    rel = getattr(base, "release", None)
    if callable(rel):
        try:
            return rel(q)      # PyOpenCL recent: release(queue) -> Event|None
        except TypeError:
            return rel()       # fallback signatures
    unm = getattr(base, "unmap", None)
    if callable(unm):
        try:
            return unm(q)
        except TypeError:
            return unm()
    return None


def _host_to_dev(q: cl.CommandQueue, h_np: np.ndarray, dev_buf: cl.MemoryObject, staging=None):
    import numpy as np
    if staging is not None:
        mapped, _ = cl.enqueue_map_buffer(
            q, staging, cl.map_flags.WRITE, 0,
            h_np.shape, h_np.dtype, is_blocking=True
        )
        np.copyto(mapped, h_np)
        evt_unmap = _safe_unmap(mapped, q)
        waits = [evt_unmap] if evt_unmap is not None else None
        # Buffer -> Buffer: chain via wait_for
        return cl.enqueue_copy(q, dest=dev_buf, src=staging, wait_for=waits)
    else:
        # Host -> Device
        return cl.enqueue_copy(q, dest=dev_buf, src=h_np, is_blocking=False)

# --- accept wait_for for OOO robustness ---

def _dev_to_host(q: cl.CommandQueue, dev_buf: cl.MemoryObject, h_np: np.ndarray, staging=None, wait_for=None):
    import numpy as np
    if staging is not None:
        # Device -> staging (Buffer->Buffer)
        evt_copy = cl.enqueue_copy(q, dest=staging, src=dev_buf, wait_for=wait_for)
        # Map after copy completes
        mapped, _ = cl.enqueue_map_buffer(
            q, staging, cl.map_flags.READ, 0,
            h_np.shape, h_np.dtype, is_blocking=True, wait_for=[evt_copy]
        )
        np.copyto(h_np, mapped)
        _safe_unmap(mapped, q)
        return evt_copy
    else:
        return cl.enqueue_copy(q, dest=h_np, src=dev_buf, is_blocking=False, wait_for=wait_for)


def _ensure_device_buffer(ctx: cl.Context, role: str, nbytes: int, flags):
    ckey = (_ctx_key(ctx), role)
    ent = _BUF_CACHE.get(ckey)
    if ent is None or int(ent.get("size", 0)) < int(nbytes):
        buf = cl.Buffer(ctx, flags, int(nbytes))
        _BUF_CACHE[ckey] = {"size": int(nbytes), "buf": buf}
        print(f"[OCL][BUF] alloc {role}: {nbytes/1024:.1f} KB")
        return buf
    return ent["buf"]


def _evt_ms(evt):
    try:
        return (evt.profile.end - evt.profile.start) * 1e-6
    except Exception:
        return 0.0


def _sum_evt_ms(events):
    return sum(_evt_ms(e) for e in events if e is not None)


def _log_profile(label: str, h2d_events, kernel_event, d2h_event):
    h2d_ms = _sum_evt_ms(h2d_events)
    krn_ms = _evt_ms(kernel_event)
    d2h_ms = _evt_ms(d2h_event)
    total = (h2d_ms or 0.0) + (krn_ms or 0.0) + (d2h_ms or 0.0)
    print(f"[OCL][PROFILE] H2D={h2d_ms:.2f} ms  KRN={krn_ms:.2f} ms  D2H={d2h_ms:.2f} ms  TOTAL={total:.2f} ms")
    return total


def _ceil_div(a, b):
    return (a + b - 1) // b


def _fits_local_mem(dev: cl.Device, TM, TN, TK, bytes_per=4, pad=1):
    need = (TM*(TK+pad) + TK*(TN+pad)) * bytes_per
    return need <= int(getattr(dev, "local_mem_size", 32*1024))


def _cap_tiles_for_device(dev: cl.Device, TM, TN, TK, pad=1):
    max_wg = int(getattr(dev, "max_work_group_size", 256))
    while TM*TN > max_wg and TM > 1:
        TM //= 2
    while TM*TN > max_wg and TN > 1:
        TN //= 2
    while not _fits_local_mem(dev, TM, TN, TK, 4, pad) and TK > 1:
        TK //= 2
    return TM, TN, TK

_TUNING_CACHE_PATH = os.path.join(os.path.expanduser("~"), ".axiomos_ocl_gemm_cache.json")


def _device_key_from_ctx(ctx: cl.Context) -> str:
    d = ctx.devices[0]
    return f"{d.platform.name}::{d.name}::{d.vendor}::{d.version}"


def _load_tuning_cache():
    try:
        with open(_TUNING_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_tuning_cache(cache: dict):
    tmp = _TUNING_CACHE_PATH + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
        os.replace(tmp, _TUNING_CACHE_PATH)
    except Exception as e:
        print(f"[OCL][TUNE] warning: unable to save cache: {e}")

# ================================================================
# ENV helpers + autotune (tile search)
# ================================================================

def _env_true(name: str) -> bool:
    v = os.getenv(name, "")
    return v in ("1", "true", "True", "yes", "YES", "on", "ON")


def _env_tile_override():
    s = (os.getenv("AXIOMOS_OCL_TILE", "") or "").strip().lower()
    if not s:
        return None
    try:
        s = s.replace("x", " ").replace(",", " ")
        tm, tn, tk = [int(x) for x in s.split()]
        return int(tm), int(tn), int(tk)
    except Exception:
        return None


def _candidates_for_device(dev: cl.Device):
    cand = [
        (8, 16, 16),
        (16, 16, 16),
        (8, 32, 16),
        (16, 8, 16),
        (8, 16, 32),
        (16, 16, 8),
    ]
    out = []
    for TM, TN, TK in cand:
        TM2, TN2, TK2 = _cap_tiles_for_device(dev, TM, TN, TK)
        if (TM2, TN2, TK2) not in out:
            out.append((TM2, TN2, TK2))
    return out


def _time_kernel_once(q, knl, gsz, lsz, wait_for=None):
    evt = cl.enqueue_nd_range_kernel(q, knl, gsz, lsz, wait_for=wait_for)
    evt.wait()
    return _evt_ms(evt)


def _autotune_tiles(ctx: cl.Context, q: cl.CommandQueue, M, N, K, fuse_bias, use_relu, fastmath_env, user_opts):
    dev = q.device
    A = np.arange(M*K, dtype=np.float32).reshape(M, K)
    B = np.arange(K*N, dtype=np.float32).reshape(K, N)
    bytesA, bytesB, bytesC = M*K*4, K*N*4, M*N*4

    dA = _ensure_device_buffer(ctx, "TUNE_A", bytesA, cl.mem_flags.READ_ONLY)
    dB = _ensure_device_buffer(ctx, "TUNE_B", bytesB, cl.mem_flags.READ_ONLY)
    dC = _ensure_device_buffer(ctx, "TUNE_C", bytesC, cl.mem_flags.WRITE_ONLY)

    cl.enqueue_copy(q, dA, A, is_blocking=False)
    cl.enqueue_copy(q, dB, B, is_blocking=True)

    best = None
    for (TM, TN, TK) in _candidates_for_device(dev):
        prg = _get_program_cached(ctx, user_opts, TM, TN, TK, fuse_bias, use_relu, fastmath_env)
        knl = _get_kernel(prg, "matmul_tiled")
        lda, ldb, ldc = K, N, N
        if fuse_bias:
            dummy = _ensure_device_buffer(ctx, "TUNE_BIAS", N*4, cl.mem_flags.READ_ONLY)
            knl.set_args(dA, dB, dummy, dC,
                         np.int32(M), np.int32(N), np.int32(K),
                         np.int32(lda), np.int32(ldb), np.int32(ldc))
        else:
            knl.set_args(dA, dB, dC,
                         np.int32(M), np.int32(N), np.int32(K),
                         np.int32(lda), np.int32(ldb), np.int32(ldc))
        gsz = (_ceil_div(N, TN) * TN, _ceil_div(M, TM) * TM)
        lsz = (TN, TM)

        t_ms = _time_kernel_once(q, knl, gsz, lsz)
        if best is None or t_ms < best[0]:
            best = (t_ms, TM, TN, TK)

    if best is None:
        return None
    _, TMb, TNb, TKb = best
    return {"TM": TMb, "TN": TNb, "TK": TKb}

# --- parse manual tile override from environment (historique) ---

def _parse_tile_env():
    s = os.getenv("AXIOMOS_OCL_TILE", "")
    if not s:
        return None
    s = s.lower().replace("x", ",").replace("*", ",")
    parts = [p.strip() for p in s.split(",") if p.strip()]
    if len(parts) != 3:
        return None
    try:
        tm, tn, tk = (int(parts[0]), int(parts[1]), int(parts[2]))
        return max(1, tm), max(1, tn), max(1, tk)
    except Exception:
        return None

# ================================================================
# Host buffer loader & MNK resolution
# ================================================================

def _host_from_ax(ax, key, shape, dtype):
    try:
        if not ax:
            return None
        bufs = ax.get("buffers", {}) or {}
        ent_buf = bufs.get(key, None)
        top_val = ax.get(key, None)

        data = None
        # 1) si buffers[key] a un champ 'data', on l'utilise
        if isinstance(ent_buf, dict) and ("data" in ent_buf):
            data = ent_buf.get("data")
        # 2) sinon, on regarde le top-level (ce que 'HostMake' a injecté)
        elif top_val is not None:
            data = top_val
        else:
            return None

        arr = np.asarray(data, dtype=dtype)
        if shape is not None:
            arr = arr.reshape(shape)
        return arr.copy(order="C")
    except Exception:
        return None


def _read_int_scalar(ax: dict, key: str):
    try:
        v = ((ax.get("types", {}) or {}).get("scalars", {}) or {}).get(key, {}).get("value")
        if v is not None:
            return int(v)
    except Exception:
        pass
    try:
        v = ((ax.get("scalars", {}) or {}).get(key, {}) or {}).get("value")
        if v is not None:
            return int(v)
    except Exception:
        pass
    try:
        if key in ax:
            return int(ax[key])
    except Exception:
        pass
    return None


def _infer_mnk_from_buffers_meta(ax: dict):
    bufs = ax.get("buffers", {}) or {}

    def _shape(ent):
        if isinstance(ent, dict) and isinstance(ent.get("shape"), (list, tuple)):
            return tuple(int(x) for x in ent["shape"])
        return None

    shA = _shape(bufs.get("hA"))
    shB = _shape(bufs.get("hB"))
    shC = _shape(bufs.get("hC"))
    M = N = K = None
    if shA and len(shA) == 2:
        M, K = shA
    if shB and len(shB) == 2:
        K = K if K is not None else shB[0]
        N = shB[1]
    if shC and len(shC) == 2:
        M = M if M is not None else shC[0]
        N = N if N is not None else shC[1]
    if all(v is not None for v in (M, N, K)):
        return int(M), int(N), int(K)
    return None, None, None


def _infer_mnk_by_loading(ax: dict):
    try:
        A = _host_from_ax(ax, "hA", None, np.float32)
    except Exception:
        A = None
    try:
        B = _host_from_ax(ax, "hB", None, np.float32)
    except Exception:
        B = None
    try:
        C = _host_from_ax(ax, "hC", None, np.float32)
    except Exception:
        C = None
    M = N = K = None
    if isinstance(A, np.ndarray) and A.ndim == 2:
        M, K = A.shape
    if isinstance(B, np.ndarray) and B.ndim == 2:
        K = K if K is not None else B.shape[0]
        N = B.shape[1]
    if isinstance(C, np.ndarray) and C.ndim == 2:
        M = M if M is not None else C.shape[0]
        N = N if N is not None else C.shape[1]
    if all(v is not None for v in (M, N, K)):
        return int(M), int(N), int(K)
    return None, None, None

# -------------------- _resolve_mnk (PATCHED) --------------------

def _read_scalar(ax, name: str):
    try:
        v = ((ax.get("types", {}) or {}).get("scalars", {}) or {}).get(name, {})
        if isinstance(v, dict) and "value" in v:
            return int(v["value"])
    except Exception:
        pass
    try:
        v = ((ax.get("scalars", {}) or {}).get(name, {}) or {}).get("value")
        if v is not None:
            return int(v)
    except Exception:
        pass
    try:
        if name in ax:
            return int(ax[name])
    except Exception:
        pass
    return None


def _resolve_mnk(ax):
    # 1) depuis l’op GEMM si présent
    for op in ax.get("ops", []):
        if (op.get("op") or "").lower() in ("gemm", "matmul"):
            def dim(k):
                v = op.get(k)
                if isinstance(v, int):
                    return v
                if isinstance(v, str):
                    s = _read_scalar(ax, v)
                    if s is not None:
                        return s
                    try:
                        return int(v)
                    except Exception:
                        pass
                return None
            M, N, K = dim("M"), dim("N"), dim("K")
            if None not in (M, N, K):
                return M, N, K

    # 2) scalars top-level
    M = _read_scalar(ax, "M"); N = _read_scalar(ax, "N"); K = _read_scalar(ax, "K")
    if None not in (M, N, K):
        return M, N, K

    # 3) métadonnées buffers
    M, N, K = _infer_mnk_from_buffers_meta(ax)
    if None not in (M, N, K):
        return M, N, K

    # 4) en chargeant les hA/hB/hC si fournis
    M, N, K = _infer_mnk_by_loading(ax)
    if None not in (M, N, K):
        return M, N, K

    raise RuntimeError("[OCL] Missing M/N/K in AXIR for GEMM.")

# -------------------- find first GEMM op (PATCHED case-insensitive) -------------------

def _find_gemm_op(ax):
    for op in ax.get("ops", []):
        t = (op.get("op") or "").lower()
        if t in ("gemm", "matmul"):
            return op
    return None

# -----------------------------------------------------------

# -------------------- helpers alpha/beta (CPU copy) --------

def _read_fscalar(ax, name: str, default=None):
    try:
        v = ((ax.get("types", {}) or {}).get("scalars", {}) or {}).get(name, {})
        if isinstance(v, dict) and "value" in v:
            return float(v["value"])
    except Exception:
        pass
    try:
        v = ((ax.get("scalars", {}) or {}).get(name, {}) or {}).get("value")
        if v is not None:
            return float(v)
    except Exception:
        pass
    try:
        if name in ax:
            return float(ax[name])
    except Exception:
        pass
    return default


def _resolve_f(ax, token, default):
    if isinstance(token, (int, float)):
        return float(token)
    if isinstance(token, str):
        s = _read_fscalar(ax, token, None)
        if s is not None:
            return float(s)
        try:
            return float(token)
        except Exception:
            return float(default)
    return float(default)
# -----------------------------------------------------------


def _resolve_alpha_beta(ax, gemm_op):
    def rf(v, fallback):
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            s = _read_fscalar(ax, v, None)
            if s is not None:
                return float(s)
            try:
                return float(v)
            except Exception:
                return float(fallback)
        return float(fallback)
    a = rf(gemm_op.get("alpha", _read_fscalar(ax, "alpha", 1.0)), _read_fscalar(ax, "alpha", 1.0))
    b = rf(gemm_op.get("beta",  _read_fscalar(ax, "beta",  0.0)), _read_fscalar(ax, "beta",  0.0))
    return a, b
# -----------------------------------------------------------

# ================================================================
# Kernel source (tiled, bias/relu optionnels)
# ================================================================
src_matmul_tiled = r"""
/*
   -D flags:
     TM, TN, TK
     FUSE_BIAS=0/1
     RELU=0/1
*/

__attribute__((reqd_work_group_size(TN, TM, 1)))
__kernel void matmul_tiled(
    __global const float * restrict A,
    __global const float * restrict B,
#if FUSE_BIAS
    __global const float * restrict Bias,
#endif
    __global float * restrict C,
    int M, int N, int K,
    int lda, int ldb, int ldc)
{
    const int lx = get_local_id(0);
    const int ly = get_local_id(1);
    const int gx = get_group_id(0);
    const int gy = get_group_id(1);

    const int col0 = gx*TN + lx;  // column in C
    const int row0 = gy*TM + ly;  // row in C

    __local float Asub[TM][TK];
    __local float Bsub[TK][TN];

    float acc = 0.0f;

    const int num_k_tiles = (K + TK - 1) / TK;

    for (int t = 0; t < num_k_tiles; ++t) {
        const int kk = t * TK;

        // A : (TM x TK)
        for (int p = lx; p < TK; p += TN) {
            const int a_col = kk + p;
            Asub[ly][p] = (row0 < M && a_col < K) ? A[row0*lda + a_col] : 0.0f;
        }
        // B : (TK x TN)
        for (int q = ly; q < TK; q += TM) {
            const int b_row = kk + q;
            Bsub[q][lx] = (b_row < K && col0 < N) ? B[b_row*ldb + col0] : 0.0f;
        }
        barrier(CLK_LOCAL_MEM_FENCE);

        #pragma unroll
        for (int k = 0; k < TK; ++k) {
            acc = fma(Asub[ly][k], Bsub[k][lx], acc);
        }
        barrier(CLK_LOCAL_MEM_FENCE);
    }

    if (row0 < M && col0 < N) {
#if FUSE_BIAS
        acc += Bias[col0];
#endif
#if RELU
        acc = fmax(acc, 0.0f);
#endif
        C[row0*ldc + col0] = acc;
    }
}
"""

# ================================================================
# Program build (cached)
# ================================================================

def _get_program_cached(ctx: cl.Context, user_opts: str, TM, TN, TK, fuse_bias, use_relu, fastmath: bool):
    pad = 1 if os.getenv("AXIOMOS_OCL_PAD", "1") in ("1","true","True") else 0
    opts = [
        "-cl-std=CL1.2",
        f"-DTM={int(TM)}", f"-DTN={int(TN)}", f"-DTK={int(TK)}",
        f"-DFUSE_BIAS={1 if fuse_bias else 0}", f"-DRELU={1 if use_relu else 0}",
        f"-DPAD={pad}",
    ]

    # Activation de -cl-mad-enable contrôlée par AXIOMOS_OCL_MAD (indépendant de fastmath)
    mad_ok = os.getenv("AXIOMOS_OCL_MAD", "1").lower() in ("1","true","yes","on")
    if fastmath:
        opts += ["-cl-fast-relaxed-math"]
    if mad_ok:
        opts += ["-cl-mad-enable"]

    if user_opts:
        opts.append(user_opts)
    options = " ".join(o for o in opts if o).strip()

    ctx_k = _ctx_key(ctx)
    cache_key = (ctx_k, hash(options))
    prg = _PROG_CACHE.get(cache_key)
    if prg is not None:
        return prg
    prg = cl.Program(ctx, src_matmul_tiled).build(options=options)
    _PROG_CACHE[cache_key] = prg
    return prg

# ================================================================
# GEMM runner (tiled)
# ================================================================

def _run_matmul_tiled_ocl(M: int, N: int, K: int, repeats: int = 1, ax: Optional[dict] = None, want_profile: bool = False):
    ctx, q = _ctx_queue(profile=want_profile)

    A = _host_from_ax(ax, "hA", (M, K), np.float32)
    B = _host_from_ax(ax, "hB", (K, N), np.float32)
    bias = _host_from_ax(ax, "hBias", (N,), np.float32)
    if A is None:
        A = np.arange(M * K, dtype=np.float32).reshape(M, K)
    if B is None:
        B = np.arange(K * N, dtype=np.float32).reshape(K, N)

    dbg = os.getenv("AXIOMOS_OCL_DEBUG_DATA", "0") in ("1", "true", "True", "on", "ON")
    if dbg:
        print(f"[OCL][DBG] A.shape={A.shape} B.shape={B.shape}")
        print(f"[OCL][DBG] A[0,:8]   = {A[0,:8]}")
        print(f"[OCL][DBG] B[:8,0]   = {B[:8,0]}")
        cref = (A.astype(np.float32) @ B.astype(np.float32)).astype(np.float32)
        print(f"[OCL][DBG] refC.head = {cref.ravel()[:8]}")

    fuse_bias = bias is not None
    use_relu = False

    assert A.dtype == np.float32 and B.dtype == np.float32

    cache = _load_tuning_cache()
    key = _device_key_from_ctx(ctx)
    conf = cache.get(key, {"TM": 8, "TN": 16, "TK": 16, "fastmath": False})
    TM, TN, TK = conf.get("TM", 8), conf.get("TN", 16), conf.get("TK", 16)

    _env_tiles = _parse_tile_env()
    if _env_tiles:
        TM, TN, TK = _env_tiles

    TM, TN, TK = _cap_tiles_for_device(q.device, TM, TN, TK)
    print(f"[OCL] TM={TM} TN={TN} TK={TK}")

    fastmath_env = os.getenv("AXIOMOS_OCL_FASTMATH", "0") in ("1", "true", "True") or bool(conf.get("fastmath", False))

    if os.getenv("AXIOMOS_OCL_TUNE_SAVE", "0") in ("1","true","True"):
        cache[key] = {"TM": TM, "TN": TN, "TK": TK, "fastmath": fastmath_env}
        _save_tuning_cache(cache)

    if AXIOMOS_OCL_DEBUG:
        print(f"[OCL][DBG] shapes A=({M}, {K}) B=({K}, {N}) -> M={M} N={N} K={K}")

    auto = os.getenv("AXIOMOS_OCL_AUTOTUNE", "0").lower()
    need_tune = (auto in ("1", "true", "force"))
    if need_tune:
        if not (q.properties & cl.command_queue_properties.PROFILING_ENABLE):
            q = cl.CommandQueue(ctx, properties=cl.command_queue_properties.PROFILING_ENABLE)
        tuned = _autotune_tiles(ctx, q, M, N, K, fuse_bias, use_relu, fastmath_env, os.getenv("AXIOMOS_OCL_BUILD_OPTS", ""))
        if tuned:
            TM, TN, TK = _cap_tiles_for_device(q.device, tuned["TM"], tuned["TN"], tuned["TK"])
            cache = _load_tuning_cache()
            cache[_device_key_from_ctx(ctx)] = {"TM": TM, "TN": TN, "TK": TK, "fastmath": bool(fastmath_env)}
            _save_tuning_cache(cache)
            print(f"[OCL][TUNE] best tiles TM={TM} TN={TN} TK={TK} (saved)")

    user_opts = os.getenv("AXIOMOS_OCL_BUILD_OPTS", "")
    prg = _get_program_cached(ctx, user_opts, TM, TN, TK, fuse_bias, use_relu, fastmath_env)
    knl = _get_kernel(prg, "matmul_tiled")

    bytesA = int(M * K * 4)
    bytesB = int(K * N * 4)
    bytesC = int(M * N * 4)
    dA = _ensure_device_buffer(ctx, "A", bytesA, cl.mem_flags.READ_ONLY)
    dB = _ensure_device_buffer(ctx, "B", bytesB, cl.mem_flags.READ_ONLY)
    dC = _ensure_device_buffer(ctx, "C", bytesC, cl.mem_flags.WRITE_ONLY)
    dBias = _ensure_device_buffer(ctx, "Bias", int(N * 4), cl.mem_flags.READ_ONLY) if fuse_bias else None

    sA = _ensure_pinned_host_buf(ctx, "A", bytesA)
    sB = _ensure_pinned_host_buf(ctx, "B", bytesB)
    sC = _ensure_pinned_host_buf(ctx, "C", bytesC)
    sBias = _ensure_pinned_host_buf(ctx, "Bias", int(N * 4)) if fuse_bias else None

    hC = np.empty((M, N), dtype=np.float32)
    evt_h2d = []
    evt_h2d.append(_host_to_dev(q, A, dA, sA))
    evt_h2d.append(_host_to_dev(q, B, dB, sB))
    if fuse_bias:
        evt_h2d.append(_host_to_dev(q, bias, dBias, sBias))

    global_size = (_ceil_div(N, TN) * TN, _ceil_div(M, TM) * TM)
    local_size = (TN, TM)
    lda, ldb, ldc = K, N, N
    if fuse_bias:
        knl.set_args(dA, dB, dBias, dC,
                     np.int32(M), np.int32(N), np.int32(K),
                     np.int32(lda), np.int32(ldb), np.int32(ldc))
    else:
        knl.set_args(dA, dB, dC,
                     np.int32(M), np.int32(N), np.int32(K),
                     np.int32(lda), np.int32(ldb), np.int32(ldc))

    evt_k_all = []
    wait_for = evt_h2d
    for r in range(max(1, int(repeats))):
        evt_k = cl.enqueue_nd_range_kernel(q, knl, global_size, local_size, wait_for=wait_for)
        evt_k_all.append(evt_k)
        wait_for = [evt_k]

    evt_d2h = _dev_to_host(q, dC, hC, sC, wait_for=[evt_k_all[-1]])
    evt_d2h.wait()

    if want_profile:
        _log_profile("matmul", evt_h2d, evt_k_all[-1], evt_d2h)

    return hC
# ================================================================
# Safe int expression evaluator for sizes (M, N, K, arithmetic)
# ================================================================
_ALLOWED_BINOPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.FloorDiv: operator.floordiv, ast.Div: operator.floordiv,
    ast.Mod: operator.mod,
    ast.LShift: operator.lshift, ast.RShift: operator.rshift,
    ast.BitAnd: operator.and_, ast.BitOr: operator.or_, ast.BitXor: operator.xor,
}
_ALLOWED_UNOPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}

def _safe_eval_int(expr: str, scalars: dict) -> Optional[int]:
    """Safely evaluate small integer expressions (e.g., 'M*N', '1<<20') using provided scalars."""
    try:
        node = ast.parse(str(expr), mode="eval")
    except Exception:
        return None

    def _ev(n):
        if isinstance(n, ast.Expression):
            return _ev(n.body)
        if hasattr(ast, "Constant") and isinstance(n, ast.Constant):
            if isinstance(n.value, (int, float)):
                return int(n.value)
            raise ValueError
        if isinstance(n, ast.Num):  # Py<3.8
            return int(n.n)
        if isinstance(n, ast.Name):
            v = scalars.get(n.id, None)
            if isinstance(v, (int, np.integer)):
                return int(v)
            raise ValueError
        if isinstance(n, ast.BinOp) and type(n.op) in _ALLOWED_BINOPS:
            return _ALLOWED_BINOPS[type(n.op)](_ev(n.left), _ev(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in _ALLOWED_UNOPS:
            return _ALLOWED_UNOPS[type(n.op)](_ev(n.operand))
        raise ValueError

    try:
        return int(_ev(node))
    except Exception:
        return None

def eval_bytes(expr, scalars: dict) -> Optional[int]:
    """Evaluate an int expression like 'M*N', 'K*2', '1<<20' using given scalars."""
    if isinstance(expr, (int, np.integer)):
        return int(expr)
    if isinstance(expr, str):
        return _safe_eval_int(expr, scalars)
    return None


def _clean_sym(x) -> str:
    return str(x).lstrip("&*")

# ================================================================
# Public API expected by verify_axir/smoke_axir
# ================================================================
def dev_get_any(device_map, name):
    """If a device buffer named `name` exists, copy it back as float32 ndarray.
    Returns ndarray or None."""
    nm = _clean_sym(name)
    buf = device_map.get(nm)
    if buf is None:
        return None
    try:
        ctx, q = _get_ctx_queue()
        nbytes = int(getattr(buf, 'size', 0))
        if nbytes <= 0:
            return None
        n = nbytes // 4
        out = np.empty(n, dtype=np.float32)
        cl.enqueue_copy(q, out, buf).wait()
        return out
    except Exception:
        return None

__all__ = ["run"]


def run(ax, summary: bool = False, dump: str | None = None, repeats: int = 1, profile: bool = False):
    """
    Executed by verify_axir.run_backend_inproc(...).
    For matmul, returns a NumPy array (hC). For non-matmul quick kernels, returns
    {"dump": ...} when dump is requested, otherwise {"ok": True}.
    """
    if not isinstance(ax, dict):
        raise TypeError("[OCL] run(ax=...) expects an AXIR dict")

    # --- utiliser le contexte/queue global (cache process) ---
    ctx, queue = _get_ctx_queue()
    mf = cl.mem_flags

    # --- scalars top-level ---
    scalars: dict = {}
    # --- also load scalars from types.scalars (AXIR schema)
    tscal = ((ax.get("types") or {}).get("scalars") or {})
    for k, meta in tscal.items():
        if isinstance(meta, dict) and "value" in meta:
            try:
                v = meta["value"]
                scalars[k] = int(float(v))
            except Exception:
                pass
    for _name in ("M", "N", "K"):
        if _name in ax:
            try:
                scalars[_name] = int(ax[_name])
            except Exception:
                pass

    # --- état OCL minimal ---
    host: dict = {}
    device: dict = {}
    dev_sizes: dict = {}

    # --- boucle des ops : HostMake / DeviceMallocLike / Memcpy + capture KernelLaunch ---
    kernel = ""
    args = []
    for op in ax.get("ops", []) or []:
        t = op.get("op")

        # HostMake (avec résolution de shape symbolique)
        if t == "HostMake":
            name  = op["name"]
            dtstr = (op.get("dtype") or "float32").lower()
            dt    = np.float32 if "32" in dtstr else np.float32
            shape = _resolve_shape(ax, op.get("shape", []))
            fill  = (op.get("fill") or "zeros").lower()
            if fill == "zeros":
                host[name] = np.zeros(shape, dtype=dt)
            elif fill == "ones":
                host[name] = np.ones(shape, dtype=dt)
            elif fill == "linspace":
                start = float(op.get("start", 0.0))
                step  = float(op.get("step", 1.0))
                n = int(np.prod(shape)) if shape else 0
                arr = (start + step * np.arange(n, dtype=np.float32))
                if shape:
                    arr = arr.reshape(shape)
                host[name] = arr.astype(dt, copy=False)
            else:
                raise RuntimeError(f"[OCL] HostMake: fill inconnu: {fill}")
            continue

        # DeviceMallocLike
        if t == "DeviceMallocLike":
            like = op["like"]
            dst  = _clean_sym(op["dst"])
            if like in host:
                n = int(np.asarray(host[like]).size)
            else:
                ent_any = (ax.get("buffers", {}) or {}).get(like)
                ent = ent_any if isinstance(ent_any, dict) else {}
                n = 0
                if "shape" in ent:
                    try:
                        rs = _resolve_shape(ax, ent["shape"])
                        n = int(np.prod(rs))
                    except Exception:
                        n = 0
                elif "size" in ent:
                    expr = ent.get("size")
                    b = eval_bytes(expr, scalars)  # bytes
                    if isinstance(b, (int, np.integer)):
                        n = int(b) // 4 if (int(b) >= 4 and (int(b) % 4 == 0)) else 0
                    else:
                        n = 0
            if int(n) <= 0:
                # fallback safe size if unresolved
                try:
                    n = max(int(scalars.get("N", 16)), 16)
                except Exception:
                    n = 16
            device[dst] = cl.Buffer(ctx, mf.READ_WRITE, 4 * int(n))
            dev_sizes[dst] = int(n)
            continue

        # Memcpy (priorité aux buffers host)
        if t == "Memcpy":
            dst  = _clean_sym(op["dst"])
            src  = _clean_sym(op["src"])
            kind = (op.get("kind") or "H2D").upper()

            # Appel unique softmax avant D2H sur dY/Y
            if kind == "D2H" and src.lower() in ("dy", "y"):
                _run_softmax2d(ax, host, device, dev_sizes, op)

            if kind == "H2D":
                # ensure dst key is clean
                dst = _clean_sym(dst)
                if src in host:
                    src_arr = np.asarray(host[src], dtype=np.float32).ravel()
                else:
                    # infer size from existing device/meta or fallback to N
                    n = dev_sizes.get(dst, 0) or 0
                    try:
                        n = int(n)
                    except Exception:
                        n = 0
                    if n <= 0 and dst in device:
                        try:
                            n = int(device[dst].size // 4)
                        except Exception:
                            n = 0
                    if n <= 0:
                        meta_any = ((ax.get("buffers") or {}).get(dst))
                        meta = meta_any if isinstance(meta_any, dict) else {}
                        sh = meta.get("shape")
                        if sh:
                            try:
                                rs = _resolve_shape(ax, sh)
                                n = int(np.prod(rs))
                            except Exception:
                                n = 0
                    if n <= 0:
                        try:
                            n = max(int(scalars.get("N", 16)), 16)
                        except Exception:
                            n = 16
                    # déterministe comme le CPU : si src n'existe pas côté host → arange
                    if src not in host:
                        host[src] = np.arange(int(n), dtype=np.float32)
                    src_arr = np.asarray(host[src], dtype=np.float32).ravel()

                if dst not in device:
                    device[dst] = cl.Buffer(ctx, mf.READ_WRITE, 4 * int(src_arr.size))
                    dev_sizes[dst] = int(src_arr.size)

                cl.enqueue_copy(queue, device[dst], src_arr, is_blocking=True)
                continue

            elif kind == "D2H":
                # si la "source" côté device est en fait un ndarray (fallback CPU),
                # on copie directement sans passer par OpenCL.
                src_obj = device.get(src)
                if isinstance(src_obj, np.ndarray):
                    host[dst] = np.asarray(src_obj, dtype=np.float32).copy()
                    dev_sizes[src] = src_obj.size
                    continue

                n = dev_sizes.get(src) or (device[src].size // 4 if src in device else 0)
                if n and src in device:
                    tmp = np.empty(int(n), dtype=np.float32)
                    cl.enqueue_copy(queue, tmp, device[src], is_blocking=True)
                    host[dst] = tmp
                continue

        # --------- KernelLaunch ---------
        if t == "KernelLaunch":
            # récupérer kernel ou name
            kname = (op.get("kernel") or op.get("name") or "").lower()

            # Fallback CPU pour quelques kernels non-branchés OCL
            if (kname in ("vector_add", "vadd", "add")) or ("add" in kname and "reduce" not in kname):
                # Déduction N
                try:
                    N = int(_get_scalar(ax, "N") or dev_sizes.get("dC") or 1000)
                except Exception:
                    N = 1000

                # hôtes déterministes si absents
                if "hA" not in host:
                    host["hA"] = np.arange(N, dtype=np.float32)
                if "hB" not in host:
                    host["hB"] = np.arange(N, dtype=np.float32)
                hC = host["hA"].astype(np.float32) + host["hB"].astype(np.float32)
                host["hC"] = hC

                # miroir device *buffer* pour éviter host→host plus tard
                if "dC" not in device or int(dev_sizes.get("dC", 0)) < int(N):
                    device["dC"] = cl.Buffer(ctx, mf.READ_WRITE, 4 * int(N))
                    dev_sizes["dC"] = int(N)
                cl.enqueue_copy(queue, device["dC"], hC.astype(np.float32, copy=False), is_blocking=True)
                continue

            # Appel unique softmax si demandé
            if "softmax" in kname:
                _run_softmax2d(ax, host, device, dev_sizes, op)
                continue

            # capture du premier kernel pour dispatch plus bas
            if not kernel:
                kernel = kname
                args = [str(a).lstrip("&*") for a in op.get("args", [])]
            continue
            if "softmax" in kname:
                _run_softmax2d(ax, host, device, dev_sizes, op)
                continue

            # capture du premier kernel pour dispatch plus bas
            if not kernel:
                kernel = kname
                args = [str(a).lstrip("&*") for a in op.get("args", [])]
            continue
        # --------------------------------

    fm = AXIOMOS_OCL_FASTMATH

    # ---------- SAXPY via SAXPY_SRC + cache prog & kernel + profil ----------
    if kernel.startswith("saxpy"):
        fastmath = (os.getenv("AXIOMOS_OCL_FASTMATH","0") == "1")
        debug    = (os.getenv("AXIOMOS_OCL_DEBUG","0") == "1")

        # N & alpha
        N = None; alpha = 2.0
        for a0 in args:
            try:
                v = int(a0); N = v; continue
            except Exception:
                pass
            try:
                v = float(a0); alpha = v; continue
            except Exception:
                pass
        if N is None:
            N = int(ax.get("types",{}).get("scalars",{}).get("N",{}).get("value", 65536))

        # buffers device existants ou fallback (utilise host si présent)
        dA = device.get("dA"); dB = device.get("dB"); dC = device.get("dC")
        if dA is None or dB is None:
            hA = host.get("hA")
            hB = host.get("hB")
            if hA is None:
                hA = _host_from_ax(ax, "hA", (N,), np.float32)
            if hB is None:
                hB = _host_from_ax(ax, "hB", (N,), np.float32)
            if hA is None: hA = np.arange(N, dtype=np.float32)
            if hB is None: hB = np.arange(N, dtype=np.float32)
            dA = cl.Buffer(ctx, mf.READ_ONLY  | mf.COPY_HOST_PTR, hostbuf=hA)
            dB = cl.Buffer(ctx, mf.READ_ONLY  | mf.COPY_HOST_PTR, hostbuf=hB)
            device["dA"] = dA; device["dB"] = dB
            dev_sizes["dA"] = hA.size; dev_sizes["dB"] = hB.size
        if dC is None:
            dC = cl.Buffer(ctx, mf.WRITE_ONLY, N * 4)
            device["dC"] = dC
            dev_sizes["dC"] = N

        # run kernel
        evt = _run_saxpy_ocl(ctx, queue, dA, dB, dC, N, alpha, fastmath=fastmath, debug=debug)

        if dump:
            out = np.empty(N, dtype=np.float32)
            cl.enqueue_copy(queue, out, dC).wait()
            return {"dump": out}
        return {"ok": True}

    # ------------------- autres kernels rapides existants -------------------
    if kernel in ("vector_add", "vadd", "vector_add_kernel"):
        N = _guess_N(ax)
        out = _ocl_vadd(N, repeats=repeats, fastmath=fm, profile=profile)
        return {"dump": out} if dump else {"ok": True}

    if kernel in ("relu",):
        N = _guess_N(ax)
        out = _ocl_relu(N, repeats=repeats, fastmath=fm, profile=profile)
        return {"dump": out} if dump else {"ok": True}

    if kernel in ("mul", "vmul", "mul_vec"):
        N = _guess_N(ax)
        out = _ocl_mul(N, repeats=repeats, fastmath=fm, profile=profile)
        return {"dump": out} if dump else {"ok": True}

    if kernel in ("vexp", "exp"):
        N = _guess_N(ax)
        out = _ocl_vexp(N, repeats=repeats, fastmath=fm, profile=profile)
        return {"dump": out} if dump else {"ok": True}

    if kernel in ("reduce_sum",):
        N = _guess_N(ax)
        val = _ocl_reduce_sum(N, repeats=repeats, fastmath=fm, profile=profile)
        return {"dump": np.array([val], dtype=np.float32)} if dump else {"ok": True}

    if kernel in ("reduce_max",):
        N = _guess_N(ax)
        val = _ocl_reduce_max(N, repeats=repeats, fastmath=fm, profile=profile)
        return {"dump": np.array([val], dtype=np.float32)} if dump else {"ok": True}

    if kernel in ("reduce_argmax",):
        N = _guess_N(ax)
        val, idx = _ocl_reduce_argmax(N, repeats=repeats, fastmath=fm, profile=profile)
        if dump and dump.lower() in ("hout","dout","out","hval","dval"):
            return {"dump": np.array([val], dtype=np.float32)}
        if dump and dump.lower() in ("hidx","didx","idx"):
            return {"dump": np.array([idx], dtype=np.int32)}
        return {"ok": True}

    if kernel.startswith("softmax"):
        M, N = _guess_MN(ax)
        Y = _ocl_softmax2d(M, N, repeats=repeats, fastmath=fm, profile=profile)
        return {"dump": Y.reshape(M*N)} if dump else {"ok": True}

    if kernel.startswith("layernorm"):
        M, N = _guess_MN(ax)
        Y = _ocl_layernorm2d(M, N, repeats=repeats, fastmath=fm, profile=profile)
        return {"dump": Y.reshape(M*N)} if dump else {"ok": True}

    # ----------------------------------------------------
    # sinon: chemin matmul / GEMM
    # ----------------------------------------------------
    for _name in ("hA", "hB", "hC", "hBias"):
        if _name in host and isinstance(host[_name], np.ndarray):
            ax[_name] = host[_name]

    gemm_op = _find_gemm_op(ax)
    is_matmul_kernel = bool(kernel) and (("matmul" in kernel) or ("gemm" in kernel))

    if gemm_op is None and is_matmul_kernel:
        gemm_op = {}

    M = N = K = None

    if gemm_op is not None:
        alpha, beta = _resolve_alpha_beta(ax, gemm_op)

        if alpha == 0.0 and float(beta) != 1.0:
            try:
                M, N, K = _resolve_mnk(ax)
            except Exception:
                M = _read_int_scalar(ax, "M") or 1
                N = _read_int_scalar(ax, "N") or 1
            C_in = host.get("hC")
            if C_in is None:
                C_in = _host_from_ax(ax, "hC", (int(M), int(N)), np.float32)
            if C_in is None:
                C_in = np.zeros((int(M), int(N)), dtype=np.float32)
            host["hC"] = (float(beta) * np.asarray(C_in, dtype=np.float32)).reshape(int(M), int(N))

        M, N, K = _resolve_mnk(ax)

        C_prev = host.get("hC")
        if C_prev is None:
            C_prev = _host_from_ax(ax, "hC", (int(M), int(N)), np.float32)

        M, N = int(M), int(N)
        if float(alpha) == 0.0 and float(beta) == 1.0:
            C_prev_arr = np.asarray(C_prev, dtype=np.float32) if C_prev is not None else None
            if C_prev_arr is None:
                C_prev_arr = np.zeros((M, N), dtype=np.float32)
            elif C_prev_arr.ndim == 1 and C_prev_arr.size == M * N:
                C_prev_arr = C_prev_arr.reshape(M, N)
            elif C_prev_arr.ndim != 2 or C_prev_arr.shape != (M, N):
                C_prev_arr = np.zeros((M, N), dtype=np.float32)
            host["hC"] = C_prev_arr

        hC_core = _run_matmul_tiled_ocl(int(M), int(N), int(K),
                                   repeats=max(1, int(repeats)),
                                   ax=ax, want_profile=bool(profile))

        if isinstance(hC_core, np.ndarray) and hC_core.ndim == 1 and hC_core.size == M * N:
            hC_core = hC_core.reshape(M, N)

        alpha = _resolve_f(ax, gemm_op.get("alpha", _read_fscalar(ax, "alpha", 1.0)), 1.0)
        beta  = _resolve_f(ax, gemm_op.get("beta",  _read_fscalar(ax, "beta",  0.0)), 0.0)

        if float(beta) != 0.0 and C_prev is not None:
            C_prev_arr = np.asarray(C_prev, dtype=np.float32)
            if C_prev_arr.ndim == 1 and C_prev_arr.size == M * N:
                C_prev_arr = C_prev_arr.reshape(M, N)
            elif C_prev_arr.ndim == 2 and C_prev_arr.shape == (M, N):
                pass
            else:
                C_prev_arr = np.zeros((M, N), dtype=np.float32)
        else:
            C_prev_arr = np.zeros((M, N), dtype=np.float32)

        hC = (float(alpha) * np.asarray(hC_core, dtype=np.float32) + float(beta) * C_prev_arr).astype(np.float32)
        host["hC"] = hC

        # --- Normalisation du retour pour les tests ---
    if dump:
        v = host.get(dump) if isinstance(host, dict) else None
        if isinstance(v, np.ndarray):
            return {"dump": v}
        d = dev_get_any(device if isinstance(device, dict) else {}, dump)
        if d is not None:
            return {"dump": np.asarray(d, dtype=np.float32)}
    return {"ok": True}
