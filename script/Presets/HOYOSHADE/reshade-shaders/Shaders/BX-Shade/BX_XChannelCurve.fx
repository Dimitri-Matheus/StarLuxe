// Simple Cross Channel Curve Tool For Fun!
// version 0.2.0
// Copyright (c) 2023-2024 BarricadeMKXX
// License: MIT

#include "ReShade.fxh"
#include "ReShadeUI.fxh"
#include "BX_Multilingual.fxh"

#define CURVEWINDOW_SZ 1024.0
// #define CURVEPOINT_SZ 2.0

namespace XChannelCurve {
	uniform int ___ABOUT<
		ui_type = "radio";
		ui_label = " ";
		CATEGORY("Quick Guide", "简单说明")
	#if LANGUAGE == LANG_zh_cn
		ui_text = "每通道的曲线最多添加包含起点终点在内总共8个锚点。\n"
				  "对于头尾以外的点，可以通过右键重设为默认值(-1,-1)以从曲线上移除。\n"
				  "请尽量保持曲线锚点横坐标递增，否则本着色器会干预锚点位置。\n"
				  "纵坐标的调整为加算，而非百分比乘算。0.5对应于中性/不作调整，0对应于减去MAX，1对应于加上MAX。\n"
				  "此外，本工具目前为实验性质，不保证与Krita的跨通道曲线行为一致。";
	#else
		ui_text = "Every channel supports up to 8 anchors, including the first and last.\n"
				  "You can remove anchors by right clicking and resetting to (-1, -1),\n"
				  "however the first and last anchor cannot be removed."
				  "It's better to keep the x-coord of active anchors increasing.\n"
				  "The y-coords indicate addition/subtraction to the value.\n"
				  "0.5 = neutral(no change), 1.0 = +MAX & clamp (e.g. +255 for R/G/B), 0.0 = -MAX & clamp.\n"
				  "Besides, this tool is still WIP, and may not behave the same as Krita's cross channel curve.";
	#endif
	>;

	// uniform int4 iUseChannel<
	// 	LABEL("Enable Process", "启用过程")
	// 	ui_type = "slider";
	// 	ui_min = 0; ui_max = 1;
	// 	TOOLTIP("Setting to 1 = Enable the process. I~IV one by one.", "设为1表示使用相应过程，I~IV依次接力。")
	// 	CATEGORY("Process", "过程")
	// > = int4(1,1,1,1);

	uniform bool bUseCh1<
		LABEL("Enable Proc I", "启用过程I")
		CATEGORY("Process I (Cyan Line)", "过程I（青色线）")
		ui_category_toggle = true;
	> = true;

    uniform int iCh1_In<
        LABEL("Select Input", "输入选择")
        ui_type = "combo";
        CATEGORY("Process I (Cyan Line)", "过程I（青色线）")
        ITEMS("Red\0Green\0Blue\0Hue\0\Saturation\0Value\0", "红色\0绿色\0蓝色\0色相\0饱和度\0明度\0")
    > = 0;

    uniform int iCh1_Out<
        LABEL("Select Output", "输出选择")
        ui_type = "combo";
        CATEGORY("Process I (Cyan Line)", "过程I（青色线）")
        ITEMS("RGB\0Red\0Green\0Blue\0Hue\0\Saturation\0Value\0", "RGB\0红色\0绿色\0蓝色\0色相\0饱和度\0明度\0")
    > = 0;

