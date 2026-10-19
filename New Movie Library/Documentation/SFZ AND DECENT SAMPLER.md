# New Movie Library: SFZ and Decent Sampler

Besides Kontakt and the player plugin, every instrument also comes ready to load in two
free sampler formats. They use the same samples (nothing is copied), so keep the
`New Movie Library` folder in one piece.

| Folder | Format | Free players |
|---|---|---|
| `SFZ/<Category>/` | `.sfz` (81 files) | [sfizz](https://sfz.tools/sfizz/) (VST3/LV2/AU), Plogue sforzando, TAL-Sampler, Bitwig Sampler, LinuxSampler |
| `Decent Sampler/<Category>/` | `.dspreset` (94 files) | [Decent Sampler](https://www.decentsamples.com/product/decent-sampler-plugin/) (VST/VST3/AU/standalone) |

## What's included, and what isn't

These are simpler versions of the Kontakt instruments:

| Feature | SFZ | Decent Sampler |
|---|---|---|
| Key / velocity mapping, velocity layers | yes | yes |
| Round robins | yes (sequential, random for drums) | yes |
| Seamless loops for sustained sounds | yes | yes |
| Articulations | keyswitches in one file (same keys as Kontakt) | one preset per articulation |
| Soft/loud dynamics on the mod wheel (CC1) | yes (crossfade) | yes (crossfade) |
| Close + Hall microphones (Ensemble Strings, Brass Ensemble) | both, hall at -6 dB | both, hall at -6 dB |
| Hi-hat choke groups | yes | yes |
| Attack / Release, Tone, Reverb, Volume knobs | sampler's own controls | on the preset's front panel |
| Performer (scale lock, chords, arpeggiator), legato, Note Repeat, effect chains | no | no |

For the full feature set use the Kontakt instruments or the player plugin.

## Files per instrument

- **Synths with two layers** (for example Warm Analog Pad): one file per layer (`Warm Analog Pad - Warm`,
  `Warm Analog Pad - Air`). In SFZ there's also a file with the default two-layer blend.
- **Orchestral and solo instruments:** SFZ has one file with keyswitches (`C0` = first articulation).
  Decent Sampler has one preset per articulation (`Ensemble Strings - Staccato`, and so on).
- **Keys, mallets, organ, guitars, world instruments:** one file per sound (`Cinematic Mallets - Celesta`).
- **Drum kits and FX:** one file with the full key map. The [Instrument Guide](INSTRUMENT%20GUIDE.md)
  lists the keys.

The Instrument Guide lists the exact file names for every instrument.

## Tested

Every SFZ file loads in sfizz with no unknown opcodes, and all of them were played with
files from the MIDI pack (strings with CC1 dynamics, timpani keyswitches, three drum kits,
pads, piano, kalimba). Every sample path in both formats was checked. **Not tested here:** the
Decent Sampler presets in Decent Sampler itself (it wasn't available). They're valid XML in
Decent Sampler's documented format. If one doesn't load, note the message Decent Sampler shows.
