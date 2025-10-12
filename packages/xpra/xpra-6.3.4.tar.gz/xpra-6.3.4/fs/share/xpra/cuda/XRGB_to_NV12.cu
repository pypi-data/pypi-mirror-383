/*
 * This file is part of Xpra.
 * Copyright (C) 2013-2024 Antoine Martin <antoine@xpra.org>
 * Xpra is released under the terms of the GNU GPL v2, or, at your option, any
 * later version. See the file COPYING for details.
 */

#include <stdint.h>

// Y = 0.257 * R + 0.504 * G + 0.098 * B + 0
#define YR 0.257
#define YG 0.504
#define YB 0.098
#define YC 0
// U = -0.148 * R - 0.291 * G + 0.439 * B + 128
#define UR -0.148
#define UG -0.291
#define UB 0.439
#define UC 128
// V = 0.439 * R - 0.368 * G - 0.071 * B + 128
#define VR 0.439
#define VG -0.368
#define VB -0.071
#define VC 128

extern "C" __global__ void XRGB_to_NV12(uint8_t *srcImage, int src_w, int src_h, int srcPitch,
                          uint8_t *dstImage, int dst_w, int dst_h, int dstPitch,
                          int w, int h)
{
    const uint32_t gx = blockIdx.x * blockDim.x + threadIdx.x;
    const uint32_t gy = blockIdx.y * blockDim.y + threadIdx.y;
    const uint32_t src_y = gy*2 * src_h / dst_h;
    const uint32_t src_x = gx*2 * src_w / dst_w;

    if ((src_x < w) & (src_y < h)) {
        //4 bytes per pixel, and 2 pixels width/height at a time:
        //byte index:
        uint32_t si = (src_y * srcPitch) + src_x * 4;

        //we may read up to 4 32-bit RGB pixels:
        uint8_t R[4];
        uint8_t G[4];
        uint8_t B[4];
        uint8_t j = 0;
        R[0] = srcImage[si+1];
        G[0] = srcImage[si+2];
        B[0] = srcImage[si+3];
        for (j=1; j<4; j++) {
            R[j] = R[0];
            G[j] = G[0];
            B[j] = B[0];
        }

        //write up to 4 Y pixels:
        uint32_t di = (gy * 2 * dstPitch) + gx * 2;
        dstImage[di] = __float2int_rn(YR * R[0] + YG * G[0] + YB * B[0] + YC);
        if (gx*2 + 1 < src_w) {
            R[1] = srcImage[si+5];
            G[1] = srcImage[si+6];
            B[1] = srcImage[si+7];
            dstImage[di + 1] = __float2int_rn(YR * R[1] + YG * G[1] + YB * B[1] + YC);
        }
        if (gy*2 + 1 < src_h) {
            si += srcPitch;
            di += dstPitch;
            R[2] = srcImage[si+1];
            G[2] = srcImage[si+2];
            B[2] = srcImage[si+3];
            dstImage[di] = __float2int_rn(YR * R[2] + YG * G[2] + YB * B[2] + YC);
            if (gx*2 + 1 < src_w) {
                R[3] = srcImage[si+5];
                G[3] = srcImage[si+6];
                B[3] = srcImage[si+7];
                dstImage[di + 1] = __float2int_rn(YR * R[3] + YG * G[3] + YB * B[3] + YC);
            }
        }

        //write 1 U and 1 V pixel:
        float u = 0;
        float v = 0;
        for (j=0; j<4; j++) {
            u += UR * R[j] + UG * G[j] + UB * B[j] + UC;
            v += VR * R[j] + VG * G[j] + VB * B[j] + VC;
        }
        di = (dst_h + gy) * dstPitch + gx * 2;
        dstImage[di]      = __float2int_rn(u / 4.0);
        dstImage[di + 1]  = __float2int_rn(v / 4.0);
    }
}
