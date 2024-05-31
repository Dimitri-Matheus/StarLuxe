// Chance 'Valeour' Millar
// Updated for Reshade 3.0 on 27/11/2016
// Follow me on Twitter @ValeourM for whatever reasons you can imagine.

// Colour of the green screen
uniform float3 greenScreen = float3(0, 1, 0);

// How far into the depth to be cut off.
uniform float depthCutoff = 0.95;

// Need the reshade header.
#include "Reshade.fxh"

// Pixel shader
void PS_GreenScreenDepth(in float4 position : SV_Position, in float2 texcoord : TEXCOORD0, out float3 color : SV_Target)
{
	// Fairly standard shader. Get the colour, get the depth.
	// If the depth is less than the cutoff, change the colour to green.
	color = tex2D(ReShade::BackBuffer, texcoord).rgb;

	// Reverse the depth
	float depth = 1 - ReShade::GetLinearizedDepth(texcoord).r;

	if( depth < depthCutoff )
	{
		color = greenScreen;
	}
}

technique GreenScreen_Tech
{
	pass
	{
		VertexShader = PostProcessVS;
		PixelShader = PS_GreenScreenDepth;
	}
}