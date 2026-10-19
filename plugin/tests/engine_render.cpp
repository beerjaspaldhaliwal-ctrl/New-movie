// Offline test for the playback engine: loads instruments from the library,
// plays a short phrase through the engine and reports levels (optionally writes WAVs).
//   engine_render <library dir> [instrument key|all] [out dir]
#include <cmath>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#include "engine/Engine.hpp"

using namespace nml;

static void writeWav(const std::string& path, const std::vector<float>& l, const std::vector<float>& r, int sr) {
    FILE* f = std::fopen(path.c_str(), "wb");
    if (!f) return;
    const uint32_t n = (uint32_t)l.size(), data = n * 4, riff = 36 + data;
    auto u32 = [&](uint32_t v) { std::fwrite(&v, 4, 1, f); };
    auto u16 = [&](uint16_t v) { std::fwrite(&v, 2, 1, f); };
    std::fwrite("RIFF", 1, 4, f); u32(riff); std::fwrite("WAVEfmt ", 1, 8, f);
    u32(16); u16(1); u16(2); u32(sr); u32(sr * 4); u16(4); u16(16);
    std::fwrite("data", 1, 4, f); u32(data);
    for (uint32_t i = 0; i < n; ++i) {
        const int16_t a = (int16_t)std::lround(std::max(-1.f, std::min(1.f, l[i])) * 32767.f);
        const int16_t b = (int16_t)std::lround(std::max(-1.f, std::min(1.f, r[i])) * 32767.f);
        std::fwrite(&a, 2, 1, f); std::fwrite(&b, 2, 1, f);
    }
    std::fclose(f);
}

struct Note { double t; int note, vel; double len; };

static std::vector<Note> phraseFor(const InstrumentDef& d) {
    std::vector<Note> ph;
    if (d.engine == EngineType::Drums) {
        double t = 0;
        for (size_t i = 0; i < d.pieces.size() && i < 12; ++i, t += 0.35) ph.push_back({t, d.pieces[i].key, 110, 0.3});
        return ph;
    }
    const int mid = std::max(d.rangeLo, std::min(d.rangeHi - 7, (d.rangeLo + d.rangeHi) / 2 - 3));
    ph.push_back({0.0, mid, 90, 1.6});
    ph.push_back({0.0, mid + 4, 80, 1.6});
    ph.push_back({0.0, mid + 7, 80, 1.6});
    ph.push_back({2.2, mid + 2, 120, 0.4});
    ph.push_back({2.7, mid + 5, 60, 0.4});
    return ph;
}

int main(int argc, char** argv) {
    if (argc < 2) { std::fprintf(stderr, "usage: engine_render <library> [key|all] [outdir]\n"); return 2; }
    const std::string lib = argv[1];
    const std::string which = argc > 2 ? argv[2] : "all";
    const std::string outDir = argc > 3 ? argv[3] : "";
    const Catalog& cat = Catalog::get();
    const int sr = 48000, block = 256;
    int failures = 0;
    for (size_t ii = 0; ii < cat.instruments.size(); ++ii) {
        const InstrumentDef& d = cat.instruments[ii];
        if (which != "all" && which != d.key) continue;
        std::atomic<float> prog{0};
        LoadedInstrument* li = loadInstrument((int)ii, lib, prog);
        std::vector<float> params(cat.params.size());
        for (size_t p = 0; p < params.size(); ++p) params[p] = cat.params[p].def;
        for (auto& c : d.controls) if (c.param >= 0) params[c.param] = (float)c.def;
        const bool measure = std::getenv("NML_MEASURE") != nullptr;
        if (measure) params[0] = 0.f;  // master volume at unity
        const char* arp = std::getenv("NML_TEST_ARP");
        if (arp && cat.param("arp_mode") >= 0 && d.control("arp_mode")) params[cat.param("arp_mode")] = (float)std::atoi(arp);
        Engine eng;
        eng.setSampleRate(sr);
        eng.setParamPointer(params.data());
        eng.setInstrument(li);
        const std::vector<Note> ph = phraseFor(d);
        const double total = 5.0;
        const int frames = (int)(total * sr);
        std::vector<float> L(frames), R(frames);
        struct Ev { int frame; uint8_t d[3]; };
        std::vector<Ev> evs;
        for (auto& n : ph) {
            evs.push_back({(int)(n.t * sr), {0x90, (uint8_t)n.note, (uint8_t)n.vel}});
            evs.push_back({(int)((n.t + n.len) * sr), {0x80, (uint8_t)n.note, 0}});
        }
        std::sort(evs.begin(), evs.end(), [](const Ev& a, const Ev& b) { return a.frame < b.frame; });
        size_t e = 0;
        TimeInfo ti;
        ti.playing = true; ti.bbtValid = true; ti.bpm = 120;
        int maxVoices = 0;
        for (int pos = 0; pos < frames; pos += block) {
            const int n = std::min(block, frames - pos);
            std::vector<MidiMsg> mm;
            while (e < evs.size() && evs[e].frame < pos + n) {
                MidiMsg m; m.frame = (uint32_t)std::max(0, evs[e].frame - pos);
                std::memcpy(m.data, evs[e].d, 3);
                mm.push_back(m); ++e;
            }
            ti.ppq = (double)pos / sr * ti.bpm / 60.0;
            eng.process(&L[pos], &R[pos], (uint32_t)n, mm.data(), (uint32_t)mm.size(), ti);
            maxVoices = std::max(maxVoices, eng.activeVoices.load());
        }
        double sum = 0, peak = 0;
        bool nan = false;
        for (int i = 0; i < frames; ++i) {
            if (!std::isfinite(L[i]) || !std::isfinite(R[i])) nan = true;
            peak = std::max(peak, (double)std::max(std::fabs(L[i]), std::fabs(R[i])));
            sum += L[i] * L[i] + R[i] * R[i];
        }
        const double rmsDb = 10 * std::log10(sum / (2.0 * frames) + 1e-12);
        const double peakDb = 20 * std::log10(peak + 1e-12);
        const bool bad = nan || peakDb < -40 || li->missing > 0;
        if (bad) ++failures;
        if (measure)  // levels without the catalog trim, for tools/measure_plugin_levels.py
            std::printf("LEVEL %s %.2f %.2f\n", d.key.c_str(), peakDb - d.gainDb, rmsDb - d.gainDb);
        else
            std::printf("%-15s %-6s zones %4zu missing %d  peak %6.1f dB  rms %6.1f dB  voices %3d %s\n", d.key.c_str(),
                    d.engine == EngineType::Synth ? "synth" : d.engine == EngineType::Artic ? "artic"
                    : d.engine == EngineType::Keys ? "keys" : "drums",
                    d.zones.size(), li->missing, peakDb, rmsDb, maxVoices, bad ? "  <-- PROBLEM" : "");
        if (!outDir.empty()) writeWav(outDir + "/" + d.key + ".wav", L, R, sr);
        eng.setInstrument(nullptr);
        delete li;
    }
    std::printf("%d problem(s)\n", failures);
    return failures ? 1 : 0;
}
