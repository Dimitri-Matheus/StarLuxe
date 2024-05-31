/*------------------.
| :: Description :: |
'-------------------/
	it moves pixels one side or another in an alternating pattern
	not spectecular, but it does the job as a corruption effect, or turn on the horizontal bar effect for some of the visual flair interlaced video can provide
*/


/*---------------.
| :: Includes :: |
'---------------*/


#include "ReShadeUI.fxh"
#include "ReShade.fxh"


/*------------------.
| :: UI Settings :: |
'------------------*/
uniform int SectionSizeX < __UNIFORM_SLIDER_INT1
	ui_min = 1;
	ui_max = 50;
	ui_label = "horizontal sections to be displaced";
	ui_tooltip = "this is in terms of pixels so just go into the code and change the max if you have an abseurdly high res thing";
> = 2;

uniform int SectionSizeY < __UNIFORM_SLIDER_INT1
	ui_min = 1;
	ui_max = 50;
	ui_label = "vertical sections to be displaced";
	ui_tooltip = "this is in terms of pixels so just go into the code and change the max if you have an abseurdly high res thing";
> = 2;

uniform int sizX < __UNIFORM_SLIDER_INT1
	ui_min = 0;
	ui_max = 50;
	ui_label = "vertical displacement";
	ui_tooltip = "this is in terms of pixels so just go into the code and change the max if you have an abseurdly high res thing";
> = 0;

uniform int sizY < __UNIFORM_SLIDER_INT1
	ui_min = 0;
	ui_max = 50;
	ui_label = "horizontal displacement";
	ui_tooltip = "this is in terms of pixels so just go into the code and change the max if you have an abseurdly high res thing";
> = 20;

uniform bool flipx < 
	ui_label= "flip horizontal displacement";
	ui_tooltip = "changes the wibbles, may be handy if you wanna line something up";
> = FALSE;

uniform bool flipy < 
	ui_label= "flip vertical displacement";
	ui_tooltip = "changes the wibbles, may be handy if you wanna line something up";
> = FALSE;
/*-------------------------.
| :: Sampler and timers :: |
'-------------------------*/

#define AnnSampler ReShade::BackBuffer

/*-------------.
| :: Effect :: |
'-------------*/
float3 PS_PixelShift(float4 position : SV_Position, float2 texcoord : TEXCOORD) : SV_Target{  
	//get coordinates in a easy to use per pixel term
	int2 PixelBlock = int2(SectionSizeX, SectionSizeY);
	int2 pointint = trunc((texcoord/ (PixelBlock*BUFFER_PIXEL_SIZE )));
	//this is a terribly squeezed together function, lets call this optimisation
	//it samples colour from shifted coordinates 
	return(tex2D(AnnSampler,texcoord+ BUFFER_PIXEL_SIZE*((flipx+pointint.x)%2)*float2(0,1)*sizX+ BUFFER_PIXEL_SIZE*((flipy+pointint.y)%2)*float2(1,0)*sizY  -BUFFER_PIXEL_SIZE*trunc(float2(sizY,sizX)/2-0.001)).rgb);
}

/*-----------------.
| :: Techniques :: |
'-----------------*/
technique PixelShifter
{
	pass PixelShift{
		VertexShader=PostProcessVS;
		PixelShader=PS_PixelShift;
	}
}