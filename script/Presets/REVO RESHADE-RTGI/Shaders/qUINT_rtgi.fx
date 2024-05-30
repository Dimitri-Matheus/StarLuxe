/*=============================================================================

   Copyright (c) Pascal Gilcher. All rights reserved.

	ReShade effect file
    github.com/martymcmodding

	Support me:
   		patreon.com/mcflypg

    Path Traced Global Illumination 

    * Unauthorized copying of this file, via any medium is strictly prohibited
 	* Proprietary and confidential
    * See accompanying license document for terms and conditions

=============================================================================*/

//TODO: fix flicker - maybe go for 2D sampling again?

#if __RESHADE__ < 40802
 #error "Update ReShade to at least 4.8.2."
#endif

/*=============================================================================
	Preprocessor settings
=============================================================================*/

#ifndef INFINITE_BOUNCES
 #define INFINITE_BOUNCES       0   //[0 or 1]      If enabled, path tracer samples previous frame GI as well, causing a feedback loop to simulate secondary bounces, causing a more widespread GI.
#endif

#ifndef SKYCOLOR_MODE
 #define SKYCOLOR_MODE          0   //[0 to 3]      0: skycolor feature disabled | 1: manual skycolor | 2: dynamic skycolor | 3: dynamic skycolor with manual tint overlay
#endif

#ifndef IMAGEBASEDLIGHTING
 #define IMAGEBASEDLIGHTING     0   //[0 to 3]      0: no ibl infill | 1: use ibl infill
#endif

#ifndef MATERIAL_TYPE
 #define MATERIAL_TYPE          0   //[0 to 1]      0: Lambert diffuse | 1: GGX BRDF
#endif

#ifndef SMOOTHNORMALS
 #define SMOOTHNORMALS 			0   //[0 to 3]      0: off | 1: enables some filtering of the normals derived from depth buffer to hide 3d model blockyness
#endif

#ifndef HALFRES_INPUT
 #define HALFRES_INPUT 			0   //[0 to 1]      0: use full resolution color and depth input | 1 : use half resolution color and depth input (faster)
#endif

/*=============================================================================
	UI Uniforms
=============================================================================*/

uniform int UIHELP <
	ui_type = "radio";
	ui_label = " ";	
	ui_text ="This shader adds ray traced / ray marched global illumination to games\nby traversing the height field described by the depth map of the game.\n\nHover over the settings below to display more information.\n\n          >>>>>>>>>> IMPORTANT <<<<<<<<<      \n\nIf the shader appears to do nothing when enabled, make sure ReShade's\ndepth access is properly set up - no output without proper input.\n\n          >>>>>>>>>> IMPORTANT <<<<<<<<<      ";
	ui_category = ">>>> OVERVIEW / HELP (click me) <<<<";
	ui_category_closed = true;
>;

uniform float RT_SAMPLE_RADIUS <
	ui_type = "drag";
	ui_min = 0.5; ui_max = 20.0;
    ui_step = 0.01;
    ui_label = "Ray Length";
	ui_tooltip = "Maximum ray length, directly affects\nthe spread radius of shadows / bounce lighting";
    ui_category = "Ray Tracing";
> = 4.0;

uniform float RT_SAMPLE_RADIUS_FAR <
	ui_type = "drag";
	ui_min = 0.0; ui_max = 1.0;
    ui_step = 0.01;
    ui_label = "Extended Ray Length Multiplier";
	ui_tooltip = "Increases ray length in the background to achieve ultra wide light bounces.";
    ui_category = "Ray Tracing";
> = 0.0;

uniform int RT_RAY_AMOUNT <
	ui_type = "slider";
	ui_min = 1; ui_max = 20;
    ui_label = "Amount of Rays";
    ui_tooltip = "Amount of rays launched per pixel in order to\nestimate the global illumination at this location.\nAmount of noise to filter is proportional to sqrt(rays).";
    ui_category = "Ray Tracing";
> = 3;

uniform int RT_RAY_STEPS <
	ui_type = "slider";
	ui_min = 1; ui_max = 40;
    ui_label = "Amount of Steps per Ray";
    ui_tooltip = "RTGI performs step-wise raymarching to check for ray hits.\nFewer steps may result in rays skipping over small details.";
    ui_category = "Ray Tracing";
> = 12;

uniform float RT_Z_THICKNESS <
	ui_type = "drag";
	ui_min = 0.0; ui_max = 4.0;
    ui_step = 0.01;
    ui_label = "Z Thickness";
	ui_tooltip = "The shader can't know how thick objects are, since it only\nsees the side the camera faces and has to assume a fixed value.\n\nUse this parameter to remove halos around thin objects.";
    ui_category = "Ray Tracing";
> = 0.5;

uniform bool RT_HIGHP_LIGHT_SPREAD <
    ui_label = "Enable precise light spreading";
    ui_tooltip = "Rays accept scene intersections within a small error margin.\nEnabling this will snap rays to the actual hit location.\nThis results in sharper but more realistic lighting.";
    ui_category = "Ray Tracing";
> = true;

uniform bool RT_BACKFACE_MIRROR <
    ui_label = "Enable simulation of backface lighting";
    ui_tooltip = "RTGI can only simulate light bouncing of the objects visible on the screen.\nTo estimate light coming from non-visible sides of otherwise visible objects,\nthis feature will just take the front-side color instead.";
    ui_category = "Ray Tracing";
> = false;

#if MATERIAL_TYPE == 1
uniform float RT_SPECULAR <
	ui_type = "drag";
	ui_min = 0.01; ui_max = 1.0;
    ui_step = 0.01;
    ui_label = "Specular";
    ui_tooltip = "Specular Material parameter for GGX Microfacet BRDF";
    ui_category = "Material";
