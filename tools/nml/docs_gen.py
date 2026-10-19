"""Generates the Instrument Guide (Markdown) straight from the catalog, so the
documentation always matches the samples and scripts."""
import os

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
            if cfg.get("mics"):
                out.append("- **Microphones:** Close and Hall on the sustained articulations (Close Mic / Hall Mic faders); "
                           "the short articulations use the close mics")
            out.append("- **Presets:** Default, " + ", ".join(p[0] for p in inst.presets))
            if not inst.samples_from:
                from . import formats
                sfz = sorted(formats.sfz_files(inst))
                ds = sorted(formats.dspreset_files(inst))
                out.append(f"- **Other formats:** SFZ: {', '.join(f'`{f}`' for f in sfz)}; "
                           f"Decent Sampler: {', '.join(f'`{f}`' for f in ds)} (in `SFZ/{cat}` and `Decent Sampler/{cat}`)")
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


def build_guide(catalog):
    """The Build Guide, with the script / file table generated from the catalog."""
    rows = "\n".join(f"| `Build {i.name}.lua` | `Instruments/{i.category}/{i.name}.nki` |" for i in catalog)
    cats = []
    for i in catalog:
        if i.category not in cats:
            cats.append(i.category)
    walls = "\n".join(f"| {c} | `Resources/pictures/NML Wallpaper - {c.split(' ', 1)[1]}.png` |" for c in cats)
    ex = next(i for i in catalog if i.key == "Strings")
    example = f"{ex.name}: {len(ex.zones)} zones in {len(ex.groups)} groups."
    return BUILD_GUIDE.format(n=len(catalog), minutes=round(len(catalog) * 0.9 / 5) * 5, rows=rows, walls=walls,
                              lib=LIB_NAME, example=example)


