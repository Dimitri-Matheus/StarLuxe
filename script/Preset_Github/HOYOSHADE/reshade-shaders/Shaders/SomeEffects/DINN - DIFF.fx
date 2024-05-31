/*------------------.
| :: Description :: |
'-------------------/

	Ann's dumb shader
	includes the blue noise pattern from here
	https://momentsingraphics.de/BlueNoise.html
	i'm cool with you using it for whatever, if it's like a commercial thing, dm me, i'd like to know and credit would be nice
	io_person
	
*/


/*---------------.
| :: Includes :: |
'---------------*/
#include "ReShadeUI.fxh"
#include "ReShade.fxh"
#include "shared/cImageProcessing.fxh"
//credit for this effect goes to the people who made cshade

/*------------------.
| :: UI Settings :: |
'------------------*/

#ifndef NUM_OF_JUMPS
    #define NUM_OF_JUMPS 4
#endif
#ifndef FIRST_JUMP_SIZE
    #define FIRST_JUMP_SIZE 8
#endif
#ifndef SECOND_JUMP_SIZE
    #define SECOND_JUMP_SIZE 4
#endif
#ifndef THIRD_JUMP_SIZE
    #define THIRD_JUMP_SIZE 2
#endif
#ifndef FOURTH_JUMP_SIZE
    #define FOURTH_JUMP_SIZE 1
#endif

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

uniform bool greyscale  <
	ui_label = "greyscale";
	ui_category = "greyscale";
	ui_tooltip = "makes image greyscale (main effect)";
> = 1;

uniform bool dither  <
	ui_label = "dither";
	ui_category = "greyscale";
	ui_tooltip = "dithers the greyscale image, required for most effects to be visible";
> = 1;

uniform float3 Greyscale_vector < __UNIFORM_COLOR_FLOAT3
	ui_label = "Custom Conversion values";
	ui_category = "greyscale";
	ui_tooltip = "greyscale along this vector";
> = float3(1, 1, 1);

uniform float3 dinnwhite < __UNIFORM_COLOR_FLOAT3
	ui_label = "obra dinnw white";
	ui_category = "greyscale";
	ui_tooltip = "whites replaced with this";
> = float3(0.95, 1., 1.);

uniform float3 dinnblack < __UNIFORM_COLOR_FLOAT3
	ui_label = "obra dinnw black";
	ui_category = "greyscale";
	ui_tooltip = "blacks replaced with this";
> = float3(0.2, 0.2, 0.1);

uniform float Colour_Bleed < __UNIFORM_SLIDER_FLOAT1
	ui_label = "Grey sat";
	ui_category = "greyscale";
	ui_tooltip = "brings original colour back into image";
	ui_min = 0.0; ui_max = 1.0;
> = 0.0;

uniform int GreyLevel < __UNIFORM_SLIDER_INT1
	ui_min = 1;
	ui_max = 50;
	ui_label = "grey levels";
	ui_tooltip = "gives you levels of grey, 1 results in no levels";
	ui_category = "greyscale";
> = 2;

uniform bool ordered  <
	ui_label = "ordered";
	ui_category = "greyscale";
	ui_tooltip = "gives you ordered dither";
> = 0;

uniform int orderedmask  < __UNIFORM_SLIDER_INT1
	ui_min = 2;
	ui_max = 4;
	ui_label = "ordered dither mask choice";
	ui_category = "greyscale";
	ui_tooltip = "gives you ordered dither";
> = 2;

uniform float DithDeg < __UNIFORM_SLIDER_FLOAT1
	ui_label = "how far does one dither";
	ui_category = "greyscale";
	ui_tooltip = "the higher this is the more grey values are represented by dither";
	ui_min = 0.01; ui_max = 5.0;
> = 1.1;

uniform bool diag  <
	ui_label = "diagnostic";
	ui_category = "image";
	ui_tooltip = "makes image a b-w slope";
> = 0;
uniform bool colmod  < 
	ui_label = "image single col";
	ui_category = "image";
	ui_tooltip = "replaces image wtih one singular colour allowing you to see the effects of edge detection without influwence of background colour";
> = 0;