> = 1.0;

uniform float RT_ROUGHNESS <
	ui_type = "drag";
	ui_min = 0.15; ui_max = 1.0;
    ui_step = 0.01;
    ui_label = "Roughness";
    ui_tooltip = "Roughness Material parameter for GGX Microfacet BRDF";
    ui_category = "Material";
> = 1.0;
#endif

#if SKYCOLOR_MODE != 0
#if SKYCOLOR_MODE == 1
uniform float3 SKY_COLOR <
	ui_type = "color";
	ui_label = "Sky Color";
    ui_category = "Blending";
> = float3(1.0, 1.0, 1.0);
#endif

#if SKYCOLOR_MODE == 3
uniform float3 SKY_COLOR_TINT <
	ui_type = "color";
	ui_label = "Sky Color Tint";
    ui_category = "Blending";
> = float3(1.0, 1.0, 1.0);
#endif

#if SKYCOLOR_MODE == 2 || SKYCOLOR_MODE == 3
uniform float SKY_COLOR_SAT <
	ui_type = "drag";
	ui_min = 0; ui_max = 5.0;
    ui_step = 0.01;
    ui_label = "Auto Sky Color Saturation";
    ui_category = "Blending";
> = 1.0;
#endif

uniform float SKY_COLOR_AMBIENT_MIX <
	ui_type = "drag";
	ui_min = 0; ui_max = 1.0;
    ui_step = 0.01;
    ui_label = "Sky Color Ambient Mix";
    ui_tooltip = "How much of the occluded ambient color is considered skycolor\n\nIf 0, Ambient Occlusion removes white ambient color,\nif 1, Ambient Occlusion only removes skycolor";
    ui_category = "Blending";
> = 0.2;

uniform float SKY_COLOR_AMT <
	ui_type = "drag";
	ui_min = 0; ui_max = 10.0;
    ui_step = 0.01;
    ui_label = "Sky Color Intensity";
    ui_category = "Blending";
> = 4.0;
#endif

uniform float RT_AO_AMOUNT <
	ui_type = "drag";
	ui_min = 0; ui_max = 10.0;
    ui_step = 0.01;
    ui_label = "Ambient Occlusion Intensity";
    ui_category = "Blending";
> = 4.0;

uniform float RT_IL_AMOUNT <
	ui_type = "drag";
	ui_min = 0; ui_max = 10.0;
    ui_step = 0.01;
    ui_label = "Bounce Lighting Intensity";
    ui_category = "Blending";
> = 4.0;

#if IMAGEBASEDLIGHTING != 0
uniform float RT_IBL_AMOUT <
    ui_type = "drag";
    ui_min = 0; ui_max = 1.0;
    ui_step = 0.01;
    ui_label = "Image Based Lighting Intensity";
    ui_category = "Blending";
> = 0.0;
#endif

#if INFINITE_BOUNCES != 0
uniform float RT_IL_BOUNCE_WEIGHT <
    ui_type = "drag";
    ui_min = 0; ui_max = 1.0;
    ui_step = 0.01;
    ui_label = "Next Bounce Weight";
    ui_category = "Blending";
> = 0.0;
#endif

uniform int FADEOUT_MODE_UI < //rename because possible clash with older config
	ui_type = "slider";
    ui_min = 0; ui_max = 2;
    ui_label = "Fade Out Mode";
    ui_category = "Blending";
> = 2;

uniform float RT_FADE_DEPTH <
	ui_type = "drag";
    ui_label = "Fade Out Range";
	ui_min = 0.001; ui_max = 1.0;
	ui_tooltip = "Distance falloff, higher values increase RTGI draw distance.";
    ui_category = "Blending";
> = 0.3;

uniform int RT_DEBUG_VIEW <
	ui_type = "radio";
    ui_label = "Enable Debug View";
	ui_items = "None\0Lighting Channel\0Normal Channel\0History Confidence\0";
	ui_tooltip = "Different debug outputs";
    ui_category = "Debug";
> = 0;

uniform bool RT_DO_RENDER <
    ui_label = "Render a still frame (for screenshots, reload effects after enabling)";
    ui_category = "Experimental";
    ui_tooltip = "This will progressively render a still frame. Make sure to set rays low, and steps high. \nTo start rendering, check the box and wait until the result is sufficiently noise-free.\nYou can still adjust blending and toggle debug mode, but do not touch anything else.\nTo resume the game, uncheck the box.\n\nRequires a scene with no moving objects to work properly.";
> = false;

uniform bool RT_USE_ACESCG <
    ui_label = "Use ACEScg color space";
    ui_category = "Experimental";
    ui_tooltip = "This uses the ACEScg color space for illumination calculations.\nIt produces better bounce colors and reduces tone shifts,\nbut can result in colors outside screen gamut";
> = false;

uniform bool RT_USE_SRGB <
    ui_label = "Assume sRGB input";
     ui_tooltip = "Converts color to linear before converting to HDR.";
    ui_category = "Experimental";
> = false;

uniform int UIHELP2 <
	ui_type = "radio";
	ui_label = " ";	
	ui_text ="Description for preprocessor definitions:\n\nINFINITE_BOUNCES\n0: off\n1: allows the light to reflect more than once.\n\nSKYCOLOR_MODE\n0: off\n1: static color\n2: dynamic detection (wip)\n3: dynamic detection + manual tint\n\nIMAGEBASELIGHTING:\n0: off\n1: analyzes the image for main lighting directions and recovers rays that did not return data.\n\nMATERIAL_TYPE\n0: Lambertian surface (matte)\n1: GGX Material, allows to model matte, glossy, specular surfaces based off roughness and specularity parameters\n\nSMOOTHNORMALS\n0: off\n1: enables normal map filtering, reduces blockyness on low poly surfaces.";
	ui_category = ">>>> PREPROCESSOR DEFINITION GUIDE (click me) <<<<";
	ui_category_closed = false;
