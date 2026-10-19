// Functional tests for the playback engine: arpeggiator, Note Repeat, strum, sustain pedal,
// mono glide, legato, keyswitches, all-notes-off and stuck voices.
//   engine_features <library dir>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <functional>
#include <string>
#include <vector>

#include "engine/Engine.hpp"

using namespace nml;

static const int kSr = 48000, kBlock = 256;
static int gFail = 0;

struct Rig {
    const Catalog& cat = Catalog::get();
    LoadedInstrument* li = nullptr;
    std::vector<float> params;
    Engine eng;
    std::vector<float> L = std::vector<float>(kBlock), R = std::vector<float>(kBlock);
    std::vector<MidiMsg> queue;
    TimeInfo ti;
    double pos = 0;

    Rig(const std::string& lib, const std::string& key) {
        std::atomic<float> prog{0};
        const int idx = cat.instrument(key);
        li = loadInstrument(idx, lib, prog);
        params.resize(cat.params.size());
        for (size_t p = 0; p < params.size(); ++p) params[p] = cat.params[p].def;
        for (auto& c : li->def->controls) params[c.param] = (float)c.def;
        eng.setSampleRate(kSr);
        eng.setParamPointer(params.data());
        eng.setInstrument(li);
        ti.playing = true; ti.bbtValid = true; ti.bpm = 120;
    }
    ~Rig() { eng.setInstrument(nullptr); delete li; }
    void set(const char* var, float v) { params[cat.param(var)] = v; }
    void midi(uint8_t a, uint8_t b, uint8_t c) { MidiMsg m; m.frame = 0; m.data[0] = a; m.data[1] = b; m.data[2] = c; queue.push_back(m); }
    void on(int n, int v = 100) { midi(0x90, (uint8_t)n, (uint8_t)v); }
    void off(int n) { midi(0x80, (uint8_t)n, 0); }
    void cc(int n, int v) { midi(0xB0, (uint8_t)n, (uint8_t)v); }
    float run(double secs) {  // returns peak
        float peak = 0;
        const int blocks = (int)(secs * kSr / kBlock);
        for (int b = 0; b < blocks; ++b) {
            ti.ppq = pos / kSr * ti.bpm / 60.0;
            eng.process(L.data(), R.data(), kBlock, queue.data(), (uint32_t)queue.size(), ti);
            queue.clear();
            for (int i = 0; i < kBlock; ++i) peak = std::max(peak, std::max(std::fabs(L[i]), std::fabs(R[i])));
            pos += kBlock;
        }
        return peak;
    }
    uint32_t started() const { return eng.voicesStarted.load(); }
    int active() const { return eng.activeVoices.load(); }
};

static void check(bool ok, const char* name, const std::string& detail) {
    std::printf("%s  %-44s %s\n", ok ? "ok  " : "FAIL", name, detail.c_str());
    if (!ok) ++gFail;
}
static std::string fmt(const char* f, double a, double b = 0) { char s[128]; std::snprintf(s, sizeof(s), f, a, b); return s; }

