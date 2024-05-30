// Simple Curve Tool For Fun!
// version 0.2.0
// Copyright (c) 2023-2024 BarricadeMKXX
// License: MIT

#include "ReShade.fxh"
#include "ReShadeUI.fxh"
#include "BX_Multilingual.fxh"

#define CURVEWINDOW_SZ 1024.0
// #define CURVEPOINT_SZ 2.0


namespace SimpleCurveTool {
	uniform int ___ABOUT<
		ui_type = "radio";
		ui_label = " ";
		CATEGORY("Quick Guide", "简单说明")
	#if LANGUAGE == LANG_zh_cn
		ui_text = "每通道的曲线最多添加包含起点终点在内总共8个锚点。\n"
				  "对于头尾以外的点，可以通过右键重设为默认值(-1,-1)以从曲线上移除。\n"
				  "请尽量保持曲线锚点横坐标递增，否则本着色器会干预锚点位置。\n"
				  "且，本工具为实验性质，不保证与PS等软件的曲线工具行为一致。";
	#else
		ui_text = "Every channel supports up to 8 anchors, including the first and last.\n"
				  "You can remove anchors by right clicking and resetting to (-1, -1),\n"
				  "however the first and last anchor cannot be removed."
				  "It's better to keep the x-coord of active anchors increasing.\n"
				  "Besides, this tool is still WIP, and may not behave the same as softwares like Photoshop.";
	#endif
	>;

	uniform bool bUseChR<
		LABEL("Enable: Red", "启用红色通道")
		CATEGORY("Channel: Red", "红色通道")
		ui_category_toggle = true;
	> = false;

