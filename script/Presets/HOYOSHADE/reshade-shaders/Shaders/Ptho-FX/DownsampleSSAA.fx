/**
	DownsampleSSAA version 1.0
	by PthoEastCoast

	Makes it look as if the image was downsampled from it's native resolution to a custom lower resolution. 
	Giving the impression of rendering at a lower resolution but with higher image quality comparable to supersampling.
	It blurs the original image and then pixelates the image after blurring.
	For best image quality - run the game at the native resolution of your display. (higher render resolution = higher quality anti-aliasing/pixelation when downsampling)
**/

#include "ReShadeUI.fxh"

uniform int UpscalingSetting
<
	ui_type = "combo";
	ui_items =	"Nearest-neighbor" "\0"
				"Bilinear" "\0"
				"Weighted Bilinear 1" "\0"
				"Weighted Bilinear 2" "\0"
				"Weighted Bilinear 3" "\0"
				"Weighted Bilinear 4" "\0";
	ui_label = "Image upscaling setting";
	ui_tooltip = "Sets the method used to upscale the downsampled image.\n"
	"Nearest-neighbor provides a pixel sharp image.\n"
	"Bilinear provides a smooth image by blending between neighboring pixels.\n"
	"Weighted Bilinear 1-4 will provide a progressively sharper image than Bilinear.";
> = 4;

uniform int VerticalResolution 
< __UNIFORM_SLIDER_INT1
	ui_min = 240.0; ui_max = 1080.0;
	ui_tooltip = "Sets the vertical resolution of the downsampled image (horizontal resolution is automagically calculated)";
> = 480.0;

uniform int DownsampleBlurFactor
< __UNIFORM_SLIDER_INT1
	ui_min = 0.0; ui_max = 5.0;
	ui_tooltip = "Sets the amount of blur applied to the image when downsampling. (Lower values produce a sharper but more aliased image. Higher values produce a smoother but blurrier image.)";
> = 1.0;

#include "ReShade.fxh"

#define numOfSamplesRight 14.0

texture BoxBlurHTex < pooled = true; > { Width = BUFFER_WIDTH; Height = BUFFER_HEIGHT; Format = RGBA8; };
texture BoxBlurVTex < pooled = true; > { Width = BUFFER_WIDTH; Height = BUFFER_HEIGHT; Format = RGBA8; };

sampler BoxBlurHSampler{ Texture = BoxBlurHTex; };
sampler BoxBlurVSampler{ Texture = BoxBlurVTex; };

float4 BoxBlurHorizontalPass(in float4 pos : SV_Position, in float2 texcoord : TEXCOORD) : COLOR
{
	float aspectRatio = 1.0 / BUFFER_ASPECT_RATIO;
	float pixelUVSize = (1.0 / (float)VerticalResolution) * aspectRatio;
	float smoothScale = (float)DownsampleBlurFactor * 0.05 + 0.25;
	float uvDistBetweenSamples = (pixelUVSize * smoothScale) / numOfSamplesRight;

	float4 accumulatedColor = float4(0.0, 0.0, 0.0, 1.0);

	for (float i = -numOfSamplesRight; i <= numOfSamplesRight; i++)
	{
		accumulatedColor = accumulatedColor + tex2D( ReShade::BackBuffer, texcoord + float2(i * uvDistBetweenSamples, 0.0) );
	}
	accumulatedColor = accumulatedColor * (1.0 / (numOfSamplesRight * 2.0 + 1.0));

	return accumulatedColor;
}

float4 BoxBlurVerticalPass(in float4 pos : SV_Position, in float2 texcoord : TEXCOORD) : COLOR
{
	float pixelUVSize = 1.0 / (float)VerticalResolution;
	float smoothScale = (float)DownsampleBlurFactor * 0.05 + 0.25;
	float uvDistBetweenSamples = (pixelUVSize * smoothScale) / numOfSamplesRight;

	float4 accumulatedColor = float4(0.0, 0.0, 0.0, 1.0);

	for (float i = -numOfSamplesRight; i <= numOfSamplesRight; i++)
	{
		accumulatedColor = accumulatedColor + tex2D( BoxBlurHSampler, texcoord + float2(0.0, i * uvDistBetweenSamples) );
	}
	accumulatedColor = accumulatedColor * (1.0 / (numOfSamplesRight * 2.0 + 1.0));

	return accumulatedColor;
}

float3 PixelationPass(in float4 pos : SV_Position, in float2 texcoord : TEXCOORD) : COLOR
{
	float aspectRatio = 1.0 / BUFFER_ASPECT_RATIO;
	float PixelUVSize = 1.0 / (float)VerticalResolution;

	float pixelUVSizeX = PixelUVSize * aspectRatio;
	float pixelUVSizeY = PixelUVSize;

	float texcoordDistFromPixelX = texcoord.x % pixelUVSizeX;
	float texcoordDistFromPixelY = texcoord.y % pixelUVSizeY;

	float2 thisCoord;
	thisCoord.x = texcoord.x - texcoordDistFromPixelX;
	thisCoord.y = texcoord.y - texcoordDistFromPixelY;
	float3 thisPixelColor = tex2D(BoxBlurVSampler, thisCoord).rgb;

	if (UpscalingSetting == 0)
	{
		return thisPixelColor;
	}

	float2 nextCoordUp;
	nextCoordUp.x = thisCoord.x;
	nextCoordUp.y = thisCoord.y + pixelUVSizeY;
	float3 nextPixelColorUp = tex2D(BoxBlurVSampler, nextCoordUp).rgb;

	float2 nextCoordRight;
	nextCoordRight.x = thisCoord.x + pixelUVSizeX;
	nextCoordRight.y = thisCoord.y;
	float3 nextPixelColorRight = tex2D(BoxBlurVSampler, nextCoordRight).rgb;

	float2 nextCoordUpRight;
	nextCoordUpRight.x = thisCoord.x + pixelUVSizeX;
	nextCoordUpRight.y = thisCoord.y + pixelUVSizeY;
	float3 nextPixelColorUpRight = tex2D(BoxBlurVSampler, nextCoordUpRight).rgb;

	float tx = texcoordDistFromPixelX / pixelUVSizeX;
	float ty = texcoordDistFromPixelY / pixelUVSizeY;

	float powerAmount = 0.75 + UpscalingSetting * 0.25;
		
	tx = tx < 0.5 ? pow( abs(tx), powerAmount ) : pow( abs(tx), 1.0 / powerAmount );
	ty = ty < 0.5 ? pow( abs(ty), powerAmount ) : pow( abs(ty), 1.0 / powerAmount );

	float3 lerpCurrentToRight = lerp(thisPixelColor, nextPixelColorRight, tx);
	float3 lerpUpToUpRight = lerp(nextPixelColorUp, nextPixelColorUpRight, tx);

	float3 pixelColor = lerp(lerpCurrentToRight, lerpUpToUpRight, ty);

	return pixelColor;
}

technique DownsampleSSAA
{
	pass BoxBlurHorizontalPass
	{
		VertexShader = PostProcessVS;
		PixelShader = BoxBlurHorizontalPass;
		RenderTarget = BoxBlurHTex;
	}
	pass BoxBlurVerticalPass
	{
		VertexShader = PostProcessVS;
		PixelShader = BoxBlurVerticalPass;
		RenderTarget = BoxBlurVTex;
	}
	pass PixelationPass
	{
		VertexShader = PostProcessVS;
		PixelShader = PixelationPass;
	}
}