uniform float monocol < __UNIFORM_SLIDER_FLOAT1
	ui_label = "single col";
	ui_category = "image";
	ui_tooltip = "picks the monochrome colour to replace the image with";
	ui_min = 0.0; ui_max = 1.0;
	> = 0.0;
	
uniform float SIG1 < __UNIFORM_SLIDER_FLOAT1
	ui_label = "blur";
	ui_category = "image";
	ui_tooltip = "blurs base image for sake of stability";
	ui_min = 0.00; ui_max = 5.0;
> = 0.;

uniform bool EdgeDetect < 
	ui_label = "edge detect";
	ui_category = "edges";
> = TRUE;

uniform float threshold < __UNIFORM_SLIDER_FLOAT1
	ui_label = "edge treshold";
	ui_category = "edges";
	ui_tooltip = "more means less edges";
	ui_min = 0.00; ui_max = 5.0;
> = 1.;

uniform float3 dotedge < __UNIFORM_COLOR_FLOAT3
	ui_label = "edge dot product";
	ui_category = "edges";
	ui_tooltip = "edges calculated along this colour vector";
> = float3(1., 1., 1.);

uniform float inter < __UNIFORM_SLIDER_FLOAT1
	ui_label = "intercept";
	ui_category = "edges";
	ui_tooltip = "base sensitivity for edge";
	ui_min = 0.; ui_max = 2.0;
> = 0.1;
uniform float slope < __UNIFORM_SLIDER_FLOAT1
	ui_label = "slope";
	ui_category = "edges";
	ui_tooltip = "edge recognition darkness adjustment";
	ui_min = 0.0; ui_max = 2.;
> = 0.01;
uniform float range < __UNIFORM_SLIDER_FLOAT1
	ui_label = "lerprange";
	ui_category = "edges";
	ui_tooltip = "details edges";
	ui_min = 0.0; ui_max = 3.;
> = 0.5;


/*---------------.
| :: Samplers :: |
'----------------*/

#define AnnSampler ReShade::BackBuffer

texture BlueNoise < source ="HDR_LA_3.png" ; > { Width = 256; Height = 256; };
sampler BlueNoiseSamp { Texture = BlueNoise; AddressU = REPEAT;	AddressV = REPEAT;	AddressW = REPEAT;};

texture BLURSTORE {Width = BUFFER_WIDTH; Height = BUFFER_HEIGHT; Format = RGBA16F; };
sampler2D BLURSTOREs { Texture = BLURSTORE; MagFilter = POINT; MinFilter = POINT; MipFilter = POINT; };

texture bigblur {Width = BUFFER_WIDTH; Height = BUFFER_HEIGHT; Format = RGBA16F; };
sampler2D BigBlurM { Texture = bigblur; MagFilter = POINT; MinFilter = POINT; MipFilter = POINT; };

#define DITHER_MATRIX1 float3x3(0.75,-0.75,0.25,-0.5,-1,0,0.5,-0.25,1)
#define DITHER_MATRIX2 float4x4(0,8,2,10,12,4,14,6,3,11,1,9,15,7,13,5)

/*-------------.
| :: Effect :: |
'-------------*/
float3 BlurPass( float2 Tex, bool Horizontal, float SIGMA, sampler SAMP){
	//this function blurs in one direction based on the bool Horizontal
	float2 Direction = Horizontal ? float2(1.0, 0.0) : float2(0.0, 1.0);
    float2 PixelSize = (1.0 / float2(BUFFER_WIDTH, BUFFER_HEIGHT)) * Direction;
    float KernelSize = SIGMA * 3.0;
	if(SIGMA == 0.0)
		{
			//skips the for loop when no blurring is actually specified, saves on time
			return tex2Dlod(SAMP, float4(Tex, 0.0, 0.0)).rgb;
		}
		else
		{
			// Sample and weight center first to get even number sides
			float TotalWeight = GetGaussianWeight(0.0, SIGMA);
			float3 OutputColor = tex2D(SAMP, Tex).rgb * TotalWeight;

			for(float i = 1.0; i < KernelSize; i += 2.0)
			{
				float LinearWeight = 0.0;
				float LinearOffset = GetGaussianOffset(i, SIGMA, LinearWeight);
				OutputColor += tex2Dlod(SAMP, float4(Tex - LinearOffset * PixelSize, 0.0, 0.0)).rgb * LinearWeight;
				OutputColor += tex2Dlod(SAMP, float4(Tex + LinearOffset * PixelSize, 0.0, 0.0)).rgb * LinearWeight;
				TotalWeight += LinearWeight * 2.0;
			}
			// Normalize intensity to prevent altered output
			return OutputColor/ TotalWeight;
		}
}