>;
/*
uniform float4 tempF1 <
    ui_type = "drag";
    ui_min = -100.0;
    ui_max = 100.0;
> = float4(1,1,1,1);

uniform float4 tempF2 <
    ui_type = "drag";
    ui_min = -100.0;
    ui_max = 100.0;
> = float4(1,1,1,1);

uniform float4 tempF3 <
    ui_type = "drag";
    ui_min = -100.0;
    ui_max = 100.0;
> = float4(1,1,1,1);

uniform float4 tempF4 <
    ui_type = "drag";
    ui_min = -100.0;
    ui_max = 100.0;
> = float4(1,1,1,1);

uniform float4 tempF5 <
    ui_type = "drag";
    ui_min = -100.0;
    ui_max = 100.0;
> = float4(1,1,1,1);
*/
/*=============================================================================
	Textures, Samplers, Globals
=============================================================================*/

uniform uint  FRAMECOUNT  < source = "framecount"; >;
uniform float FRAMETIME   < source = "frametime";  >;

//debug flags, toy around at your own risk
#define RTGI_DEBUG_SKIP_FILTER      0
#define MONTECARLO_MAX_STACK_SIZE   512

//log2 macro for uints up to 16 bit, inefficient in runtime but preprocessor doesn't care
#define T1(x,n) ((uint(x)>>(n))>0)
#define T2(x,n) (T1(x,n)+T1(x,n+1))
#define T4(x,n) (T2(x,n)+T2(x,n+2))
#define T8(x,n) (T4(x,n)+T4(x,n+4))
#define LOG2(x) (T8(x,0)+T8(x,8))

//double the screen size, use one mip level more
//the macro returns floor() of log
//for 3840x2160 use miplevels 0 to 4
//1920 -> log2(1920) -> 10, minus 7 = 3    
//3840 -> log2(3840) -> 11, minus 7 = 4
//#define MIP_AMT 	(LOG2(BUFFER_WIDTH) - 7)

texture ColorInputTex : COLOR;
texture DepthInputTex : DEPTH;
sampler ColorInput 	            { Texture = ColorInputTex; };
sampler DepthInput              { Texture = DepthInputTex; };
 
#if HALFRES_INPUT != 0 
#define MIP_AMT 	(LOG2(BUFFER_WIDTH) - 6)
texture ZTex <pooled = true;>                   { Width = BUFFER_WIDTH>>1;      Height = BUFFER_HEIGHT>>1;   Format = R16F;         MipLevels = 1 + MIP_AMT; };
texture ColorTex <pooled = true;>               { Width = BUFFER_WIDTH>>1;      Height = BUFFER_HEIGHT>>1;   Format = RGBA16F;      MipLevels = 1 + MIP_AMT; };
#else 
#define MIP_AMT 	(LOG2(BUFFER_WIDTH) - 7)
texture ZTex <pooled = true;>                   { Width = BUFFER_WIDTH;         Height = BUFFER_HEIGHT;     Format = R16F;          MipLevels = 1 + MIP_AMT; };
texture ColorTex <pooled = true;>               { Width = BUFFER_WIDTH;         Height = BUFFER_HEIGHT;     Format = RGBA16F;       MipLevels = 1 + MIP_AMT; };
#endif

texture GITex <pooled = true;>  { Width = BUFFER_WIDTH;         Height = BUFFER_HEIGHT;     Format = RGBA16F;       MipLevels = 4; };
texture GITexFilter1            { Width = BUFFER_WIDTH;         Height = BUFFER_HEIGHT;     Format = RGBA16F; }; //also holds gbuffer pre-smooth normals
texture GITexFilter0            { Width = BUFFER_WIDTH;         Height = BUFFER_HEIGHT;     Format = RGBA16F; }; //also holds prev frame GI after everything is done
texture GBufferTex <pooled = true;>  { Width = BUFFER_WIDTH;         Height = BUFFER_HEIGHT;     Format = RGBA16F; };
texture GBufferTexPrev          { Width = BUFFER_WIDTH;         Height = BUFFER_HEIGHT;     Format = RGBA16F; };

texture JitterTex < source = "bluenoise.png"; > { Width = 32; Height = 32; Format = RGBA8; };
sampler	sJitterTex      { Texture = JitterTex; AddressU = WRAP; AddressV = WRAP; };

sampler sZTex	            	{ Texture = ZTex;           };
sampler sColorTex	        	{ Texture = ColorTex;       };
sampler sGITex	                { Texture = GITex;          };
sampler sGITexFilter1	        { Texture = GITexFilter1;   };
sampler sGITexFilter0	        { Texture = GITexFilter0;   };
sampler sGBufferTex	            { Texture = GBufferTex;     };
sampler sGBufferTexPrev	        { Texture = GBufferTexPrev; };

#if IMAGEBASEDLIGHTING != 0 || SKYCOLOR_MODE >= 2
texture ProbeTex      			{ Width = 64;   Height = 64;  Format = RGBA16F;};
texture ProbeTexPrev      		{ Width = 64;   Height = 64;  Format = RGBA16F;};
sampler sProbeTex	    		{ Texture = ProbeTex;	    };
sampler sProbeTexPrev	    	{ Texture = ProbeTexPrev;	};
#endif

