# New Movie Library: a Kontakt 8 sample library for film scoring

An original, Kontakt-ready sample library in the layout of a Kontakt 8 library:
`Instruments`, `Samples` and `Resources` folders, scripted performance views,
articulations, keyswitches, round robins, velocity layers, effects and
performance tools. It has **21 instruments** in three categories, **571 samples**
(24-bit / 44.1 kHz, about 208 MB) and one complete Kontakt script for each instrument.

> **Every sound here is original.** All samples are synthesized from scratch by
> the Python code in [`tools/`](tools/): oscillators, physical string models,
> modal synthesis, formant synthesis and synthetic reverbs. Nothing is copied
> from Native Instruments' factory content or any other commercial library. The
> genuine Kontakt 8 factory library comes with Kontakt 8 or Komplete through
> Native Access, and the free Kontakt 8 Player includes a Factory Selection.

## What's inside

| Category | Instrument | Engine | Highlights |
|---|---|---|---|
| 01 Synths and Pads | Warm Analog Pad | Synth | 2 blendable layers (Warm / Air), filter Movement, octave stacks |
| | Glass Shimmer Pad | Synth | FM glass bells into a shimmering sustain |
| | Supersaw Stack | Synth | 7-voice supersaw, poly or mono/glide lead |
| | Analog Mono Bass | Synth | Sub + growl blend, mono legato with glide |
| | Pluck Synth | Keys | Filter-envelope pluck with 2 round robins, great with the arp |
| | Pulse Arp | Keys | Same samples as Pluck Synth, preset as a tempo-synced 1/16 arpeggio |
| | Ethereal Choir | Synth | Formant choir, Blend morphs the vowel Aah to Ooh |
| 02 Orchestral and Band | Ensemble Strings | Articulation | Sustain (2 dynamics), Tremolo, Staccato, Pizzicato, Swell, legato |
| | Brass Ensemble | Articulation | Sustain (2 dynamics), Swell, Staccato |
| | Woodwind Ensemble | Articulation | Flute, Clarinet, Staccato |
| | Cinematic Timpani | Articulation | Pitched hits (round robins) and looped rolls with CC1 crescendo |
| | Electric Piano | Keys | 3 velocity layers, tremolo / drive preamp |
| | Nylon Guitar | Keys | Physical string model, 2 layers x 2 round robins, strum with Performer |
| | Finger Bass | Keys | 2 layers x 2 round robins |
| | Studio Drum Kit | Drums | 20 pieces, GM layout, hi-hat choke, 6-bus mixer |
| | Drawbar Organ | Keys | 2 registrations, rotary speaker on the mod wheel |
| | Cinematic Mallets | Keys | Marimba, Vibraphone, Celesta, Glockenspiel, layerable |
| | Orchestral Percussion | Drums | Gran cassa, taiko, snare, rolls, cymbals, tam-tam, metals |
| 03 Cinematic | Braams and Hits | Keys | Trailer braams, "Blaster" variant, layerable |
| | Drones and Textures | Synth | 8 evolving underscore beds, pick any two and blend |
| | Cinematic FX | Drums | 20 impacts, risers, whooshes, downers and stingers |

Full details are in the [Instrument Guide](New%20Movie%20Library/Documentation/INSTRUMENT%20GUIDE.md):
ranges, keyswitches, key maps and effects for every instrument.

### Every instrument has a full performance view

- **PLAY page:** controls for that engine, such as layers/blend, articulations,
  dynamics, legato and portamento, attack/release, velocity curves, mono/glide,
  octave layering, round robins, drum bus mixer and choke groups.
- **SOUND page:** an effects chain the script builds by itself: Filter (Tone),
  Stereo Modeller (Width), Choral (Chorus), Replika (tempo-synced Delay) and Raum
  (Reverb). Some instruments add EP Preamp, Rotator, Supercharger GT or Bus
  Compressor. Sustain pedal and pitch-bend range are also here.
- **PERFORM page** (all melodic instruments): Scale Lock (16 scales), Chords (17
  types, including diatonic triads and 7ths), Strum, a tempo-synced Arpeggiator
  (6 modes, 1/4 to 1/32 including triplets, octaves, gate, swing, latch, accent)
  and Humanize.

See [Controls](New%20Movie%20Library/Documentation/CONTROLS.md) for every knob.

## Quick start: turn the kit into .nki files

Kontakt instrument files (`.nki`) can only be written by Kontakt itself, so
each instrument is built once with **Creator Tools** (free, installed with
Kontakt 8). It takes about a minute per instrument:

1. Download or clone this repository and keep the `New Movie Library` folder
   intact.
2. In Kontakt 8, double-click the empty rack area to create an empty instrument.
3. Open **Creator Tools**, select that instrument in the Instrument Editor and
   load `New Movie Library/Creator Tools/Build <Instrument>.lua` in the
   **Lua Script** panel. Press **Run**, then **Push**.
4. In Kontakt, choose **Save as** and save it as
   `New Movie Library/Instruments/<Category>/<Instrument>.nki`.

The script creates every group, maps every zone (root key, key range, velocity
range), sets the loop points and attaches the performance script. The
[Build Guide](New%20Movie%20Library/Documentation/BUILD%20GUIDE.md) has
step-by-step instructions, a manual method without Creator Tools, and
troubleshooting.

## Folder layout

```
New Movie Library/
├── Instruments/            save the .nki files here (one folder per category)
├── Samples/                571 WAVs: <Category>/<Instrument>/<Group>/<file>.wav
├── Resources/
│   ├── scripts/            the KSP performance script of every instrument (.txt)
│   └── ir_samples/         4 bonus impulse responses for Kontakt's Convolution effect
├── Creator Tools/          one Lua build script per instrument
└── Documentation/          Build Guide, Instrument Guide, Controls, manifest.json
tools/                      the Python generator (samples, KSP, Lua, docs) + QA/tests
```

Each sample's name carries its mapping: `<Instrument>_<Group>_<root>_<low key>_<high key>_<low vel>_<high vel>.wav`.
Loop points and root key are also embedded in the WAV `smpl` chunk.

## Rebuilding or changing the sounds

Everything is generated reproducibly. See [`tools/README.md`](tools/README.md).

```bash
pip install -r tools/requirements.txt
python3 tools/build_library.py          # renders all samples + scripts + docs in about 30 s
python3 tools/qa_report.py              # clipping / DC / pitch / loop-seam checks
python3 tools/test_build_scripts.py     # dry-runs every Creator Tools script
```

## Status and honest limits

- **Tested here:** every KSP script compiles with the SublimeKSP compiler's
  extra syntax checks. Every Lua build script was dry-run against a mock of
  the Creator Tools API, checking groups, zones, mapping, loops, sample paths
  and the attached script. Every sample passed QA: no clipping, no DC offset,
  seamless loops, tuned within a few cents.
- **Not tested here:** Kontakt itself, which can't run in this build
  environment. If Kontakt reports a script error or a control behaves
  unexpectedly, note the message and the instrument and it can be fixed in
  `tools/nml/ksp_gen.py`.
- The orchestral and band instruments are **synthesized and modeled**, not
  recorded. They work well for sketching, hybrid and synth-orchestral scoring,
  but they won't match the realism of libraries recorded with live players.
