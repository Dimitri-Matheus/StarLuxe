/*------------------.
| :: Description :: |
'-------------------/

	quantizer and ditherer in CMYK colourspace (the one your printer has)
	nothing fancy, just converts RGB to CMYK and back
	the black reduce function allows for some odd artistic effects
	
	includes the blue noise pattern from here
	https://momentsingraphics.de/BlueNoise.html
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
	ui_max = 30;
	ui_label = "Size of new pixels horizontally";
	ui_tooltip = "scales with size";
	ui_category = "Pixel size";
> = 2;

uniform int PixelationSizeY < __UNIFORM_SLIDER_INT1
	ui_min = 1;
	ui_max = 30;
	ui_label = "Size of new pixels vertically";
	ui_tooltip = "scales with size";
	ui_category = "Pixel size";
> = 2;


uniform int4 GreyLevel < 
	ui_label = "CMYK levels";
	ui_tooltip = "gives you levels of the CMYK colours, 0 and 1 result in a singular level";
	ui_category = "colour quantisation";
> = (4,4,4,4);

uniform float4 addto < 
	ui_label = "add colours";
	ui_tooltip = "adds to each level after quantization";
	ui_category = "colour quantisation";
> = (0,0,0,0);

uniform int blackmode < __UNIFORM_SLIDER_INT1
	ui_min = 0;
	ui_max = 2;
	ui_label = "black subtraction mode";
	ui_tooltip = "0=off, 1=binary, 2=linear";
	ui_category = "black reduce";
> = 0;

uniform float trueblacksel < __UNIFORM_SLIDER_FLOAT1
	ui_min = 0;
	ui_max = 1;
	ui_label = "full black select";
	ui_tooltip = "the lower the more gets affected by the black reduction";
	ui_category = "black reduce";
> = 0.95;

uniform float trueblack < __UNIFORM_SLIDER_FLOAT1
	ui_min = -3;
	ui_max = 20;
	ui_label = "full black subtract";
	ui_tooltip = "the higher the lessdark your black is";
	ui_category = "black reduce";
> = 0.2;

uniform float4 dithdeg < 
	ui_label = "dither degree";
	ui_tooltip = "gives you levels of grey, 1 results in no levels";
	ui_category = "dither";
> = (1,1,1,1);

uniform int dithmod <__UNIFORM_SLIDER_INT1
	ui_min = 0;
	ui_max = 4;
	ui_label = "dither mode";
	ui_tooltip = "selects dither mask, 0 means no mask";
	ui_category = "dither";
> = 2;

uniform int4 xdithoffset < 
	ui_label = "x offset";
	ui_tooltip = "offsets dithermap vertically";
	ui_category = "dithermap offset";
> = (0,0,0,0);
uniform int4 ydithoffset < 
	ui_label = "y offset";
	ui_tooltip = "offsets dithermap horizontally";
	ui_category = "dithermap offset";
> = (0,0,0,0);

uniform bool flipc < 
	ui_label= "flip c dithermat";
	ui_category = "dithermap offset";
> = FALSE;

uniform bool flipm < 
	ui_label= "flip m dithermat";
	ui_category = "dithermap offset";
> = FALSE;

uniform bool flipy < 
	ui_label= "flip y dithermat";
	ui_category = "dithermap offset";
> = FALSE;

uniform bool flipk < 
	ui_label= "flip k dithermat";
	ui_category = "dithermap offset";
> = TRUE;

/*-------------------------.
| :: Sampler and timers :: |
'-------------------------*/

#define AnnSampler ReShade::BackBuffer

texture BlueNoise < source ="HDR_LA_3.png" ; > { Width = 256; Height = 256; };
sampler BlueNoiseSamp { Texture = BlueNoise; AddressU = REPEAT;	AddressV = REPEAT;	AddressW = REPEAT;};


