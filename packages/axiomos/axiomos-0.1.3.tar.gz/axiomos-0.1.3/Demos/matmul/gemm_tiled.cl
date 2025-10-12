// Demos/matmul/gemm_tiled.cl
#define TILE 16

__kernel void gemm_tiled(
    __global const float* A,
    __global const float* B,
    __global float* C,
    int M, int N, int K)
{
    int row = get_global_id(0);
    int col = get_global_id(1);

    __local float Asub[TILE][TILE];
    __local float Bsub[TILE][TILE];

    float acc = 0.0f;

    int localRow = get_local_id(0);
    int localCol = get_local_id(1);

    for (int t = 0; t < K; t += TILE) {
        int aRow = row;
        int aCol = t + localCol;
        if (aRow < M && aCol < K)
            Asub[localRow][localCol] = A[aRow * K + aCol];
        else
            Asub[localRow][localCol] = 0.0f;

        int bRow = t + localRow;
        int bCol = col;
        if (bRow < K && bCol < N)
            Bsub[localRow][localCol] = B[bRow * N + bCol];
        else
            Bsub[localRow][localCol] = 0.0f;

        barrier(CLK_LOCAL_MEM_FENCE);

        for (int k = 0; k < TILE; k++) {
            acc += Asub[localRow][k] * Bsub[k][localCol];
        }

        barrier(CLK_LOCAL_MEM_FENCE);
    }

    if (row < M && col < N) {
        C[row * N + col] = acc;
    }
}
