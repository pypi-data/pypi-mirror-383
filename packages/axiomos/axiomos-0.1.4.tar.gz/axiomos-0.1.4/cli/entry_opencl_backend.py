#!/usr/bin/env python3
# entry_opencl_backend.py — mince wrapper CLI pour Backends.opencl_backend.run
import argparse, json, pathlib, sys, numpy as np


def _extract_array(res):
    import numpy as np

    def _coerce(x):
        try:
            a = np.asarray(x)
            if a.dtype == object or a.size == 0:
                return None
            return a
        except Exception:
            return None

    def _best_from_dict(d):
        keys = ("hC", "C", "out", "result", "hOut", "data", "array")
        candidates = []

        # 1) clés prioritaires (avec coercition, pas seulement ndarray)
        for k in keys:
            if k in d:
                a = _coerce(d[k])
                if a is not None:
                    candidates.append(a)

        # 2) dump imbriqué
        if "dump" in d and isinstance(d["dump"], dict):
            a = _best_from_dict(d["dump"])
            if a is not None:
                candidates.append(a)

        # 3) balayage générique des valeurs
        for v in d.values():
            a = _coerce(v)
            if a is not None:
                candidates.append(a)

        if not candidates:
            return None

        # 4) on préfère les non-scalaires ; puis le plus "grand"
        non_scalar = [a for a in candidates if a.ndim >= 1 and a.size > 1]
        if non_scalar:
            return max(non_scalar, key=lambda a: (a.ndim, a.size))
        return candidates[0]  # dernier recours: scalaire

    # Cas simples
    a = _coerce(res)
    if a is not None and not (a.ndim == 0):
        return a

    # Dict -> meilleure valeur
    if isinstance(res, dict):
        return _best_from_dict(res)

    # Liste/tuple -> premier sous-élément valable
    if isinstance(res, (list, tuple)):
        best = None
        for v in res:
            a = _coerce(v)
            if a is not None and a.ndim >= 1 and a.size > 1:
                # on prend le plus gros qu'on trouve
                if best is None or (a.ndim, a.size) > (best.ndim, best.size):
                    best = a
        if best is not None:
            return best
        # dernier recours: n'importe quel convertible
        for v in res:
            a = _coerce(v)
            if a is not None:
                return a
        return None

    # Si on arrive ici et que c'est un scalaire: pas bon
    return None


