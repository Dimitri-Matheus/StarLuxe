///////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////
///                                                                                             ///
///                                                                                             ///
///        \  __ __|   \  |   _ \    ___|    _ \   |   |  ____|   _ \   ____|                   ///
///       _ \    |    |\/ |  |   | \___ \   |   |  |   |  __|    |   |  __|                     ///
///      ___ \   |    |   |  |   |       |  ___/   ___ |  |      __ <   |                       ///
///    _/    _\ _|   _|  _| \___/  _____/  _|     _|  _| _____| _| \_\ _____|                   ///
///                                                                                             ///
///                                                                                             ///
///    HOMOGENOUS FOG USING KOSCHMIEDER'S LAW                                                   /// 
///    <> BY TREYM                                                                              ///
///                                                                                             ///
///////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////

/*  ///////////////////////////////////////////////////////////////////////////////////////////  **
**  ///////////////////////////////////////////////////////////////////////////////////////////  **

    DO NOT REDISTRIBUTE WITHOUT PERMISION!

**  ///////////////////////////////////////////////////////////////////////////////////////////  **
**  ///////////////////////////////////////////////////////////////////////////////////////////  */


// FILE SETUP /////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////
#define   CATEGORIZE
#include "ReShade.fxh"
#include "Include/Lib/Common.fxh"

// USER INTERFACE /////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////

// PREPROCESSOR SETTINGS /////////////////////////
#ifndef ENABLE_MISC_CONTROLS
    #define ENABLE_MISC_CONTROLS 0
#endif

// #ifndef ENABLE_LINEAR_GAMMA
//     #define ENABLE_LINEAR_GAMMA 0
// #endif

#define CATEGORY "Fog Physical Properties" ///////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
UI_INT_S (DISTANCE, "Density", "Determines the apparent thickness of the fog.", 1, 100, 75, 0)
#define UI_DIST pow(DISTANCE * 0.01, 0.125)
UI_INT_S (HIGHLIGHT_DIST, "Highlight Distance", "Controls how far into the fog that highlights can penetrate.", 0, 100, 100, 1)

UI_COLOR (FOG_TINT, "Fog Color", "", 0.4, 0.45, 0.5, 5)
UI_COMBO (AUTO_COLOR, "Fog Color Mode", "", 2, 1,
    "Exact Fog Color\0"
    "Preserve Scene Luminance\0"
    "Use Blurred Scene Luminance\0")
UI_INT_S (WIDTH, "Light Scattering", "Controls width of light glow. Needs blurred scene luminance enabled.", 0, 100, 50, 1)
#undef  CATEGORY /////////////////////////////////////////////////////////////////////////////////

#if (ENABLE_MISC_CONTROLS != 0)
#define CATEGORY "Misc Controls" /////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
UI_INT_S (FOG_SAT, "Fog Saturation Boost", "(Unrealistic) Boosts the colorfulness of the fog", 0, 100, 0, 0)
UI_INT_S (BLUR_WIDTH, "Blur Width", "Determines the size of the blur used to generate the fog.", 50, 100, 100, 1)
UI_INT_S (BLEND, "Overall Blend", "(Unrealistic) Simply mixes fog with the original image.\n"
                                  "Anything below 100 is not really correct, but\n"
                                  "the control is here for those who want it.", 0, 100, 100, 1)
#undef  CATEGORY /////////////////////////////////////////////////////////////////////////////////
#endif


// FUNCTIONS /////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
#include "Include/Functions/AVGen.fxh"
#include "Include/Functions/BlendingModes.fxh"
#include "Include/Functions/TriDither.fxh"
#include "Include/Functions/GaussianBlurBounds.fxh"


// RENDERTARGETS //////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////
#if   (BUFFER_COLOR_BIT_DEPTH == 8)
    #define _COPY_BIT_DEPTH RGBA8
#elif (BUFFER_COLOR_BIT_DEPTH == 10)
    #define _COPY_BIT_DEPTH RGB10A2
