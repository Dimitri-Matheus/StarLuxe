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
    o.gbuffer = tex2Dlod(sGBufferTex, uv, 0);
    o.val     = tex2Dlod(gi, uv, 0);
    return o;
}

float3 srgb_to_acescg(float3 srgb)
{
    float3x3 m = float3x3(  0.613097, 0.339523, 0.047379,
                            0.070194, 0.916354, 0.013452,
                            0.020616, 0.109570, 0.869815);
    return mul(m, srgb);           
}

float3 acescg_to_srgb(float3 acescg)
{     
    float3x3 m = float3x3(  1.704859, -0.621715, -0.083299,
                            -0.130078,  1.140734, -0.010560,
                            -0.023964, -0.128975,  1.153013);
    return mul(m, acescg);            
}

float3 unpack_hdr(float3 color)
{
    color  = saturate(color);
    if(RT_USE_SRGB) color *= color;    
    if(RT_USE_ACESCG) color = srgb_to_acescg(color);
    color = color * rcp(1.04 - saturate(color));   
    
    return color;
}

float3 pack_hdr(float3 color)
{
    color =  1.04 * color * rcp(color + 1.0);   
    if(RT_USE_ACESCG) color = acescg_to_srgb(color);    
    color  = saturate(color);    
    if(RT_USE_SRGB) color = sqrt(color);   
    return color;     
}

float4 atrous(in VSOUT i, in sampler gi, int iteration, int mode)
{
    FilterSample center = fetch_sample(i.uv, gi);

    if(mode != 0)
        return center.val;

    float4 kernel = float4(2,4,8,16);
    float4 sigma_z = 16;
    float4 sigma_n = 5;
    float4 sigma_v = float4(0.02, 1, 1, 2);
    float curr_sigma_z = sigma_z[iteration];
    float curr_sigma_n = sigma_n[iteration];
    float curr_sigma_v = sigma_v[iteration];      

    float expectederrormult = sqrt(RT_RAY_AMOUNT);
    curr_sigma_v *= expectederrormult;   

    int stacksize = round(tex2D(sStackCounterTex, i.uv).x); 
    float mip = max(0, 2 - stacksize);

    float multi = exp2(mip);
    kernel += multi;
    
    float3 centerpos = Projection::uv_to_proj(i.uv, center.gbuffer.w);
    float4 value_sum = center.val * 0.000001; 
    float4 weight_sum = 0.00001;
   
    for(float x = -1; x <= 1; x++)
    for(float y = -1; y <= 1; y++)
    { 
       float2 uv = i.uv + float2(x, y) * kernel[iteration] * BUFFER_PIXEL_SIZE;
        FilterSample tap = fetch_sample(uv, gi);

        float3 tappos = Projection::uv_to_proj(uv, tap.gbuffer.w);
        float3 deltav = tappos - centerpos;

        float wn = dot(normalize(deltav), center.gbuffer.xyz); //0 when sample was horizontal to surface
        wn = saturate(1 - abs(wn));
        wn *= saturate(dot(tap.gbuffer.xyz, center.gbuffer.xyz));
        wn = pow(wn, curr_sigma_n);

        float wz = length(deltav) / center.gbuffer.w;
        wz = saturate(1 - wz * curr_sigma_z);
        wz *= saturate(1-abs(dot(normalize(deltav), tap.gbuffer.xyz)));

        wn = lerp(wn, 1, wz * wz);

        float4 wi;
        wi.rgb = dot(abs(pack_hdr(tap.val.rgb) - pack_hdr(center.val.rgb)), float3(0.3, 0.59, 0.11));
        wi.w = abs(tap.val.w - center.val.w);
        wi = exp2(-wi * float4(1, 1, 1, 4) * curr_sigma_v);

        float4 w = saturate(wn * wz * wi);

        value_sum += tap.val * w;
        weight_sum += w;
    }    

    float4 result = value_sum / weight_sum;
    return result;
}

} //Namespace