texture StackCounterTex          { Width = BUFFER_WIDTH;         Height = BUFFER_HEIGHT;     Format = R16F; };
texture StackCounterTexPrev      { Width = BUFFER_WIDTH;         Height = BUFFER_HEIGHT;     Format = R16F; MipLevels = 4; };
sampler sStackCounterTex	     { Texture = StackCounterTex; };
sampler sStackCounterTexPrev	 { Texture = StackCounterTexPrev; };

struct VSOUT
{
	float4 vpos : SV_Position;
    float2 uv   : TEXCOORD0;
};

#include "qUINT\Global.fxh"
#include "qUINT\Depth.fxh"
#include "qUINT\Projection.fxh"
#include "qUINT\Normal.fxh"
#include "qUINT\Random.fxh"
#include "qUINT\RayTracing.fxh"
#include "qUINT\Denoise.fxh"

/*=============================================================================
	Functions
=============================================================================*/

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

float3 ggx_vndf(float2 uniform_disc, float2 alpha, float3 v)
{
	//scale by alpha, 3.2
	float3 Vh = normalize(float3(alpha * v.xy, v.z));
	//point on projected area of hemisphere
	float2 p = uniform_disc;
	p.y = lerp(sqrt(1.0 - p.x*p.x), 
		       p.y,
		       Vh.z * 0.5 + 0.5);

	float3 Nh =  float3(p.xy, sqrt(saturate(1.0 - dot(p, p)))); //150920 fixed sqrt() of z

	//reproject onto hemisphere
	Nh = mul(Nh, Normal::base_from_vector(Vh));

	//revert scaling
	Nh = normalize(float3(alpha * Nh.xy, saturate(Nh.z)));

	return Nh;
}

float3 schlick_fresnel(float vdoth, float3 f0)
{
	vdoth = saturate(vdoth);
	return lerp(pow(vdoth, 5), 1, f0);
}

float ggx_g2_g1(float3 l, float3 v, float2 alpha)
{
	//smith masking-shadowing g2/g1, v and l in tangent space
	l.xy *= alpha;
	v.xy *= alpha;
	float nl = length(l);
	float nv = length(v);

    float ln = l.z * nv;
    float lv = l.z * v.z;
    float vn = v.z * nl;
    //in tangent space, v.z = ndotv and l.z = ndotl
    return (ln + lv) / (vn + ln + 1e-7);
}

float3 dither(in VSOUT i)
{
    const float2 magicdot = float2(0.75487766624669276, 0.569840290998);
    const float3 magicadd = float3(0, 0.025, 0.0125) * dot(magicdot, 1);

    const int bit_depth = 8; //TODO: add BUFFER_COLOR_DEPTH once it works
    const float lsb = exp2(bit_depth) - 1;

    float3 dither = frac(dot(i.vpos.xy, magicdot) + magicadd);
    dither /= lsb;
    
    return dither;
}

float fade_distance(in VSOUT i)
{
    float distance = saturate(length(Projection::uv_to_proj(i.uv)) / RESHADE_DEPTH_LINEARIZATION_FAR_PLANE);
    float fade;
    switch(FADEOUT_MODE_UI)
    {
        case 0:
        fade = saturate((RT_FADE_DEPTH - distance) / RT_FADE_DEPTH);
        break;
        case 1:
        fade = saturate((RT_FADE_DEPTH - distance) / RT_FADE_DEPTH);
        fade *= fade; fade *= fade;
        break;
        case 2:
        float fadefact = rcp(RT_FADE_DEPTH * 0.32);
        float cutoff = exp(-fadefact);
        fade = saturate((exp(-distance * fadefact) - cutoff)/(1 - cutoff));
        break;
    }    

    return fade;    
}

float3 get_jitter(uint2 texelpos)
{
    uint4 p = texelpos.xyxy;
    p.zw /= 32u;
    p %= 32u;
    
    float3 jitter = tex2Dfetch(sJitterTex, p.xy).rgb;
    float3 jitter2 = tex2Dfetch(sJitterTex, p.zw).rgb;

    return frac(jitter + jitter2);
}

/*=============================================================================
	Shader entry points
=============================================================================*/

VSOUT VS_RT(in uint id : SV_VertexID)
{
    VSOUT o;
    VS_FullscreenTriangle(id, o.vpos, o.uv); //use original fullscreen triangle VS
    return o;
}

void PS_InputSetupFull(in VSOUT i, out MRT3 o)
{ 
    float depth = Depth::get_linear_depth(i.uv);
    float3 n    = Normal::normal_from_depth(i.uv);
    float3 col  = tex2D(ColorInput, i.uv).rgb;

    o.t0.w = depth < 0.999;
    o.t0.rgb = col;
    float2 offs = float2(1.5, 0.5);
    for(int j = 0; j < 4; j++)
    {
        o.t0.rgb = min(o.t0.rgb, tex2D(ColorInput, i.uv + offs * BUFFER_PIXEL_SIZE).rgb);
        offs = mul(offs, float2x2(0,-1,1,0));
    }

    o.t0.rgb = unpack_hdr(o.t0.rgb);
    o.t1 = Projection::depth_to_z(depth);
    o.t2 = float4(n, o.t1.x);  
}

void PS_InputSetupHalfGbuf(in VSOUT i, out float4 o : SV_Target0)
{ 
    float depth = Depth::get_linear_depth(i.uv);
    float3 n    = Normal::normal_from_depth(i.uv);
    o = float4(n, Projection::depth_to_z(depth));
}

