// The instrument catalog (generated from tools/nml, embedded as JSON).
#pragma once

#include <map>
#include <string>
#include <vector>

namespace nml {

extern const char* const kCatalogJson;

enum class EngineType { Synth, Artic, Keys, Drums };
enum class Fx { Filter, EpPre, Rotator, SuperGt, Comp, Stereo, Choral, Replika, Raum };
enum Page { kPagePlay = 0, kPageSound = 1, kPagePerform = 2, kPageAlways = -1 };

struct ZoneDef {
    int group = 0, root = 60, lo = 0, hi = 127, vlo = 1, vhi = 127;
    std::string file;
    int loopStart = -1, loopEnd = -1;
};

struct ControlDef {
    std::string var, kind, text, unit, help;
    int page = 0, lo = 0, hi = 1000, def = 0, ratio = 1;
    int x = 0, y = 0, w = 90;  // position on the Kontakt panel (pixels)
    std::vector<std::string> items;
    int param = -1;  // global host parameter index
};

struct ArtDef { std::string name; int type = 0; std::vector<int> groups; int ks = -1; };
struct PatchDef { std::string name; std::vector<std::vector<int>> layers; std::vector<int> splits; bool loop = false; };
struct PieceDef {
    int key = 36; std::string name; int bus = 0; float pan = 0; int cg = 0, cut = 0; bool hold = false;
    std::vector<std::vector<int>> layers; std::vector<int> splits;
};
struct PresetDef { std::string name; std::vector<std::pair<int, int>> values; };  // (param index, value)

struct InstrumentDef {
    std::string key, name, category, blurb, info;
    EngineType engine = EngineType::Synth;
    int channels = 2;
    std::vector<std::string> groups;
    std::vector<ZoneDef> zones;
    std::vector<Fx> fx;
    bool ladder = false;
    float gainDb = 0;                  // output trim that evens out loudness between instruments
    int rangeLo = 0, rangeHi = 127;
    std::vector<ControlDef> controls;
    std::vector<PresetDef> presets;
    // engine specific
    std::vector<int> layers;           // synth
    std::vector<ArtDef> arts;          // artic
    std::vector<int> hallOf;           // artic: group -> hall twin group (-1)
    float legOffsetMs = 60;
    std::vector<PatchDef> patches;     // keys
    std::vector<std::string> buses;    // drums
    std::vector<PieceDef> pieces;      // drums

    const ControlDef* control(const std::string& var) const {
        for (auto& c : controls) if (c.var == var) return &c;
        return nullptr;
    }
    bool hasFx(Fx f) const {
        for (auto x : fx) if (x == f) return true;
        return false;
    }
};

struct ParamDef { std::string var, name; float lo = 0, hi = 1, def = 0; std::string kind = "knob"; };

class Catalog {
public:
    static const Catalog& get();
    std::vector<std::string> categories;
    std::vector<ParamDef> params;        // index 0 = master volume (plugin only)
    std::vector<InstrumentDef> instruments;
    std::map<std::string, int> paramIndex;

    int param(const std::string& var) const {
        auto it = paramIndex.find(var);
        return it == paramIndex.end() ? -1 : it->second;
    }
    int instrument(const std::string& key) const {
        for (size_t i = 0; i < instruments.size(); ++i) if (instruments[i].key == key) return (int)i;
        return -1;
    }

private:
    Catalog();
};

}  // namespace nml
