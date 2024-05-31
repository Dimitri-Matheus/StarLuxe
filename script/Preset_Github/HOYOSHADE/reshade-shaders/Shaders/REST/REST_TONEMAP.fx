#include "ReShade.fxh"

//By Krzysztof Narkowicz (https://knarkowicz.wordpress.com/2016/01/06/aces-filmic-tone-mapping-curve/)
float3 ACESFilm(float3 x)
{
    float a = 2.51f;
    float b = 0.03f;
    float c = 2.43f;
    float d = 0.59f;
    float e = 0.14f;
    return saturate((x*(a*x+b))/(x*(c*x+d)+e));
}

float3 ACESFilmInv(float3 x)
{
    float a = 2.51f;
    float b = 0.03f;
    float c = 2.43f;
    float d = 0.59f;
    float e = 0.14f;
    return -(sqrt(-(4.0*c*e-d*d)*x*x + 2.0*(2.0*a*e-b*d)*x + b*b) + d*x-b) / (2.0*(c*x-a));
}

void TonemapHDRtoSDR(in float4 pos : SV_Position, in float2 texcoord : Texcoord, out float4 o : SV_Target0)
{
    float4 color = tex2D(ReShade::BackBuffer, texcoord);
    color.rgb = ACESFilm(color.rgb);
    o = color;
}

void TonemapSDRtoHDR(in float4 pos : SV_Position, in float2 texcoord : Texcoord, out float4 o : SV_Target0)
{
    float4 color = tex2D(ReShade::BackBuffer, texcoord);
    color.rgb = ACESFilmInv(saturate(color.rgb));
    o = color;
}

technique REST_TONEMAP_TO_SDR
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = TonemapHDRtoSDR; 
    }
}

technique REST_TONEMAP_TO_HDR
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = TonemapSDRtoHDR; 
    }
}
