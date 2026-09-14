// symoneural-cuda-probe - proves the estate CUDA authority end to end on the target:
// the binary is cross-built by nvcc from the NATIVE sysroot for sm_120, links libcudart
// from the TARGET sysroot, and at run time (through the target loader, libcuda.so.1 from
// the host driver) enumerates the device, launches a kernel and checks every element.
// Output is one JSON line; exit 0 on success, 2 when no CUDA device is reachable, 1 on
// any other failure. Copyright (c) 2026 SyMoNeuRaL. SPDX-License-Identifier: MIT
#include <cuda_runtime.h>
#include <cstdio>
#include <cstdlib>
#include <cmath>

__global__ void saxpy(int n, float a, const float *x, float *y)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) y[i] = a * x[i] + y[i];
}

static int fail(const char *what, cudaError_t e)
{
    std::fprintf(stderr, "symoneural-cuda-probe: %s: %s\n", what, cudaGetErrorString(e));
    return e == cudaErrorNoDevice || e == cudaErrorInsufficientDriver ? 2 : 1;
}

int main()
{
    int rt = 0, drv = 0, ndev = 0;
    cudaRuntimeGetVersion(&rt);
    cudaError_t e = cudaDriverGetVersion(&drv);
    if (e != cudaSuccess) return fail("cudaDriverGetVersion", e);
    e = cudaGetDeviceCount(&ndev);
    if (e != cudaSuccess) return fail("cudaGetDeviceCount", e);
    if (ndev < 1) return fail("no device", cudaErrorNoDevice);
    cudaDeviceProp p;
    if ((e = cudaGetDeviceProperties(&p, 0)) != cudaSuccess) return fail("cudaGetDeviceProperties", e);

    const int n = 1 << 20;
    float *hx = (float *)std::malloc(n * sizeof(float)), *hy = (float *)std::malloc(n * sizeof(float));
    for (int i = 0; i < n; i++) { hx[i] = 1.0f * (i % 97); hy[i] = 2.0f; }
    float *dx, *dy;
    if ((e = cudaMalloc(&dx, n * sizeof(float))) != cudaSuccess) return fail("cudaMalloc", e);
    if ((e = cudaMalloc(&dy, n * sizeof(float))) != cudaSuccess) return fail("cudaMalloc", e);
    cudaMemcpy(dx, hx, n * sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(dy, hy, n * sizeof(float), cudaMemcpyHostToDevice);
    saxpy<<<(n + 255) / 256, 256>>>(n, 3.0f, dx, dy);
    if ((e = cudaGetLastError()) != cudaSuccess) return fail("kernel launch", e);
    if ((e = cudaDeviceSynchronize()) != cudaSuccess) return fail("cudaDeviceSynchronize", e);
    cudaMemcpy(hy, dy, n * sizeof(float), cudaMemcpyDeviceToHost);
    double max_err = 0.0;
    for (int i = 0; i < n; i++) { double want = 3.0 * (i % 97) + 2.0; double d = std::fabs(hy[i] - want); if (d > max_err) max_err = d; }
    cudaFree(dx); cudaFree(dy); std::free(hx); std::free(hy);

    std::printf("{\"probe\":\"saxpy\",\"n\":%d,\"max_abs_err\":%.3g,\"device\":\"%s\",\"compute_capability\":\"%d.%d\","
                "\"sms\":%d,\"total_mem_mib\":%zu,\"runtime_version\":%d,\"driver_version\":%d,\"devices\":%d}\n",
                n, max_err, p.name, p.major, p.minor, p.multiProcessorCount, (size_t)(p.totalGlobalMem >> 20), rt, drv, ndev);
    return max_err == 0.0 ? 0 : 1;
}
