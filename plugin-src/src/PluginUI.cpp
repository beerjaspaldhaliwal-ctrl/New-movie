// New Movie Library player: the plugin window (Dear ImGui).
// Instrument browser, the PLAY / SOUND / PERFORM pages (same controls and layout as the
// Kontakt panels), presets, master volume, an on-screen keyboard and library-folder setup.
#include "DistrhoUI.hpp"
#include "src/Resources.hpp"

#include <algorithm>
#include <cctype>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#include "PluginShared.hpp"

namespace nml {
SharedStatus* sharedStatusFromPlugin(void* plugin);  // PluginDSP.cpp
}

START_NAMESPACE_DISTRHO

using namespace nml;

namespace {

const ImU32 kBg = IM_COL32(17, 18, 22, 255);
const ImU32 kPanel = IM_COL32(26, 28, 34, 255);
const ImU32 kPanel2 = IM_COL32(36, 39, 47, 255);
const ImU32 kLine = IM_COL32(56, 60, 72, 255);
const ImU32 kText = IM_COL32(228, 230, 234, 255);
const ImU32 kDim = IM_COL32(138, 144, 158, 255);
const ImU32 kGold = IM_COL32(222, 182, 92, 255);
const ImU32 kGoldDark = IM_COL32(112, 90, 46, 255);
const ImU32 kRed = IM_COL32(210, 82, 70, 255);
const ImU32 kWarn = IM_COL32(236, 150, 70, 255);

const ImU32 kBusColors[8] = {IM_COL32(236, 140, 70, 255), IM_COL32(232, 206, 86, 255), IM_COL32(150, 214, 92, 255),
                             IM_COL32(84, 200, 220, 255), IM_COL32(150, 120, 230, 255), IM_COL32(222, 100, 190, 255),
                             IM_COL32(70, 200, 170, 255), IM_COL32(190, 140, 200, 255)};

const char* const kNoteNames[12] = {"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"};
const char* const kSyncNames[13] = {"1/32", "1/16 T", "1/16", "1/8 T", "1/16 D", "1/8", "1/4 T",
                                    "1/8 D", "1/4", "1/2 T", "1/4 D", "1/2", "1 Bar"};
const char* const kPageNames[3] = {"PLAY", "SOUND", "PERFORM"};

constexpr int kBaseW = 980, kBaseH = 640;
constexpr int kKeyLo = 21, kKeyHi = 108;  // 88-key keyboard

std::string noteName(int m) { return std::string(kNoteNames[m % 12]) + std::to_string(m / 12 - 2); }  // C3 = 60
bool isBlack(int m) { const int pc = m % 12; return pc == 1 || pc == 3 || pc == 6 || pc == 8 || pc == 10; }

std::string lower(std::string s) {
    for (auto& ch : s) ch = (char)std::tolower((unsigned char)ch);
    return s;
}

ImU32 mix(ImU32 a, ImU32 b, float t) {
    const ImVec4 x = ImGui::ColorConvertU32ToFloat4(a), y = ImGui::ColorConvertU32ToFloat4(b);
    return ImGui::ColorConvertFloat4ToU32(ImVec4(x.x + (y.x - x.x) * t, x.y + (y.y - x.y) * t,
                                                 x.z + (y.z - x.z) * t, x.w + (y.w - x.w) * t));
}

std::string categoryTitle(const std::string& c) {  // "02 Orchestral" -> "Orchestral"
    const size_t sp = c.find(' ');
    return (sp != std::string::npos && sp <= 3) ? c.substr(sp + 1) : c;
}

}  // namespace

class NMLUI : public UI {
public:
    NMLUI()
        : UI(kBaseW, kBaseH) {
        const Catalog& cat = Catalog::get();
        s_ = (float)getScaleFactor();
        setGeometryConstraints((uint)(860 * s_), (uint)(580 * s_), false, false);
        status_ = sharedStatusFromPlugin(getPluginInstancePointer());
        params_.resize(cat.params.size(), 0.f);
        current_ = std::max(0, cat.instrument("Strings"));
        if (status_) {
            const int loaded = status_->loadedIndex.load(), loading = status_->loadingIndex.load();
            if (loaded >= 0) current_ = loaded;
            if (loading >= 0) current_ = loading;
        }
        for (size_t i = 0; i < params_.size(); ++i) params_[i] = cat.params[i].def;
        for (auto& c : cat.instruments[current_].controls) params_[c.param] = (float)c.def;
        openCategory_ = cat.instruments[current_].category;
        setupFonts();
        setupStyle();
    }

protected:
    // ------------------------------------------------------------------ host callbacks
    void parameterChanged(uint32_t index, float value) override {
        if (index < params_.size()) params_[index] = value;
    }

    void stateChanged(const char* key, const char* value) override {
        if (std::strcmp(key, "instrument") == 0) {
            const int idx = Catalog::get().instrument(value);
            if (idx >= 0 && idx != current_) {
                current_ = idx;
                presetIndex_ = -1;
                openCategory_ = Catalog::get().instruments[idx].category;
            }
        } else if (std::strcmp(key, "library") == 0 && value && *value) {
            std::snprintf(pathBuf_, sizeof(pathBuf_), "%s", value);
        }
    }

    void uiFileBrowserSelected(const char* filename) override {
        if (!filename || !*filename) return;
        const std::string lib = paths::libraryFromAnyPath(filename);
        std::snprintf(pathBuf_, sizeof(pathBuf_), "%s", lib.empty() ? filename : lib.c_str());
        if (lib.empty()) browseError_ = true;
        else { browseError_ = false; setState("library", lib.c_str()); }
    }

