// Demos/cuda/matmul.cu
// AXIR demo — GEMM naïf: C[M,N] = A[M,K] * B[K,N]
#define M 256
#define N 256
#define K 256

extern "C" __global__
void matmul(const float* __restrict__ A,
            const float* __restrict__ B,
            float* __restrict__ C,
            int m /* ignoré si #define M présent */,
            int n /* ignoré si #define N présent */,
            int k /* ignoré si #define K présent */)
{
    int row = blockIdx.y * blockDim.y + threadIdx.y; // y = M
    int col = blockIdx.x * blockDim.x + threadIdx.x; // x = N

    if (row < M && col < N) {
        float acc = 0.0f;
        for (int kk = 0; kk < K; ++kk) {
            acc += A[row * K + kk] * B[kk * N + col];
        }
        C[row * N + col] = acc;
    }
}