void PS_InputSetupHalfZCol(in VSOUT i, out MRT2 o)
{
    float4 texels; //TODO: replace with gather()
    texels.x = Depth::get_linear_depth(i.uv + float2( 0.5, 0.5) * BUFFER_PIXEL_SIZE);
    texels.y = Depth::get_linear_depth(i.uv + float2(-0.5, 0.5) * BUFFER_PIXEL_SIZE);
    texels.z = Depth::get_linear_depth(i.uv + float2( 0.5,-0.5) * BUFFER_PIXEL_SIZE);
    texels.w = Depth::get_linear_depth(i.uv + float2(-0.5,-0.5) * BUFFER_PIXEL_SIZE);

    float depth = max(max(texels.x, texels.y), max(texels.z, texels.w));

    o.t0 = float4(unpack_hdr(tex2D(ColorInput, i.uv).rgb), depth < 0.999);    
    o.t1 = Projection::depth_to_z(depth);
}

void PS_Smoothnormals(in VSOUT i, out float4 gbuffer : SV_Target0)
{ 
    const float max_n_n = 0.63;
    const float max_v_s = 0.65;
    const float max_c_p = 0.5;
    const float searchsize = 0.0125;
    const int dirs = 5;

    float4 gbuf_center = tex2D(sGITexFilter1, i.uv);

    float3 n_center = gbuf_center.xyz;
    float3 p_center = Projection::uv_to_proj(i.uv, gbuf_center.w);
    float radius = searchsize + searchsize * rcp(p_center.z) * 2.0;
    float worldradius = radius * p_center.z;

    int steps = clamp(ceil(radius * 300.0) + 1, 1, 7);
    float3 n_sum = 0.001 * n_center;

    for(float j = 0; j < dirs; j++)
    {
        float2 dir; sincos(radians(360.0 * j / dirs + 0.666), dir.y, dir.x);

        float3 n_candidate = n_center;
        float3 p_prev = p_center;

        for(float stp = 1.0; stp <= steps; stp++)
        {
            float fi = stp / steps;   
            fi *= fi * rsqrt(fi);

            float offs = fi * radius;
            offs += length(BUFFER_PIXEL_SIZE);

            float2 uv = i.uv + dir * offs * BUFFER_ASPECT_RATIO;            
            if(!all(saturate(uv - uv*uv))) break;

            float4 gbuf = tex2Dlod(sGITexFilter1, uv, 0);
            float3 n = gbuf.xyz;
            float3 p = Projection::uv_to_proj(uv, gbuf.w);

            float3 v_increment  = normalize(p - p_prev);

            float ndotn         = dot(n, n_center); 
            float vdotn         = dot(v_increment, n_center); 
            float v2dotn        = dot(normalize(p - p_center), n_center); 
          
            ndotn *= max(0, 1.0 + fi *0.5 * (1.0 - abs(v2dotn)));

            if(abs(vdotn)  > max_v_s || abs(v2dotn) > max_c_p) break;       

            if(ndotn > max_n_n)
            {
                float d = distance(p, p_center) / worldradius;
                float w = saturate(4.0 - 2.0 * d) * smoothstep(max_n_n, lerp(max_n_n, 1.0, 2), ndotn); //special recipe
                w = stp < 1.5 && d < 2.0 ? 1 : w;  //special recipe       
                n_candidate = lerp(n_candidate, n, w);
                n_candidate = normalize(n_candidate);
            }

            p_prev = p;
            n_sum += n_candidate;
        }
    }

    n_sum = normalize(n_sum);
    gbuffer = float4(n_sum, gbuf_center.w);
}

