// LUT shader loading a custom .cube 1D LUT
// Author: BarricadeMKXX
// 2024-01-15
// License: MIT
// Credits to Marty McFly's LUT shader!

#include "ReShade.fxh"

#if __RESHADE__ < 60000
    #error "This ReShade version does not support .cube LUT files. Please update to at least ReShade 6.0.0."
#endif
uniform int iSample_Mode<
    ui_type = "combo";
    ui_label = "Sampling Mode";
    ui_items = "ReShade Internal\0Linear\0";
> = 1;

uniform float fLUT_Intensity <
    ui_type = "slider";
    ui_min = 0.00; ui_max = 1.00;
    ui_label = "LUT Intensity";
    ui_tooltip = "Overall intensity of the LUT effect.";
> = 1.00;

uniform float fLUT_AmountChroma <
	ui_type = "slider";
	ui_min = 0.00; ui_max = 1.00;
	ui_label = "LUT Chroma Amount";
	ui_tooltip = "Intensity of color/chroma change of the LUT.";
> = 1.00;

uniform float fLUT_AmountLuma <
	ui_type = "slider";
	ui_min = 0.00; ui_max = 1.00;
	ui_label = "LUT Luma Amount";
	ui_tooltip = "Intensity of luma change of the LUT.";
> = 1.00;

#ifndef SOURCE_CUBELUT1D_FILE
    #define SOURCE_CUBELUT1D_FILE "Neutral33-1D.cube"
#endif

#ifndef CUBE_1D_SIZE
    #define CUBE_1D_SIZE 33
#endif

texture1D texCube1D < source = SOURCE_CUBELUT1D_FILE; >
{
    Width = CUBE_1D_SIZE;
    Format = RGBA32F;
};

sampler1D sampCube1D
{
    Texture = texCube1D;
    AddressU = CLAMP;
    MinFilter = LINEAR; MagFilter = LINEAR; MipFilter = LINEAR;
};

float3 Cube1D_Liniar(sampler1D cube1D, float3 in_color, int cube_size)
{
    in_color = saturate(in_color) * (cube_size - 1);
    int3 indexL = int3(floor(in_color).xyz);
    int3 indexR = int3(ceil(in_color).xyz);
    float3 q = in_color - indexL;

    float3 colorL, colorR;
    for(int i = 0; i < 3; i++)
    {
        float3 tmp = tex1Dfetch(cube1D, indexL[i]).xyz;
        colorL[i] = tmp[i];
        tmp = tex1Dfetch(cube1D, indexR[i]).xyz;
        colorR[i] = tmp[i];
    }
    return float3(
        lerp(colorL.x, colorR.x, q.x),
        lerp(colorL.y, colorR.y, q.y),
        lerp(colorL.z, colorR.z, q.z)
    );
}

void PS_CubeLUT1D_Apply(float4 vpos : SV_Position, float2 texcoord : TEXCOORD, out float4 res : SV_TARGET0)
{
    float3 color = tex2D(ReShade::BackBuffer, texcoord.xy).xyz;

    float3 lutcolor;
    
    switch(iSample_Mode)
    {
        case 1:
        {
            lutcolor = Cube1D_Liniar(sampCube1D, color, CUBE_1D_SIZE);
            break;
        }
        default:
        {
            color = (color - 0.5) *((CUBE_1D_SIZE - 1.0) / CUBE_1D_SIZE) + 0.5;
            lutcolor = float3(tex1D(sampCube1D, color.x).x, tex1D(sampCube1D, color.y).y, tex1D(sampCube1D, color.z).z);
            break;
        }
    }

    lutcolor = lerp(color.xyz, lutcolor, fLUT_Intensity);

    color.xyz = lerp(normalize(color.xyz), normalize(lutcolor.xyz), fLUT_AmountChroma) *
	            lerp(length(color.xyz),    length(lutcolor.xyz),    fLUT_AmountLuma);

    res.xyz = color.xyz;
    res.w = 1.0;
}

technique CubeLUT1D<
    ui_label = "Cube LUT 1D";
>
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader = PS_CubeLUT1D_Apply;
    }
}