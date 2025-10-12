import numpy as np

# adapte si tu changes M,N,K
M=N=K=512
A = np.arange(M*K, dtype=np.float32).reshape(M,K)
B = (2*np.arange(K*N, dtype=np.float32)).reshape(K,N)
bias = np.ones(N, dtype=np.float32)

act = "relu"  # "gelu" ou "none" pour tester d'autres modes
C = A @ B + bias
if act == "relu":
    C = np.maximum(0, C)
elif act == "gelu":
    # approx rapide GELU (même forme que le backend)
    C = 0.5*C*(1.0 + np.tanh(np.sqrt(2.0/np.pi)*(C+0.044715*(C**3))))

ref = np.load("build/hC.npy").reshape(M,N)
print("max|diff| =", float(np.max(np.abs(C - ref))))
print("max rel   =", float(np.max(np.abs(C - ref) / (np.abs(C)+1e-7))))
