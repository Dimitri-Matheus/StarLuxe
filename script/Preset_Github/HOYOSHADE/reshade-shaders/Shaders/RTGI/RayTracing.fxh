/*=============================================================================

    Copyright (c) Pascal Gilcher. All rights reserved.

 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 
=============================================================================*/

#pragma once 

//Functions and primitives required to trace/march rays in screen space
//against the depth buffer.

/*===========================================================================*/

namespace RayTracing
{

struct RayDesc 
{
    float3 pos;
    float3 dir;
    float2 uv;
    float currlen;
    float maxlen;
    float steplen;
    float width; //faux cone tracing
};

float compute_intersection(inout RayDesc ray, in RTInputs parameters, in VSOUT i)
{
	float intersected = 0;
	bool inside_screen = 1;

    float3 prevraypos = parameters.pos;
    float prevdelta = 0;

    float z_thickness = ray.maxlen * (RT_Z_THICKNESS * RT_Z_THICKNESS);

    [loop]
	while(ray.currlen < ray.maxlen && inside_screen)
    {   
    	float lambda = ray.currlen / ray.maxlen;    
        lambda = lambda * (lambda * (1.25 * lambda - 0.375) + 0.125); //fitted ray length growth

       	ray.pos = parameters.pos + ray.dir * lambda * ray.maxlen;

        ray.uv = Projection::proj_to_uv(ray.pos);
        inside_screen = all(saturate(-ray.uv * ray.uv + ray.uv));

        ray.width = clamp(log2(length((ray.uv - i.uv) * qUINT::SCREEN_SIZE)) - 4.5, 0, MIP_AMT);

        float3 pos = Projection::uv_to_proj(ray.uv, sZTex, ray.width);

        float delta = pos.z - ray.pos.z;

        if(RT_ALTERNATE_INTERSECT_TEST) 
        	z_thickness = ray.maxlen * (RT_Z_THICKNESS * RT_Z_THICKNESS) * lerp(0.02, 1, lambda) * 10.0;

		[branch]
		if(abs(delta * 2.0 + z_thickness) < z_thickness)
        //if(delta < 0 && delta > -z_thickness * abs(ray.dir.z))
        //if(delta * (delta + z_thickness) < 0)
        {
            intersected = inside_screen;

            ray.pos = lerp(prevraypos, ray.pos, prevdelta / (prevdelta + abs(delta)));
            ray.uv = Projection::proj_to_uv(ray.pos); //no need to check for screen boundaries, current and previous step are inside screen, so must be something inbetween

            if(RT_HIGHP_LIGHT_SPREAD)
                ray.dir = normalize(pos - parameters.pos);

            ray.currlen = 10000; //break
        }
      
        ray.currlen += ray.steplen;
        prevraypos = ray.pos;
        prevdelta = delta;
    }

    return intersected;
}

} //namespace