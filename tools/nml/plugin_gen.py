"""Exports the catalog for the VST3/CLAP player plugin.

Writes plugin/src/generated/catalog_data.cpp: one JSON document (embedded as a
C++ string) describing every instrument - zones and loops, engine settings,
the controls (shared with the Kontakt scripts, same names, ranges and units)
and the presets - plus the global host-parameter list.
"""
import json
import os

from . import ksp_gen
from .library import CATEGORIES

ART_TYPES = {"sus": 0, "short": 1, "swell": 2}
# friendly host-automation names for controls whose on-screen label depends on the instrument
HOST_NAMES = {f"bus{i}": f"Bus {i + 1} Level" for i in range(8)}
HOST_NAMES.update(dyn_knob="Dynamics", layer_a="Layer A", layer_b="Layer B", patch="Instrument", patch2="Layer",
                  mix2="Layer Level", art_menu="Articulation", release="Release", oct_lvl="Octave Level",
                  ep_drive="Preamp Drive")


def _menu_label(c, labels):
    """The caption of a drop-down menu is a separate label placed just above it."""
    best = None
    for (_, page, x, y, text, _w) in labels:
        if page == c.page and abs(x - c.x) <= 2 and 0 < c.y - y <= 30:
            if best is None or y > best[0]:
                best = (y, text)
    return best[1] if best else ""


def _ctl_json(c, labels=()):
    text = c.text or (_menu_label(c, labels) if c.kind == "menu" else "")
    d = {"var": c.var, "kind": c.kind, "page": c.page, "text": text, "lo": c.lo, "hi": c.hi, "def": c.default,
         "ratio": c.ratio, "unit": c.unit or "", "help": c.help, "x": c.x, "y": c.y,
         "w": c.width or {"menu": 120, "switch": 88, "value": 96}.get(c.kind, 90)}
    if c.kind == "menu":
        d["items"] = list(c.items)
        d["lo"], d["hi"] = 0, len(c.items) - 1
    if c.kind == "switch":
        d["lo"], d["hi"] = 0, 1
    return d


LEVELS_FILE = os.path.join(os.path.dirname(__file__), "plugin_levels.json")


def _levels():
    """Per-instrument output trims (dB) measured by tools/measure_plugin_levels.py."""
    if not os.path.exists(LEVELS_FILE):
        return {}
    with open(LEVELS_FILE) as f:
        return json.load(f)


def export(catalog, out_dir):
    levels = _levels()
    instruments = []
    params = {}
    order = []
    for inst in catalog:
        s = ksp_gen.build_script(inst)
        groups = inst.groups
        gi = {g: i for i, g in enumerate(groups)}
        cfg = inst.cfg
        ctls = [c for c in s.ctls if c.var not in ("preset", "tab_play", "tab_sound", "tab_perf")]
        e = {
            "key": inst.key, "name": inst.name, "category": inst.category, "engine": inst.engine,
            "blurb": inst.blurb, "info": cfg.get("info", inst.name), "channels": inst.channels,
            "groups": groups,
            "zones": [[gi[z.group], z.root, z.lo, z.hi, z.vlo, z.vhi, z.file,
                       z.loop[0] if z.loop else -1, z.loop[1] if z.loop else -1] for z in inst.zones],
            "fx": cfg.get("fx", []),
            "ladder": "LDR" in cfg.get("filter_type", ""),
            "gain": levels.get(inst.key, 0.0),
            "range": list(cfg.get("range", (0, 127))),
            "controls": [_ctl_json(c, s.labels) for c in ctls],
            "presets": [{"name": n, "values": v} for n, v in ksp_gen.preset_snapshots(s)],
        }
        if inst.engine == "synth":
            e["layers"] = [gi[g] for g in cfg.get("layers", groups)]
        elif inst.engine == "artic":
            e["arts"] = [{"name": a["name"], "type": ART_TYPES[a["type"]], "groups": [gi[g] for g in a["groups"]],
                          "ks": a["ks"]} for a in cfg["arts"]]
            e["hall"] = {str(gi[c]): gi[h] for c, h in cfg.get("mics", {}).items()}
            e["leg_offset_ms"] = cfg.get("leg_offset_us", 60000) / 1000
        elif inst.engine == "keys":
            e["patches"] = [{"name": p["name"], "layers": [[gi[g] for g in layer] for layer in p["layers"]],
                             "splits": p.get("splits", []), "loop": bool(p.get("loop", False))} for p in cfg["patches"]]
        else:
            buses = cfg["buses"]
            e["buses"] = buses
            e["pieces"] = [{"key": p["key"], "name": p["name"], "bus": buses.index(p["bus"]), "pan": p.get("pan", 0.0),
                            "cg": p.get("cg", 0), "cut": p.get("cut", 0), "hold": bool(p.get("hold", False)),
                            "layers": [[gi[g] for g in layer] for layer in p["layers"]],
                            "splits": p.get("splits", [127])} for p in cfg["pieces"]]
        instruments.append(e)
        for c in ctls:
            cj = _ctl_json(c, s.labels)
            if c.var not in params:
                params[c.var] = {"var": c.var, "name": HOST_NAMES.get(c.var, cj["text"] or c.var), "lo": cj["lo"],
                                 "hi": cj["hi"], "def": cj["def"], "kind": c.kind}
                order.append(c.var)
            else:
                p = params[c.var]
                p["lo"] = min(p["lo"], cj["lo"])
                p["hi"] = max(p["hi"], cj["hi"])
    doc = {"categories": CATEGORIES, "params": [params[v] for v in order], "instruments": instruments}
    text = json.dumps(doc, separators=(",", ":"))
    os.makedirs(out_dir, exist_ok=True)
    chunks = [text[i:i + 12000] for i in range(0, len(text), 12000)]
    with open(os.path.join(out_dir, "catalog_data.cpp"), "w", newline="\n") as f:
        f.write("// Generated by tools/nml/plugin_gen.py - do not edit.\n")
        f.write('#include "../engine/Catalog.hpp"\n\nnamespace nml {\n\nconst char* const kCatalogJson =\n')
        for ch in chunks:
            f.write('R"NMLJSON(' + ch + ')NMLJSON"\n')
        f.write(";\n\n}  // namespace nml\n")
    return len(instruments), len(order), len(text)