    // ------------------------------------------------------------------ drawing
    void onImGuiDisplay() override {
        const Catalog& cat = Catalog::get();
        const float W = (float)getWidth(), H = (float)getHeight();
        const InstrumentDef& inst = cat.instruments[current_];
        help_.clear();
        syncArticulation(inst);

        ImGui::SetNextWindowPos(ImVec2(0, 0));
        ImGui::SetNextWindowSize(ImVec2(W, H));
        ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(0, 0));
        ImGui::Begin("NML", nullptr, ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_NoMove |
                                         ImGuiWindowFlags_NoScrollWithMouse | ImGuiWindowFlags_NoBringToFrontOnFocus);
        ImGui::PopStyleVar();
        ImDrawList* dl = ImGui::GetWindowDrawList();
        dl->AddRectFilled(ImVec2(0, 0), ImVec2(W, H), kBg);

        const float headerH = 64 * s_, keysH = 96 * s_, browserW = 222 * s_, gap = 10 * s_;
        drawHeader(dl, inst, ImVec2(0, 0), ImVec2(W, headerH));
        drawBrowser(ImVec2(gap, headerH + gap), ImVec2(browserW, H - headerH - keysH - 3 * gap));
        const ImVec2 mainPos(browserW + 2 * gap, headerH + gap);
        const ImVec2 mainSize(W - browserW - 3 * gap, H - headerH - keysH - 3 * gap);
        if (status_ && !status_->libraryFound.load()) drawLibrarySetup(dl, mainPos, mainSize);
        else drawMain(dl, inst, mainPos, mainSize);
        drawKeyboard(dl, inst, ImVec2(gap, H - keysH - gap), ImVec2(W - 2 * gap, keysH));
        ImGui::End();
    }