#else
    #define _COPY_BIT_DEPTH RGBA16
#endif

RENDERTARGET(Copy,  BUFFER_WIDTH, BUFFER_HEIGHT, _COPY_BIT_DEPTH, MIRROR)
RENDERTARGET(Blur1, BUFFER_WIDTH, BUFFER_HEIGHT,  RGBA16F,        MIRROR)
RENDERTARGET(Blur2, BUFFER_WIDTH, BUFFER_HEIGHT,  RGBA16F,        MIRROR)


// SHADERS ///////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////

// COPY BACKBUFFER //////////////////////////////
void PS_Copy(PS_IN(vpos, coord), out float3 color : SV_Target)
{
    color  = tex2D(TextureColor, coord).rgb;
}

// IMAGE PREP ///////////////////////////////////
// Luma
void PS_PrepLuma(PS_IN(vpos, coord), out float3 luma : SV_Target)
{
    float depth, sky;
    luma  = tex2D(TextureColor, coord).rgb;
    depth = ReShade::GetLinearizedDepth(coord);
    sky   = all(1-depth);

    // Darken the background with distance
    luma  = lerp(luma, pow(abs(luma), lerp(2.0, 4.0, UI_DIST)), depth * sky);

    // Take only the luminance for next step
    luma  = GetLuma(luma);

    // #if (ENABLE_LINEAR_GAMMA != 0)
    //     luma = pow(luma, 2.2);
    // #endif
}

// Full backbuffer
void PS_Prep(PS_IN(vpos, coord), out float3 color : SV_Target)
{
    float depth, sky, width, luma;
    float3 tint, orig;
    color  = tex2D(TextureColor, coord).rgb;

    if (AUTO_COLOR > 1)
    {
        // Scale back up to 100%
        #if (ENABLE_MISC_CONTROLS != 0)
            luma  = tex2Dbicub(TextureBlur1, SCALE(coord, (1.0 / lerp(0.25, 0.125, BLUR_WIDTH * 0.01)))).rgb;
        #else
            luma  = tex2Dbicub(TextureBlur1, SCALE(coord, 8.0)).rgb;
        #endif
    }
    else
    {
        // Pass through
        luma  = tex2D(TextureBlur1, coord).xxx;
    }

    depth  = ReShade::GetLinearizedDepth(coord);
    sky    = all(1-depth);

    // Fog density setting (gamma controls how thick the fog is)
    depth  = pow(abs(depth), lerp(10.0, 0.25, UI_DIST));

    // Darken the background with distance
    color  = lerp(color, pow(abs(color), lerp(2.0, 4.0, UI_DIST)), depth * sky);

    // Desaturate slightly with distance
    color  = lerp(color, lerp(GetLuma(color), color, lerp(0.75, 1.0, (AUTO_COLOR != 0))), depth);

    // Grab the user defined color value for fog
    tint   = FOG_TINT;

    // Optionally modify the fog color value based on original scene luminance
    if (AUTO_COLOR > 0)
    {
        // Light scattering
        if (AUTO_COLOR > 1)
        {
            // Curve formula taken from CeeJay.dk's Curves shader
            width  = sin(3.1415927 * 0.5 * luma);
            width *= width;
            luma   = lerp(luma, width, lerp(1.0, -1.0, WIDTH * 0.01));
        }

        tint = tint - GetAvg(tint); // Remove average brightness from tint color
        tint = tint + luma;         // Replace tint brightness with scene brightness
    }

    // Overlay fog color to the scene before blurring in next step.
    // Additional masking for highlight protection. Code is a mess, I know.
    color  = lerp(color, lerp(tint + 0.125, tint, tint), depth * (1-smoothstep(0.0, 1.0, color) * (smoothstep(1.0, lerp(0.5, lerp(1.0, 0.75, UI_DIST), HIGHLIGHT_DIST * 0.01), depth))));
                         // Avoid black fog                      // Protect highlights using smoothstep on color input, then place the highlights in the scene with a second smoothstep depth mask
                                                                 // (this avoids the original sky color bleeding in on "Exact Fog Color" mode in the UI)

    // #if (ENABLE_LINEAR_GAMMA != 0)
    //     color = pow(color, 2.2);
    // #endif
}