void PS_RTGI(in VSOUT i, out float4 o : SV_Target0)
{ 
    float3 jitter = get_jitter(i.vpos.xy);
    float3 n = tex2D(sGBufferTex, i.uv).xyz;
    float3 p = Projection::uv_to_proj(i.uv); //can't hurt to have best data..
    float d = Projection::z_to_depth(p.z); p *= 0.999; p += n * d;  

    float ray_maxT = RT_SAMPLE_RADIUS * RT_SAMPLE_RADIUS;
    ray_maxT *= lerp(1.0, 100.0, saturate(d * RT_SAMPLE_RADIUS_FAR));
    ray_maxT = min(ray_maxT, RESHADE_DEPTH_LINEARIZATION_FAR_PLANE);

#if MATERIAL_TYPE == 1
    float3 specular_color = tex2D(ColorInput, i.uv).rgb; 
    specular_color = lerp(dot(specular_color, 0.333), specular_color, 0.666);
    specular_color *= RT_SPECULAR * 2.0;
    float3 eyedir = -normalize(p);
    float3x3 tangent_base = Normal::base_from_vector(n);
    float3 tangent_eyedir = mul(eyedir, transpose(tangent_base));
#endif 

    int nrays  = RT_DO_RENDER ? 3   : RT_RAY_AMOUNT;
    int nsteps = RT_DO_RENDER ? 100 : RT_RAY_STEPS;

    o = 0;

    [loop]  
    for(int r = 0; r < 0 + nrays; r++)
    {        
        RayTracing::RayDesc ray;
        float3 r3;

        if(RT_DO_RENDER)
            //r3 =  Random::goldenweyl3(r * 64 + (FRAMECOUNT % 64), jitter);     
            r3 =  Random::goldenweyl3(r * MONTECARLO_MAX_STACK_SIZE + (FRAMECOUNT % MONTECARLO_MAX_STACK_SIZE), jitter);             
        else 
            r3 = Random::goldenweyl3(r, jitter);

#if MATERIAL_TYPE == 0
        //lambert cosine distribution without TBN reorientation
        sincos(r3.x * 3.1415927 * 2,  ray.dir.y,  ray.dir.x);
        ray.dir.z = (r + r3.y) / nrays * 2.0 - 1.0; 
        ray.dir.xy *= sqrt(1.0 - ray.dir.z * ray.dir.z); //build sphere
        ray.dir = normalize(ray.dir + n);
#elif MATERIAL_TYPE == 1
        float alpha = RT_ROUGHNESS * RT_ROUGHNESS; //isotropic       
        //"random" point on disc - do I have to do sqrt() ?
        float2 uniform_disc;
        sincos(r3.x * 3.1415927 * 2,  uniform_disc.y,  uniform_disc.x);
        uniform_disc *= sqrt(r3.y);       
        float3 v = tangent_eyedir;
        float3 h = ggx_vndf(uniform_disc, alpha.xx, v);
        float3 l = reflect(-v, h);

        //single scatter lobe
        float3 brdf = ggx_g2_g1(l, v , alpha.xx); //if l.z > 0 is checked later
        brdf = l.z < 1e-7 ? 0 : brdf; //test?
        float vdoth = dot(eyedir, h);
        brdf *= schlick_fresnel(vdoth, specular_color);

        ray.dir = mul(l, tangent_base); //l from tangent to projection

        if (dot(ray.dir, n) < 0.02) continue;
#endif

        float ray_incT = (ray_maxT / nsteps) * rsqrt(saturate(1.0 - ray.dir.z * ray.dir.z)); 
  
        ray.length = ray_incT * r3.z;
        ray.origin = p;
        ray.uv = i.uv;

        float intersected = RayTracing::compute_intersection(ray, ray_maxT, ray_incT, RT_Z_THICKNESS * RT_Z_THICKNESS, RT_HIGHP_LIGHT_SPREAD);
    
        [branch]
        if(RT_IL_AMOUNT * intersected < 0.05)
        {
            o.w += intersected;
#if IMAGEBASEDLIGHTING != 0
            float4 probe = tex2Dlod(sProbeTex, ray.dir.xy * 0.5 + 0.5, 0);  unpack_hdr(probe.rgb);
            o += probe * RT_IBL_AMOUT;
#endif
            continue;     
        }
        else
        {
#if MATERIAL_TYPE == 1
            //revert to fullres mips for sharper reflection at low roughness settings
            ray.width *= smoothstep(0.05, 0.3, RT_ROUGHNESS);
#endif
            float4 albedofetch = tex2Dlod(sColorTex, ray.uv, ray.width + 2);
            float3 albedo = albedofetch.rgb * albedofetch.a; //mask out sky
            float3 intersect_normal = tex2Dlod(sGBufferTex, ray.uv, 0).xyz; 
            albedo *= lerp(RT_BACKFACE_MIRROR ? 0.2 : 0, 1, saturate(dot(-intersect_normal, ray.dir) * 64.0));  
#if MATERIAL_TYPE == 1  
            albedo *= brdf;
            albedo *= 10.0;
#endif
#if INFINITE_BOUNCES != 0
            float4 nextbounce = tex2Dlod(sGITexFilter0, ray.uv, ray.width);
            float3 compounded = normalize(albedo+0.1) * nextbounce.rgb;
            albedo += compounded * RT_IL_BOUNCE_WEIGHT;
#endif
            //for lambert: * cos theta / pdf == 1 because cosine weighted
            o += float4(albedo * intersected, intersected);
        }        
    }

    o /= nrays;
}

void PS_TemporalBlend(in VSOUT i, out MRT2 o)
{
    if(RT_DO_RENDER)
    {
        float4 gi_curr = tex2D(sGITex, i.uv);
        float4 gi_prev = tex2D(sGITexFilter0, i.uv);
        int stacksize = round(tex2Dlod(sStackCounterTexPrev, i.uv, 0).x);
        o.t0 = stacksize < MONTECARLO_MAX_STACK_SIZE ? lerp(gi_prev, gi_curr, rcp(1 + stacksize)) : gi_prev;
        o.t1 = ++stacksize;
        return;
    }

    float4 gbuf_curr = tex2D(sGBufferTex,     i.uv);
    float4 gbuf_prev = tex2D(sGBufferTexPrev, i.uv);

    float4 delta = abs(gbuf_curr - gbuf_prev);
    float normal_sensitivity = 2.0;
	float z_sensitivity = 1.0;
    delta /= max(FRAMETIME, 1.0) / 16.7; //~1 for 60 fps, expected range;
    float d = dot(delta, float4(delta.xyz * normal_sensitivity, z_sensitivity)); //normal squared, depth linear
	float w = saturate(exp2(-d * 2.0));

    int stacksize = round(tex2Dlod(sStackCounterTexPrev, i.uv, 3).x); //using a mip here causes a temporal fading so the history is blurred as well for soft transitions
    stacksize = w > 0.001 ? min(64, ++stacksize) : 1;
    
    float lerpspeed = rcp(stacksize);
    float mip = max(0, 2 - stacksize);

    float4 gi_curr = tex2Dlod(sGITex, i.uv, mip);
    float4 gi_prev = tex2D(sGITexFilter0, i.uv);

    uint window = exp2(mip);
    float4 m1 = gi_curr, m2 = gi_curr * gi_curr;
    [loop]for(int x = -2; x <= 2; x++)
    [loop]for(int y = -2; y <= 2; y++)
    {
        float4 t = tex2Dlod(sGITex, i.uv + float2(x, y) * BUFFER_PIXEL_SIZE * window, 0);
        m1 += t; m2 += t * t;
    }
    m1 /= 25.0; m2 /= 25.0;
    float4 sigma = sqrt(abs(m2 - m1 * m1));
    float4 expectederror = float4(1,1,1,0.01) * rsqrt(RT_RAY_AMOUNT);
    float4 acceptederror = sigma * expectederror;
    gi_prev = clamp(gi_prev, m1 - acceptederror, m1 + acceptederror);

    float4 gi = lerp(gi_prev, gi_curr, lerpspeed);
    o.t0 = gi;
    o.t1 = stacksize;
}