int main(int argc, char** argv) {
    if (argc < 2) return 2;
    const std::string lib = argv[1];
    {   // arpeggiator: Up, 1/16 at 120 BPM = 8 notes per second
        Rig r(lib, "Pluck");
        r.set("arp_mode", 1); r.set("arp_rate", 3);
        r.on(60); r.on(64); r.on(67);
        r.run(2.0);
        const uint32_t n = r.started();
        check(n >= 15 && n <= 18, "arp Up 1/16, 2 s at 120 BPM", fmt("%.0f notes (expect ~16)", n));
        r.off(60); r.off(64); r.off(67);
        const uint32_t before = r.started();
        r.run(1.0);
        check(r.started() == before, "arp stops after release (no latch)", fmt("%.0f extra notes", r.started() - before));
        r.run(3.0);
        check(r.active() == 0, "arp leaves no voices", fmt("%.0f active", r.active()));
    }
    {   // chord repeat: 3 notes per step
        Rig r(lib, "Pluck");
        r.set("arp_mode", 6); r.set("arp_rate", 1);  // 1/8 = 4 steps per second
        r.on(60); r.on(64); r.on(67);
        r.run(1.0);
        check(r.started() >= 11 && r.started() <= 15, "arp Chord Repeat 1/8, 1 s", fmt("%.0f notes (expect ~12)", r.started()));
    }
    {   // chord memory + strum
        Rig r(lib, "Guitar");
        r.set("chord", 3); r.set("strum", 100);
        r.on(52);
        r.run(0.05);
        const uint32_t early = r.started();
        r.run(0.5);
        check(early == 1 && r.started() == 3, "chord Major + strum 100 ms", fmt("%.0f then %.0f notes (expect 1 then 3)", early, r.started()));
    }
    {   // scale lock: C# snaps to C in C major
        Rig r(lib, "FeltPiano");
        r.set("scale_type", 1); r.set("chord", 3);
        r.on(61);
        r.run(0.2);
        check(r.started() == 3, "scale lock + chord", fmt("%.0f notes", r.started()));
    }
    {   // Note Repeat 1/32 at 120 BPM = 16 hits per second
        Rig r(lib, "TrapKit");
        r.set("repeat", 5);
        r.on(42, 100);
        r.run(1.0);
        check(r.started() >= 15 && r.started() <= 18, "Note Repeat 1/32, 1 s", fmt("%.0f hits (expect ~16)", r.started()));
        r.off(42);
        const uint32_t b = r.started();
        r.run(0.5);
        check(r.started() == b, "Note Repeat stops on release", fmt("%.0f extra hits", r.started() - b));
    }
    {   // sustain pedal holds notes, pedal up releases them
        Rig r(lib, "EPiano");
        r.cc(64, 127); r.on(60); r.run(0.2); r.off(60); r.run(0.5);
        const int held = r.active();
        r.cc(64, 0); r.run(3.0);
        check(held > 0 && r.active() == 0, "sustain pedal hold + release", fmt("%.0f held, %.0f after pedal up", held, r.active()));
    }
    {   // mono glide: overlapping notes reuse the voices
        Rig r(lib, "MonoBass");
        r.set("mono", 1);
        r.on(36); r.run(0.2);
        const uint32_t first = r.started();
        r.on(43); r.run(0.3); r.off(36); r.run(0.2);
        check(r.started() == first, "mono glide reuses voices", fmt("%.0f then %.0f voices started", first, r.started()));
        r.off(43); r.run(3.0);
        check(r.active() == 0, "mono release", fmt("%.0f active", r.active()));
    }
    {   // legato crossfades into new voices and releases cleanly
        Rig r(lib, "SoloViolin");
        r.set("legato", 1);
        r.on(67); r.run(0.4); r.on(69); r.run(0.4); r.off(67); r.run(0.2); r.off(69); r.run(3.0);
        check(r.started() >= 2 && r.active() == 0, "legato transition + release", fmt("%.0f started, %.0f active", r.started(), r.active()));
    }
    {   // keyswitch changes the articulation and makes no sound itself
        Rig r(lib, "Strings");
        r.on(26); r.run(0.1); r.off(26);
        const uint32_t ks = r.started();
        r.on(60); r.run(0.2); r.off(60); r.run(2.0);
        check(ks == 0 && r.eng.currentArt.load() == 2 && r.started() == 1, "keyswitch to Staccato",
              fmt("art %.0f, %.0f voices", r.eng.currentArt.load(), r.started()));
    }
    {   // mic faders: hall off halves the sustain voices
        Rig r(lib, "Strings");
        r.on(60); r.run(0.2);
        const uint32_t both = r.started();
        r.off(60); r.run(1.0);
        r.set("mic_hall", -400);
        r.on(62); r.run(0.2);
        check(both == 4 && r.started() - both == 2, "close + hall mics, hall off", fmt("%.0f then %.0f voices", both, r.started() - both));
    }
    {   // all notes off
        Rig r(lib, "WarmPad");
        r.on(60); r.on(64); r.run(0.5);
        r.cc(123, 0); r.run(0.5);
        check(r.active() == 0, "CC123 all notes off", fmt("%.0f active", r.active()));
    }
    // no stuck voices on any instrument: play, release, wait
    const Catalog& cat = Catalog::get();
    int stuck = 0;
    for (auto& d : cat.instruments) {
        Rig r(lib, d.key);
        std::vector<int> keys;
        if (d.engine == EngineType::Drums) for (auto& p : d.pieces) keys.push_back(p.key);
        else for (int k = std::max(d.rangeLo, 36); k <= std::min(d.rangeHi, 84); k += 7) keys.push_back(k);
        for (int k : keys) r.on(k, 100);
        r.run(1.0);
        for (int k : keys) r.off(k);
        r.run(14.0);
        if (r.active() != 0) { ++stuck; std::printf("      stuck voices: %s %d\n", d.key.c_str(), r.active()); }
    }
    check(stuck == 0, "no stuck voices (45 instruments)", fmt("%.0f instruments with voices left", stuck));
    std::printf("%d failure(s)\n", gFail);
    return gFail ? 1 : 0;
}