BUILD_GUIDE = """# {lib}: Build Guide

Kontakt instruments (`.nki`) are a Kontakt-only file format, so this library
ships everything an instrument needs: the samples, mapping, loops and scripts.
Kontakt assembles them into `.nki` files once. After that you load them like
any other library.

You need Kontakt 8 (7.10 or newer also works) and Creator Tools, which installs
with Kontakt. Building all {n} instruments takes about {minutes} minutes. Build
only the ones you want: each instrument is independent.

> **No Kontakt?** You don't need to build anything to use the sounds:
> - the [player plugin](../../Plugin/README.md) (VST3 / CLAP for Windows and Linux)
>   plays every instrument with the same controls;
> - the `SFZ` and `Decent Sampler` folders hold ready-made versions for free samplers
>   (see [SFZ AND DECENT SAMPLER](SFZ%20AND%20DECENT%20SAMPLER.md)).

---

## Method A: Creator Tools (recommended, fully automatic)

Repeat for each instrument:

1. **Create an empty instrument.** In Kontakt, double-click the empty rack area
   (or choose *File > New instrument*).
2. **Connect Creator Tools.** Start Creator Tools. In the **Instrument Editor**
   (F2), pick the new instrument from the drop-down at the top.
3. **Run the build script.** Open the **Lua Script** panel (Shift+F3) and load
   `New Movie Library/Creator Tools/Build <Instrument>.lua` (double-click it in
   the file browser, or drag it in). Press **Run** (Ctrl/Cmd+R). The console
   prints something like
   `{example}` followed by `Performance script attached.`
4. **Push.** Press **Push** (Ctrl/Cmd+Alt+Up) to send the result to Kontakt.
5. **Check the script.** Click the instrument header in Kontakt. The
   performance view (PLAY / SOUND / PERFORM, with the Preset menu at the top
   right) should appear. If it doesn't, open *Script Editor*, select slot 1 and
   press **Apply**.
6. **Wallpaper (optional).** Open the wrench (Edit) view, then *Instrument Options >
   Instrument > Wallpaper* and pick the category picture from
   `Resources/pictures` (table below). It's stored inside the `.nki`.
7. **Save.** Choose *File > Save as...* and save to
   `New Movie Library/Instruments/<Category>/<Instrument>.nki`.
   Choose **Patch only** and leave *absolute sample paths* off, so the library
   keeps working when you move the folder.

The script builds the effects chain (filter, width, chorus, delay, reverb...)
the first time it runs. It's then saved inside the `.nki`.

### Which script for which file

| Build script | Save as |
|---|---|
{rows}

*Pulse Arp* uses the Pluck Synth samples with an arpeggiator preset, so it
needs no samples of its own.

### Wallpapers (800 x 398 px)

| Category | Picture |
|---|---|
{walls}

### Multis

A multi (`.nkm`) is a rack of several instruments on different MIDI channels.
[MULTIS AND MIDI](MULTIS%20AND%20MIDI.md) has ready-to-build combinations. Load
the instruments into one rack, set their MIDI channels, then choose
*File > Save multi as...*. Save multis in `New Movie Library/Multis`.

---

## Method B: by hand, without Creator Tools

Every instrument can also be built in Kontakt's own editors. The
[Instrument Guide](INSTRUMENT%20GUIDE.md) and `manifest.json` list the groups
and zones.

1. Create an empty instrument and open **Edit** mode (wrench icon).
2. **Groups.** In the Group Editor, create one group per sample folder and name
   it **exactly** like the folder (for example `SusP`, `SusF`, `StacRR1`,
   `SusPHall`). The script finds groups by name, so the names must match; their
   order doesn't matter. In each group's Source module choose **Sampler** mode.
3. **Samples.** Select one group, then drag all WAVs from its folder
   (`Samples/<Category>/<Instrument>/<Group>/`) into the Mapping Editor.
4. **Auto-map.** With the new zones selected, open *Edit > Auto-map: Setup*.
   File names look like `Strings_SusP_069_067_071_001_127.wav`. Set token 3 =
   *Root Key*, token 4 = *Low Key*, token 5 = *High Key*, token 6 = *Low
   Velocity*, token 7 = *High Velocity* and the others to *Ignore*. Then run
   *Auto-map selected*. Repeat steps 3-4 for every group.
5. **Loops.** Loop points are embedded in the WAV files, and Kontakt reads them
   on import. If a sustained sound stops instead of holding, open the Loop
   Editor and check that loop 1 is set to **Until End** (no crossfade needed:
   it's baked into the audio).
6. **Script.** Open the *Script Editor*, select slot 1, paste the contents of
   `Resources/scripts/NML <Instrument>.txt` and press **Apply**.
7. Save as described in Method A, step 7.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Creator Tools prints `MISSING SAMPLE` | The `.lua` file must stay inside `New Movie Library/Creator Tools`. It finds the samples relative to its own folder. On Windows, avoid paths with non-English characters (a Creator Tools limitation). |
| Status bar shows `NML: group not found: ...` | A group was renamed or not created. Rebuild with the Lua script, or rename the group to match exactly. |
| No sound, but keys light up | Check that the script in slot 1 is applied, and that you aren't playing a keyswitch (red keys). On orchestral instruments, check the Close Mic fader isn't fully down. |
| Sustained notes stop after ~2 seconds | Loops aren't enabled. Set loop 1 to *Until End* (Method B, step 5). |
| Effects missing | Re-apply the script once: it re-creates the effects chain in the instrument insert slots. |
| Wallpaper looks cut off | It is 800 x 398 px: the 330 px panel plus Kontakt's 68 px instrument header. If your Kontakt version draws it differently, the panel still works; the wallpaper is decoration only. |
| "Content missing" when reopening | The library folder moved and the instrument was saved with absolute paths. Use *Browse for folder* and point Kontakt to `New Movie Library`, then re-save. |

If the script editor reports an error, note the error text and the instrument
name. The scripts are generated by `tools/nml/ksp_gen.py`, so one fix there
updates all of them.
"""