void PS_Filter0(in VSOUT i, out float4 o : SV_Target0) {     o = Denoise::atrous(i, sGITexFilter1, 0, RT_DO_RENDER - RTGI_DEBUG_SKIP_FILTER * 2); }
void PS_Filter1(in VSOUT i, out float4 o : SV_Target0) {     o = Denoise::atrous(i, sGITexFilter0, 1, RT_DO_RENDER - RTGI_DEBUG_SKIP_FILTER * 2); }
void PS_Filter2(in VSOUT i, out float4 o : SV_Target0) {     o = Denoise::atrous(i, sGITexFilter1, 2, RT_DO_RENDER - RTGI_DEBUG_SKIP_FILTER * 2); }
void PS_Filter3(in VSOUT i, out float4 o : SV_Target0) {     o = Denoise::atrous(i, sGITexFilter0, 3, RT_DO_RENDER - RTGI_DEBUG_SKIP_FILTER * 2); }

//void PS_CopyPrev(in VSOUT i, out MRT2 o)
void PS_CopyPrev(in VSOUT i, out MRT3 o)
{
    o.t0 = tex2D(sGITexFilter1, i.uv);
    o.t1 = tex2D(sGBufferTex, i.uv);
    o.t2 = tex2D(sStackCounterTex, i.uv);
}

void PS_Display(in VSOUT i, out float4 o : SV_Target0)
{ 
    float4 gi = tex2D(sGITexFilter0, i.uv);
    float3 color = tex2D(ColorInput, i.uv).rgb;

    color = unpack_hdr(color);
    
    color = RT_DEBUG_VIEW == 1 ? 0.8 : color;    
   
    float fade = fade_distance(i);
    gi *= fade; 

    float gi_intensity = RT_IL_AMOUNT * RT_IL_AMOUNT * (RT_USE_SRGB ? 3 : 1);
    float ao_intensity = RT_AO_AMOUNT* (RT_USE_SRGB ? 2 : 1);

#if SKYCOLOR_MODE != 0
 #if SKYCOLOR_MODE == 1
    float3 skycol = SKY_COLOR;
 #elif SKYCOLOR_MODE == 2
    float3 skycol = tex2Dfetch(sProbeTex, 0).rgb; //take topleft pixel of probe tex, outside of hemisphere range //tex2Dfetch(sSkyCol, 0).rgb;
    skycol = lerp(dot(skycol, 0.333), skycol, SKY_COLOR_SAT * 0.2);
 #elif SKYCOLOR_MODE == 3
    float3 skycol = tex2Dfetch(sProbeTex, 0).rgb * SKY_COLOR_TINT; //tex2Dfetch(sSkyCol, 0).rgb * SKY_COLOR_TINT;
    skycol = lerp(dot(skycol, 0.333), skycol, SKY_COLOR_SAT * 0.2);
 #endif
    skycol *= fade;  

    color += color * gi.rgb * gi_intensity; //apply GI
    color = color / (1.0 + lerp(1.0, skycol, SKY_COLOR_AMBIENT_MIX) * gi.w * ao_intensity); //apply AO as occlusion of skycolor
    color = color * (1.0 + skycol * SKY_COLOR_AMT);
#else    
    color += color * gi.rgb * gi_intensity; //apply GI
    color = color / (1.0 + gi.w * ao_intensity);  
#endif

    color = pack_hdr(color); 

    //dither a little bit as large scale lighting might exhibit banding
    color += dither(i);

    color = RT_DEBUG_VIEW == 3 ? tex2D(sStackCounterTex, i.uv).x/64.0 : RT_DEBUG_VIEW == 2 ? tex2D(sGBufferTex, i.uv).xyz * float3(0.5, 0.5, -0.5) + 0.5 : color;
    o = float4(color, 1);
}