	uniform float2 fPointR_0<
		LABEL("Anchor #0", "锚点#0")
		ui_type = "slider";
		CATEGORY("Channel: Red", "红色通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(0.0, 0.0);
	uniform float2 fPointR_1<
		LABEL("Anchor #1", "锚点#1")
		ui_type = "slider";
		CATEGORY("Channel: Red", "红色通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);
	uniform float2 fPointR_2<
		LABEL("Anchor #2", "锚点#2")
		ui_type = "slider";
		CATEGORY("Channel: Red", "红色通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);
	uniform float2 fPointR_3<
		LABEL("Anchor #3", "锚点#3")
		ui_type = "slider";
		CATEGORY("Channel: Red", "红色通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);
	uniform float2 fPointR_4<
		LABEL("Anchor #4", "锚点#4")
		ui_type = "slider";
		CATEGORY("Channel: Red", "红色通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);
	uniform float2 fPointR_5<
		LABEL("Anchor #5", "锚点#5")
		ui_type = "slider";
		CATEGORY("Channel: Red", "红色通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);
	uniform float2 fPointR_6<
		LABEL("Anchor #6", "锚点#6")
		ui_type = "slider";
		CATEGORY("Channel: Red", "红色通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);
	uniform float2 fPointR_7<
		LABEL("Anchor #7", "锚点#7")
		ui_type = "slider";
		CATEGORY("Channel: Red", "红色通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(1, 1);

	uniform bool bUseChG<
		LABEL("Enable: Green", "启用绿色通道")
		CATEGORY("Channel: Green", "绿色通道")
		ui_category_toggle = true;
	> = false;

	uniform float2 fPointG_0<
		LABEL("Anchor #0", "锚点#0")
		ui_type = "slider";
		CATEGORY("Channel: Green", "绿色通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(0.0, 0.0);
	uniform float2 fPointG_1<
		LABEL("Anchor #1", "锚点#1")
		ui_type = "slider";
		CATEGORY("Channel: Green", "绿色通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);
	uniform float2 fPointG_2<
		LABEL("Anchor #2", "锚点#2")
		ui_type = "slider";
		CATEGORY("Channel: Green", "绿色通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);
	uniform float2 fPointG_3<
		LABEL("Anchor #3", "锚点#3")
		ui_type = "slider";
		CATEGORY("Channel: Green", "绿色通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);
	uniform float2 fPointG_4<
		LABEL("Anchor #4", "锚点#4")
		ui_type = "slider";
		CATEGORY("Channel: Green", "绿色通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);
	uniform float2 fPointG_5<
		LABEL("Anchor #5", "锚点#5")
		ui_type = "slider";
		CATEGORY("Channel: Green", "绿色通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);
	uniform float2 fPointG_6<
		LABEL("Anchor #6", "锚点#6")
		ui_type = "slider";
		CATEGORY("Channel: Green", "绿色通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);
	uniform float2 fPointG_7<
		LABEL("Anchor #7", "锚点#7")
		ui_type = "slider";
		CATEGORY("Channel: Green", "绿色通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(1, 1);

	uniform bool bUseChB<
		LABEL("Enable: Blue", "启用蓝色通道")
		CATEGORY("Channel: Blue", "蓝色通道")
		ui_category_toggle = true;
	> = false;

	uniform float2 fPointB_0<
		LABEL("Anchor #0", "锚点#0")
		ui_type = "slider";
		CATEGORY("Channel: Blue", "蓝色通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(0.0, 0.0);
	uniform float2 fPointB_1<
		LABEL("Anchor #1", "锚点#1")
		ui_type = "slider";
		CATEGORY("Channel: Blue", "蓝色通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);
	uniform float2 fPointB_2<
		LABEL("Anchor #2", "锚点#2")
		ui_type = "slider";
		CATEGORY("Channel: Blue", "蓝色通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);
	uniform float2 fPointB_3<
		LABEL("Anchor #3", "锚点#3")
		ui_type = "slider";
		CATEGORY("Channel: Blue", "蓝色通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);
	uniform float2 fPointB_4<
		LABEL("Anchor #4", "锚点#4")
		ui_type = "slider";
		CATEGORY("Channel: Blue", "蓝色通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);
	uniform float2 fPointB_5<
		LABEL("Anchor #5", "锚点#5")
		ui_type = "slider";
		CATEGORY("Channel: Blue", "蓝色通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);
	uniform float2 fPointB_6<
		LABEL("Anchor #6", "锚点#6")
		ui_type = "slider";
		CATEGORY("Channel: Blue", "蓝色通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);
	uniform float2 fPointB_7<
		LABEL("Anchor #7", "锚点#7")
		ui_type = "slider";
		CATEGORY("Channel: Blue", "蓝色通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(1, 1);

	uniform bool bUseChA<
		LABEL("Enable: RGB", "启用RGB通道")
		CATEGORY("Channel: RGB All", "RGB通道")
		ui_category_toggle = true;
	> = true;

	uniform float2 fPointA_0<
		LABEL("Anchor #0", "锚点#0")
		ui_type = "slider";
		CATEGORY("Channel: RGB All", "RGB通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(0.0, 0.0);
	uniform float2 fPointA_1<
		LABEL("Anchor #1", "锚点#1")
		ui_type = "slider";
		CATEGORY("Channel: RGB All", "RGB通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);
	uniform float2 fPointA_2<
		LABEL("Anchor #2", "锚点#2")
		ui_type = "slider";
		CATEGORY("Channel: RGB All", "RGB通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);
	uniform float2 fPointA_3<
		LABEL("Anchor #3", "锚点#3")
		ui_type = "slider";
		CATEGORY("Channel: RGB All", "RGB通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);
	uniform float2 fPointA_4<
		LABEL("Anchor #4", "锚点#4")
		ui_type = "slider";
		CATEGORY("Channel: RGB All", "RGB通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);
	uniform float2 fPointA_5<
		LABEL("Anchor #5", "锚点#5")
		ui_type = "slider";
		CATEGORY("Channel: RGB All", "RGB通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);
	uniform float2 fPointA_6<
		LABEL("Anchor #6", "锚点#6")
		ui_type = "slider";
		CATEGORY("Channel: RGB All", "RGB通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);
	uniform float2 fPointA_7<
		LABEL("Anchor #7", "锚点#7")
		ui_type = "slider";
		CATEGORY("Channel: RGB All", "RGB通道")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(1, 1);

	uniform bool bShowOverlay <
		LABEL("Show Overlay", "显示曲线图")
		CATEGORY("Overlay", "覆盖层")
	> = true;

	uniform float2 fPosition<
		LABEL("Position", "位置")
		ui_type = "slider";
		CATEGORY("Overlay", "覆盖层")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(0.5, 0.5);

	uniform int4 iChannel <
		LABEL("Show Which Curve (R/G/B/All)", "显示哪些曲线（R/G/B/All）")
		ui_type = "slider";
		CATEGORY("Overlay", "覆盖层")
		TOOLTIP("Setting to 1 = Display this curve.", "设为1表示显示对应通道的曲线。")
		ui_min = 0; ui_max = 1;
	> = int4(1,1,1,1);
	
	uniform int iPlotSize <
		LABEL("Overlay Size", "覆盖层尺寸")
		ui_type = "slider";
		CATEGORY("Overlay", "覆盖层")
		ui_min = 256; ui_max = 512;
	> = 512;

	uniform float iPointSize <
		LABEL("Anchor Size", "锚点尺寸")
		ui_type = "slider";
		CATEGORY("Overlay", "覆盖层")
		ui_min = 1; ui_max = 10;
	> = 4;

	uniform float fCurveThick <
		LABEL("Line Width", "线宽")
		ui_type = "slider";
		CATEGORY("Overlay", "覆盖层")
		ui_min = 1; ui_max = 10;
	> = 2;

	uniform int3 iShowChannel<
		LABEL("Show Which Channel (R/G/B)", "显示输出通道(R/G/B)")
		ui_type = "slider";
		ui_min = 0; ui_max = 1;
		TOOLTIP("Setting to 1 = Display this image channel.", "设为1表示输出相应通道，顺序为RGB。")
		CATEGORY("Output", "输出")
	> = int3(1,1,1);

	texture2D texPointData{
		Width = 8;
		Height = 4;
		Format = RGBA32F; // x, y: Point Coord, z: valid, w: always 1.0
	};
	storage2D wPointData{ Texture = texPointData; };
	sampler2D sampPointData { Texture = texPointData; };

	texture texPointN{
		Width = 1;
		Height = 4;
		Format = R8;
	};
	storage2D wPointN { Texture = texPointN; };
	sampler2D sampPointN { Texture = texPointN; };

	texture texCurvePlot{
		Width = CURVEWINDOW_SZ;
		Height = CURVEWINDOW_SZ;
		Format = RGBA8;
	};
	sampler2D sampCurvePlot { Texture = texCurvePlot; };

	texture texCurveData{
		Width = CURVEWINDOW_SZ;
		Height = 4;
		Format = R32F;
	};
	sampler2D sampCurveData{ Texture = texCurveData; AddressU = CLAMP; AddressV = CLAMP;};

	struct Points{
		float2 elem[8];
		int size;
	};
	groupshared Points AllPoints[4];

	struct Matrix{
		float mat[64];
		int size;
	};
	groupshared Matrix AllMatrices[4];

	struct Params{
		float4 coef[8];
		float2 diffXY[8];
		float diffK[8];
	};
	groupshared Params AllParams[4];

	texture texCurveParam{
		Width = 8;          // curve slices
		Height = 4;         // rgba curve channels
		Format = RGBA32F;   // xyzw<->abcd, where: a + b*(x-x0) + c*(x-x0)^2 + d*(x-x0)^3
	};
	storage2D wCurveParam{ Texture = texCurveParam; };
	sampler2D sampCurveParam{ Texture = texCurveParam; };

	int pointSequence(in uint3 id, inout Points pts){
		float2 output[8];
		output[0] = pts.elem[0];
		int i = 1, j = 1; float x_max = 0;
		while(i < 8 && j < 8){
			if(all(pts.elem[j] >= 0)){
				if(output[i-1].x < pts.elem[j].x){
					output[i] = pts.elem[j];
					x_max = pts.elem[j].x;
				}
				else{
					output[i] = float2(output[i-1].x + 0.001, pts.elem[j].y);
					x_max = output[i].x;
				}
				i++;
			}
			j++;
		}
		int ret = i;
		while(i < 8){
			output[i] = float2(-1, -1);
			i++;
		}
		if(x_max > 1.0)
			for (int i = 0; i < 8; i++)
				output[i].x = (output[i].y >= 0) ? output[i].x * (2.0 - x_max) : output[i].x;
		[unroll]
		for (int i = 0; i < 8; i++)
			pts.elem[i] = output[i];
		return ret;
	}

	void getPoints(uint3 id : SV_DispatchThreadID){
		// id.x: 0~7(Points) id.y: 0~3 (RGBA Channels)
		if(id.x == 0){
			switch(id.y){
				case 0:
					AllPoints[id.y].elem = {fPointR_0, fPointR_1, fPointR_2, fPointR_3, fPointR_4, fPointR_5, fPointR_6, fPointR_7};
					break;
				case 1:
					AllPoints[id.y].elem = {fPointG_0, fPointG_1, fPointG_2, fPointG_3, fPointG_4, fPointG_5, fPointG_6, fPointG_7};
					break;
				case 2:
					AllPoints[id.y].elem = {fPointB_0, fPointB_1, fPointB_2, fPointB_3, fPointB_4, fPointB_5, fPointB_6, fPointB_7};
					break;
				case 3:
					AllPoints[id.y].elem = {fPointA_0, fPointA_1, fPointA_2, fPointA_3, fPointA_4, fPointA_5, fPointA_6, fPointA_7};
					break;
				default:
					AllPoints[id.y].elem = {float2(0,0),float2(-1,-1),float2(-1,-1),float2(-1,-1),float2(-1,-1),float2(-1,-1),float2(-1,-1),float2(1,1)};
					break;
			}
			AllPoints[id.y].size = pointSequence(id, AllPoints[id.y]);
		}
		barrier();
		float edgeR = (id.x == 7 || AllPoints[id.y].elem[id.x+1].y < 0) ? 0.0 : AllPoints[id.y].elem[id.x+1].x;
		if(AllPoints[id.y].elem[id.x].y >= 0)
			tex2Dstore(wPointData, id.xy, float4(AllPoints[id.y].elem[id.x].xy, edgeR, 1));
		else
			tex2Dstore(wPointData, int2(id.x, id.y), float4(AllPoints[id.y].elem[id.x].xy, 0, 0));
		if(id.x == 0)
			tex2Dstore(wPointN, int2(0, id.y), AllPoints[id.y].size/8.0);
		barrier();
	}

	void solveMatrix(uint3 id : SV_DispatchThreadID){
		const int size = round(tex2Dfetch(sampPointN, int2(0,id.y)).x * 8);

		// calculate dx & dy
		if(id.x < size - 1)
			AllParams[id.y].diffXY[id.x] = tex2Dfetch(sampPointData, id.xy + int2(1,0)).xy - tex2Dfetch(sampPointData, id.xy).xy;
		else
			AllParams[id.y].diffXY[id.x] = float2(-1, 0);
		// calculate k = dy/dx
		AllParams[id.y].diffK[id.x] = AllParams[id.y].diffXY[id.x].y / AllParams[id.y].diffXY[id.x].x;
		// calculate dk
		barrier();
		float dk = 0;
		if(id.x > 0 && id.x < size - 1)
			dk = 3 * (AllParams[id.y].diffK[id.x] - AllParams[id.y].diffK[id.x-1]);
		AllParams[id.y].diffK[id.x] = dk;
		//barrier();
		// build matrix
		for(int m = 0; m < 8; m++){
			if(m == 0 || m == size - 1){
				AllMatrices[id.y].mat[m*8+id.x] = (id.x == m) ? 1 : 0;
			}
			else if(m >= size){
				AllMatrices[id.y].mat[m*8+id.x] = 0;
			}
			else{
				if(id.x == m)
					AllMatrices[id.y].mat[m*8+id.x] = 2 * (AllParams[id.y].diffXY[id.x-1].x + AllParams[id.y].diffXY[id.x].x);
				else if(id.x == m-1)
					AllMatrices[id.y].mat[m*8+id.x] = AllParams[id.y].diffXY[m-1].x;
				else if(id.x == m+1)
					AllMatrices[id.y].mat[m*8+id.x] = AllParams[id.y].diffXY[m].x;
				else
					AllMatrices[id.y].mat[m*8+id.x] = 0;
			}
		}
		barrier();
		// gaussian elimination
		for (int i = 1; i < 8; i++){
			if(i < size - 1){
				float r = AllMatrices[id.y].mat[i*9-1] / AllMatrices[id.y].mat[(i-1)*9];
				AllMatrices[id.y].mat[i*8+id.x] -= r * AllMatrices[id.y].mat[(i-1)*8+id.x];
				if(id.x == 0)
				AllParams[id.y].diffK[i] -= r * AllParams[id.y].diffK[i-1];
			}
			barrier();
		}
		// solve!
		float tmpACoeff = tex2Dfetch(sampPointData, id.xy).y;
		if(id.x == 0){
			AllParams[id.y].coef[0].z = 0;
			for(int i = 7; i > 0; i--){
				if(i >= size - 1){
					AllParams[id.y].coef[i].z = 0;
					continue;
				}
				// c[i] = (dk[i] - mat[i,i+1]*c[i+1]) / mat[i,i] :
				AllParams[id.y].coef[i].z = 
					(AllParams[id.y].diffK[i] - AllMatrices[id.y].mat[i*9+1] * AllParams[id.y].coef[i+1].z) / AllMatrices[id.y].mat[i*9];
			}
		}
		barrier();
		if(id.x < size - 1){
			float ks = AllParams[id.y].diffXY[id.x].y / AllParams[id.y].diffXY[id.x].x;
			AllParams[id.y].coef[id.x].y = ks 
											- AllParams[id.y].diffXY[id.x].x * AllParams[id.y].coef[id.x+1].z * 0.333333
											- AllParams[id.y].diffXY[id.x].x * AllParams[id.y].coef[id.x].z * 0.666667;
			AllParams[id.y].coef[id.x].x = tex2Dfetch(sampPointData, id.xy).y;
			AllParams[id.y].coef[id.x].w = (AllParams[id.y].coef[id.x+1].z - AllParams[id.y].coef[id.x].z) 
											* 0.333333 / AllParams[id.y].diffXY[id.x].x;
		}
		else{
			AllParams[id.y].coef[id.x].xyzw = float4(0,0,0,0);
		}
		barrier();
		tex2Dstore(wCurveParam, int2(id.x, id.y), AllParams[id.y].coef[id.x].xyzw);
	}

	void buildCurve(in float4 pos : SV_Position, in float2 texCoord : TEXCOORD, out float4 curveTex : SV_Target) {
		float2 pixelSize = 1.0 / iPlotSize;
		// calculate curve
		float curveData = 0;
		float4 ThisCoef;
		int i = floor(texCoord.y / 0.25);
		ThisCoef = 0;
		float edgeL = tex2Dfetch(sampPointData, int2(0, i)).x;
		float edgeR = tex2Dfetch(sampPointData, int2(0, i)).z;

		if(texCoord.x < edgeL){
			ThisCoef = float4(tex2Dfetch(sampPointData, int2(0, i)).y, 0,0,0);
			curveData = ThisCoef.x;
		}
		else{
			for(int j = 0; j <= 7; j++){
				edgeL = tex2Dfetch(sampPointData, int2(j, i)).x;
				edgeR = tex2Dfetch(sampPointData, int2(j, i)).z;
				if(texCoord.x >= edgeL && texCoord.x <= edgeR){
					ThisCoef = float4(tex2Dfetch(sampCurveParam, int2(j, i)));
					float xx0 = texCoord.x - tex2Dfetch(sampPointData, int2(j, i)).x;
					curveData = saturate(((ThisCoef.w * xx0 + ThisCoef.z) * xx0 + ThisCoef.y) * xx0 + ThisCoef.x);
					break;
				}
				else if(edgeR == 0){
					ThisCoef = float4(tex2Dfetch(sampPointData, int2(j, i)).y, 0,0,0);
					curveData = ThisCoef.x;
					break;
				}
			}
		}
		curveTex = curveData;
	}

	void applyCurve(in float4 pos : SV_Position, in float2 texCoord : TEXCOORD, out float4 output : SV_Target) {
		float2 texelSize = float2(1.0, 1.0) / float2(CURVEWINDOW_SZ, 4);
		//float2 texelSize = 0.0;
		float3 curColor = tex2D(ReShade::BackBuffer, texCoord);
		float3 stage1 = float3(			
			bUseChR ? tex2D(sampCurveData, float2(curColor.r, 0) + 0.5*texelSize).x : curColor.r,
			bUseChG ? tex2D(sampCurveData, float2(curColor.g, 0.25) + 0.5*texelSize).x : curColor.g,
			bUseChB ? tex2D(sampCurveData, float2(curColor.b, 0.5) + 0.5*texelSize).x : curColor.b
		);
		float3 stage2 = bUseChA ? float3(
			tex2D(sampCurveData, float2(stage1.r, 0.75) + 0.5*texelSize).x,
			tex2D(sampCurveData, float2(stage1.g, 0.75) + 0.5*texelSize).x,
			tex2D(sampCurveData, float2(stage1.b, 0.75) + 0.5*texelSize).x
		) : stage1;
		output = float4(stage2 * iShowChannel, 1);
	}

	#define fmod(x, y)(x - y * round(x / y))

	void buildOverlay(in float4 pos : SV_Position, in float2 texCoord : TEXCOORD, out float4 plotColor : SV_Target) {
		const float2 pixelSize = 1.0 / iPlotSize;

		float4 gridAlpha = (1 - smoothstep(fCurveThick*0.5-1, fCurveThick*0.5+1, 
									min(abs(fmod(texCoord.x,0.25)), abs(fmod(texCoord.y,0.25)))*iPlotSize)
							);
		plotColor = lerp(float4(0,0,0,1), float4(0.3,0.3,0.3,1), gridAlpha);

		for(int it = 0; it < 4; it ++){
			if(!iChannel[it])
				continue;
			// draw curve
			const float2 p = texCoord;
			const float2 lp = float2(texCoord.x - pixelSize.x*2, 1 - tex2D(sampCurveData, float2(texCoord.x - pixelSize.x*2, (it+0.5)/4.0)).x);
			const float2 rp = float2(texCoord.x + pixelSize.x*2, 1 - tex2D(sampCurveData, float2(texCoord.x + pixelSize.x*2, (it+0.5)/4.0)).x);
			float t = clamp(dot(p - lp, rp - lp)/dot(lp - rp, lp - rp),0,1);
			float2 prj = lerp(lp, rp, t);
			float dis = min(min(length(p - lp), length(p - rp)), length(prj - p));
			const float4 palette[4] = {float4(0.7,0,0,1), float4(0,0.7,0,1), float4(0,0,0.7,1), float4(0.7,0.7,0.7,1)};
			//plotColor = (1 - pow(2*dis*rcp(fCurveThick * pixelSize.xy), 3)) * palette[iChannel];
			float4 curveAlpha = (1 - smoothstep(fCurveThick*0.5-1, fCurveThick*0.5+1, dis*iPlotSize.x));
			plotColor = lerp(plotColor, palette[it], curveAlpha);
			// draw point
			for (int i = 0; i < 8; i++){
				float2 point_coord = tex2Dfetch(sampPointData, int2(i, it)).xy;
				if (point_coord.y >= 0){
					point_coord.y = 1 - point_coord.y;
					float dis = dot(abs(texCoord.xy - point_coord.xy), float2(1,1));
					if(dis <= iPointSize * pixelSize.x && dis > iPointSize * pixelSize.x * 0.5){
						float pointAlpha = 1.0;
						plotColor = lerp(plotColor, palette[it]!=0, pointAlpha);
						break;
					}
				}
			}
		}
	}

	void drawOverlay(in float4 pos : SV_Position, in float2 texCoord : TEXCOORD, out float4 passColor : SV_Target) {
		passColor = tex2D(ReShade::BackBuffer, texCoord);
		if(!bShowOverlay)
			return;
		const float3 pivot = float3(0.5, 0.5, 0.0);
		const float3 mulUV = float3(texCoord.x, texCoord.y, 1);
		const float2 ScaleSize = float2(iPlotSize, iPlotSize) / BUFFER_SCREEN_SIZE;

		const float3x3 positionMatrix = float3x3 (
			1, 0, 0,
			0, 1, 0,
			-fPosition.x, -fPosition.y, 1
		);
		const float3x3 scaleMatrix = float3x3 (
			1/ScaleSize.x, 0, 0,
			0, 1/ScaleSize.y, 0,
			0, 0, 1
		);
		const float3 SumUV = mul (mul (mulUV, positionMatrix), scaleMatrix);
		const float4 tex1 = tex2D(sampCurvePlot, SumUV.xy + pivot.xy) * all(SumUV + pivot == saturate(SumUV + pivot));
		passColor = lerp(passColor.rgb, tex1.rgb, tex1.a);
	}

	technique BX_ToyCurveTool<
		LABEL("BX::Toy Curve Tool (Alpha)", "BX::曲线工具内测版[BX_ToyCurveTool]")
		TOOLTIP("A simple curve tool WIP. Just for fun. Everything might be changed in the future.\n" \
				"Author: BarricadeMKXX" \
				, \
				"开发中的非正式版本，仅供娱乐，一切内容均有可能在后续版本中变化。\n" \
				"作者：路障MKXX。" \
				)
	>
	{
		pass passGetPoints{
			ComputeShader = getPoints<8, 4>;
			DispatchSizeX = 1;
			DispatchSizeY = 1;
		}
		pass passMatrix{
			ComputeShader = solveMatrix<8, 4>;
			DispatchSizeX = 1;
			DispatchSizeY = 1;
		}
		pass buildCurve{
			VertexShader = PostProcessVS;
			PixelShader = buildCurve;
			RenderTarget = texCurveData;
		}
		pass applyCurve{
			VertexShader = PostProcessVS;
			PixelShader = applyCurve;
		}
		pass buildOverlay{
			VertexShader = PostProcessVS;
			PixelShader = buildOverlay;
			RenderTarget = texCurvePlot;
		}
	}

	technique BX_ToyCurveTool_Overlay<
		LABEL("BX::Toy Curve Tool (Alpha) - Overlay", "BX::曲线工具内测版:覆盖层[BX_ToyCurveTool_Overlay]")
		TOOLTIP( \
			"The overlay of the curve tool. You can place it seperately from the main technique.\n" \
			"Just for fun. Everything might be changed in the future.\n" \
			"Author: BarricadeMKXX" \
			, \
			"独立拆分出的覆盖层，可以和曲线工具本体分开放置在着色器列表的不同位置。\n" \
			"开发中的非正式版本，仅供娱乐，一切内容均有可能在后续版本中变化。\n" \
			"作者：路障MKXX。" \
		)
	>
	{
		pass drawOverlay{
			VertexShader = PostProcessVS;
			PixelShader = drawOverlay;
		}
	}
}