# (name, mood, [(instrument name, setting)], [MIDI file name prefixes])
MULTIS = [
    ("Epic Trailer", "Driving ostinatos, braams and hybrid percussion for trailers and action cues.",
     [("Ensemble Strings", "Staccato, preset Ostinato 1/16"), ("Brass Ensemble", "Sustain, preset Epic Legato"),
      ("French Horns", "Sustain, Legato on"), ("Hybrid Trailer Percussion", "preset Big Room"),
      ("Braams and Hits", "preset Inception Stack"), ("Cinematic FX", "Default")],
     ["String Ostinato 16ths", "Trailer Rise", "Trailer Build", "Braam Hits", "Riser into Trailer Hit"]),
    ("Heroic Adventure", "A soaring horn theme over galloping strings, timpani and taikos.",
     [("French Horns", "Sustain, Legato on"), ("Ensemble Strings", "Staccato"), ("Brass Ensemble", "Staccato"),
      ("Cinematic Timpani", "Hits / Roll keyswitches"), ("Orchestral Percussion", "preset Big Room")],
     ["Heroic Theme", "Gallop", "Heroic I-V-vi-IV", "Timpani Hits into Roll", "Taiko Ensemble"]),
    ("Horror Underscore", "Slow dread: dark beds, ticking, scraping strings and a lonely cello.",
     [("Dark Atmospheres", "preset Dark and Close"), ("Tension Toolkit", "Default"),
      ("Solo Cello", "Sustain, preset Soft Underscore"), ("Reverse Swells", "Reverse Strings"),
      ("Cinematic FX", "Default")],
     ["Tension Bed", "Mystery Phrygian", "Lament Theme", "Dark Tension"]),
    ("Fantasy Wonder", "Sparkling harp and celesta, a choir and warm strings for magical moments.",
     [("Concert Harp", "preset Glissando"), ("Ethereal Choir", "Aah + Ooh blend"),
      ("Ensemble Strings", "Sustain, preset Concert Hall"), ("Cinematic Mallets", "preset Celesta + Glock"),
      ("Kalimba", "preset Ambient Wash")],
     ["Wonder Lydian", "Broken Chords", "Lullaby"]),
    ("Synthwave Night Drive", "80s neon: supersaws, gated drums, octave bass and a pulsing arp.",
     [("Supersaw Stack", "preset Lush and Wide"), ("Analog Mono Bass", "Mono / Glide on"),
      ("Synthwave Kit", "preset Big Room"), ("Pluck Synth", "Arpeggiator Up 1/16"),
      ("Wavetable Pad", "preset Dark and Close")],
     ["Synthwave Octaves", "Synthwave Gated", "Synth Pulse", "Space Drift"]),
    ("Desert Journey", "Duduk and sitar over a tanpura drone, hang drum and taikos.",
     [("Duduk", "preset Desert Lament"), ("Sitar and Tanpura", "Sitar + Tanpura Drone layer"),
      ("Hang Drum", "preset Pentatonic Arp"), ("Orchestral Percussion", "Taiko keys"),
      ("Drones and Textures", "DarkStrings + GlassAir")],
     ["Desert Lament", "Raga Phrase", "Taiko Ensemble", "Mystery Phrygian"]),
    ("Modern Trap Score", "808s, rolling hats, felt piano and a dark atmosphere.",
     [("808 Bass", "preset Distorted Slide"), ("Trap Kit", "preset Hat Rolls 1/32"),
      ("Felt Piano", "preset Intimate"), ("Dark Atmospheres", "Default")],
     ["Trap 808 Pattern", "Trap Hats and Rolls", "Sad Strings"]),
    ("Indie Band", "A small band: keys, guitars, bass and a real-sounding kit.",
     [("Felt Piano", "Default"), ("Electric Piano", "Default"), ("Electric Guitar", "Clean"),
      ("Finger Bass", "Default"), ("Studio Drum Kit", "preset Studio Dry"), ("Drawbar Organ", "preset Church Soft")],
     ["Halftime Ballad", "Shuffle Ride", "Broken Chords", "Cinematic Pulse"]),
]


def multis_and_midi(catalog, midi_files):
    names = {i.name for i in catalog}
    out = [f"# {LIB_NAME}: Multis and MIDI", "",
           "Ready-made combinations of instruments, and the MIDI phrase pack that comes with the library.", "",
           "## Building a multi", "",
           "- **Kontakt:** load the instruments into one rack. Give each one its own MIDI channel (the channel",
           "  number in each instrument header), set the settings below, then *File > Save multi as...* and save",
           "  into `New Movie Library/Multis`.",
           "- **Player plugin / other samplers:** put each instrument on its own track in your DAW. Route one",
           "  MIDI keyboard to all of them (or record each part separately).", "",
           "Drag the MIDI files listed under each multi onto the matching tracks to hear it straight away.", ""]
    stems = [os.path.basename(f)[:-4] for f in sorted(midi_files)]
    for name, mood, parts, midis in MULTIS:
        out += [f"## {name}", "", mood, "", "| Channel | Instrument | Setting |", "|---|---|---|"]
        for ch, (inst, setting) in enumerate(parts, 1):
            if inst not in names:
                raise ValueError(f"multi {name}: unknown instrument {inst}")
            out.append(f"| {ch} | {inst} | {setting} |")
        matches = []
        for m in midis:
            hit = [s for s in stems if s.startswith(m)]
            if not hit:
                raise ValueError(f"multi {name}: no MIDI file starting with {m}")
            matches += hit
        out += ["", "MIDI: " + ", ".join(f"`{m}`" for m in matches), ""]
    out += ["## The MIDI phrase pack", "",
            "In `New Movie Library/MIDI`. Standard MIDI files on channel 1, with the tempo set. Each name gives the",
            "key, the tempo and the instruments it was written for. String and brass parts include mod-wheel (CC1)",
            "dynamics, and the drum files use the key map of the kit named in the file.", ""]
    folder = None
    for f in sorted(midi_files):
        d, base = os.path.split(f)
        if d != folder:
            folder = d
            out += ["", f"### {d}", ""]
        out.append(f"- `{base}`")
    out.append("")
    return "\n".join(out)
