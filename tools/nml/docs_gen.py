"""Generates the Instrument Guide (Markdown) straight from the catalog, so the
documentation always matches the samples and scripts."""
from .library import LIB_NAME, note_name
from . import ksp_gen

ENGINE_TEXT = {
    "synth": "Synth engine - two blendable layers, attack/release, filter with tempo-synced Movement, "
             "octave layering, mono/glide.",
    "artic": "Articulation engine - keyswitches, mod-wheel dynamics crossfade, legato with portamento, "
             "round-robin shorts.",
    "keys": "Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.",
    "drums": "Drum engine - one piece per key, velocity layers, round robins, choke groups, per-bus mixer.",
}


def _range(inst):
    lo, hi = inst.cfg.get("range", (min(z.lo for z in inst.zones), max(z.hi for z in inst.zones)))
    return f"{note_name(lo)} - {note_name(hi)} (MIDI {lo}-{hi})"


def instrument_guide(catalog, sizes):
    out = [f"# {LIB_NAME} - Instrument Guide", "",
           "Generated from `tools/nml/catalog.py`. Note names use Kontakt's convention (C3 = MIDI 60).", ""]
    cats = []
    for inst in catalog:
        if inst.category not in cats:
            cats.append(inst.category)
    for cat in cats:
        out += [f"## {cat}", ""]
        for inst in [i for i in catalog if i.category == cat]:
            out += [f"### {inst.name}", "", inst.blurb, ""]
            out.append(f"- **File:** `Instruments/{cat}/{inst.name}.nki` (build with `Creator Tools/Build {inst.name}.lua`)")
            out.append(f"- **Engine:** {ENGINE_TEXT[inst.engine]}")
            if inst.engine != "drums":
                out.append(f"- **Playable range:** {_range(inst)}")
            src = inst.samples_from or inst.key
            out.append(f"- **Samples:** {len(inst.zones)} zones in {len(inst.groups)} groups "
                       f"({', '.join(inst.groups)}), {'mono' if inst.channels == 1 else 'stereo'}, "
                       f"24-bit / 44.1 kHz, {sizes.get(src, 0) / 1e6:.1f} MB"
                       + (f" (shared with {inst.samples_from})" if inst.samples_from else ""))
            cfg = inst.cfg
            if inst.engine == "artic":
                out.append("- **Articulations / keyswitches:**")
                for a in cfg["arts"]:
                    kind = {"sus": "sustain, CC1 dynamics", "short": "short, round robin, velocity",
                            "swell": "auto-swell, CC1 dynamics"}[a["type"]]
                    out.append(f"  - `{note_name(a['ks'])}` **{a['name']}** - {kind} ({' / '.join(a['groups'])})")
            if inst.engine == "keys":
                pats = cfg["patches"]
                if len(pats) > 1:
                    out.append("- **Instruments (menu + layer):** " + ", ".join(p["name"] for p in pats))
                for p in pats:
                    if len(p["layers"]) > 1:
                        out.append(f"- **{p['name']} velocity layers:** {len(p['layers'])} "
                                   f"(splits at velocity {', '.join(map(str, p.get('splits', [])))}), "
                                   f"{len(p['layers'][0])} round robin(s) each")
            if inst.engine == "drums":
                out.append("- **Key map:**")
                out.append("")
                out.append("  | Key | MIDI | Piece | Bus |")
                out.append("  |---|---|---|---|")
                for p in cfg["pieces"]:
                    extra = " (hold = roll)" if p.get("hold") else ""
                    extra += " (choked by closed/pedal hat)" if p.get("cg") else ""
                    out.append(f"  | {note_name(p['key'])} | {p['key']} | {p['name']}{extra} | {p['bus']} |")
                out.append("")
            fx = cfg.get("fx", [])
            out.append("- **Effects chain (built by the script):** " + " > ".join(
                {"filter": "Filter", "eppre": "EP Preamp", "rotator": "Rotator", "supergt": "Supercharger GT",
                 "comp": "Bus Compressor", "stereo": "Stereo Modeller", "choral": "Choral",
                 "replika": "Replika Delay", "raum": "Raum Reverb"}[f] for f in fx))
            if cfg.get("info"):
                out.append(f"- **Tip:** {cfg['info'].split('|', 1)[-1].strip()}")
            out.append("")
    out += ["## Performer (PERFORM page, all melodic instruments)", "",
            "- **Scale Lock:** " + ", ".join(n for n, _ in ksp_gen.SCALES),
            "- **Chord:** " + ", ".join(n for n, _ in ksp_gen.CHORDS),
            "- **Arpeggiator:** " + ", ".join(ksp_gen.ARP_MODES[1:]) + "; rates "
            + ", ".join(n for n, _ in ksp_gen.ARP_RATES) + "; 1-4 octaves, gate, swing, latch, accent",
            "- **Strum** (0-150 ms) and **Humanize** (timing and velocity)", ""]
    return "\n".join(out)