private:
    // ------------------------------------------------------------------ setup
    void setupFonts() {
        using namespace dpf_resources;
        ImGuiIO& io = ImGui::GetIO();
        io.Fonts->Clear();
        ImFontConfig fc;
        fc.FontDataOwnedByAtlas = false;
        fc.OversampleH = 2;
        fc.OversampleV = 1;
        fc.PixelSnapH = true;
        fontBody_ = io.Fonts->AddFontFromMemoryTTF((void*)dejavusans_ttf, dejavusans_ttf_size, 14.f * s_, &fc);
        fontSmall_ = io.Fonts->AddFontFromMemoryTTF((void*)dejavusans_ttf, dejavusans_ttf_size, 11.5f * s_, &fc);
        fontTitle_ = io.Fonts->AddFontFromMemoryTTF((void*)dejavusans_ttf, dejavusans_ttf_size, 23.f * s_, &fc);
        fontLogo_ = io.Fonts->AddFontFromMemoryTTF((void*)dejavusans_ttf, dejavusans_ttf_size, 16.f * s_, &fc);
        io.Fonts->Build();
    }

    void setupStyle() {
        ImGuiStyle& st = ImGui::GetStyle();
        st.FrameRounding = 4 * s_;
        st.PopupRounding = 4 * s_;
        st.ChildRounding = 6 * s_;
        st.GrabRounding = 4 * s_;
        st.ScrollbarRounding = 6 * s_;
        st.ScrollbarSize = 10 * s_;
        st.FramePadding = ImVec2(8 * s_, 4 * s_);
        st.ItemSpacing = ImVec2(6 * s_, 4 * s_);
        st.WindowBorderSize = 0;
        st.PopupBorderSize = 1;
        ImVec4* c = st.Colors;
        c[ImGuiCol_Text] = ImGui::ColorConvertU32ToFloat4(kText);
        c[ImGuiCol_TextDisabled] = ImGui::ColorConvertU32ToFloat4(kDim);
        c[ImGuiCol_WindowBg] = ImGui::ColorConvertU32ToFloat4(kBg);
        c[ImGuiCol_ChildBg] = ImGui::ColorConvertU32ToFloat4(kPanel);
        c[ImGuiCol_PopupBg] = ImVec4(0.12f, 0.13f, 0.16f, 0.98f);
        c[ImGuiCol_Border] = ImGui::ColorConvertU32ToFloat4(kLine);
        c[ImGuiCol_FrameBg] = ImGui::ColorConvertU32ToFloat4(kPanel2);
        c[ImGuiCol_FrameBgHovered] = ImVec4(0.19f, 0.20f, 0.24f, 1.f);
        c[ImGuiCol_FrameBgActive] = ImVec4(0.22f, 0.23f, 0.28f, 1.f);
        c[ImGuiCol_Button] = ImGui::ColorConvertU32ToFloat4(kPanel2);
        c[ImGuiCol_ButtonHovered] = ImVec4(0.22f, 0.23f, 0.28f, 1.f);
        c[ImGuiCol_ButtonActive] = ImGui::ColorConvertU32ToFloat4(kGoldDark);
        c[ImGuiCol_Header] = ImVec4(0.87f, 0.71f, 0.36f, 0.22f);
        c[ImGuiCol_HeaderHovered] = ImVec4(0.87f, 0.71f, 0.36f, 0.14f);
        c[ImGuiCol_HeaderActive] = ImVec4(0.87f, 0.71f, 0.36f, 0.30f);
        c[ImGuiCol_ScrollbarBg] = ImVec4(0, 0, 0, 0);
        c[ImGuiCol_ScrollbarGrab] = ImGui::ColorConvertU32ToFloat4(kLine);
        c[ImGuiCol_CheckMark] = ImGui::ColorConvertU32ToFloat4(kGold);
        c[ImGuiCol_PlotHistogram] = ImGui::ColorConvertU32ToFloat4(kGold);
        c[ImGuiCol_TextSelectedBg] = ImVec4(0.87f, 0.71f, 0.36f, 0.35f);
        c[ImGuiCol_NavHighlight] = ImVec4(0, 0, 0, 0);
    }

    // ------------------------------------------------------------------ parameters
    float param(int idx) const { return (idx >= 0 && idx < (int)params_.size()) ? params_[idx] : 0.f; }

    void setParam(int idx, float v, bool gesture = true) {
        if (idx < 0 || idx >= (int)params_.size()) return;
        if (gesture) editParameter((uint32_t)idx, true);
        setParameterValue((uint32_t)idx, v);
        if (gesture) editParameter((uint32_t)idx, false);
        params_[idx] = v;
    }

    void selectInstrument(int idx) {
        const InstrumentDef& d = Catalog::get().instruments[idx];
        current_ = idx;
        setState("instrument", d.key.c_str());
        for (auto& c : d.controls) setParam(c.param, (float)c.def);  // start from the instrument's own patch
        presetIndex_ = 0;
    }

    void applyPreset(const InstrumentDef& d, int p) {
        if (p < 0 || p >= (int)d.presets.size()) return;
        for (auto& c : d.controls) setParam(c.param, (float)c.def);
        for (auto& kv : d.presets[p].values) setParam(kv.first, (float)kv.second);
        presetIndex_ = p;
    }

    // Keyswitches change the articulation inside the engine; mirror that on the menu.
    void syncArticulation(const InstrumentDef& d) {
        if (!status_ || !status_->engine || d.engine != EngineType::Artic) return;
        if (status_->loadedIndex.load() != current_) return;
        const int art = status_->engine->currentArt.load();
        if (art != lastArt_) {
            lastArt_ = art;
            const int idx = Catalog::get().param("art_menu");
            if (idx >= 0 && (int)param(idx) != art) setParam(idx, (float)art);
        }
    }

    std::string formatValue(const ControlDef& c, float v) const {
        char b[64];
        const int iv = (int)std::lround(v);
        if (c.kind == "menu") return (iv >= 0 && iv < (int)c.items.size()) ? c.items[iv] : std::string("-");
        if (c.kind == "switch") return iv ? "On" : "Off";
        if ((c.var == "mic_close" || c.var == "mic_hall") && iv <= -400) return "Off";
        if (c.var.rfind("bus", 0) == 0 && iv <= -400) return "Off";
        if (c.var == "dly_time") {
            if (param(Catalog::get().param("dly_sync")) > 0.5f) return kSyncNames[std::min(12, std::max(0, (int)std::lround(v / 1000.f * 12.f)))];
            std::snprintf(b, sizeof(b), "%.0f ms", 10.0 * std::pow(200.0, v / 1000.0));
            return b;
        }
        if (c.var == "rev_decay") { std::snprintf(b, sizeof(b), "%.1f s", 0.4 + 11.6 * std::pow(v / 1000.0, 2.0)); return b; }
        if (c.var == "tone") {
            if (iv >= 1000) return "Open";
            const double hz = 20.0 * std::pow(1000.0, v / 1000.0);
            if (hz >= 1000) std::snprintf(b, sizeof(b), "%.1f kHz", hz / 1000.0);
            else std::snprintf(b, sizeof(b), "%.0f Hz", hz);
            return b;
        }
        if (c.var == "trem_rate") { std::snprintf(b, sizeof(b), "%.1f Hz", 0.5 + 9.5 * std::pow(v / 1000.0, 1.5)); return b; }
        const double x = (double)v / std::max(1, c.ratio);
        if (c.unit == "DB") std::snprintf(b, sizeof(b), c.ratio > 1 ? "%.1f dB" : "%.0f dB", x);
        else if (c.unit == "PERCENT") std::snprintf(b, sizeof(b), "%.0f%%", x);
        else if (c.unit == "MS") {
            if (v >= 1000) std::snprintf(b, sizeof(b), "%.2f s", v / 1000.0);
            else std::snprintf(b, sizeof(b), "%d ms", iv);
        } else if (c.unit == "ST") std::snprintf(b, sizeof(b), "%+.1f st", x);
        else std::snprintf(b, sizeof(b), c.ratio > 1 ? "%.1f" : "%.0f", x);
        return b;
    }

    // ------------------------------------------------------------------ widgets
    void text(ImDrawList* dl, ImFont* f, ImVec2 p, ImU32 col, const std::string& t) {
        dl->AddText(f, f->FontSize, p, col, t.c_str());
    }
    void textCentered(ImDrawList* dl, ImFont* f, ImVec2 c, ImU32 col, const std::string& t, float maxW = 0) {
        std::string s = t;
        ImVec2 sz = f->CalcTextSizeA(f->FontSize, FLT_MAX, 0, s.c_str());
        while (maxW > 0 && sz.x > maxW && s.size() > 3) {
            s = s.substr(0, s.size() - 4) + "..";
            sz = f->CalcTextSizeA(f->FontSize, FLT_MAX, 0, s.c_str());
        }
        dl->AddText(f, f->FontSize, ImVec2(c.x - sz.x * 0.5f, c.y), col, s.c_str());
    }

    void knob(ImDrawList* dl, const ControlDef& c, ImVec2 pos, float k) {
        const float w = 90 * k, size = 46 * k;
        ImGui::SetCursorScreenPos(pos);
        ImGui::PushID(c.var.c_str());
        ImGui::InvisibleButton("##knob", ImVec2(w, 84 * k));
        const bool hovered = ImGui::IsItemHovered(), active = ImGui::IsItemActive();
        float v = param(c.param);
        const float range = (float)(c.hi - c.lo);
        const ImGuiIO& io = ImGui::GetIO();
        if (ImGui::IsItemActivated()) {
            if (ImGui::IsMouseDoubleClicked(0)) { setParam(c.param, (float)c.def); dragging_ = false; }
            else { editParameter((uint32_t)c.param, true); dragging_ = true; dragValue_ = v; }
        }
        if (active && dragging_) {
            const float speed = range / (240.f * s_) * (io.KeyShift ? 0.1f : 1.f);
            dragValue_ = std::min((float)c.hi, std::max((float)c.lo, dragValue_ - io.MouseDelta.y * speed));
            const float nv = std::round(dragValue_);
            if (nv != v) { setParameterValue((uint32_t)c.param, nv); params_[c.param] = nv; v = nv; presetIndex_ = -1; }
        }
        if (ImGui::IsItemDeactivated() && dragging_) { editParameter((uint32_t)c.param, false); dragging_ = false; }
        if (hovered && io.MouseWheel != 0.f && !active) {
            const float step = std::max(1.f, std::round(range / (io.KeyShift ? 400.f : 50.f)));
            setParam(c.param, std::min((float)c.hi, std::max((float)c.lo, v + (io.MouseWheel > 0 ? step : -step))));
            v = param(c.param);
            presetIndex_ = -1;
        }
        if (hovered || active) help_ = c.help.empty() ? c.text : c.help;
        if (hovered) ImGui::SetMouseCursor(ImGuiMouseCursor_ResizeNS);

        const ImVec2 ctr(pos.x + w * 0.5f, pos.y + 18 * k + size * 0.5f);
        const float r = size * 0.5f;
        const float t = range > 0 ? (v - c.lo) / range : 0.f;
        const float a0 = kPi * 0.75f, a1 = kPi * 2.25f, av = a0 + (a1 - a0) * t;
        textCentered(dl, fontSmall_, ImVec2(ctr.x, pos.y), active || hovered ? kText : kDim, c.text, w);
        dl->AddCircleFilled(ctr, r * 0.80f, kPanel2, 32);
        dl->AddCircle(ctr, r * 0.80f, kLine, 32, 1.f);
        dl->PathArcTo(ctr, r, a0, a1, 40);
        dl->PathStroke(kLine, 0, 3.5f * k);
        // bipolar knobs (e.g. tune, velocity curve) fill from the centre
        const float tz = (c.lo < 0 && c.hi > 0 && c.unit != "DB") ? (0.f - c.lo) / range : 0.f;
        const float az = a0 + (a1 - a0) * tz;
        if (std::fabs(av - az) > 0.01f) {
            dl->PathArcTo(ctr, r, std::min(az, av), std::max(az, av), 40);
            dl->PathStroke(active ? kText : kGold, 0, 3.5f * k);
        }
        const ImVec2 tip(ctr.x + std::cos(av) * r * 0.72f, ctr.y + std::sin(av) * r * 0.72f);
        const ImVec2 base(ctr.x + std::cos(av) * r * 0.25f, ctr.y + std::sin(av) * r * 0.25f);
        dl->AddLine(base, tip, kText, 2.2f * k);
        textCentered(dl, fontSmall_, ImVec2(ctr.x, ctr.y + r + 4 * k), active ? kGold : kText, formatValue(c, v), w);
        ImGui::PopID();
    }

    void menu(ImDrawList* dl, const ControlDef& c, ImVec2 pos, float k) {
        text(dl, fontSmall_, ImVec2(pos.x, pos.y - 17 * k), kDim, c.text);
        ImGui::SetCursorScreenPos(pos);
        ImGui::PushID(c.var.c_str());
        ImGui::SetNextItemWidth(std::max(60.f, (float)c.w * k));
        const int cur = (int)std::lround(param(c.param));
        const std::string preview = formatValue(c, (float)cur);
        ImGui::PushFont(fontSmall_);
        ImGui::PushStyleVar(ImGuiStyleVar_FramePadding, ImVec2(6 * k, 5 * k));
        const bool open = ImGui::BeginCombo("##menu", preview.c_str(), ImGuiComboFlags_HeightLarge);
        ImGui::PopStyleVar();
        if (open) {
            for (int i = 0; i < (int)c.items.size(); ++i) {
                if (ImGui::Selectable(c.items[i].c_str(), i == cur)) { setParam(c.param, (float)i); presetIndex_ = -1; }
                if (i == cur) ImGui::SetItemDefaultFocus();
            }
            ImGui::EndCombo();
        }
        ImGui::PopFont();
        if (ImGui::IsItemHovered()) help_ = c.help;
        ImGui::PopID();
    }

    void toggle(ImDrawList* dl, const ControlDef& c, ImVec2 pos, float k) {
        const ImVec2 sz(std::max(70.f, (float)c.w * k), 24 * k);
        ImGui::SetCursorScreenPos(pos);
        ImGui::PushID(c.var.c_str());
        const bool on = param(c.param) > 0.5f;
        if (ImGui::InvisibleButton("##sw", sz)) { setParam(c.param, on ? 0.f : 1.f); presetIndex_ = -1; }
        const bool hovered = ImGui::IsItemHovered();
        if (hovered) help_ = c.help;
        const ImVec2 b(pos.x + sz.x, pos.y + sz.y);
        dl->AddRectFilled(pos, b, on ? mix(kPanel2, kGold, 0.28f) : (hovered ? mix(kPanel2, kText, 0.06f) : kPanel2), 4 * k);
        dl->AddRect(pos, b, on ? kGold : kLine, 4 * k);
        const float led = 4 * k;
        dl->AddCircleFilled(ImVec2(pos.x + 10 * k, pos.y + sz.y * 0.5f), led, on ? kGold : kLine);
        textCentered(dl, fontSmall_, ImVec2(pos.x + sz.x * 0.5f + 7 * k, pos.y + (sz.y - fontSmall_->FontSize) * 0.5f),
                     on ? kText : kDim, c.text, sz.x - 22 * k);
        ImGui::PopID();
    }

    void valueBox(ImDrawList* dl, const ControlDef& c, ImVec2 pos, float k) {
        const float h = 24 * k, bw = 22 * k, w = std::max(110.f, (float)c.w * k);
        ImGui::PushID(c.var.c_str());
        const int v = (int)std::lround(param(c.param));
        dl->AddRectFilled(pos, ImVec2(pos.x + w, pos.y + h), kPanel2, 4 * k);
        char buf[64];
        std::snprintf(buf, sizeof(buf), "%s  %d", c.text.c_str(), v);
        textCentered(dl, fontSmall_, ImVec2(pos.x + w * 0.5f, pos.y + (h - fontSmall_->FontSize) * 0.5f), kText, buf, w - 2 * bw);
        ImGui::SetCursorScreenPos(pos);
        if (ImGui::Button("-", ImVec2(bw, h)) && v > c.lo) setParam(c.param, (float)(v - 1));
        if (ImGui::IsItemHovered()) help_ = c.help;
        ImGui::SetCursorScreenPos(ImVec2(pos.x + w - bw, pos.y));
        if (ImGui::Button("+", ImVec2(bw, h)) && v < c.hi) setParam(c.param, (float)(v + 1));
        if (ImGui::IsItemHovered()) help_ = c.help;
        ImGui::PopID();
    }

    // ------------------------------------------------------------------ sections
    void drawHeader(ImDrawList* dl, const InstrumentDef& inst, ImVec2 p, ImVec2 sz) {
        const Catalog& cat = Catalog::get();
        dl->AddRectFilled(p, ImVec2(p.x + sz.x, p.y + sz.y), kPanel);
        dl->AddLine(ImVec2(p.x, p.y + sz.y - 1), ImVec2(p.x + sz.x, p.y + sz.y - 1), kGoldDark, 1.f);
        // logo
        const float lx = 14 * s_;
        dl->AddRectFilled(ImVec2(lx, 14 * s_), ImVec2(lx + 4 * s_, sz.y - 14 * s_), kGold);
        text(dl, fontLogo_, ImVec2(lx + 12 * s_, 13 * s_), kGold, "NEW MOVIE");
        text(dl, fontLogo_, ImVec2(lx + 12 * s_, 31 * s_), kText, "LIBRARY");
        // instrument
        const float ix = 232 * s_;
        text(dl, fontTitle_, ImVec2(ix, 9 * s_), kText, inst.name);
        std::string sub = categoryTitle(inst.category) + "  \xC2\xB7  " + inst.blurb;
        const float subMax = sz.x - ix - 420 * s_;
        while (fontSmall_->CalcTextSizeA(fontSmall_->FontSize, FLT_MAX, 0, sub.c_str()).x > subMax && sub.size() > 8)
            sub = sub.substr(0, sub.size() - 4) + "..";
        text(dl, fontSmall_, ImVec2(ix + 1 * s_, 39 * s_), kDim, sub);

        // presets
        const float px = sz.x - 404 * s_;
        text(dl, fontSmall_, ImVec2(px, 8 * s_), kDim, "PRESET");
        ImGui::SetCursorScreenPos(ImVec2(px, 25 * s_));
        ImGui::PushID("preset");
        if (ImGui::ArrowButton("##prev", ImGuiDir_Left) && !inst.presets.empty())
            applyPreset(inst, presetIndex_ <= 0 ? (int)inst.presets.size() - 1 : presetIndex_ - 1);
        ImGui::SameLine();
        ImGui::SetNextItemWidth(160 * s_);
        const std::string pname = (presetIndex_ >= 0 && presetIndex_ < (int)inst.presets.size())
                                      ? inst.presets[presetIndex_].name : std::string("(edited)");
        if (ImGui::BeginCombo("##presets", pname.c_str(), ImGuiComboFlags_HeightLarge)) {
            for (int i = 0; i < (int)inst.presets.size(); ++i)
                if (ImGui::Selectable(inst.presets[i].name.c_str(), i == presetIndex_)) applyPreset(inst, i);
            ImGui::EndCombo();
        }
        if (ImGui::IsItemHovered()) help_ = "Presets: complete settings snapshots for this instrument. Default resets every control.";
        ImGui::SameLine();
        if (ImGui::ArrowButton("##next", ImGuiDir_Right) && !inst.presets.empty())
            applyPreset(inst, presetIndex_ < 0 ? 0 : (presetIndex_ + 1) % (int)inst.presets.size());
        ImGui::PopID();

        // master volume
        ControlDef vol;
        vol.var = "volume"; vol.text = "Master"; vol.kind = "knob"; vol.lo = -60; vol.hi = 6; vol.def = -6;
        vol.unit = "DB"; vol.ratio = 1; vol.param = 0;
        vol.help = "Master volume of the plugin output.";
        knob(dl, vol, ImVec2(sz.x - 158 * s_, 2 * s_), 0.7f * s_);

        // meters + status
        const float mx = sz.x - 86 * s_, my = 12 * s_, mh = sz.y - 24 * s_;
        const float pl = status_ && status_->engine ? status_->engine->peakL.load() : 0.f;
        const float pr = status_ && status_->engine ? status_->engine->peakR.load() : 0.f;
        auto bar = [&](float x, float pk) {
            dl->AddRectFilled(ImVec2(x, my), ImVec2(x + 5 * s_, my + mh), kPanel2, 2 * s_);
            const float db = 20.f * std::log10(std::max(pk, 1e-5f));
            const float t = std::min(1.f, std::max(0.f, (db + 48.f) / 48.f));
            if (t > 0.02f)
                dl->AddRectFilled(ImVec2(x, my + mh * (1 - t)), ImVec2(x + 5 * s_, my + mh), pk > 0.89f ? kRed : kGold, 2 * s_);
        };
        bar(mx, pl);
        bar(mx + 7 * s_, pr);
        const int voices = status_ && status_->engine ? status_->engine->activeVoices.load() : 0;
        char b[32];
        std::snprintf(b, sizeof(b), "%d", voices);
        text(dl, fontSmall_, ImVec2(mx + 18 * s_, 14 * s_), kText, b);
        text(dl, fontSmall_, ImVec2(mx + 18 * s_, 29 * s_), kDim, "voices");
        (void)cat;
    }

    void drawBrowser(ImVec2 p, ImVec2 sz) {
        const Catalog& cat = Catalog::get();
        ImGui::SetCursorScreenPos(p);
        ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(8 * s_, 8 * s_));
        ImGui::BeginChild("browser", sz, ImGuiChildFlags_AlwaysUseWindowPadding);
        ImGui::SetNextItemWidth(-FLT_MIN);
        ImGui::InputTextWithHint("##search", "Search instruments...", search_, sizeof(search_));
        const std::string q = lower(search_);
        ImGui::Dummy(ImVec2(0, 2 * s_));
        ImGui::BeginChild("list", ImVec2(0, 0), 0, ImGuiWindowFlags_NoBackground);
        const int loading = status_ ? status_->loadingIndex.load() : -1;
        for (auto& catName : cat.categories) {
            std::vector<int> items;
            for (size_t i = 0; i < cat.instruments.size(); ++i) {
                const auto& d = cat.instruments[i];
                if (d.category != catName) continue;
                if (!q.empty() && lower(d.name + " " + d.blurb + " " + d.key).find(q) == std::string::npos) continue;
                items.push_back((int)i);
            }
            if (items.empty()) continue;
            const bool open = !q.empty() || openCategory_ == catName;
            ImGui::PushFont(fontSmall_);
            ImGui::PushStyleColor(ImGuiCol_Text, ImGui::ColorConvertU32ToFloat4(kGold));
            char label[128];
            std::snprintf(label, sizeof(label), "%s %s  (%d)", open ? "-" : "+", categoryTitle(catName).c_str(), (int)items.size());
            if (ImGui::Selectable(label, false, 0, ImVec2(0, 20 * s_))) openCategory_ = open ? std::string() : catName;
            ImGui::PopStyleColor();
            ImGui::PopFont();
            if (!open) continue;
            for (int i : items) {
                const auto& d = cat.instruments[i];
                ImGui::PushID(i);
                const ImVec2 rp = ImGui::GetCursorScreenPos();
                if (ImGui::Selectable("##inst", i == current_, 0, ImVec2(0, 34 * s_)) && i != current_) selectInstrument(i);
                if (ImGui::IsItemHovered()) help_ = d.name + ": " + d.blurb;
                ImDrawList* dl = ImGui::GetWindowDrawList();
                text(dl, fontBody_, ImVec2(rp.x + 8 * s_, rp.y + 2 * s_), i == current_ ? kText : mix(kText, kDim, 0.25f), d.name);
                std::string bl = d.blurb;
                const float maxW = ImGui::GetContentRegionAvail().x - 12 * s_;
                while (fontSmall_->CalcTextSizeA(fontSmall_->FontSize, FLT_MAX, 0, bl.c_str()).x > maxW && bl.size() > 6)
                    bl = bl.substr(0, bl.size() - 4) + "..";
                text(dl, fontSmall_, ImVec2(rp.x + 8 * s_, rp.y + 19 * s_), kDim, bl);
                if (i == current_) dl->AddRectFilled(ImVec2(rp.x, rp.y + 3 * s_), ImVec2(rp.x + 3 * s_, rp.y + 31 * s_), kGold);
                if (i == loading) {
                    const float w = ImGui::GetContentRegionAvail().x;
                    const float t = status_->progress.load();
                    dl->AddRectFilled(ImVec2(rp.x + 8 * s_, rp.y + 32 * s_), ImVec2(rp.x + 8 * s_ + (w - 16 * s_) * t, rp.y + 34 * s_), kGold);
                }
                ImGui::PopID();
            }
            ImGui::Dummy(ImVec2(0, 4 * s_));
        }
        ImGui::EndChild();
        ImGui::EndChild();
        ImGui::PopStyleVar();
    }

    void drawMain(ImDrawList* dl, const InstrumentDef& inst, ImVec2 p, ImVec2 sz) {
        dl->AddRectFilled(p, ImVec2(p.x + sz.x, p.y + sz.y), kPanel, 6 * s_);
        // page tabs (only the pages this instrument uses)
        bool used[3] = {false, false, false};
        for (auto& c : inst.controls) if (c.page >= 0 && c.page < 3) used[c.page] = true;
        if (!used[page_]) page_ = 0;
        float tx = p.x + 12 * s_;
        const float ty = p.y + 10 * s_, th = 26 * s_;
        for (int pg = 0; pg < 3; ++pg) {
            if (!used[pg]) continue;
            const float tw = 92 * s_;
            ImGui::SetCursorScreenPos(ImVec2(tx, ty));
            ImGui::PushID(pg);
            if (ImGui::InvisibleButton("##tab", ImVec2(tw, th))) page_ = pg;
            const bool hov = ImGui::IsItemHovered();
            ImGui::PopID();
            const bool sel = page_ == pg;
            dl->AddRectFilled(ImVec2(tx, ty), ImVec2(tx + tw, ty + th), sel ? kPanel2 : (hov ? mix(kPanel, kPanel2, 0.5f) : kPanel), 4 * s_);
            if (sel) dl->AddRectFilled(ImVec2(tx + 10 * s_, ty + th - 3 * s_), ImVec2(tx + tw - 10 * s_, ty + th - 1 * s_), kGold, 1.f);
            textCentered(dl, fontBody_, ImVec2(tx + tw * 0.5f, ty + 5 * s_), sel ? kText : kDim, kPageNames[pg]);
            tx += tw + 6 * s_;
        }
        // status on the right of the tabs
        drawLoadStatus(dl, ImVec2(p.x + sz.x - 12 * s_, ty + 5 * s_));
        dl->AddLine(ImVec2(p.x + 10 * s_, ty + th + 6 * s_), ImVec2(p.x + sz.x - 10 * s_, ty + th + 6 * s_), kLine);

        // control area: Kontakt panel coordinates (about 800 x 260 px), scaled to fit
        const float helpH = 44 * s_;
        const ImVec2 ap(p.x + 12 * s_, ty + th + 12 * s_);
        const ImVec2 as(sz.x - 24 * s_, p.y + sz.y - helpH - ap.y);
        const float k = std::min(as.x / 805.f, as.y / 258.f);
        const float ox = ap.x + std::max(0.f, (as.x - 805.f * k) * 0.5f);
        const float oy = ap.y - 30.f * k;
        for (auto& c : inst.controls) {
            if (c.page != page_) continue;
            const ImVec2 cp(ox + c.x * k, oy + c.y * k);
            if (c.kind == "knob") knob(dl, c, cp, k);
            else if (c.kind == "menu") menu(dl, c, cp, k);
            else if (c.kind == "switch") toggle(dl, c, cp, k);
            else if (c.kind == "value") valueBox(dl, c, cp, k);
        }

        // help / info line
        const ImVec2 hp(p.x + 10 * s_, p.y + sz.y - helpH);
        dl->AddRectFilled(hp, ImVec2(p.x + sz.x - 10 * s_, p.y + sz.y - 8 * s_), kBg, 4 * s_);
        std::string msg = help_.empty() ? inst.info : help_;
        ImU32 col = help_.empty() ? kDim : kText;
        if (status_ && status_->loadedIndex.load() == current_ && status_->missing.load() > 0 && help_.empty()) {
            msg = std::to_string(status_->missing.load()) + " sample(s) missing - " + status_->errorText();
            col = kWarn;
        }
        ImGui::PushClipRect(hp, ImVec2(p.x + sz.x - 14 * s_, p.y + sz.y - 8 * s_), true);
        dl->AddText(fontSmall_, fontSmall_->FontSize, ImVec2(hp.x + 8 * s_, hp.y + 4 * s_), col, msg.c_str(), nullptr,
                    sz.x - 40 * s_);
        ImGui::PopClipRect();
    }

    void drawLoadStatus(ImDrawList* dl, ImVec2 rightTop) {
        if (!status_) return;
        const int loading = status_->loadingIndex.load();
        std::string s;
        ImU32 col = kDim;
        if (loading >= 0) {
            char b[96];
            std::snprintf(b, sizeof(b), "Loading %s  %d%%", Catalog::get().instruments[loading].name.c_str(),
                          (int)(status_->progress.load() * 100));
            s = b;
            col = kGold;
        } else if (status_->loadedIndex.load() >= 0) {
            s = "Ready";
        }
        const ImVec2 tsz = fontSmall_->CalcTextSizeA(fontSmall_->FontSize, FLT_MAX, 0, s.c_str());
        text(dl, fontSmall_, ImVec2(rightTop.x - tsz.x, rightTop.y + 2 * s_), col, s);
    }

    void drawLibrarySetup(ImDrawList* dl, ImVec2 p, ImVec2 sz) {
        dl->AddRectFilled(p, ImVec2(p.x + sz.x, p.y + sz.y), kPanel, 6 * s_);
        const float x = p.x + 28 * s_;
        float y = p.y + 24 * s_;
        text(dl, fontTitle_, ImVec2(x, y), kGold, "Find the sample library");
        y += 40 * s_;
        const char* lines[] = {
            "The plugin plays the samples in the \"New Movie Library\" folder (the one with the Samples folder).",
            "Easiest: copy that folder into your Documents folder, then press Search Again.",
            "Or browse to it: pick any file inside the library folder (for example README.md or a .wav).",
        };
        for (auto* l : lines) { text(dl, fontBody_, ImVec2(x, y), kText, l); y += 22 * s_; }
        y += 14 * s_;
        ImGui::SetCursorScreenPos(ImVec2(x, y));
        ImGui::SetNextItemWidth(sz.x - 210 * s_);
        ImGui::InputTextWithHint("##libpath", "C:\\Users\\you\\Documents\\New Movie Library", pathBuf_, sizeof(pathBuf_));
        ImGui::SameLine();
        if (ImGui::Button("Use This Folder", ImVec2(130 * s_, 0))) {
            const std::string lib = paths::libraryFromAnyPath(pathBuf_);
            browseError_ = lib.empty();
            if (!lib.empty()) setState("library", lib.c_str());
        }
        y += 38 * s_;
        ImGui::SetCursorScreenPos(ImVec2(x, y));
#if DISTRHO_UI_FILE_BROWSER
        if (ImGui::Button("Browse...", ImVec2(130 * s_, 30 * s_))) {
            FileBrowserOptions opts;
            opts.title = "Pick any file inside the New Movie Library folder";
            openFileBrowser(opts);
        }
        ImGui::SameLine();
#endif
        if (ImGui::Button("Search Again", ImVec2(130 * s_, 30 * s_))) setState("library", "");
        y += 46 * s_;
        if (browseError_) {
            text(dl, fontBody_, ImVec2(x, y), kWarn, "That location is not inside a New Movie Library folder (no Samples folder found).");
            y += 24 * s_;
        }
        text(dl, fontSmall_, ImVec2(x, y), kDim,
             "Searched: the saved location, NML_LIBRARY_PATH, next to the plugin, Documents, Desktop, Downloads and C:\\ D:\\ E:\\");
    }

    // ------------------------------------------------------------------ keyboard
    void drawKeyboard(ImDrawList* dl, const InstrumentDef& inst, ImVec2 p, ImVec2 sz) {
        const int whites = 52;
        const float ww = sz.x / whites, wh = sz.y - 2 * s_, bw = ww * 0.62f, bh = wh * 0.62f;
        std::vector<float> keyX(128, 0.f);
        int wi = 0;
        for (int n = kKeyLo; n <= kKeyHi; ++n) {
            if (!isBlack(n)) keyX[n] = p.x + ww * wi++;
            else keyX[n] = p.x + ww * wi - bw * 0.5f;
        }
        // key roles
        std::vector<ImU32> role(128, 0);
        std::vector<std::string> names(128);
        int activeKs = -1;
        if (inst.engine == EngineType::Drums) {
            for (auto& pc : inst.pieces) if (pc.key >= 0 && pc.key < 128) { role[pc.key] = kBusColors[pc.bus % 8]; names[pc.key] = pc.name; }
        } else {
            for (int n = inst.rangeLo; n <= inst.rangeHi && n < 128; ++n) role[n] = IM_COL32(110, 160, 230, 255);
            if (inst.engine == EngineType::Artic) {
                const int art = (int)std::lround(param(Catalog::get().param("art_menu")));
                for (size_t a = 0; a < inst.arts.size(); ++a) {
                    const int ks = inst.arts[a].ks;
                    if (ks < 0 || ks > 127) continue;
                    role[ks] = (int)a == art ? kGold : kRed;
                    names[ks] = inst.arts[a].name;
                    if ((int)a == art) activeKs = ks;
                }
            }
        }
        (void)activeKs;
        const Engine* eng = status_ ? status_->engine : nullptr;
        auto down = [&](int n) { return n == mouseNote_ || (eng && eng->keyDown[n].load()); };

        // mouse
        ImGui::SetCursorScreenPos(p);
        ImGui::InvisibleButton("##keys", sz);
        const bool hov = ImGui::IsItemHovered(), act = ImGui::IsItemActive();
        int hit = -1;
        const ImVec2 m = ImGui::GetIO().MousePos;
        if (hov || act) {
            for (int n = kKeyLo; n <= kKeyHi && hit < 0; ++n)
                if (isBlack(n) && m.x >= keyX[n] && m.x < keyX[n] + bw && m.y >= p.y && m.y < p.y + bh) hit = n;
            for (int n = kKeyLo; n <= kKeyHi && hit < 0; ++n)
                if (!isBlack(n) && m.x >= keyX[n] && m.x < keyX[n] + ww && m.y >= p.y && m.y < p.y + wh) hit = n;
        }
        if (act && hit >= 0 && hit != mouseNote_) {
            if (mouseNote_ >= 0) sendNote(0, (uint8_t)mouseNote_, 0);
            const float yrel = (m.y - p.y) / (isBlack(hit) ? bh : wh);
            const int vel = std::min(127, std::max(20, (int)(40 + 87 * yrel)));
            sendNote(0, (uint8_t)hit, (uint8_t)vel);
            mouseNote_ = hit;
        }
        if (!act && mouseNote_ >= 0) { sendNote(0, (uint8_t)mouseNote_, 0); mouseNote_ = -1; }
        if (hov && hit >= 0) {
            help_ = noteName(hit) + (names[hit].empty() ? std::string() : "  -  " + names[hit]);
            if (inst.engine == EngineType::Artic)
                for (auto& a : inst.arts) if (a.ks == hit) help_ += "  (keyswitch)";
        }

        dl->AddRectFilled(p, ImVec2(p.x + sz.x, p.y + sz.y), IM_COL32(8, 8, 10, 255), 3 * s_);
        for (int n = kKeyLo; n <= kKeyHi; ++n) {
            if (isBlack(n)) continue;
            const ImVec2 a(keyX[n] + 0.5f, p.y), b(keyX[n] + ww - 0.5f, p.y + wh);
            ImU32 col = role[n] ? mix(IM_COL32(236, 236, 232, 255), role[n], 0.30f) : IM_COL32(150, 150, 150, 255);
            if (down(n)) col = kGold;
            dl->AddRectFilled(a, b, col, 2 * s_, ImDrawFlags_RoundCornersBottom);
            if (role[n] && !down(n) && inst.engine != EngineType::Synth && inst.engine != EngineType::Keys)
                dl->AddRectFilled(ImVec2(a.x + 1, b.y - 6 * s_), ImVec2(b.x - 1, b.y - 1), role[n], 2 * s_);
            if (n % 12 == 0)
                textCentered(dl, fontSmall_, ImVec2((a.x + b.x) * 0.5f, b.y - fontSmall_->FontSize - 8 * s_), IM_COL32(70, 70, 76, 255), noteName(n));
        }
        for (int n = kKeyLo; n <= kKeyHi; ++n) {
            if (!isBlack(n)) continue;
            const ImVec2 a(keyX[n], p.y), b(keyX[n] + bw, p.y + bh);
            ImU32 col = role[n] ? mix(IM_COL32(34, 34, 38, 255), role[n], 0.45f) : IM_COL32(24, 24, 26, 255);
            if (down(n)) col = kGold;
            dl->AddRectFilled(a, b, col, 2 * s_, ImDrawFlags_RoundCornersBottom);
        }
    }

    // ------------------------------------------------------------------ state
    float s_ = 1.f;
    SharedStatus* status_ = nullptr;
    std::vector<float> params_;
    int current_ = 0;
    int page_ = 0;
    int presetIndex_ = 0;
    int lastArt_ = -1;
    int mouseNote_ = -1;
    bool dragging_ = false;
    float dragValue_ = 0.f;
    bool browseError_ = false;
    std::string help_;
    std::string openCategory_;
    char search_[64] = {0};
    char pathBuf_[1024] = {0};
    ImFont* fontBody_ = nullptr;
    ImFont* fontSmall_ = nullptr;
    ImFont* fontTitle_ = nullptr;
    ImFont* fontLogo_ = nullptr;

    DISTRHO_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(NMLUI)
};

UI* createUI() { return new NMLUI(); }

END_NAMESPACE_DISTRHO