def main():
    ap = argparse.ArgumentParser(description="OpenCL entry — run AXIR and dump a buffer")
    ap.add_argument("--axir", required=True, help="Path to AXIR JSON")
    ap.add_argument("--buffer", required=True, help="Buffer name to dump (e.g., hC, hOut)")
    ap.add_argument("--out", required=True, help="Output .npy path or directory")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--repeat", type=int, default=1)
    # aligne verify_axir: on active le profilage pour récupérer [OCL][PROFILE]
    ap.add_argument("--profile", action="store_true", default=True)
    args = ap.parse_args()

    ax = json.loads(pathlib.Path(args.axir).read_text(encoding="utf-8-sig"))

    try:
        from Backends.opencl_backend import run as run_ocl
    except ImportError:
        from backends.opencl_backend import run as run_ocl

    # --- Exécution backend ---
    result = run_ocl(
        ax,
        summary=args.summary,
        dump=args.buffer,
        repeats=args.repeat,
        profile=args.profile,
    )

    # --- Préparation du chemin de sortie robuste ---
    out_arg = pathlib.Path(args.out)
    if out_arg.suffix.lower() == ".npy":
        out_dir = out_arg.parent
        out_path = out_arg
    else:
        out_dir = out_arg
        out_path = out_dir / "verify_opencl_hC.npy"

    out_dir.mkdir(parents=True, exist_ok=True)

    # --- utilitaire centralisé de sauvegarde ---
    def _save_array(arr, path):
        try:
            arr = np.asarray(arr, dtype=np.float32)  # cast doux pour éviter dtype=object
        except Exception:
            pass  # si cast impossible, on sauve tel quel
        np.save(path, arr)
        print(f"[entry_ocl] saved {path} shape={getattr(arr, 'shape', None)}")

    # --- Passthrough explicite alpha=0.0 & beta=1.0 : on doit émettre hC quoi qu'il arrive ---
    try:
        if isinstance(result, dict):
            alpha = result.get("alpha")
            beta = result.get("beta")
            if (alpha == 0 or alpha == 0.0) and (beta == 1 or beta == 1.0):
                # Tentative D2H si buffer device présent
                queue = result.get("queue") or result.get("ocl_queue") or result.get("cl_queue")
                dC = (
                    result.get("buf_C")
                    or result.get("C_buf")
                    or result.get("device_C")
                    or result.get("clbuf_C")
                )
                hC = (
                    result.get("hC")
                    or result.get("host_C")
                    or result.get("C_host")
                    or result.get("C")
                    or result.get("out")
                    or result.get("hOut")
                )

                # Si dC est disponible, on reconstruit un host_C de la bonne forme/dtype et on copie
                if dC is not None and queue is not None:
                    try:
                        import pyopencl as cl  # protégé
                        shape = (
                            result.get("C_shape")
                            or result.get("shape_C")
                            or result.get("MN")
                            or result.get("shape")
                        )
                        dtype = result.get("C_dtype") or result.get("dtype_C") or result.get("dtype")

                        # Essayer d'inférer M,N
                        if isinstance(shape, (list, tuple)) and len(shape) >= 2:
                            M, N = int(shape[-2]), int(shape[-1])
                        else:
                            M = int(result.get("M") or result.get("rows") or result.get("M_out") or 0)
                            N = int(result.get("N") or result.get("cols") or result.get("N_out") or 0)
                            if (not M or not N) and hC is not None:
                                try:
                                    hc_arr = np.asarray(hC)
                                    if hc_arr.ndim >= 2:
                                        M, N = int(hc_arr.shape[-2]), int(hc_arr.shape[-1])
                                except Exception:
                                    pass

                        if not dtype:
                            dtype = np.float32
                        elif isinstance(dtype, str):
                            dtype = np.dtype(dtype)

                        if M and N:
                            host_C = np.empty((M, N), dtype=dtype)
                            cl.enqueue_copy(queue, host_C, dC).wait()
                            _save_array(host_C, out_path)
                            print("[entry_ocl] alpha=0,beta=1 passthrough: saved hC from device copy")
                            return
                    except Exception:
                        # Si la copie device échoue, on retombera sur le hC host si dispo
                        pass

                # Sinon, s'il y a déjà un hC côté host, on le sauvegarde tel quel
                if hC is not None:
                    _save_array(hC, out_path)
                    print("[entry_ocl] alpha=0,beta=1 passthrough: saved existing host hC")
                    return
    except Exception:
        # En cas d'erreur inattendue, on ne casse rien : on passe à la détection générique
        pass

    # --- sélection robuste de la sortie ---
    # 1) collecteurs utilitaires
    import os

    def _collect_ndarrays(obj):
        # numpy-like
        if hasattr(obj, "dtype") and hasattr(obj, "shape"):
            yield obj
            return
        # dict
        if isinstance(obj, dict):
            for v in obj.values():
                yield from _collect_ndarrays(v)
            return
        # séquences
        if isinstance(obj, (list, tuple)):
            for v in obj:
                yield from _collect_ndarrays(v)
            return

    prefer = {"hC": 3, "C": 2, "out": 2, "y": 1, "Y": 1}

    best = None
    best_score = -1

    # 2) passe 1 : si c'est un dict, scorer par nom + taille
    if isinstance(result, dict):
        for name, val in result.items():
            for arr in _collect_ndarrays(val):
                if getattr(arr, "ndim", 0) == 0:
                    continue
                score = int(getattr(arr, "size", 0)) + 10_000_000 * prefer.get(name, 0)
                if score > best_score:
                    best, best_score = arr, score
    else:
        # 3) passe 2 : générique
        for arr in _collect_ndarrays(result):
            if getattr(arr, "ndim", 0) == 0:
                continue
            score = int(getattr(arr, "size", 0))
            if score > best_score:
                best, best_score = arr, score

    # 4) passe 3 : compat avec l’ancien heuristique _extract_array
    if best is None:
        try:
            arr = _extract_array(result)
            if arr is not None and getattr(arr, "ndim", 0) >= 1 and getattr(arr, "size", 0) > 0:
                best = arr
        except Exception:
            pass

    # 5) fallback: tentative de readback explicite du buffer device C si exposé par le backend
    # On tente d’être “tolérant nommage” via le dict 'result'
    if best is None and isinstance(result, dict):
        try:
            import pyopencl as cl  # peut ne pas être dispo ici ; protégé

            queue = result.get("queue") or result.get("ocl_queue") or result.get("cl_queue")
            buf_C = result.get("buf_C") or result.get("C_buf") or result.get("device_C") or result.get("clbuf_C")
            shape = result.get("C_shape") or result.get("shape_C") or result.get("MN") or result.get("shape")
            dtype = result.get("C_dtype") or result.get("dtype_C") or result.get("dtype")
            # normalisation shape -> (M,N) si possible
            if isinstance(shape, (list, tuple)) and len(shape) >= 2:
                M, N = int(shape[-2]), int(shape[-1])
            else:
                M = int(result.get("M") or result.get("rows") or 0)
                N = int(result.get("N") or result.get("cols") or 0)
                if not (M and N):
                    M = int(result.get("M_out") or 0)
                    N = int(result.get("N_out") or 0)
            if not dtype:
                dtype = np.float32
            elif isinstance(dtype, str):
                # conversion simple
                dtype = np.dtype(dtype)
            host_C = np.empty((M, N), dtype=dtype)
            if queue is not None and buf_C is not None and M and N:
                cl.enqueue_copy(queue, host_C, buf_C).wait()
                best = host_C
                print("[OCL] fallback: readback C from device buffer")
        except Exception:
            pass

    # 6) dernier recours: alpha=0, beta=1 -> renvoyer C_init/host_C_init si exposé
    if best is None and isinstance(result, dict):
        try:
            alpha = result.get("alpha")
            beta = result.get("beta")
            if (alpha == 0 or alpha == 0.0) and (beta == 1 or beta == 1.0):
                init_keys = ("host_C_init", "C_init", "hC_init", "init_C")
                for k in init_keys:
                    if k in result:
                        arr = np.asarray(result[k])
                        if arr.ndim >= 1 and arr.size > 0:
                            best = arr
                            print("[OCL] fallback: alpha=0,beta=1 -> return initial C")
                            break
        except Exception:
            pass

    # 7) si toujours rien, écrire au moins un placeholder pour ne pas échouer
    if best is None:
        print("[entry_ocl] WARNING: nothing to save (no array found) — writing empty array placeholder")
        best = np.asarray([], dtype=np.float32)

    # Sauvegarde finale via utilitaire
    _save_array(best, out_path)


if __name__ == "__main__":
    main()
