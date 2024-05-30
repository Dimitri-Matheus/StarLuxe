#define LANG_en 0
#define LANG_zh_cn 1

#ifndef LANGUAGE
	#define LANGUAGE LANG_en
#endif

#if !defined(LANGUAGE) || LANGUAGE == LANG_en
	#define LABEL(en, zh_cn) ui_label = en;
#elif LANGUAGE == LANG_zh_cn
	#define LABEL(en, zh_cn) ui_label = zh_cn;
#else
	#define LABEL(en, zh_cn) ui_label = en;
#endif

#if !defined(LANGUAGE) || LANGUAGE == LANG_en
	#define CATEGORY(en, zh_cn) ui_category = en;
#elif LANGUAGE == LANG_zh_cn
	#define CATEGORY(en, zh_cn) ui_category = zh_cn;
#else
	#define CATEGORY(en, zh_cn) ui_category = en;
#endif

#if !defined(LANGUAGE) || LANGUAGE == LANG_en
	#define TOOLTIP(en, zh_cn) ui_tooltip = en;
#elif LANGUAGE == LANG_zh_cn
	#define TOOLTIP(en, zh_cn) ui_tooltip = zh_cn;
#else
	#define TOOLTIP(en, zh_cn) ui_tooltip = en;
#endif

#if !defined(LANGUAGE) || LANGUAGE == LANG_en
	#define ITEMS(en, zh_cn) ui_items = en;
#elif LANGUAGE == LANG_zh_cn
	#define ITEMS(en, zh_cn) ui_items = zh_cn;
#else
	#define ITEMS(en, zh_cn) ui_items = en;
#endif