	uniform float2 fPoint1_0<
		LABEL("Anchor #0", "锚点#0")
		ui_type = "slider";
		CATEGORY("Process I (Cyan Line)", "过程I（青色线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(0.0, 0.5);

	uniform float2 fPoint1_1<
		LABEL("Anchor #1", "锚点#1")
		ui_type = "slider";
		CATEGORY("Process I (Cyan Line)", "过程I（青色线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);

	uniform float2 fPoint1_2<
		LABEL("Anchor #2", "锚点#2")
		ui_type = "slider";
		CATEGORY("Process I (Cyan Line)", "过程I（青色线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);

	uniform float2 fPoint1_3<
		LABEL("Anchor #3", "锚点#3")
		ui_type = "slider";
		CATEGORY("Process I (Cyan Line)", "过程I（青色线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);

	uniform float2 fPoint1_4<
		LABEL("Anchor #4", "锚点#4")
		ui_type = "slider";
		CATEGORY("Process I (Cyan Line)", "过程I（青色线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);

	uniform float2 fPoint1_5<
		LABEL("Anchor #5", "锚点#5")
		ui_type = "slider";
		CATEGORY("Process I (Cyan Line)", "过程I（青色线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);

	uniform float2 fPoint1_6<
		LABEL("Anchor #6", "锚点#6")
		ui_type = "slider";
		CATEGORY("Process I (Cyan Line)", "过程I（青色线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);

	uniform float2 fPoint1_7<
		LABEL("Anchor #7", "锚点#7")
		ui_type = "slider";
		CATEGORY("Process I (Cyan Line)", "过程I（青色线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(1, 0.5);

	uniform bool bUseCh2<
		LABEL("Enable Proc II", "启用过程II")
		CATEGORY("Process II (Magenta Line)", "过程II（品红线）")
		ui_category_toggle = true;
	> = true;

	uniform int iCh2_InSrc<
		LABEL("Image Source", "图像源")
		ui_type = "combo";
		CATEGORY("Process II (Magenta Line)", "过程II（品红线）")
		TOOLTIP( \
			"Chose the image source for this process.\n" \
			"Since modifying RGB/HSV will also affect HSV/RGB, you might need to select a proper\n" \
			"image source to make the adjustment more accurate.\n" \
			"e.g. If you want to add yellow to areas with higher Value, here's an example setting:\n" \
			"  Process I:  Select Input = Value, Select Output = Red\n" \
			"  Process II: Image Source = Original Image, Select Input = Value, Select Output = Green\n" \
			"However, please remember that, a process always adjusts the output of previous process!" \
			, \
			"使用哪一阶段图像的颜色数据用作输入。\n" \
			"由于对RGB/HSV的调整会同步影响HSV/RGB，因此你可能需要调整图像数据源以保证复合调整的准确性。\n" \
			"举例：如果你想在明度较高的区域添加黄色（而非单纯的红或绿），那么可能需要类似下面的设置：\n" \
			"  过程I：输入选择=明度，输出选择=红色\n" \
			"  过程II：图像源=原始图像，输入选择=明度，输出选择=绿色\n" \
			"但是，输出端作出的调整仍然是基于前一个通道的！" \
		)
		ITEMS("Original Image\0Output of Process I\0", "原始图像\0过程I输出图像\0")
	> = 0;

    uniform int iCh2_In<
        LABEL("Select Input", "输入选择")
        ui_type = "combo";
        CATEGORY("Process II (Magenta Line)", "过程II（品红线）")
        ITEMS("Red\0Green\0Blue\0Hue\0\Saturation\0Value\0", "红色\0绿色\0蓝色\0色相\0饱和度\0明度\0")
    > = 0;

    uniform int iCh2_Out<
        LABEL("Select Output", "输出选择")
        ui_type = "combo";
        CATEGORY("Process II (Magenta Line)", "过程II（品红线）")
        ITEMS("RGB\0Red\0Green\0Blue\0Hue\0\Saturation\0Value\0", "RGB\0红色\0绿色\0蓝色\0色相\0饱和度\0明度\0")
    > = 0;

	uniform float2 fPoint2_0<
		LABEL("Anchor #0", "锚点#0")
		ui_type = "slider";
		CATEGORY("Process II (Magenta Line)", "过程II（品红线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(0.0, 0.5);

	uniform float2 fPoint2_1<
		LABEL("Anchor #1", "锚点#1")
		ui_type = "slider";
		CATEGORY("Process II (Magenta Line)", "过程II（品红线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);

	uniform float2 fPoint2_2<
		LABEL("Anchor #2", "锚点#2")
		ui_type = "slider";
		CATEGORY("Process II (Magenta Line)", "过程II（品红线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);

	uniform float2 fPoint2_3<
		LABEL("Anchor #3", "锚点#3")
		ui_type = "slider";
		CATEGORY("Process II (Magenta Line)", "过程II（品红线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);

	uniform float2 fPoint2_4<
		LABEL("Anchor #4", "锚点#4")
		ui_type = "slider";
		CATEGORY("Process II (Magenta Line)", "过程II（品红线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);

	uniform float2 fPoint2_5<
		LABEL("Anchor #5", "锚点#5")
		ui_type = "slider";
		CATEGORY("Process II (Magenta Line)", "过程II（品红线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);

	uniform float2 fPoint2_6<
		LABEL("Anchor #6", "锚点#6")
		ui_type = "slider";
		CATEGORY("Process II (Magenta Line)", "过程II（品红线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);

	uniform float2 fPoint2_7<
		LABEL("Anchor #7", "锚点#7")
		ui_type = "slider";
		CATEGORY("Process II (Magenta Line)", "过程II（品红线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(1, 0.5);

	uniform bool bUseCh3<
		LABEL("Enable Proc III", "启用过程III")
		CATEGORY("Process III (Yellow Line)", "过程 III（黄色线）")
		ui_category_toggle = true;
	> = true;

	uniform int iCh3_InSrc<
		LABEL("Image Source", "图像源")
		ui_type = "combo";
		CATEGORY("Process III (Yellow Line)", "过程 III（黄色线）")
		TOOLTIP( \
			"Chose the image source for this process.\n" \
			"Since modifying RGB/HSV will also affect HSV/RGB, you might need to select a proper\n" \
			"image source to make the adjustment more accurate.\n" \
			"e.g. If you want to add yellow to areas with higher Value, here's an example setting:\n" \
			"  Process I:  Select Input = Value, Select Output = Red\n" \
			"  Process II: Image Source = Original Image, Select Input = Value, Select Output = Green\n" \
			"However, please remember that, a process always adjusts the output of previous process!" \
			, \
			"使用哪一阶段图像的颜色数据用作输入。\n" \
			"由于对RGB/HSV的调整会同步影响HSV/RGB，因此你可能需要调整图像数据源以保证复合调整的准确性。\n" \
			"举例：如果你想在明度较高的区域添加黄色（而非单纯的红或绿），那么可能需要类似下面的设置：\n" \
			"  过程I：输入选择=明度，输出选择=红色\n" \
			"  过程II：图像源=原始图像，输入选择=明度，输出选择=绿色\n" \
			"但是，输出端作出的调整仍然是基于前一个通道的！" \
		)
		ITEMS("Original Image\0Output of Process I\0Output of Process II\0", "原始图像\0过程I输出图像\0过程II输出图像\0")
	> = 0;

    uniform int iCh3_In<
        LABEL("Select Input", "输入选择")
        ui_type = "combo";
        CATEGORY("Process III (Yellow Line)", "过程 III（黄色线）")
        ITEMS("Red\0Green\0Blue\0Hue\0\Saturation\0Value\0", "红色\0绿色\0蓝色\0色相\0饱和度\0明度\0")
    > = 0;

    uniform int iCh3_Out<
        LABEL("Select Output", "输出选择")
        ui_type = "combo";
        CATEGORY("Process III (Yellow Line)", "过程 III（黄色线）")
        ITEMS("RGB\0Red\0Green\0Blue\0Hue\0\Saturation\0Value\0", "RGB\0红色\0绿色\0蓝色\0色相\0饱和度\0明度\0")
    > = 0;

	uniform float2 fPoint3_0<
		LABEL("Anchor #0", "锚点#0")
		ui_type = "slider";
		CATEGORY("Process III (Yellow Line)", "过程 III（黄色线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(0.0, 0.5);

	uniform float2 fPoint3_1<
		LABEL("Anchor #1", "锚点#1")
		ui_type = "slider";
		CATEGORY("Process III (Yellow Line)", "过程 III（黄色线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);

	uniform float2 fPoint3_2<
		LABEL("Anchor #2", "锚点#2")
		ui_type = "slider";
		CATEGORY("Process III (Yellow Line)", "过程 III（黄色线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);

	uniform float2 fPoint3_3<
		LABEL("Anchor #3", "锚点#3")
		ui_type = "slider";
		CATEGORY("Process III (Yellow Line)", "过程 III（黄色线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);

	uniform float2 fPoint3_4<
		LABEL("Anchor #4", "锚点#4")
		ui_type = "slider";
		CATEGORY("Process III (Yellow Line)", "过程 III（黄色线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);

	uniform float2 fPoint3_5<
		LABEL("Anchor #5", "锚点#5")
		ui_type = "slider";
		CATEGORY("Process III (Yellow Line)", "过程 III（黄色线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);

	uniform float2 fPoint3_6<
		LABEL("Anchor #6", "锚点#6")
		ui_type = "slider";
		CATEGORY("Process III (Yellow Line)", "过程 III（黄色线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);

	uniform float2 fPoint3_7<
		LABEL("Anchor #7", "锚点#7")
		ui_type = "slider";
		CATEGORY("Process III (Yellow Line)", "过程 III（黄色线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(1, 0.5);

	uniform bool bUseCh4<
		LABEL("Enable Proc IV", "启用过程IV")
		CATEGORY("Process IV (Black Line)", "过程 IV（黑色线）")
		ui_category_toggle = true;
	> = true;

	uniform int iCh4_InSrc<
		LABEL("Image Source", "图像源")
		ui_type = "combo";
		CATEGORY("Process IV (Black Line)", "过程 IV（黑色线）")
		TOOLTIP( \
			"Chose the image source for this process.\n" \
			"Since modifying RGB/HSV will also affect HSV/RGB, you might need to select a proper\n" \
			"image source to make the adjustment more accurate.\n" \
			"e.g. If you want to add yellow to areas with higher Value, here's an example setting:\n" \
			"  Process I:  Select Input = Value, Select Output = Red\n" \
			"  Process II: Image Source = Original Image, Select Input = Value, Select Output = Green\n" \
			"However, please remember that, a process always adjusts the output of previous process!" \
			, \
			"使用哪一阶段图像的颜色数据用作输入。\n" \
			"由于对RGB/HSV的调整会同步影响HSV/RGB，因此你可能需要调整图像数据源以保证复合调整的准确性。\n" \
			"举例：如果你想在明度较高的区域添加黄色（而非单纯的红或绿），那么可能需要类似下面的设置：\n" \
			"  过程I：输入选择=明度，输出选择=红色\n" \
			"  过程II：图像源=原始图像，输入选择=明度，输出选择=绿色\n" \
			"但是，输出端作出的调整仍然是基于前一个通道的！" \
		)
		ITEMS("Original Image\0Output of Process I\0Output of Process II\0Output of Process III\0", "原始图像\0过程I输出图像\0过程II输出图像\0过程III输出图像\0")
	> = 0;

    uniform int iCh4_In<
        LABEL("Select Input", "输入选择")
        ui_type = "combo";
        CATEGORY("Process IV (Black Line)", "过程 IV（黑色线）")
        ITEMS("Red\0Green\0Blue\0Hue\0\Saturation\0Value\0", "红色\0绿色\0蓝色\0色相\0饱和度\0明度\0")
    > = 0;

    uniform int iCh4_Out<
        LABEL("Select Output", "输出选择")
        ui_type = "combo";
        CATEGORY("Process IV (Black Line)", "过程 IV（黑色线）")
        ITEMS("RGB\0Red\0Green\0Blue\0Hue\0\Saturation\0Value\0", "RGB\0红色\0绿色\0蓝色\0色相\0饱和度\0明度\0")
    > = 0;

	uniform float2 fPoint4_0<
		LABEL("Anchor #0", "锚点#0")
		ui_type = "slider";
		CATEGORY("Process IV (Black Line)", "过程 IV（黑色线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(0.0, 0.5);

	uniform float2 fPoint4_1<
		LABEL("Anchor #1", "锚点#1")
		ui_type = "slider";
		CATEGORY("Process IV (Black Line)", "过程 IV（黑色线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);

	uniform float2 fPoint4_2<
		LABEL("Anchor #2", "锚点#2")
		ui_type = "slider";
		CATEGORY("Process IV (Black Line)", "过程 IV（黑色线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);

	uniform float2 fPoint4_3<
		LABEL("Anchor #3", "锚点#3")
		ui_type = "slider";
		CATEGORY("Process IV (Black Line)", "过程 IV（黑色线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);

	uniform float2 fPoint4_4<
		LABEL("Anchor #4", "锚点#4")
		ui_type = "slider";
		CATEGORY("Process IV (Black Line)", "过程 IV（黑色线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);

	uniform float2 fPoint4_5<
		LABEL("Anchor #5", "锚点#5")
		ui_type = "slider";
		CATEGORY("Process IV (Black Line)", "过程 IV（黑色线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);

	uniform float2 fPoint4_6<
		LABEL("Anchor #6", "锚点#6")
		ui_type = "slider";
		CATEGORY("Process IV (Black Line)", "过程 IV（黑色线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(-1, -1);

	uniform float2 fPoint4_7<
		LABEL("Anchor #7", "锚点#7")
		ui_type = "slider";
		CATEGORY("Process IV (Black Line)", "过程 IV（黑色线）")
		ui_min = 0.0; ui_max = 1.0; ui_step = 0.001;
	> = float2(1, 0.5);

	uniform int iOutputLayers<
		LABEL("Output Processes", "输出层数")
		ui_type = "slider";
		CATEGORY("Output", "输出")
		TOOLTIP( \
			"Show the adjustments until which process's output.\n" \
			"0 = Original Image, 1 = Output of Process I, 4 = After I~IV all applied." \
			, \
			"显示直到哪个通道输出端为止的图像变换结果。\n" \
			"0对应原图，1对应只使用过程I，4对应过程I~IV全部发挥作用。" \
		)
		ui_min = 0; ui_max = 4;
	> = 4;

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
		LABEL("Show Which Curve", "显示哪些曲线")
		ui_type = "slider";
		CATEGORY("Overlay", "覆盖层")
		TOOLTIP( \
			"Setting to 1 = Display this curve.\n" \
			"Process I~IV are shown with cyan / magenta / yellow / black." \
			,
			"设为1表示显示对应通道的曲线。\n" \
            "I~IV的图示颜色顺序为青、品红、黄、黑。" \
		)
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

	texture2D texXPointData{
		Width = 8;
		Height = 4;
		Format = RGBA32F; // x, y: Point Coord, z: valid, w: always 1.0
	};
	storage2D wXPointData{ Texture = texXPointData; };
	sampler2D sampXPointData { Texture = texXPointData; };

	texture texXPointN{
		Width = 1;
		Height = 4;
		Format = R8;
	};
	storage2D wXPointN { Texture = texXPointN; };
	sampler2D sampXPointN { Texture = texXPointN; };

	texture texXCurvePlot{
		Width = CURVEWINDOW_SZ;
		Height = CURVEWINDOW_SZ;
		Format = RGBA8;
	};
	sampler2D sampXCurvePlot { Texture = texXCurvePlot; };

	texture texXCurveData{
		Width = CURVEWINDOW_SZ;
		Height = 4;
		Format = R32F;
	};
	sampler2D sampXCurveData{ Texture = texXCurveData; AddressU = CLAMP; AddressV = CLAMP;};

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

	texture texXCurveParam{
		Width = 8;          // curve slices
		Height = 4;         // rgba curve channels
		Format = RGBA32F;   // xyzw<->abcd, where: a + b*(x-x0) + c*(x-x0)^2 + d*(x-x0)^3
	};
	storage2D wXCurveParam{ Texture = texXCurveParam; };
	sampler2D sampXCurveParam{ Texture = texXCurveParam; };

	#define fmod(x, y)(x - y * round(x / y))

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
					AllPoints[id.y].elem = {fPoint1_0, fPoint1_1, fPoint1_2, fPoint1_3, fPoint1_4, fPoint1_5, fPoint1_6, fPoint1_7};
					break;
				case 1:
					AllPoints[id.y].elem = {fPoint2_0, fPoint2_1, fPoint2_2, fPoint2_3, fPoint2_4, fPoint2_5, fPoint2_6, fPoint2_7};
					break;
				case 2:
					AllPoints[id.y].elem = {fPoint3_0, fPoint3_1, fPoint3_2, fPoint3_3, fPoint3_4, fPoint3_5, fPoint3_6, fPoint3_7};
					break;
				case 3:
					AllPoints[id.y].elem = {fPoint4_0, fPoint4_1, fPoint4_2, fPoint4_3, fPoint4_4, fPoint4_5, fPoint4_6, fPoint4_7};
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
			tex2Dstore(wXPointData, id.xy, float4(AllPoints[id.y].elem[id.x].xy, edgeR, 1));
		else
			tex2Dstore(wXPointData, int2(id.x, id.y), float4(AllPoints[id.y].elem[id.x].xy, 0, 0));
		if(id.x == 0)
			tex2Dstore(wXPointN, int2(0, id.y), AllPoints[id.y].size/8.0);
		barrier();
	}

	void solveMatrix(uint3 id : SV_DispatchThreadID){
		const int size = round(tex2Dfetch(sampXPointN, int2(0,id.y)).x * 8);

		// calculate dx & dy
		if(id.x < size - 1)
			AllParams[id.y].diffXY[id.x] = tex2Dfetch(sampXPointData, id.xy + int2(1,0)).xy - tex2Dfetch(sampXPointData, id.xy).xy;
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
		float tmpACoeff = tex2Dfetch(sampXPointData, id.xy).y;
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
			AllParams[id.y].coef[id.x].x = tex2Dfetch(sampXPointData, id.xy).y;
			AllParams[id.y].coef[id.x].w = (AllParams[id.y].coef[id.x+1].z - AllParams[id.y].coef[id.x].z) 
											* 0.333333 / AllParams[id.y].diffXY[id.x].x;
		}
		else{
			AllParams[id.y].coef[id.x].xyzw = float4(0,0,0,0);
		}
		barrier();
		tex2Dstore(wXCurveParam, int2(id.x, id.y), AllParams[id.y].coef[id.x].xyzw);
	}

	void buildCurve(in float4 pos : SV_Position, in float2 texCoord : TEXCOORD, out float4 curveTex : SV_Target) {
		float2 pixelSize = 1.0 / iPlotSize;
		// calculate curve
		float curveData = 0;
		float4 ThisCoef;
		int i = floor(texCoord.y / 0.25);
		ThisCoef = 0;
		float edgeL = tex2Dfetch(sampXPointData, int2(0, i)).x;
		float edgeR = tex2Dfetch(sampXPointData, int2(0, i)).z;

		if(texCoord.x < edgeL){
			ThisCoef = float4(tex2Dfetch(sampXPointData, int2(0, i)).y, 0,0,0);
			curveData = ThisCoef.x;
		}
		else{
			for(int j = 0; j <= 7; j++){
				edgeL = tex2Dfetch(sampXPointData, int2(j, i)).x;
				edgeR = tex2Dfetch(sampXPointData, int2(j, i)).z;
				if(texCoord.x >= edgeL && texCoord.x <= edgeR){
					ThisCoef = float4(tex2Dfetch(sampXCurveParam, int2(j, i)));
					float xx0 = texCoord.x - tex2Dfetch(sampXPointData, int2(j, i)).x;
					curveData = saturate(((ThisCoef.w * xx0 + ThisCoef.z) * xx0 + ThisCoef.y) * xx0 + ThisCoef.x);
					break;
				}
				else if(edgeR == 0){
					ThisCoef = float4(tex2Dfetch(sampXPointData, int2(j, i)).y, 0,0,0);
					curveData = ThisCoef.x;
					break;
				}
			}
		}
		curveTex = curveData;
	}

    float3 RGBToHSV(float3 c) {
        float4 K = float4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
        float4 p = c.g < c.b ? float4(c.bg, K.wz) : float4(c.gb, K.xy);
        float4 q = c.r < p.x ? float4(p.xyw, c.r) : float4(c.r, p.yzx);

        float d = q.x - min(q.w, q.y);
        float e = 1.0e-10;
        return float3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
    }

    float3 HSVToRGB(float3 c) {
        float4 K = float4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
        float3 p = abs(frac(c.xxx + K.xyz) * 6.0 - K.www);
        return c.z * lerp(K.xxx, saturate(p - K.xxx), c.y);
    }

	void applyXCurve(in float4 pos : SV_Position, in float2 texCoord : TEXCOORD, out float4 output : SV_Target) {
		float2 texelSize = float2(1.0, 1.0) / float2(CURVEWINDOW_SZ, 4);
		//float2 texelSize = 0.0;
		float3 curColor = tex2D(ReShade::BackBuffer, texCoord);
		float3 chRGB[5] = {curColor, curColor, curColor, curColor, curColor};
        int source[4] = {iCh1_In, iCh2_In, iCh3_In, iCh4_In};
        int target[4] = {iCh1_Out, iCh2_Out, iCh3_Out, iCh4_Out};
		int imageSrc[4] = {0, iCh2_InSrc, iCh3_InSrc, iCh4_InSrc};
        float src_val = 0;
		const int4 iUseChannel = int4(bUseCh1, bUseCh2, bUseCh3, bUseCh4);
        for(int i = 0; i < 4; i++){
            if(iUseChannel[i] == 0){
				chRGB[i+1] = chRGB[i];
				continue;
			}
            float3 hsv = RGBToHSV(chRGB[imageSrc[i]]);
            switch(source[i]){
                case 0:
                    src_val = chRGB[imageSrc[i]].r;    
                    break;
                case 1:
                    src_val = chRGB[imageSrc[i]].g;    
                    break;
                case 2:
                    src_val = chRGB[imageSrc[i]].b;    
                    break;
                case 3:
                    src_val = hsv.x;    
                    break;
                case 4:
                    src_val = hsv.y;    
                    break;
                case 5:
                    src_val = hsv.z;    
                    break;
                default:
                    src_val = hsv.z;
                    break;
            }
            float adjust = tex2D(sampXCurveData, float2(src_val, float(i)/4.0) + 0.5 * texelSize).x;
            adjust = (adjust - 0.5) * 2;
			hsv = RGBToHSV(chRGB[i]); // 输出端作用在上次的输出上。
			chRGB[i+1] = chRGB[i];
            switch(target[i]){
                case 0: // rgb
                    chRGB[i+1] = saturate(chRGB[i] + adjust.xxx);
                    break;
                case 1: // r
                    chRGB[i+1].r = saturate(chRGB[i].r + adjust);
                    break;
                case 2: // g
                    chRGB[i+1].g = saturate(chRGB[i].g + adjust); 
                    break;
                case 3: // b
                    chRGB[i+1].b = saturate(chRGB[i].b + adjust);
                    break;
                case 4: // h
                    hsv.x = frac(hsv.x + adjust);
                    chRGB[i+1].rgb = HSVToRGB(hsv);
                    break;
                case 5: // s
                    hsv.y = saturate(hsv.y + adjust);
                    chRGB[i+1].rgb = HSVToRGB(hsv);
                    break;
                case 6: // v
                    hsv.z = saturate(hsv.z + adjust);
                    chRGB[i+1].rgb = HSVToRGB(hsv);
                    break;
                default:
                    chRGB[i+1].rgb = saturate(chRGB[i].rgb + adjust.xxx);
                    break;
            }
        }
		output = float4(chRGB[iOutputLayers], 1);
	}

	void buildOverlay(in float4 pos : SV_Position, in float2 texCoord : TEXCOORD, out float4 plotColor : SV_Target) {
		const float2 pixelSize = 1.0 / iPlotSize;

		float4 gridAlpha = (1 - smoothstep(fCurveThick*0.5-1, fCurveThick*0.5+1, 
									min(abs(fmod(texCoord.x,0.25)), abs(fmod(texCoord.y,0.25)))*iPlotSize)
							);
		plotColor = lerp(texCoord.y < 0.5?float4(1,1,1,1):float4(0.7,0.7,0.7,1), float4(0.8,0.8,0.8,1), gridAlpha);

		for(int it = 0; it < 4; it ++){
			if(!iChannel[it])
				continue;
			// draw curve
			const float2 p = texCoord;
			const float2 lp = float2(texCoord.x - pixelSize.x*2, 1 - tex2D(sampXCurveData, float2(texCoord.x - pixelSize.x*2, (it+0.5)/4.0)).x);
			const float2 rp = float2(texCoord.x + pixelSize.x*2, 1 - tex2D(sampXCurveData, float2(texCoord.x + pixelSize.x*2, (it+0.5)/4.0)).x);
			float t = clamp(dot(p - lp, rp - lp)/dot(lp - rp, lp - rp),0,1);
			float2 prj = lerp(lp, rp, t);
			float dis = min(min(length(p - lp), length(p - rp)), length(prj - p));
			const float4 palette[4] = {float4(0,0.7,0.7,1), float4(0.7,0,0.7,1), float4(0.7,0.7,0,1), float4(0,0,0,1)};
			//plotColor = (1 - pow(2*dis*rcp(fCurveThick * pixelSize.xy), 3)) * palette[iChannel];
			float4 curveAlpha = (1 - smoothstep(fCurveThick*0.5-1, fCurveThick*0.5+1, dis*iPlotSize.x));
			plotColor = lerp(plotColor, palette[it], curveAlpha);
			// draw point
			for (int i = 0; i < 8; i++){
				float2 point_coord = tex2Dfetch(sampXPointData, int2(i, it)).xy;
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
		const float4 tex1 = tex2D(sampXCurvePlot, SumUV.xy + pivot.xy) * all(SumUV + pivot == saturate(SumUV + pivot));
		passColor = lerp(passColor.rgb, tex1.rgb, tex1.a);
	}

	technique BX_XChannelCurve<
		LABEL("BX::Cross Channel Curve (Alpha)", "BX::跨通道曲线内测版[BX_XChannelCurve]")
		TOOLTIP( \
			"Cross channel curve tool WIP. Just for fun. Everything might be changed in the future.\n" \
			"This shader is inspired by the cross channel curve tool in Krita, but I'm not sure if this behaves the same. \n"
			"Author: BarricadeMKXX\n" \
			, \
			"开发中的非正式版本，仅供娱乐，一切内容均有可能在后续版本中变化。\n" \
			"该工具的灵感来源于Krita的跨通道曲线工具，但并不保证行为与其一致。\n" \
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
			RenderTarget = texXCurveData;
		}
		pass applyXCurve{
			VertexShader = PostProcessVS;
			PixelShader = applyXCurve;
		}
		pass buildOverlay{
			VertexShader = PostProcessVS;
			PixelShader = buildOverlay;
			RenderTarget = texXCurvePlot;
		}
	}

	technique BX_XChannelCurve_Overlay<
		LABEL("BX::Cross Channel Curve (Alpha) - Overlay", "BX::跨通道曲线内测版:覆盖层[BX_XChannelCurve_Overlay]")
		TOOLTIP( \
			"The overlay of the cross channel curve tool. You can place it seperately from the main technique.\n" \
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