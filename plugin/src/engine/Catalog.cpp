#include "Catalog.hpp"
#include "Json.hpp"

namespace nml {

static std::vector<std::vector<int>> intLists(const Json& j) {
    std::vector<std::vector<int>> out;
    for (auto& l : j.arr) {
        std::vector<int> v;
        for (auto& x : l.arr) v.push_back(x.i());
        out.push_back(std::move(v));
    }
    return out;
}

static std::vector<int> ints(const Json& j) {
    std::vector<int> v;
    for (auto& x : j.arr) v.push_back(x.i());
    return v;
}

static Fx fxFromName(const std::string& n) {
    if (n == "filter") return Fx::Filter;
    if (n == "eppre") return Fx::EpPre;
    if (n == "rotator") return Fx::Rotator;
    if (n == "supergt") return Fx::SuperGt;
    if (n == "comp") return Fx::Comp;
    if (n == "stereo") return Fx::Stereo;
    if (n == "choral") return Fx::Choral;
    if (n == "replika") return Fx::Replika;
    return Fx::Raum;
}

const Catalog& Catalog::get() {
    static const Catalog instance;
    return instance;
}

Catalog::Catalog() {
    const Json doc = Json::parse(kCatalogJson);
    for (auto& c : doc["categories"].arr) categories.push_back(c.s());

    params.push_back(ParamDef{"volume", "Master Volume", -60.f, 6.f, -6.f});
    for (auto& p : doc["params"].arr) {
        ParamDef d{p["var"].s(), p["name"].s(), (float)p["lo"].d(), (float)p["hi"].d(), (float)p["def"].d(),
                   p["kind"].s()};
        params.push_back(d);
    }
    for (size_t i = 0; i < params.size(); ++i) paramIndex[params[i].var] = (int)i;

    for (auto& ji : doc["instruments"].arr) {
        InstrumentDef d;
        d.key = ji["key"].s();
        d.name = ji["name"].s();
        d.category = ji["category"].s();
        d.blurb = ji["blurb"].s();
        d.info = ji["info"].s();
        const std::string& e = ji["engine"].s();
        d.engine = e == "synth" ? EngineType::Synth : e == "artic" ? EngineType::Artic
                 : e == "keys" ? EngineType::Keys : EngineType::Drums;
        d.channels = ji["channels"].i(2);
        for (auto& g : ji["groups"].arr) d.groups.push_back(g.s());
        for (auto& z : ji["zones"].arr) {
            ZoneDef zd;
            zd.group = z[0].i(); zd.root = z[1].i(); zd.lo = z[2].i(); zd.hi = z[3].i();
            zd.vlo = z[4].i(); zd.vhi = z[5].i(); zd.file = z[6].s();
            zd.loopStart = z[7].i(-1); zd.loopEnd = z[8].i(-1);
            d.zones.push_back(zd);
        }
        for (auto& f : ji["fx"].arr) d.fx.push_back(fxFromName(f.s()));
        d.ladder = ji["ladder"].b;
        d.rangeLo = ji["range"][0].i();
        d.rangeHi = ji["range"][1].i();
        for (auto& c : ji["controls"].arr) {
            ControlDef cd;
            cd.var = c["var"].s(); cd.kind = c["kind"].s(); cd.text = c["text"].s();
            cd.unit = c["unit"].s(); cd.help = c["help"].s();
            cd.page = c["page"].i(); cd.lo = c["lo"].i(); cd.hi = c["hi"].i(); cd.def = c["def"].i();
            cd.ratio = c["ratio"].i(1);
            cd.x = c["x"].i(); cd.y = c["y"].i(); cd.w = c["w"].i(90);
            for (auto& it : c["items"].arr) cd.items.push_back(it.s());
            cd.param = param(cd.var);
            d.controls.push_back(cd);
        }
        for (auto& p : ji["presets"].arr) {
            PresetDef pd;
            pd.name = p["name"].s();
            for (auto& kv : p["values"].obj) {
                const int idx = param(kv.first);
                if (idx >= 0) pd.values.emplace_back(idx, kv.second.i());
            }
            d.presets.push_back(pd);
        }
        if (ji.has("layers")) d.layers = ints(ji["layers"]);
        if (ji.has("arts")) {
            for (auto& a : ji["arts"].arr)
                d.arts.push_back(ArtDef{a["name"].s(), a["type"].i(), ints(a["groups"]), a["ks"].i(-1)});
            d.hallOf.assign(d.groups.size(), -1);
            for (auto& kv : ji["hall"].obj) d.hallOf[std::atoi(kv.first.c_str())] = kv.second.i();
            d.legOffsetMs = (float)ji["leg_offset_ms"].d(60);
        }
        if (ji.has("patches"))
            for (auto& p : ji["patches"].arr)
                d.patches.push_back(PatchDef{p["name"].s(), intLists(p["layers"]), ints(p["splits"]), p["loop"].b});
        if (ji.has("pieces")) {
            for (auto& b : ji["buses"].arr) d.buses.push_back(b.s());
            for (auto& p : ji["pieces"].arr) {
                PieceDef pd;
                pd.key = p["key"].i(); pd.name = p["name"].s(); pd.bus = p["bus"].i(); pd.pan = (float)p["pan"].d();
                pd.cg = p["cg"].i(); pd.cut = p["cut"].i(); pd.hold = p["hold"].b;
                pd.layers = intLists(p["layers"]); pd.splits = ints(p["splits"]);
                d.pieces.push_back(pd);
            }
        }
        instruments.push_back(std::move(d));
    }
}

}  // namespace nml
