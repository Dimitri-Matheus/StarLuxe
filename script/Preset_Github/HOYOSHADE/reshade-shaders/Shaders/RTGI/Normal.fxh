/*=============================================================================

    Copyright (c) Pascal Gilcher. All rights reserved.

 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential

=============================================================================*/

#pragma once

/*===========================================================================*/

#include "Projection.fxh"

namespace Normal
{

//Generating normal vectors from depth buffer values
//v1 legacy 5 taps

float3 normal_from_depth(in VSOUT i)
{
    float3 center_position = Projection::uv_to_proj(i);

    float3 delta_x, delta_y;
    float4 neighbour_uv;
    
    neighbour_uv = i.uv.xyxy + float4(qUINT::PIXEL_SIZE.x, 0, -qUINT::PIXEL_SIZE.x, 0);

    float3 delta_right = Projection::uv_to_proj(neighbour_uv.xy) - center_position;
    float3 delta_left  = center_position - Projection::uv_to_proj(neighbour_uv.zw);

    delta_x = abs(delta_right.z) > abs(delta_left.z) ? delta_left : delta_right;

    neighbour_uv = i.uv.xyxy + float4(0, qUINT::PIXEL_SIZE.y, 0, -qUINT::PIXEL_SIZE.y);
        
    float3 delta_bottom = Projection::uv_to_proj(neighbour_uv.xy) - center_position;
    float3 delta_top  = center_position - Projection::uv_to_proj(neighbour_uv.zw);

    delta_y = abs(delta_bottom.z) > abs(delta_top.z) ? delta_top : delta_bottom;

    float3 normal = cross(delta_y, delta_x);
    normal *= rsqrt(dot(normal, normal)); //no epsilon, will cause issues for some reason

    return normal;
}   


//Generating normal vectors from depth buffer values
//v2 9 taps
//todo: resolve issues on small objects
/*
float3 normal_from_depth5(in VSOUT i)
{
	float3 a = Projection::uv_to_proj(i.uv - float2(qUINT::PIXEL_SIZE.x * 2, 0));
	float3 b = Projection::uv_to_proj(i.uv - float2(qUINT::PIXEL_SIZE.x * 1, 0));
	float3 c = Projection::uv_to_proj(i.uv);
	float3 d = Projection::uv_to_proj(i.uv + float2(qUINT::PIXEL_SIZE.x * 1, 0));
	float3 e = Projection::uv_to_proj(i.uv + float2(qUINT::PIXEL_SIZE.x * 2, 0));

	float3 c1 = b + (b - a);
	float3 c2 = d + (d - e);

	float delta1 = abs(c1.z - c.z) + 1e-7;
	float delta2 = abs(c2.z - c.z) + 1e-7;

	float3 DX = delta2/delta1 * (b-a) + delta1/delta2 * (e-d);

	a = Projection::uv_to_proj(i.uv - float2(0, qUINT::PIXEL_SIZE.x * 2));
	b = Projection::uv_to_proj(i.uv - float2(0, qUINT::PIXEL_SIZE.x * 1));
	d = Projection::uv_to_proj(i.uv + float2(0, qUINT::PIXEL_SIZE.x * 1));
	e = Projection::uv_to_proj(i.uv + float2(0, qUINT::PIXEL_SIZE.x * 2));

	c1 = b + (b - a);
	c2 = d + (d - e);

	delta1 = abs(c1.z - c.z) + 1e-7;
	delta2 = abs(c2.z - c.z) + 1e-7;

	float3 DY = delta2/delta1 * (b-a) + delta1/delta2 * (e-d);

    float3 N = normalize(cross(DY, DX));
    return N;
}*/
/*
float3 normal_from_depth(in VSOUT i)
{
    float2 offs[4] = 
    {
        float2(1, 0), // ->
        float2(1, 1), 
        float2(0, 1),
        float2(-1, 1)
    };

    float3 c = Projection::uv_to_proj(i.uv);
    float3 a,b,d,e;

    float4 vec[4];

    [unroll]
    for(int j = 0; j < 4; j++)
    {
        a = Projection::uv_to_proj(i.uv - offs[j] * qUINT::PIXEL_SIZE * 2);
        b = Projection::uv_to_proj(i.uv - offs[j] * qUINT::PIXEL_SIZE);
        d = Projection::uv_to_proj(i.uv + offs[j] * qUINT::PIXEL_SIZE);
        e = Projection::uv_to_proj(i.uv + offs[j] * qUINT::PIXEL_SIZE * 2);

        float3 c1 = b + (b - a);
        float3 c2 = d + (d - e);

        float delta1 = abs(c1.z - c.z) + 1e-7;
        float delta2 = abs(c2.z - c.z) + 1e-7;

        float3 D = delta2/delta1 * (b-a) + delta1/delta2 * (e-d);
        vec[j].xyz = D;
        vec[j].w = min(delta1, delta2);
    }

    int2 pairs[6] = 
    {
        int2(0,1),
        int2(0,2),
        int2(0,3),
        int2(1,2),
        int2(1,3),
        int2(2,3)
    };

    float4 N[6];
    
    [unroll]
    for(int j = 0; j < 6; j++)
    {
        N[j].xyz = normalize(cross(vec[pairs[j].x].xyz, vec[pairs[j].y].xyz));
        N[j].w = vec[pairs[j].x].w + vec[pairs[j].y].w;
    }

    float4 N_lowest = N[0];
    N_lowest = N_lowest.w < N[1].w ? N_lowest : N[1];
    N_lowest = N_lowest.w < N[2].w ? N_lowest : N[2];
    N_lowest = N_lowest.w < N[3].w ? N_lowest : N[3];
    N_lowest = N_lowest.w < N[4].w ? N_lowest : N[4];
    N_lowest = N_lowest.w < N[5].w ? N_lowest : N[5];

    return -N_lowest.xyz;
}
*/
float3x3 base_from_vector(float3 n)
{

    bool bestside = n.z < n.y;

    float3 n2 = bestside ? n.xzy : n;

    float3 k = (-n2.xxy * n2.xyy) * rcp(1.0 + n2.z) + float3(1, 0, 1);
    float3 u = float3(k.xy, -n2.x);
    float3 v = float3(k.yz, -n2.y);

    u = bestside ? u.xzy : u;
    v = bestside ? v.xzy : v;

    return float3x3(u, v, n);
}

} //Namespace