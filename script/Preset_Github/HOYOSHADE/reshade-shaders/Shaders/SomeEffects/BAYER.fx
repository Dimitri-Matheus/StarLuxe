/*------------------.
| :: Description :: |
'-------------------/
	This simulates the effect of the bayer mask, the pattern by wich digital cameras use to take single colour cells and generate multi coloured images.
	REBAY gives a typical visualisation of the bayer mask by colouring ceratain pixels with only their R, G or B colour relative to the mask.
	DEBAY gives innocdntly "reconstructs" the image from REBAY, note here that REBAY does not need to be ran for this
	rebayer red, green and blue settings included to make images "read" more like the underlying picture.
	Here's a quick explanation https://youtu.be/LWxu4rkZBLw .
*/


/*---------------.
| :: Includes :: |
'---------------*/


#include "ReShadeUI.fxh"
#include "ReShade.fxh"
//credit for this effect goes to the people who made cshade
/*------------------.
| :: UI Settings :: |
'------------------*/




uniform int PixelationSizeX < __UNIFORM_SLIDER_INT1
	ui_min = 1;
	ui_max = 50;
	ui_label = "Size of new pixels horizontally";
	ui_tooltip = "scales with size";
	ui_category = "Pixel options";
> = 2;

uniform int PixelationSizeY < __UNIFORM_SLIDER_INT1
	ui_min = 1;
	ui_max = 50;
	ui_label = "Size of new pixels vertically";
	ui_tooltip = "scales with size";
	ui_category = "Pixel options";
> = 2;

uniform bool on < 
	ui_label = "Rebayer";
	ui_tooltip = "Turns on a simulated bayer effect";
	ui_category = "effect";
> = TRUE;

uniform float3 RebayRed < 
	ui_label = "rebayer red";
	ui_tooltip = "RGB value for the simulated red";
	ui_category = "rebayer";
> = float3(1., 0., 0.);

uniform float3 RebayGreen < 
	ui_label = "rebayer green";
	ui_tooltip = "RGB value for the simulated green, note there are double the green pixels so these will need to be turned down to keep colours looking vaguely the same";
	ui_category = "rebayer";
> = float3(0., 1., 0.);


uniform float3 RebayBlue < 
	ui_label = "rebayer Blue";
	ui_tooltip = "RGB value for the simulated Blue";
	ui_category = "rebayer";
> = float3(0., 0., 1.);

/*-------------------------.
| :: Sampler and timers :: |
'-------------------------*/

#define AnnSampler ReShade::BackBuffer

/*-------------.
| :: Effect :: |
'-------------*/

float3 rebayer( float2 tex ){
	float2 PixelBlock = float2(float(PixelationSizeX), float(PixelationSizeY));
	int2 pointint = trunc((BUFFER_SCREEN_SIZE / PixelBlock) * tex);
	float2 Pointer = pointint * (PixelBlock / BUFFER_SCREEN_SIZE);
	float3 col = tex2D(AnnSampler, Pointer + trunc(PixelBlock*0.5)*BUFFER_PIXEL_SIZE).rgb;
	int2 cellp = pointint % 2;
	if(on){
		col = col *( cellp.x== cellp.y ?  (cellp.x==0? RebayRed: RebayBlue) : RebayGreen);
	}
	return col;
}

float3 Debayer( float2 tex ){
	float2 PixelBlock = float2(float(PixelationSizeX), float(PixelationSizeY));
	int2 pointint = trunc((BUFFER_SCREEN_SIZE / PixelBlock) * tex);
	float2 Pointer = pointint * (PixelBlock / BUFFER_SCREEN_SIZE);
	int2 cellp = pointint % 2;
		float3 col = float3(0,0,0);
	if(on){
		col.g = cellp.x != cellp.y ? tex2Dlod(AnnSampler, float4( Pointer + trunc(PixelBlock/2.)*BUFFER_PIXEL_SIZE, 0.0,0.0 )).g: 
		tex2Dlod(AnnSampler, float4( Pointer + float2(1.,0.)* (PixelBlock / BUFFER_SCREEN_SIZE) + trunc(PixelBlock/2.)*BUFFER_PIXEL_SIZE, 0.0,0.0 )).g;
		col.r =tex2Dlod(AnnSampler, float4( Pointer + (float2(0., 0.)-cellp)* (PixelBlock / BUFFER_SCREEN_SIZE) + trunc(PixelBlock/2.)*BUFFER_PIXEL_SIZE, 0.0,0.0 )).r;
		col.b =tex2Dlod(AnnSampler, float4( Pointer + (float2(1., 1.)-cellp)* (PixelBlock / BUFFER_SCREEN_SIZE) + trunc(PixelBlock/2.)*BUFFER_PIXEL_SIZE, 0.0,0.0 )).b;
	}else{
		col = tex2Dlod(AnnSampler, float4( Pointer + trunc(PixelBlock/2.)*BUFFER_PIXEL_SIZE, 0.0,0.0 )).rgb;
	}
	return col;
}

float3 PS_REBAY(float4 position : SV_Position, float2 texcoord : TEXCOORD) : SV_Target{  
	float3 color = rebayer(texcoord);
	return color.rgb;
}


float3 PS_DEBAY(float4 position : SV_Position, float2 texcoord : TEXCOORD) : SV_Target{  
	float3 color = Debayer(texcoord);
	return color.rgb;
}

/*-----------------.
| :: Techniques :: |
'-----------------*/
technique REBAY
{
	pass REBAY{
		VertexShader=PostProcessVS;
		PixelShader=PS_REBAY;
	}
	
}


technique DEBAY
{
	pass DEBAY{
		VertexShader=PostProcessVS;
		PixelShader=PS_DEBAY;
	}
	
}