float3 dxpass(float2 Tex){
	//function takes the derrivative approximations horizontally and vertically and then divides it by an adjustment for local brightness
	//float3 hold1 =ddx(tex2D(AnnSampler, Tex)).xyz;
	//float3 hold2 = ddy(tex2D(AnnSampler, Tex)).xyz;
	float aa= smoothstep(0,1, (0.5* (dot(abs(ddx(tex2D(AnnSampler, Tex)).xyz), dotedge)+0.5*dot(abs( ddy(tex2D(AnnSampler, Tex)).xyz), dotedge))/(dot(tex2D(AnnSampler,Tex).rgb,dotedge)*slope+inter)-threshold)/range);
	return  float3( aa,  aa<0.001?1:0,0.);
}


float2 contest(float2 stand, float2 cand, float s){
	//this function determines if this potential candidate for colour transfer is closer and actually has a detected edge
	return ((cand.r > 0.001) & (stand.g > (cand.g+s)))? float2(cand.r,(cand.g+s)) : stand;
}


float3 jump( float2 tex, int sizi, sampler samp){
	//establishes some variables for upcomming documentation
	float siz = sizi*0.05;
	float2 sizl = (1/BUFFER_SCREEN_SIZE) * sizi;
	float2 win = tex2D(samp, tex).rg;
	if(win.g <siz+0.01002){
		return float3(win,0);
	}

	//runs a bunch of "contests" to determine the most appropreate candidate from the 8 queen moves with distance sizi
	float2 cand = tex2Dlod(samp, float4(tex+sizl*float2(0,1),0.0,0.0)).rg;
	win = contest(win, cand, siz);
	cand = tex2Dlod(samp, float4(tex+sizl*float2(1,0),0.0,0.0)).rg;
	win = contest(win, cand, siz);
	cand = tex2Dlod(samp, float4(tex+sizl*float2(0,-1),0.0,0.0)).rg;
	win = contest(win, cand, siz);
	cand = tex2Dlod(samp, float4(tex+sizl*float2(-1,0),0.0,0.0)).rg;
	win = contest(win, cand, siz);
	siz = siz*1.41421356;
	cand = tex2Dlod(samp, float4(tex+sizl*float2(1,1),0.0,0.0)).rg;
	win = contest(win, cand, siz);
	cand = tex2Dlod(samp, float4(tex+sizl*float2(1,-1),0.0,0.0)).rg;
	win = contest(win, cand, siz);
	cand = tex2Dlod(samp, float4(tex+sizl*float2(-1,-1),0.0,0.0)).rg;
	win = contest(win, cand, siz);
	cand = tex2Dlod(samp, float4(tex+sizl*float2(-1,1),0.0,0.0)).rg;
	win = contest(win, cand, siz);
	return float3(win,0);
}




//horizontal and vertical blur
float3 PS_DIFFhb(float4 position : SV_Position, float2 texcoord : TEXCOORD) : SV_Target{  
	float3 color = BlurPass(texcoord, TRUE, SIG1, AnnSampler);
	return color.rgb;
}
float3 PS_DIFFvb(float4 position : SV_Position, float2 texcoord : TEXCOORD) : SV_Target{  
	float3 color = BlurPass(texcoord, FALSE, SIG1, BLURSTOREs);
	return color.rgb;
}

//gets the colour derrivatives
float3 PS_dx(float4 position : SV_Position, float2 texcoord : TEXCOORD) : SV_Target{  
	float3 color =dxpass(texcoord);
	return color.rgb;
}

