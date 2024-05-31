/*=============================================================================

    Copyright (c) Pascal Gilcher. All rights reserved.

 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential

=============================================================================*/

#pragma once

/*===========================================================================*/

namespace Denoise
{

struct FilterSample
{
    float4 gbuffer;
    float4 val;
};

FilterSample fetch_sample(in float2 uv, sampler gi)
{
    FilterSample o;
    o.gbuffer = tex2Dlod(sGBufferTex, float4(uv, 0, 0));
    o.val     = tex2Dlod(gi, float4(uv, 0, 0));
    return o;
}

float4 filter(in VSOUT i, in sampler gi, int iteration, bool skip)
{
    FilterSample center = fetch_sample(i.uv, gi);

    if(skip)
        return center.val;

    float4 value_sum = 0;
    float weight_sum = 0.00001; 
#if 1
float kernel[4] = {1.5,3.5,7,15};
    float sigma_z[4] = {0.7,0.7,0.7,0.7};
    float sigma_n[4] = {0.75,1.5,1.5,5};
    float sigma_v[4] = {0.035,0.6,1.4,5};
#else
    float kernel[4] = {SIZE.x, SIZE.y, SIZE.z, SIZE.w}; 
    float sigma_z[4] = {WEIGHTZ.x, WEIGHTZ.y, WEIGHTZ.z, WEIGHTZ.w};
    float sigma_n[4] = {WEIGHTN.x, WEIGHTN.y, WEIGHTN.z, WEIGHTN.w};
    float sigma_v[4] = {WEIGHTV.x, WEIGHTV.y, WEIGHTV.z, WEIGHTV.w};
#endif
    float expectederror = sqrt(RT_RAY_AMOUNT);

    for(float x = -1; x <= 1; x++)
    for(float y = -1; y <= 1; y++)
    {        
        float2 uv = i.uv + float2(x, y) * kernel[iteration] * qUINT::PIXEL_SIZE;
        FilterSample tap = fetch_sample(uv, gi);

        //calculate weights
        float wz = sigma_z[iteration] * 16.0 *  (1.0 - tap.gbuffer.w / center.gbuffer.w);
        wz = saturate(0.5 - lerp(wz, abs(wz), 0.75));

        float wn = saturate(dot(tap.gbuffer.xyz, center.gbuffer.xyz) * (sigma_n[iteration] + 1) - sigma_n[iteration]);
        float wi = dot(abs(tap.val - center.val), float4(0.3, 0.59, 0.11, 3.0));
 
        wi = exp(-wi * wi * 2.0 * sigma_v[iteration] * expectederror);

        wn = lerp(wn, 1, saturate(wz * 1.42 - 0.42)); //adjust n if z is very close

        float w = saturate(wz * wn * wi);

        value_sum += tap.val * w;
        weight_sum += w;
    }

    float4 result = value_sum / weight_sum;
    return result;
}

} //Namespace