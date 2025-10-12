// Demos/cuda/reduce_sum.cu
// AXIR demo — reduce sum (pattern simple, pas de shared mem pour la démo)
#define N 10000000

extern "C" __global__
void reduce_sum(const float* __restrict__ A,
                float* __restrict__ Out,
                int n /* ignoré si #define N présent */)
{
    // Version ultra naïve: chaque thread additionne une stride (le backend AXIR fera sa propre implémentation optimisée)
    float acc = 0.0f;
    int gid   = blockIdx.x * blockDim.x + threadIdx.x;
    int gsize = gridDim.x * blockDim.x;

    for (int i = gid; i < N; i += gsize) {
        acc += A[i];
    }

    // On ne fait pas de réduction atomique ici (la réduction réelle sera gérée par le backend)
    // Ce kernel est juste un "marqueur" pour la détection / traduction.
    if (gid == 0) {
        Out[0] = acc; // valeur partielle, le backend AXIR ne s'en sert pas
    }
}