// SCALE DOWN ///////////////////////////////////

// Luma downscale
void PS_Downscale1(PS_IN(vpos, coord), out float3 luma : SV_Target)
{
    // If modifying fog color by blurred scene luminance
    if (AUTO_COLOR > 1)
    {
        // Scale down to 12.5% before the blur passes
        #if (ENABLE_MISC_CONTROLS != 0)
            luma = tex2D(TextureColor, SCALE(coord, lerp(0.25, 0.125, BLUR_WIDTH * 0.01))).rgb;
        #else
            luma = tex2D(TextureColor, SCALE(coord, 0.125)).rgb;
        #endif
    }
    else
    {
        // Pass through
        luma = tex2D(TextureColor, coord).rgb;
    }
}

// Downscale pass for simple downscale + bi-cubic upscale for small blur
void PS_Downscale2(PS_IN(vpos, coord), out float3 color : SV_Target)
{
    // Scale down to 50% before the blur passes
    color  = tex2D(TextureColor, SCALE(coord, 0.5)).rgb;
}

// Downscale pass for the large blur
void PS_Downscale3(PS_IN(vpos, coord), out float3 color : SV_Target)
{
    // Scale down to 12.5% before the blur passes
    #if (ENABLE_MISC_CONTROLS != 0)
        color = tex2D(TextureColor, SCALE(coord, lerp(0.25, 0.125, BLUR_WIDTH * 0.01))).rgb;
    #else
        color = tex2D(TextureColor, SCALE(coord, 0.125)).rgb;
    #endif
}

// BI-LATERAL GAUSSIAN BLUR /////////////////////

// Luma blur horizontal pass
void PS_LumaBlurH(PS_IN(vpos, coord), out float3 luma : SV_Target)
{
    luma = tex2D(TextureBlur1, coord).x;

    if (AUTO_COLOR > 1)
    {
        luma  = Blur18H(luma, TextureBlur1, BoundsDefault, 1.0, coord).xxx;
    }
}
// Luma blur vertical pass
void PS_LumaBlurV(PS_IN(vpos, coord), out float3 luma : SV_Target)
{
    luma  = tex2D(TextureBlur2, coord).x;

    if (AUTO_COLOR > 1)
    {
        luma = Blur18V(luma, TextureBlur2, BoundsDefault, 1.0, coord).xxx;
    }
}

// Large color blur horizontal pass
void PS_BlurH(PS_IN(vpos, coord), out float3 color : SV_Target)
{
    color  = tex2D(TextureBlur1, coord).rgb;
    color  = Blur18H(color, TextureBlur1, 1.0, BoundsDefault, coord);
}
// Large color blur vertical pass
void PS_BlurV(PS_IN(vpos, coord), out float3 color : SV_Target)
{
    color  = tex2D(TextureBlur2, coord).rgb;
    color  = Blur18V(color, TextureBlur2, 1.0, BoundsDefault, coord);
}

// SCALE UP /////////////////////////////////////
// Simple blur upscale
void PS_UpScale(PS_IN(vpos, coord), out float3 color : SV_Target)
{
    // Scale simple downscale/upscale blur back up to 100%
    color  = tex2Dbicub(TextureBlur1, SCALE(coord, 2.0)).rgb;
}