#if IMAGEBASEDLIGHTING != 0 || SKYCOLOR_MODE >= 2
void PS_Probe(in VSOUT i, out float4 o : SV_Target0)
{
    float3 n;
    n.xy = i.uv * 2.0 - 1.0;
    n.z  = sqrt(saturate(1.0 - dot(n.xy, n.xy)));

    bool probe = length(n.xy) < 1.3; //n.z > 1e-3; //padding

    uint2 kernel_spatial   = uint2(32 * BUFFER_ASPECT_RATIO.yx);
    uint kernel_temporal   = 64;
    uint frame_num         = FRAMECOUNT;
    float2 grid_increment   = rcp(kernel_spatial); //blocksize in % of screen
    float2 grid_start      = Random::goldenweyl2(frame_num % kernel_temporal) * grid_increment;
    float2 grid_pos        = grid_start;

    float4 probe_light = 0;
    float4 sky_light   = 0;

    float wsum = 0.00001;

    for(int x = 0; x < kernel_spatial.x; x++)
    {
        for(int y = 0; y < kernel_spatial.y; y++)
        {
            float4 tapg = tex2Dlod(sGBufferTex, grid_pos, 0);
            float4 tapc = tex2Dlod(sColorTex, grid_pos, 2);
            tapc.rgb *= tapc.a;

            tapg.a = Projection::z_to_depth(tapg.a);
            
            float similarity = saturate(dot(tapg.xyz, -n)); //similarity *= similarity;       
            //similarity = pow(similarity, tempF1.x);  
            bool issky = tapg.a > 0.999;

            float3 tap_sdr = pack_hdr(tapc.rgb);

            sky_light   += float4(tap_sdr, 1) * issky;
            probe_light += float4(tapc.rgb, 1) * tapg.a * probe * similarity  * !issky;//float4(tapc.rgb * similarity * !issky, 1) * tapg.a * 0.01 * probe;    
            wsum += tapg.a * probe;
            grid_pos.y += grid_increment.y;          
        }
        grid_pos.y = grid_start.y;
        grid_pos.x += grid_increment.x;
    }

    probe_light /= wsum;
    sky_light.rgb   /= sky_light.a + 1e-3;

    float4 prev_probe = tex2D(sProbeTexPrev, i.uv); 

    o = 0;
    if(probe) //process central area with hemispherical probe light
    {
        o = lerp(prev_probe, probe_light, 0.02);  
        o = saturate(o);        
    }
    else
    {
        bool skydetectedthisframe = sky_light.w > 0.000001;
        bool skydetectedatall = prev_probe.w; 

        float h = 0;

        if(skydetectedthisframe)
            h = skydetectedatall ? saturate(0.1 * 0.01 * FRAMETIME) : 1; 

        o.rgb = lerp(prev_probe.rgb, sky_light.rgb, h);
        o.w = skydetectedthisframe || skydetectedatall;
    }
}

void PS_CopyProbe(in VSOUT i, out float4 o : SV_Target0)
{
    o = tex2D(sProbeTex, i.uv);
}
#endif


/*=============================================================================
	Techniques
=============================================================================*/

technique RTGlobalIllumination
< ui_tooltip = "              >> qUINT::RTGI 0.30 <<\n\n"
               "         EARLY ACCESS -- PATREON ONLY\n"
               "Official versions only via patreon.com/mcflypg\n"
               "\nRTGI is written by Pascal Gilcher (Marty McFly) \n"
               "Early access, featureset might be subject to change"; >
{
#if IMAGEBASEDLIGHTING != 0 || SKYCOLOR_MODE >= 2
pass{ VertexShader = VS_RT; PixelShader  = PS_Probe;            RenderTarget = ProbeTex;                                                                      } 
pass{ VertexShader = VS_RT; PixelShader  = PS_CopyProbe;        RenderTarget = ProbeTexPrev;                                                                  }
#endif //IMAGEBASEDLIGHTING
#if SMOOTHNORMALS != 0
#if HALFRES_INPUT != 0 
pass{ VertexShader = VS_RT; PixelShader = PS_InputSetupHalfGbuf;RenderTarget0 = GITexFilter1;                                                                 } 
pass{ VertexShader = VS_RT; PixelShader = PS_InputSetupHalfZCol;RenderTarget0 = ColorTex;    RenderTarget1 = ZTex;                                            } 
#else //HALFRES_INPUT 
pass{ VertexShader = VS_RT; PixelShader = PS_InputSetupFull;    RenderTarget0 = ColorTex;    RenderTarget1 = ZTex;      RenderTarget2 = GITexFilter1;         } 
#endif //HALFRES_INPUT
pass{ VertexShader = VS_RT; PixelShader = PS_Smoothnormals;     RenderTarget0 = GBufferTex;                                                                   }  
#else //SMOOTHNORMALS
#if HALFRES_INPUT != 0 
pass{ VertexShader = VS_RT; PixelShader = PS_InputSetupHalfGbuf;RenderTarget0 = GBufferTex;                                                                   } 
pass{ VertexShader = VS_RT; PixelShader = PS_InputSetupHalfZCol;RenderTarget0 = ColorTex;    RenderTarget1 = ZTex;                                            } 
#else //HALFRES_INPUT
pass{ VertexShader = VS_RT; PixelShader = PS_InputSetupFull;    RenderTarget0 = ColorTex;    RenderTarget1 = ZTex;      RenderTarget2 = GBufferTex;           }  
#endif //HALFRES_INPUT 
#endif //SMOOTHNORMALS
pass{ VertexShader = VS_RT; PixelShader = PS_RTGI;              RenderTarget0 = GITex;                                                                        } 
pass{ VertexShader = VS_RT; PixelShader = PS_TemporalBlend;     RenderTarget0 = GITexFilter1;      RenderTarget1 = StackCounterTex;                                                           } //GITex + filter 0 (prev) -> filter 1 

pass{ VertexShader = VS_RT; PixelShader = PS_Filter0;           RenderTarget0 = GITexFilter0;                                                                 } //f1 f0
pass{ VertexShader = VS_RT; PixelShader = PS_Filter1;           RenderTarget0 = GITexFilter1;                                                                 } //f0 f1
pass{ VertexShader = VS_RT; PixelShader = PS_Filter2;           RenderTarget0 = GITexFilter0;                                                                 } //f1 f0
pass{ VertexShader = VS_RT; PixelShader = PS_Filter3;           RenderTarget0 = GITexFilter1;                                                                 } //f0 f1
pass{ VertexShader = VS_RT; PixelShader = PS_CopyPrev;          RenderTarget0 = GITexFilter0;  RenderTarget1 = GBufferTexPrev;    RenderTarget2 = StackCounterTexPrev;                            } //f1 -> f0
pass{ VertexShader = VS_RT; PixelShader = PS_Display;                                                                                                         }
}
