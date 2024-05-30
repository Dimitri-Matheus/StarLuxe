#define PI 3.141592358

uniform float center_x <
    #if __RESHADE__ < 40000
        ui_type = "drag";
    #else
        ui_type = "slider";
    #endif
    ui_min = 0.0; ui_max = 360.0;
> = 0;

uniform float center_y <
    #if __RESHADE__ < 40000
        ui_type = "drag";
    #else 
        ui_type = "slider";
    #endif
    ui_min = 0.0; ui_max = 360.0;
> =0;

uniform float offset_x <
    #if __RESHADE__ < 40000
        ui_type = "drag";
    #else
        ui_type = "slider";
    #endif
    ui_min = 0.0; ui_max = 1.0;
> = 0;

uniform float offset_y <
    #if __RESHADE__ < 40000
        ui_type = "drag";
    #else 
        ui_type = "slider";
    #endif
    ui_min = 0.0; ui_max = .5;
> = 0;

uniform float scale <
    #if __RESHADE__ < 40000
        ui_type = "drag";
    #else
        ui_type = "slider";
    #endif
    ui_min = 0.0; ui_max = 10.0;
> = 10.0;

uniform float z_rotation <
    #if __RESHADE__ < 40000
        ui_type = "drag";
    #else
        ui_type = "slider";
    #endif
    ui_min = 0.0; ui_max = 360.0;
> = 0.5;


float3x3 getrot(float3 r)
{
    const float cx = cos(radians(r.x));
    const float sx = sin(radians(r.x));
    const float cy = cos(radians(r.y));
    const float sy = sin(radians(r.y));
    const float cz = cos(radians(r.z));
    const float sz = sin(radians(r.z));

    const float m1 = cy * cz;
    const float m2= cx * sz + sx * sy * cz;
    const float m3= sx * sz - cx * sy * cz;
    const float m4= -cy * sz;
    const float m5= cx * cz - sx * sy * sz;
    const float m6= sx * cz + cx * sy * sz;
    const float m7= sy;
    const float m8= -sx * cy;
    const float m9= cx * cy;

    return float3x3
    (
        m1,m2,m3,
        m4,m5,m6,
        m7,m8,m9
    );
};