//the jump functions here execute jump fill to generate edges
float3 JUMP1(float4 position : SV_Position, float2 texcoord : TEXCOORD) : SV_Target{  
	float3 color =jump(texcoord, FIRST_JUMP_SIZE, AnnSampler);
	return color.rgb;
}
float3 JUMP2(float4 position : SV_Position, float2 texcoord : TEXCOORD) : SV_Target{  
	float3 color =jump(texcoord, SECOND_JUMP_SIZE, AnnSampler);
	return color.rgb;
}
float3 JUMP3(float4 position : SV_Position, float2 texcoord : TEXCOORD) : SV_Target{  
	float3 color =jump(texcoord, THIRD_JUMP_SIZE, AnnSampler);
	return color.rgb;
}
float3 JUMP4(float4 position : SV_Position, float2 texcoord : TEXCOORD) : SV_Target{  
	float3 color =jump(texcoord, FOURTH_JUMP_SIZE, AnnSampler);
	return color.rgb;
}


float3 finisher(float4 position : SV_Position, float2 texcoord : TEXCOORD) : SV_Target{ 
	//variable setup and sampling 
	float2 PixelBlock = float2(float(PixelationSizeX), float(PixelationSizeY));
	int2 pointint = trunc((BUFFER_SCREEN_SIZE / PixelBlock) * texcoord);
	float2 Pointer = pointint * (PixelBlock / BUFFER_SCREEN_SIZE);
	float2 POINT = Pointer + trunc(PixelBlock/2.)*BUFFER_PIXEL_SIZE;
	float3 img = tex2D(BigBlurM, POINT).rgb;
	float3 dx = tex2D(AnnSampler, POINT).rgb;
	int2 cellp = pointint % 2;
	float mask = dx.r/((dx.g*5+1.)*(dx.g*5+1.));
	
	if(greyscale){
		//greyscales the image
		float gry = dot(img, Greyscale_vector);	
		if(diag){
		gry = Pointer.x;
		}else if(colmod){
		gry = monocol;
		}
		if (GreyLevel > 1) {
		//adds a dither mask if specified and seperates out different levels
			if (dither){
				if(ordered){
				if(orderedmask==2){
					gry = gry+((cellp.x)+(cellp.x==cellp.y)*2.-1.5)/((GreyLevel-1)*6./DithDeg);
				}else if(orderedmask==3){
					gry = gry +1.5*DITHER_MATRIX1[pointint.x % 3][pointint.y % 3] /((GreyLevel-1)*6./DithDeg);
				}else{
					gry = gry + 1.5*(DITHER_MATRIX2[pointint.x % 4][pointint.y % 4]/7.5-1 )/((GreyLevel-1)*6./DithDeg);
				}
				}else{
				gry = gry+(tex2Dlod(BlueNoiseSamp, float4(pointint/float2(256,256),0.0,0.0) ).r*DithDeg-0.5*DithDeg)/(GreyLevel-1.);
				}
			}
			if(EdgeDetect){
				float edge = smoothstep(0,1,mask);
				gry = gry-sign(gry-0.5)*edge;
			}
			gry = saturate((trunc(gry*GreyLevel))/(GreyLevel-1.));
		}
		img = saturate(lerp(lerp(dinnblack, dinnwhite,gry), img, Colour_Bleed));
	}
	return img;
}



/*-----------------.
| :: Techniques :: |
'-----------------*/
technique DINNDX{
	pass BLURh2{
		VertexShader=PostProcessVS;
		PixelShader=PS_DIFFhb;
		RenderTarget = BLURSTORE; 
	}
	pass BLURv2{
		VertexShader=PostProcessVS;
		PixelShader=PS_DIFFvb;
		RenderTarget = bigblur; 
	}
	pass DX{
		VertexShader=PostProcessVS;
		PixelShader=PS_dx;
	}
//the following exists as a sort of non loop to allow for some control of the jump fill
#if NUM_OF_JUMPS>0
	pass J1{
		VertexShader=PostProcessVS;
		PixelShader=JUMP1;
	}
#endif
#if NUM_OF_JUMPS>1
	pass J2{
		VertexShader=PostProcessVS;
		PixelShader=JUMP2;
	}
#endif
#if NUM_OF_JUMPS>2
	pass J3{
		VertexShader=PostProcessVS;
		PixelShader=JUMP3;
	}
#endif
#if NUM_OF_JUMPS>3
	pass J4{
		VertexShader=PostProcessVS;
		PixelShader=JUMP4;
	}
#endif
	pass composit {
		VertexShader=PostProcessVS;
		PixelShader=finisher;
	}

}

