// New Movie Library player - plugin description for DPF
#pragma once

#define DISTRHO_PLUGIN_BRAND   "New Movie Library"
#define DISTRHO_PLUGIN_NAME    "New Movie Library"
#define DISTRHO_PLUGIN_URI     "urn:newmovielibrary:player"
#define DISTRHO_PLUGIN_CLAP_ID "com.newmovielibrary.player"

#define DISTRHO_PLUGIN_HAS_UI           1
#define DISTRHO_PLUGIN_IS_RT_SAFE       1
#define DISTRHO_PLUGIN_IS_SYNTH         1
#define DISTRHO_PLUGIN_NUM_INPUTS       0
#define DISTRHO_PLUGIN_NUM_OUTPUTS      2
#define DISTRHO_PLUGIN_WANT_TIMEPOS     1
#define DISTRHO_PLUGIN_WANT_STATE       1
#define DISTRHO_PLUGIN_WANT_FULL_STATE  1
#define DISTRHO_PLUGIN_WANT_DIRECT_ACCESS 1

#define DISTRHO_UI_USE_CUSTOM           1
#define DISTRHO_UI_CUSTOM_INCLUDE_PATH  "DearImGui.hpp"
#define DISTRHO_UI_CUSTOM_WIDGET_TYPE   DGL_NAMESPACE::ImGuiTopLevelWidget
#define DISTRHO_UI_DEFAULT_WIDTH        980
#define DISTRHO_UI_DEFAULT_HEIGHT       640
#define DISTRHO_UI_USER_RESIZABLE       1
#define DISTRHO_UI_FILE_BROWSER         1

#define DISTRHO_PLUGIN_VST3_CATEGORIES  "Instrument|Sampler"
#define DISTRHO_PLUGIN_CLAP_FEATURES    "instrument", "sampler", "stereo"
#define DISTRHO_PLUGIN_LV2_CATEGORY     "lv2:InstrumentPlugin"
