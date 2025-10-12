// Demos/cuda/vector_add.cu
// AXIR demo — vector add: C[i] = A[i] + B[i]
#define N 1048576  // facultatif: le runner peut aussi faire --infer-sizes 1048576

extern "C" __global__
void vector_add(const float* __restrict__ A,
                const float* __restrict__ B,
                float* __restrict__ C,
                int n /* ignoré si #define N présent */)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < N) {
        C[i] = A[i] + B[i];
    }
}
