#include "ReShade.fxh"

void Flip(in float4 pos : SV_Position, in float2 texcoord : Texcoord, out float4 o : SV_Target0)
{
    texcoord.y = 1.0 - texcoord.y;
    o = tex2D(ReShade::BackBuffer, texcoord);
}

technique REST_FLIP
{
    pass
    {
        VertexShader = PostProcessVS;
        PixelShader  = Flip; 
    }
}