// DRAW FOG /////////////////////////////////////
void PS_Combine(PS_IN(vpos, coord), out float3 color : SV_Target)
{
    float3 orig, blur, blur2, tint;
    float  depth, depth_avg, sky;

    #if (ENABLE_MISC_CONTROLS != 0)
        blur  = tex2Dbicub(TextureBlur1, SCALE(coord, (1.0 / lerp(0.25, 0.125, BLUR_WIDTH * 0.01)))).rgb;
    #else
        blur  = tex2Dbicub(TextureBlur1, SCALE(coord, 8.0)).rgb;
    #endif

    blur2     = tex2D(TextureColor, coord).rgb;
    color     = tex2D(TextureCopy,  coord).rgb;
    depth     = ReShade::GetLinearizedDepth(coord);
    sky       = all(1-depth);
    depth_avg = avGen::get().x;
    orig      = color;

    // #if (ENABLE_LINEAR_GAMMA != 0)
    //     blur = pow(blur, 2.2);
    // #endif

    // Fog density setting (gamma controls how thick the fog is)
    depth     = pow(abs(depth), lerp(10.0, 0.33, UI_DIST));

    // Use small blur texture to decrease distant detail
    color     = lerp(color, blur2, depth);

    // Darken the already dark parts of the image to give an impression of "shadowing" from fog using the large blur texture
    // Blending this way avoids extra dark halos on bright areas like the sky
    if (AUTO_COLOR < 1)
    {
        color = lerp(color, lerp(color * pow(abs(blur), 10.0), color, color), depth * saturate(1-GetLuma(color * 0.75)) * sky);
    }

    // Overlay the blur texture (while lifting its gamma in "Exact Fog Color" mode in the UI).
    // Mask protects highlights from being darkened
    color     = lerp(color, pow(abs(blur), lerp(0.75, 1.0, (AUTO_COLOR != 0))), depth * saturate(1-GetLuma(color * 0.75)));

    // Do some additive blending to give the impression of scene lights affecting the fog
    #if (ENABLE_MISC_CONTROLS != 0)
        blur  = saturate(lerp(GetLuma(blur), blur, (FOG_SAT + 100) * 0.01));
    #endif
    color     = lerp(color, ((color * 0.5) + pow(abs(blur * 2.0), 0.75)) * 0.5, depth);

    // Dither to kill any banding
    color    += TriDither(color, coord, 8);

    #if (ENABLE_MISC_CONTROLS != 0)
        color = lerp(orig, color, BLEND * 0.01);
    #endif
}


// TECHNIQUES /////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////
TECHNIQUE    (ATMOSPHERE,   "ATMOSPHERE", "",

    // Try to detect depth buffer when it is blank to avoid drawing over stuff like pause menus
    PASS_RT  (VS_Tri, PS_Copy,       RT_Copy)  // Copy the backbuffer

    // Blur the scene luminance
    PASS_RT  (VS_Tri, PS_PrepLuma,   RT_Blur2) // Prepare the scene for luma blurring
    PASS_RT  (VS_Tri, PS_Downscale1, RT_Blur1) // Scale down scene luma 12.5%
    PASS_RT  (VS_Tri, PS_LumaBlurH,  RT_Blur2) // Blur horizontally
    PASS_RT  (VS_Tri, PS_LumaBlurV,  RT_Blur1) // Blur vertically

    // Prepare the scene for the color blur pass
    PASS     (VS_Tri, PS_Prep)                 // Prepare the backbuffer for blurring

    // Do a quick downscale + bi-cubic upscale for a small cheap blur
    PASS_RT  (VS_Tri, PS_Downscale2, RT_Blur1) // Downscale by 50%
    PASS     (VS_Tri, PS_UpScale)              // Upscale back to 100% with bi-cubic filtering (this is the small blur)

    // Downscale + blur + upscale for very large blur radius
    PASS_RT  (VS_Tri, PS_Downscale3, RT_Blur1) // Scale down prepped backbuffer from above to 12.5%
    PASS_RT  (VS_Tri, PS_BlurH,      RT_Blur2) // Blur horizontally
    PASS_RT  (VS_Tri, PS_BlurV,      RT_Blur1) // Blur vertically

    // Combine the various blurs and draw the fog
    PASS     (VS_Tri, PS_Combine))             // Blend the blurred data and original backbuffer using depth
