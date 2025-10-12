// Demos/cuda/saxpy.cu
// AXIR demo — SAXPY: C[i] = alpha * A[i] + B[i]
#define N 1048576
#define ALPHA 2.0f

extern "C" __global__
void saxpy(const float* __restrict__ A,
           const float* __restrict__ B,
           float* __restrict__ C,
           float alpha,
           int n /* ignoré si #define N présent */)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < N) {
        C[i] = ALPHA * A[i] + B[i]; // le frontend passera alpha=2.0f par défaut si besoin
    }
}