/*-------------.
| :: Effect :: |
'-------------*/
float3 CMYK_doer( float2 tex ){
	//get coordinates and colour
	int2 PixelBlock = int2(PixelationSizeX, PixelationSizeY);
	int2 pointint = trunc((tex/ (PixelBlock*BUFFER_PIXEL_SIZE )));
	float3 col = tex2D(AnnSampler, pointint * (PixelBlock*BUFFER_PIXEL_SIZE)+trunc(PixelBlock/2-0.001)*BUFFER_PIXEL_SIZE+0.5*BUFFER_PIXEL_SIZE).rgb;

	//convert to CMYK
	float4 CMYK = float4(0,0,0,0);
	CMYK.w = 1-max(col.r, max(col.b,col.g ));
	CMYK.xyz = (1-col.rgb-CMYK.w)/(1-CMYK.w);

	//add dither mask		
	if(dithmod == 1){
		static const float DITHER_MATRIX1[9] = {-1,1,-1,1,0,1,-1,1,-1};
		CMYK.x = CMYK.x +DITHER_MATRIX1[((pointint.x+xdithoffset.x )%3)*(1+2*flipc)+((pointint.y+ydithoffset.x) % 3)*(3-2*flipc)]/((GreyLevel.x-1)*6./dithdeg.x);
		CMYK.y = CMYK.y +DITHER_MATRIX1[((pointint.x+xdithoffset.y )%3)*(1+2*flipm)+((pointint.y+ydithoffset.y) % 3)*(3-2*flipm)]/((GreyLevel.y-1)*6./dithdeg.y);
		CMYK.z = CMYK.z +DITHER_MATRIX1[((pointint.x+xdithoffset.z )%3)*(1+2*flipy)+((pointint.y+ydithoffset.z) % 3)*(3-2*flipy)]/((GreyLevel.z-1)*6./dithdeg.z);
		CMYK.w = CMYK.w +DITHER_MATRIX1[((pointint.x+xdithoffset.w )%3)*(1+2*flipk)+((pointint.y+ydithoffset.w) % 3)*(3-2*flipk)]/((GreyLevel.w-1)*6./dithdeg.w);
	
	}else if (dithmod == 2){
		static const float DITHER_MATRIX1[9]= {0.75,-0.75,0.25,-0.5,-1,0,0.5,-0.25,1};
		CMYK.x = CMYK.x +DITHER_MATRIX1[((pointint.x+xdithoffset.x )%3)*(1+2*flipc)+((pointint.y+ydithoffset.x) % 3)*(3-2*flipc)]/((GreyLevel.x-1)*6./dithdeg.x);
		CMYK.y = CMYK.y +DITHER_MATRIX1[((pointint.x+xdithoffset.y )%3)*(1+2*flipm)+((pointint.y+ydithoffset.y) % 3)*(3-2*flipm)]/((GreyLevel.y-1)*6./dithdeg.y);
		CMYK.z = CMYK.z +DITHER_MATRIX1[((pointint.x+xdithoffset.z )%3)*(1+2*flipy)+((pointint.y+ydithoffset.z) % 3)*(3-2*flipy)]/((GreyLevel.z-1)*6./dithdeg.z);
		CMYK.w = CMYK.w +DITHER_MATRIX1[((pointint.x+xdithoffset.w )%3)*(1+2*flipk)+((pointint.y+ydithoffset.w) % 3)*(3-2*flipk)]/((GreyLevel.w-1)*6./dithdeg.w);
	}else if(dithmod == 3){
		static const float DITHER_MATRIX1[4]= {-1,0.3333,1,-0.33333};
		CMYK.x = CMYK.x +DITHER_MATRIX1[((pointint.x+xdithoffset.x )%2)*(1+1*flipc)+((pointint.y+ydithoffset.x) % 2)*(2-1*flipc)]/((GreyLevel.x-1)*6./dithdeg.x);
		CMYK.y = CMYK.y +DITHER_MATRIX1[((pointint.x+xdithoffset.y )%2)*(1+1*flipm)+((pointint.y+ydithoffset.y) % 2)*(2-1*flipm)]/((GreyLevel.y-1)*6./dithdeg.y);
		CMYK.z = CMYK.z +DITHER_MATRIX1[((pointint.x+xdithoffset.z )%2)*(1+1*flipy)+((pointint.y+ydithoffset.z) % 2)*(2-1*flipy)]/((GreyLevel.z-1)*6./dithdeg.z);
		CMYK.w = CMYK.w +DITHER_MATRIX1[((pointint.x+xdithoffset.w )%2)*(1+1*flipk)+((pointint.y+ydithoffset.w) % 2)*(2-1*flipk)]/((GreyLevel.w-1)*6./dithdeg.w);
	
	}else if(dithmod == 4){
		CMYK.x = CMYK.x+ (-1+2*tex2Dlod(BlueNoiseSamp, float4((pointint.xy*(flipc)+pointint.yx*(!flipc)+float2(xdithoffset.x, ydithoffset.x) )/float2(256,256),0.0,0.0) ).r*2-1)/((GreyLevel.x-1)*6./dithdeg.x);	
		CMYK.y = CMYK.y+ (-1+2*tex2Dlod(BlueNoiseSamp, float4((pointint.xy*(flipm)+pointint.yx*(!flipm)+float2(xdithoffset.y, ydithoffset.y) )/float2(256,256),0.0,0.0) ).r*2-1 )/((GreyLevel.y-1)*6./dithdeg.y);	
		CMYK.z = CMYK.z+ (-1+2*tex2Dlod(BlueNoiseSamp, float4((pointint.xy*(flipy)+pointint.yx*(!flipy)+float2(xdithoffset.z, ydithoffset.z) )/float2(256,256),0.0,0.0) ).r*2-1 )/((GreyLevel.z-1)*6./dithdeg.z);
		CMYK.w = CMYK.w+ (-1+2*tex2Dlod(BlueNoiseSamp, float4((pointint.xy*(flipk)+pointint.yx*(!flipk)+float2(xdithoffset.w, ydithoffset.w))/float2(256,256),0.0,0.0) ).r*2-1 )/((GreyLevel.w-1)*6./dithdeg.w);		
	}


	//quantize
	CMYK= saturate((trunc(CMYK*GreyLevel))/(GreyLevel-1.));
	
	//reduce black (as a high K level results in just black this function allows users to change that)
	if(CMYK.w >trueblacksel){
		if(blackmode == 1){
			CMYK.w = CMYK.w- trueblack;
		} else if(blackmode == 2){
			CMYK.w = trueblacksel+(trueblack-1)*(trueblacksel-CMYK.w);
		}
	}
	//add final colours
	CMYK = CMYK +addto;
	col.rgb = (1-CMYK.rgb)*(1-CMYK.w);
	return(col.rgb);
}




float3 PS_CMYK(float4 position : SV_Position, float2 texcoord : TEXCOORD) : SV_Target{  
	float3 color = CMYK_doer(texcoord);
	return color.rgb;
}


/*-----------------.
| :: Techniques :: |
'-----------------*/
technique CMYK_quantizer
{

	pass CMYK{
		VertexShader=PostProcessVS;
		PixelShader=PS_CMYK;
	}
}