# New Movie Library - Instrument Guide

Generated from `tools/nml/catalog.py`. Note names use Kontakt's convention (C3 = MIDI 60).

## 01 Synths and Pads

### Warm Analog Pad

Seven-voice detuned analog stack (Warm) and a breathy, tonal-noise shimmer (Air).

- **File:** `Instruments/01 Synths and Pads/Warm Analog Pad.nki` (build with `Creator Tools/Build Warm Analog Pad.lua`)
- **Engine:** Synth engine - two blendable layers, attack/release, filter with tempo-synced Movement, octave layering, mono/glide.
- **Playable range:** C0 - C7 (MIDI 24-108)
- **Samples:** 22 zones in 2 groups (Warm, Air), stereo, 24-bit / 44.1 kHz, 14.8 MB
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Lush and Wide, Dark and Close, Epic Octaves, Tempo Pulse
- **Other formats:** SFZ: `Warm Analog Pad - Air.sfz`, `Warm Analog Pad - Warm.sfz`, `Warm Analog Pad.sfz`; Decent Sampler: `Warm Analog Pad - Air.dspreset`, `Warm Analog Pad - Warm.dspreset` (in `SFZ/01 Synths and Pads` and `Decent Sampler/01 Synths and Pads`)
- **Tip:** Mod wheel opens the filter, Blend mixes Warm and Air

### Glass Shimmer Pad

FM glass bells with an octave shimmer, chorus and a long hall.

- **File:** `Instruments/01 Synths and Pads/Glass Shimmer Pad.nki` (build with `Creator Tools/Build Glass Shimmer Pad.lua`)
- **Engine:** Synth engine - two blendable layers, attack/release, filter with tempo-synced Movement, octave layering, mono/glide.
- **Playable range:** C0 - C7 (MIDI 24-108)
- **Samples:** 11 zones in 1 groups (Glass), stereo, 24-bit / 44.1 kHz, 7.5 MB
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Lush and Wide, Dark and Close, Epic Octaves, Tempo Pulse
- **Other formats:** SFZ: `Glass Shimmer Pad.sfz`; Decent Sampler: `Glass Shimmer Pad.dspreset` (in `SFZ/01 Synths and Pads` and `Decent Sampler/01 Synths and Pads`)
- **Tip:** FM bell attack into a shimmering sustain

### Wavetable Pad

Slowly morphing wavetable pad plus a wavefolded digital layer.

- **File:** `Instruments/01 Synths and Pads/Wavetable Pad.nki` (build with `Creator Tools/Build Wavetable Pad.lua`)
- **Engine:** Synth engine - two blendable layers, attack/release, filter with tempo-synced Movement, octave layering, mono/glide.
- **Playable range:** C0 - C7 (MIDI 24-108)
- **Samples:** 22 zones in 2 groups (Morph, Digital), stereo, 24-bit / 44.1 kHz, 13.1 MB
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Lush and Wide, Dark and Close, Epic Octaves, Tempo Pulse
- **Other formats:** SFZ: `Wavetable Pad - Digital.sfz`, `Wavetable Pad - Morph.sfz`, `Wavetable Pad.sfz`; Decent Sampler: `Wavetable Pad - Digital.dspreset`, `Wavetable Pad - Morph.dspreset` (in `SFZ/01 Synths and Pads` and `Decent Sampler/01 Synths and Pads`)
- **Tip:** Morphing additive tables (Morph) and wavefolded Digital layer

### Supersaw Stack

Seven detuned saws, trance/trailer style. Poly, or mono with glide.

- **File:** `Instruments/01 Synths and Pads/Supersaw Stack.nki` (build with `Creator Tools/Build Supersaw Stack.lua`)
- **Engine:** Synth engine - two blendable layers, attack/release, filter with tempo-synced Movement, octave layering, mono/glide.
- **Playable range:** C0 - C7 (MIDI 24-108)
- **Samples:** 11 zones in 1 groups (Saw), stereo, 24-bit / 44.1 kHz, 4.9 MB
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Lush and Wide, Dark and Close, Epic Octaves, Tempo Pulse, Mono Lead
- **Other formats:** SFZ: `Supersaw Stack.sfz`; Decent Sampler: `Supersaw Stack.dspreset` (in `SFZ/01 Synths and Pads` and `Decent Sampler/01 Synths and Pads`)
- **Tip:** Mono / Glide for leads, Octave Layer for anthems

### Analog Brass Synth

Classic polysynth brass: detuned saws with a swelling filter envelope.

- **File:** `Instruments/01 Synths and Pads/Analog Brass Synth.nki` (build with `Creator Tools/Build Analog Brass Synth.lua`)
- **Engine:** Synth engine - two blendable layers, attack/release, filter with tempo-synced Movement, octave layering, mono/glide.
- **Playable range:** C0 - C7 (MIDI 24-108)
- **Samples:** 11 zones in 1 groups (Brass), stereo, 24-bit / 44.1 kHz, 5.4 MB
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Lush and Wide, Dark and Close, Epic Octaves, Tempo Pulse
- **Other formats:** SFZ: `Analog Brass Synth.sfz`; Decent Sampler: `Analog Brass Synth.dspreset` (in `SFZ/01 Synths and Pads` and `Decent Sampler/01 Synths and Pads`)
- **Tip:** 80s poly brass with a filter-envelope 'bwaa'

### Analog Mono Bass

Pure sub and a resonant, driven growl layer. Mono legato with glide.

- **File:** `Instruments/01 Synths and Pads/Analog Mono Bass.nki` (build with `Creator Tools/Build Analog Mono Bass.lua`)
- **Engine:** Synth engine - two blendable layers, attack/release, filter with tempo-synced Movement, octave layering, mono/glide.
- **Playable range:** C-1 - C4 (MIDI 12-72)
- **Samples:** 14 zones in 2 groups (Sub, Growl), mono, 24-bit / 44.1 kHz, 2.7 MB
- **Effects chain (built by the script):** Filter > Supercharger GT > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Lush and Wide, Dark and Close, Epic Octaves, Tempo Pulse
- **Other formats:** SFZ: `Analog Mono Bass - Growl.sfz`, `Analog Mono Bass - Sub.sfz`, `Analog Mono Bass.sfz`; Decent Sampler: `Analog Mono Bass - Growl.dspreset`, `Analog Mono Bass - Sub.dspreset` (in `SFZ/01 Synths and Pads` and `Decent Sampler/01 Synths and Pads`)
- **Tip:** Blend: clean sub to growl. Mono/Glide on by default

### 808 Bass

Long trap 808 with pitch punch; clean and distorted layers, mono slide.

- **File:** `Instruments/01 Synths and Pads/808 Bass.nki` (build with `Creator Tools/Build 808 Bass.lua`)
- **Engine:** Synth engine - two blendable layers, attack/release, filter with tempo-synced Movement, octave layering, mono/glide.
- **Playable range:** C-1 - C4 (MIDI 12-72)
- **Samples:** 14 zones in 2 groups (Clean, Dist), mono, 24-bit / 44.1 kHz, 5.2 MB
- **Effects chain (built by the script):** Filter > Supercharger GT > Stereo Modeller > Raum Reverb
- **Presets:** Default, Lush and Wide, Dark and Close, Epic Octaves, Tempo Pulse, Distorted Slide
- **Other formats:** SFZ: `808 Bass - Clean.sfz`, `808 Bass - Dist.sfz`; Decent Sampler: `808 Bass - Clean.dspreset`, `808 Bass - Dist.dspreset` (in `SFZ/01 Synths and Pads` and `Decent Sampler/01 Synths and Pads`)
- **Tip:** Mono glide slides like trap 808s. Layer B adds distortion

### Tape Keys

Tape-replay keyboard: flute, strings and choir with wow, flutter and hiss.

- **File:** `Instruments/01 Synths and Pads/Tape Keys.nki` (build with `Creator Tools/Build Tape Keys.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** C1 - C6 (MIDI 36-96)
- **Samples:** 27 zones in 3 groups (TapeFlute, TapeStrings, TapeChoir), mono, 24-bit / 44.1 kHz, 6.9 MB
- **Instruments (menu + layer):** Tape Flute, Tape Strings, Tape Choir
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Studio, Ambient Wash, Strummed Chords
- **Other formats:** SFZ: `Tape Keys - Tape Choir.sfz`, `Tape Keys - Tape Flute.sfz`, `Tape Keys - Tape Strings.sfz`; Decent Sampler: `Tape Keys - Tape Choir.dspreset`, `Tape Keys - Tape Flute.dspreset`, `Tape Keys - Tape Strings.dspreset` (in `SFZ/01 Synths and Pads` and `Decent Sampler/01 Synths and Pads`)
- **Tip:** Vintage tape-replay flutes, strings and choir with wow and flutter

### Pluck Synth

Snappy filter-envelope pluck with three round robins.

- **File:** `Instruments/01 Synths and Pads/Pluck Synth.nki` (build with `Creator Tools/Build Pluck Synth.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** C0 - C7 (MIDI 24-108)
- **Samples:** 33 zones in 3 groups (RR1, RR2, RR3), stereo, 24-bit / 44.1 kHz, 10.5 MB
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Studio, Ambient Wash, Strummed Chords
- **Other formats:** SFZ: `Pluck Synth.sfz`; Decent Sampler: `Pluck Synth.dspreset` (in `SFZ/01 Synths and Pads` and `Decent Sampler/01 Synths and Pads`)
- **Tip:** Try PERFORM > Arpeggiator

### Pulse Arp

The Pluck Synth preset as a ready-to-go tempo-synced arpeggiator.

- **File:** `Instruments/01 Synths and Pads/Pulse Arp.nki` (build with `Creator Tools/Build Pulse Arp.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** C0 - C7 (MIDI 24-108)
- **Samples:** 33 zones in 3 groups (RR1, RR2, RR3), stereo, 24-bit / 44.1 kHz, 10.5 MB (shared with Pluck)
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Studio, Ambient Wash, Strummed Chords
- **Tip:** Hold a chord: 1/16 arpeggio synced to tempo

### Sequencer Bass

Punchy resonant sequence bass, arpeggiator on by default.

- **File:** `Instruments/01 Synths and Pads/Sequencer Bass.nki` (build with `Creator Tools/Build Sequencer Bass.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** C-1 - C5 (MIDI 12-84)
- **Samples:** 9 zones in 1 groups (Seq), mono, 24-bit / 44.1 kHz, 0.9 MB
- **Effects chain (built by the script):** Filter > Supercharger GT > Stereo Modeller > Replika Delay > Raum Reverb
- **Presets:** Default, Studio, Ambient Wash, Strummed Chords
- **Other formats:** SFZ: `Sequencer Bass.sfz`; Decent Sampler: `Sequencer Bass.dspreset` (in `SFZ/01 Synths and Pads` and `Decent Sampler/01 Synths and Pads`)
- **Tip:** Hold notes for a pulsing 1/16 bass line (arp on)

### Ethereal Choir

Formant-synthesised mixed choir, Aah and Ooh vowels, morphable.

- **File:** `Instruments/01 Synths and Pads/Ethereal Choir.nki` (build with `Creator Tools/Build Ethereal Choir.lua`)
- **Engine:** Synth engine - two blendable layers, attack/release, filter with tempo-synced Movement, octave layering, mono/glide.
- **Playable range:** A0 - C6 (MIDI 33-96)
- **Samples:** 18 zones in 2 groups (Aah, Ooh), stereo, 24-bit / 44.1 kHz, 12.1 MB
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Lush and Wide, Dark and Close, Epic Octaves, Tempo Pulse
- **Other formats:** SFZ: `Ethereal Choir - Aah.sfz`, `Ethereal Choir - Ooh.sfz`, `Ethereal Choir.sfz`; Decent Sampler: `Ethereal Choir - Aah.dspreset`, `Ethereal Choir - Ooh.dspreset` (in `SFZ/01 Synths and Pads` and `Decent Sampler/01 Synths and Pads`)
- **Tip:** Blend morphs the vowel from Aah to Ooh

## 02 Orchestral

### Ensemble Strings

Eight-player bowed ensemble: sustain (2 dynamics, 2 mics), tremolo, staccato, pizzicato, swell.

- **File:** `Instruments/02 Orchestral/Ensemble Strings.nki` (build with `Creator Tools/Build Ensemble Strings.lua`)
- **Engine:** Articulation engine - keyswitches, mod-wheel dynamics crossfade, legato with portamento, round-robin shorts.
- **Playable range:** G0 - G6 (MIDI 31-103)
- **Samples:** 168 zones in 14 groups (SusP, SusF, Trem, StacRR1, StacRR2, StacRR3, StacRR4, PizzRR1, PizzRR2, PizzRR3, PizzRR4, SusPHall, SusFHall, TremHall), stereo, 24-bit / 44.1 kHz, 61.4 MB
- **Articulations / keyswitches:**
  - `C0` **Sustain** - sustain, CC1 dynamics (SusP / SusF)
  - `C#0` **Tremolo** - sustain, CC1 dynamics (Trem)
  - `D0` **Staccato** - short, round robin, velocity (StacRR1 / StacRR2 / StacRR3 / StacRR4)
  - `D#0` **Pizzicato** - short, round robin, velocity (PizzRR1 / PizzRR2 / PizzRR3 / PizzRR4)
  - `E0` **Swell** - auto-swell, CC1 dynamics (SusP / SusF)
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Microphones:** Close and Hall on the sustained articulations (Close Mic / Hall Mic faders); the short articulations use the close mics
- **Presets:** Default, Close Mics, Concert Hall, Epic Legato, Soft Underscore, Ostinato 1/16
- **Other formats:** SFZ: `Ensemble Strings.sfz`; Decent Sampler: `Ensemble Strings - Pizzicato.dspreset`, `Ensemble Strings - Staccato.dspreset`, `Ensemble Strings - Sustain.dspreset`, `Ensemble Strings - Swell.dspreset`, `Ensemble Strings - Tremolo.dspreset` (in `SFZ/02 Orchestral` and `Decent Sampler/02 Orchestral`)
- **Tip:** CC1 = dynamics, keyswitches C0-E0, Close/Hall mics

### Solo Violin

Expressive single violin with legato, staccato and pizzicato.

- **File:** `Instruments/02 Orchestral/Solo Violin.nki` (build with `Creator Tools/Build Solo Violin.lua`)
- **Engine:** Articulation engine - keyswitches, mod-wheel dynamics crossfade, legato with portamento, round-robin shorts.
- **Playable range:** G2 - E6 (MIDI 55-100)
- **Samples:** 42 zones in 6 groups (SusP, SusF, StacRR1, StacRR2, PizzRR1, PizzRR2), mono, 24-bit / 44.1 kHz, 7.0 MB
- **Articulations / keyswitches:**
  - `C0` **Sustain** - sustain, CC1 dynamics (SusP / SusF)
  - `C#0` **Staccato** - short, round robin, velocity (StacRR1 / StacRR2)
  - `D0` **Pizzicato** - short, round robin, velocity (PizzRR1 / PizzRR2)
  - `D#0` **Swell** - auto-swell, CC1 dynamics (SusP / SusF)
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Epic Legato, Soft Underscore, Ostinato 1/16
- **Other formats:** SFZ: `Solo Violin.sfz`; Decent Sampler: `Solo Violin - Pizzicato.dspreset`, `Solo Violin - Staccato.dspreset`, `Solo Violin - Sustain.dspreset`, `Solo Violin - Swell.dspreset` (in `SFZ/02 Orchestral` and `Decent Sampler/02 Orchestral`)
- **Tip:** Legato on by default, CC1 = dynamics

### Solo Cello

Warm single cello with legato, staccato and pizzicato.

- **File:** `Instruments/02 Orchestral/Solo Cello.nki` (build with `Creator Tools/Build Solo Cello.lua`)
- **Engine:** Articulation engine - keyswitches, mod-wheel dynamics crossfade, legato with portamento, round-robin shorts.
- **Playable range:** C1 - G4 (MIDI 36-79)
- **Samples:** 42 zones in 6 groups (SusP, SusF, StacRR1, StacRR2, PizzRR1, PizzRR2), mono, 24-bit / 44.1 kHz, 7.0 MB
- **Articulations / keyswitches:**
  - `C0` **Sustain** - sustain, CC1 dynamics (SusP / SusF)
  - `C#0` **Staccato** - short, round robin, velocity (StacRR1 / StacRR2)
  - `D0` **Pizzicato** - short, round robin, velocity (PizzRR1 / PizzRR2)
  - `D#0` **Swell** - auto-swell, CC1 dynamics (SusP / SusF)
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Epic Legato, Soft Underscore, Ostinato 1/16
- **Other formats:** SFZ: `Solo Cello.sfz`; Decent Sampler: `Solo Cello - Pizzicato.dspreset`, `Solo Cello - Staccato.dspreset`, `Solo Cello - Sustain.dspreset`, `Solo Cello - Swell.dspreset` (in `SFZ/02 Orchestral` and `Decent Sampler/02 Orchestral`)
- **Tip:** Legato on by default, CC1 = dynamics

### Brass Ensemble

Horn/trombone section with loudness-driven brightness, swells and shorts.

- **File:** `Instruments/02 Orchestral/Brass Ensemble.nki` (build with `Creator Tools/Build Brass Ensemble.lua`)
- **Engine:** Articulation engine - keyswitches, mod-wheel dynamics crossfade, legato with portamento, round-robin shorts.
- **Playable range:** F0 - F#5 (MIDI 29-90)
- **Samples:** 72 zones in 8 groups (SusP, SusF, StacRR1, StacRR2, StacRR3, StacRR4, SusPHall, SusFHall), stereo, 24-bit / 44.1 kHz, 26.3 MB
- **Articulations / keyswitches:**
  - `C0` **Sustain** - sustain, CC1 dynamics (SusP / SusF)
  - `C#0` **Swell** - auto-swell, CC1 dynamics (SusP / SusF)
  - `D0` **Staccato** - short, round robin, velocity (StacRR1 / StacRR2 / StacRR3 / StacRR4)
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Microphones:** Close and Hall on the sustained articulations (Close Mic / Hall Mic faders); the short articulations use the close mics
- **Presets:** Default, Close Mics, Concert Hall, Epic Legato, Soft Underscore, Ostinato 1/16
- **Other formats:** SFZ: `Brass Ensemble.sfz`; Decent Sampler: `Brass Ensemble - Staccato.dspreset`, `Brass Ensemble - Sustain.dspreset`, `Brass Ensemble - Swell.dspreset` (in `SFZ/02 Orchestral` and `Decent Sampler/02 Orchestral`)
- **Tip:** CC1 = dynamics (soft to blaring), keyswitches C0-D0, Close/Hall mics

### French Horns

Four-horn section, mellow to heroic, with swells and shorts.

- **File:** `Instruments/02 Orchestral/French Horns.nki` (build with `Creator Tools/Build French Horns.lua`)
- **Engine:** Articulation engine - keyswitches, mod-wheel dynamics crossfade, legato with portamento, round-robin shorts.
- **Playable range:** G0 - A4 (MIDI 31-81)
- **Samples:** 32 zones in 4 groups (SusP, SusF, StacRR1, StacRR2), mono, 24-bit / 44.1 kHz, 5.9 MB
- **Articulations / keyswitches:**
  - `C0` **Sustain** - sustain, CC1 dynamics (SusP / SusF)
  - `C#0` **Swell** - auto-swell, CC1 dynamics (SusP / SusF)
  - `D0` **Staccato** - short, round robin, velocity (StacRR1 / StacRR2)
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Epic Legato, Soft Underscore, Ostinato 1/16
- **Other formats:** SFZ: `French Horns.sfz`; Decent Sampler: `French Horns - Staccato.dspreset`, `French Horns - Sustain.dspreset`, `French Horns - Swell.dspreset` (in `SFZ/02 Orchestral` and `Decent Sampler/02 Orchestral`)
- **Tip:** Warm, heroic horn section. CC1 = dynamics

### Woodwind Ensemble

Breathy flute pair, clarinet pair and a woodwind staccato.

- **File:** `Instruments/02 Orchestral/Woodwind Ensemble.nki` (build with `Creator Tools/Build Woodwind Ensemble.lua`)
- **Engine:** Articulation engine - keyswitches, mod-wheel dynamics crossfade, legato with portamento, round-robin shorts.
- **Playable range:** E1 - E6 (MIDI 40-100)
- **Samples:** 54 zones in 6 groups (Flute, Clarinet, StacRR1, StacRR2, StacRR3, StacRR4), mono, 24-bit / 44.1 kHz, 7.6 MB
- **Articulations / keyswitches:**
  - `C0` **Flute Sustain** - sustain, CC1 dynamics (Flute)
  - `C#0` **Clarinet Sustain** - sustain, CC1 dynamics (Clarinet)
  - `D0` **Staccato** - short, round robin, velocity (StacRR1 / StacRR2 / StacRR3 / StacRR4)
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Epic Legato, Soft Underscore, Ostinato 1/16
- **Other formats:** SFZ: `Woodwind Ensemble.sfz`; Decent Sampler: `Woodwind Ensemble - Clarinet Sustain.dspreset`, `Woodwind Ensemble - Flute Sustain.dspreset`, `Woodwind Ensemble - Staccato.dspreset` (in `SFZ/02 Orchestral` and `Decent Sampler/02 Orchestral`)
- **Tip:** Flutes, clarinets and staccato, keyswitches C0-D0

### Concert Harp

Plucked concert harp, 2 velocity layers x 2 round robins, rings out naturally.

- **File:** `Instruments/02 Orchestral/Concert Harp.nki` (build with `Creator Tools/Build Concert Harp.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** B-1 - G#6 (MIDI 23-104)
- **Samples:** 56 zones in 4 groups (V1RR1, V1RR2, V2RR1, V2RR2), mono, 24-bit / 44.1 kHz, 15.6 MB
- **Harp velocity layers:** 2 (splits at velocity 85), 2 round robin(s) each
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Studio, Ambient Wash, Strummed Chords, Glissando
- **Other formats:** SFZ: `Concert Harp.sfz`; Decent Sampler: `Concert Harp.dspreset` (in `SFZ/02 Orchestral` and `Decent Sampler/02 Orchestral`)
- **Tip:** For glissandi: PERFORM > Scale Lock + Arp Up 1/32

### Cinematic Timpani

Pitched timpani hits with 4 round robins and looped rolls with crescendo control.

- **File:** `Instruments/02 Orchestral/Cinematic Timpani.nki` (build with `Creator Tools/Build Cinematic Timpani.lua`)
- **Engine:** Articulation engine - keyswitches, mod-wheel dynamics crossfade, legato with portamento, round-robin shorts.
- **Playable range:** C1 - A2 (MIDI 36-57)
- **Samples:** 24 zones in 6 groups (HitRR1, HitRR2, HitRR3, HitRR4, RollP, RollF), mono, 24-bit / 44.1 kHz, 7.9 MB
- **Articulations / keyswitches:**
  - `C0` **Hits** - short, round robin, velocity (HitRR1 / HitRR2 / HitRR3 / HitRR4)
  - `C#0` **Roll** - sustain, CC1 dynamics (RollP / RollF)
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Epic Legato, Soft Underscore
- **Other formats:** SFZ: `Cinematic Timpani.sfz`; Decent Sampler: `Cinematic Timpani - Hits.dspreset`, `Cinematic Timpani - Roll.dspreset` (in `SFZ/02 Orchestral` and `Decent Sampler/02 Orchestral`)
- **Tip:** C0 hits, C#0 rolls (CC1 = roll dynamics)

### Orchestral Percussion

Gran cassa, taiko, snare, cymbals, tam-tam and metals with 3 round robins and rolls.

- **File:** `Instruments/02 Orchestral/Orchestral Percussion.nki` (build with `Creator Tools/Build Orchestral Percussion.lua`)
- **Engine:** Drum engine - one piece per key, velocity layers, round robins, choke groups, per-bus mixer.
- **Samples:** 48 zones in 3 groups (RR1, RR2, RR3), mono, 24-bit / 44.1 kHz, 15.4 MB
- **Key map:**

  | Key | MIDI | Piece | Bus |
  |---|---|---|---|
  | C1 | 36 | Gran Cassa | Drums |
  | C#1 | 37 | Gran Cassa Roll (hold = roll) | Drums |
  | D1 | 38 | Taiko | Taiko |
  | D#1 | 39 | Taiko Ensemble | Taiko |
  | E1 | 40 | Taiko Rim | Taiko |
  | F1 | 41 | Boom Drum | Drums |
  | F#1 | 42 | Orch Snare | Snare |
  | G1 | 43 | Snare Roll (hold = roll) | Snare |
  | A1 | 45 | Piatti | Cymbals |
  | A#1 | 46 | Cymbal Swell | Cymbals |
  | B1 | 47 | Sus Cymbal | Cymbals |
  | C2 | 48 | Tam-tam | Metals |
  | D2 | 50 | Triangle | Metals |
  | E2 | 52 | Anvil | Metals |
  | F2 | 53 | Woodblock | Metals |
  | F#2 | 54 | Tambourine | Snare |

- **Effects chain (built by the script):** Filter > Bus Compressor > Stereo Modeller > Raum Reverb
- **Presets:** Default, Studio Dry, Big Room, Crushed
- **Other formats:** SFZ: `Orchestral Percussion.sfz`; Decent Sampler: `Orchestral Percussion.dspreset` (in `SFZ/02 Orchestral` and `Decent Sampler/02 Orchestral`)
- **Tip:** Hold C#2 / G2 for rolls, CC1 = roll level

## 03 Band and Keys

### Felt Piano

Physically modelled felt piano: hammer, 1-3 strings per note and a soundboard.

- **File:** `Instruments/03 Band and Keys/Felt Piano.nki` (build with `Creator Tools/Build Felt Piano.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** A-1 - C7 (MIDI 21-108)
- **Samples:** 45 zones in 3 groups (V1, V2, V3), mono, 24-bit / 44.1 kHz, 18.5 MB
- **Felt Piano velocity layers:** 3 (splits at velocity 50, 98), 1 round robin(s) each
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Studio, Ambient Wash, Strummed Chords, Intimate
- **Other formats:** SFZ: `Felt Piano.sfz`; Decent Sampler: `Felt Piano.dspreset` (in `SFZ/03 Band and Keys` and `Decent Sampler/03 Band and Keys`)
- **Tip:** Soft hammered-string piano, 3 velocity layers

### Electric Piano

FM tine electric piano with velocity-dependent bark, tremolo preamp.

- **File:** `Instruments/03 Band and Keys/Electric Piano.nki` (build with `Creator Tools/Build Electric Piano.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** A-1 - C7 (MIDI 21-108)
- **Samples:** 39 zones in 3 groups (V1, V2, V3), mono, 24-bit / 44.1 kHz, 13.2 MB
- **Tine EP velocity layers:** 3 (splits at velocity 52, 98), 1 round robin(s) each
- **Effects chain (built by the script):** Filter > EP Preamp > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Studio, Ambient Wash, Strummed Chords
- **Other formats:** SFZ: `Electric Piano.sfz`; Decent Sampler: `Electric Piano.dspreset` (in `SFZ/03 Band and Keys` and `Decent Sampler/03 Band and Keys`)
- **Tip:** 3 velocity layers, tremolo and drive on the SOUND page

### Drawbar Organ

Tonewheel-style additive organ with key click, rotary speaker and drive.

- **File:** `Instruments/03 Band and Keys/Drawbar Organ.nki` (build with `Creator Tools/Build Drawbar Organ.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** C0 - C7 (MIDI 24-108)
- **Samples:** 22 zones in 2 groups (Full, Soft), mono, 24-bit / 44.1 kHz, 4.6 MB
- **Instruments (menu + layer):** Full Drawbars, Soft Flutes
- **Effects chain (built by the script):** Filter > Rotator > Supercharger GT > Replika Delay > Raum Reverb
- **Presets:** Default, Gospel Fast, Church Soft
- **Other formats:** SFZ: `Drawbar Organ - Full Drawbars.sfz`, `Drawbar Organ - Soft Flutes.sfz`; Decent Sampler: `Drawbar Organ - Full Drawbars.dspreset`, `Drawbar Organ - Soft Flutes.dspreset` (in `SFZ/03 Band and Keys` and `Decent Sampler/03 Band and Keys`)
- **Tip:** Mod wheel up = fast rotary

### Nylon Guitar

Physically modelled nylon-string guitar with body resonance, 3 layers x 2 round robins.

- **File:** `Instruments/03 Band and Keys/Nylon Guitar.nki` (build with `Creator Tools/Build Nylon Guitar.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** D1 - C5 (MIDI 38-84)
- **Samples:** 42 zones in 6 groups (V1RR1, V1RR2, V2RR1, V2RR2, V3RR1, V3RR2), mono, 24-bit / 44.1 kHz, 13.3 MB
- **Nylon velocity layers:** 3 (splits at velocity 60, 100), 2 round robin(s) each
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Studio, Ambient Wash, Strummed Chords
- **Other formats:** SFZ: `Nylon Guitar.sfz`; Decent Sampler: `Nylon Guitar.dspreset` (in `SFZ/03 Band and Keys` and `Decent Sampler/03 Band and Keys`)
- **Tip:** Use PERFORM > Chord + Strum for strummed chords

### Electric Guitar

Electric guitar model with pickup, amp and cabinet: clean, overdrive and palm mutes.

- **File:** `Instruments/03 Band and Keys/Electric Guitar.nki` (build with `Creator Tools/Build Electric Guitar.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** D1 - D5 (MIDI 38-86)
- **Samples:** 56 zones in 8 groups (V1RR1, V1RR2, V2RR1, V2RR2, DriveRR1, DriveRR2, MuteRR1, MuteRR2), mono, 24-bit / 44.1 kHz, 14.7 MB
- **Instruments (menu + layer):** Clean, Drive, Palm Mute
- **Clean velocity layers:** 2 (splits at velocity 90), 2 round robin(s) each
- **Effects chain (built by the script):** Filter > Supercharger GT > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Studio, Ambient Wash, Strummed Chords, Power Chords, Chugs
- **Other formats:** SFZ: `Electric Guitar - Clean.sfz`, `Electric Guitar - Drive.sfz`, `Electric Guitar - Palm Mute.sfz`; Decent Sampler: `Electric Guitar - Clean.dspreset`, `Electric Guitar - Drive.dspreset`, `Electric Guitar - Palm Mute.dspreset` (in `SFZ/03 Band and Keys` and `Decent Sampler/03 Band and Keys`)
- **Tip:** Clean, Drive and Palm Mute. Power chords: PERFORM > Chord > Power

### Finger Bass

Fingered electric bass model with pickup comb filtering and thump.

- **File:** `Instruments/03 Band and Keys/Finger Bass.nki` (build with `Creator Tools/Build Finger Bass.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** B-1 - E3 (MIDI 23-64)
- **Samples:** 36 zones in 6 groups (V1RR1, V1RR2, V2RR1, V2RR2, V3RR1, V3RR2), mono, 24-bit / 44.1 kHz, 9.3 MB
- **Finger velocity layers:** 3 (splits at velocity 60, 100), 2 round robin(s) each
- **Effects chain (built by the script):** Filter > Supercharger GT > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Studio, Ambient Wash, Strummed Chords
- **Other formats:** SFZ: `Finger Bass.sfz`; Decent Sampler: `Finger Bass.dspreset` (in `SFZ/03 Band and Keys` and `Decent Sampler/03 Band and Keys`)
- **Tip:** 3 velocity layers x 2 round robins

### Studio Drum Kit

Synthesised acoustic/hybrid kit: 20 pieces, 3 velocity layers x 3 round robins.

- **File:** `Instruments/03 Band and Keys/Studio Drum Kit.nki` (build with `Creator Tools/Build Studio Drum Kit.lua`)
- **Engine:** Drum engine - one piece per key, velocity layers, round robins, choke groups, per-bus mixer.
- **Samples:** 180 zones in 9 groups (V1RR1, V1RR2, V1RR3, V2RR1, V2RR2, V2RR3, V3RR1, V3RR2, V3RR3), mono, 24-bit / 44.1 kHz, 28.1 MB
- **Key map:**

  | Key | MIDI | Piece | Bus |
  |---|---|---|---|
  | C1 | 36 | Kick | Kick |
  | C#1 | 37 | Side Stick | Snare |
  | D1 | 38 | Snare | Snare |
  | D#1 | 39 | Clap | Perc |
  | E1 | 40 | Rimshot | Snare |
  | F1 | 41 | Floor Tom 2 | Toms |
  | F#1 | 42 | Closed Hat | Hats |
  | G1 | 43 | Floor Tom 1 | Toms |
  | G#1 | 44 | Pedal Hat | Hats |
  | A1 | 45 | Low Tom | Toms |
  | A#1 | 46 | Open Hat (choked by closed/pedal hat) | Hats |
  | B1 | 47 | Mid Tom | Toms |
  | C2 | 48 | Hi-Mid Tom | Toms |
  | C#2 | 49 | Crash | Cymbals |
  | D2 | 50 | High Tom | Toms |
  | D#2 | 51 | Ride | Cymbals |
  | F2 | 53 | Ride Bell | Cymbals |
  | F#2 | 54 | Tambourine | Perc |
  | A2 | 57 | Crash 2 | Cymbals |
  | A#3 | 70 | Shaker | Perc |

- **Effects chain (built by the script):** Filter > Bus Compressor > Supercharger GT > Stereo Modeller > Raum Reverb
- **Presets:** Default, Studio Dry, Big Room, Crushed
- **Other formats:** SFZ: `Studio Drum Kit.sfz`; Decent Sampler: `Studio Drum Kit.dspreset` (in `SFZ/03 Band and Keys` and `Decent Sampler/03 Band and Keys`)
- **Tip:** GM layout, 3 velocity layers x 3 round robins, Note Repeat

### Synthwave Kit

80s drum machine kit with gated snares, Simmons-style toms and cowbell.

- **File:** `Instruments/03 Band and Keys/Synthwave Kit.nki` (build with `Creator Tools/Build Synthwave Kit.lua`)
- **Engine:** Drum engine - one piece per key, velocity layers, round robins, choke groups, per-bus mixer.
- **Samples:** 68 zones in 4 groups (V1RR1, V1RR2, V2RR1, V2RR2), mono, 24-bit / 44.1 kHz, 7.6 MB
- **Key map:**

  | Key | MIDI | Piece | Bus |
  |---|---|---|---|
  | C1 | 36 | Kick | Kick |
  | C#1 | 37 | Rim | Snare |
  | D1 | 38 | Gated Snare | Snare |
  | D#1 | 39 | Gated Clap | Snare |
  | E1 | 40 | Snare 2 | Snare |
  | F1 | 41 | Tom 1 | Toms |
  | G1 | 43 | Tom 2 | Toms |
  | A1 | 45 | Tom 3 | Toms |
  | B1 | 47 | Tom 4 | Toms |
  | C2 | 48 | Tom 5 | Toms |
  | F#1 | 42 | Closed Hat | Hats |
  | G#1 | 44 | Pedal Hat | Hats |
  | A#1 | 46 | Open Hat (choked by closed/pedal hat) | Hats |
  | C#2 | 49 | Crash | Cymbals |
  | D#2 | 51 | Ride | Cymbals |
  | F#2 | 54 | Tambourine | Perc |
  | G#2 | 56 | Cowbell | Perc |

- **Effects chain (built by the script):** Filter > Bus Compressor > Supercharger GT > Stereo Modeller > Raum Reverb
- **Presets:** Default, Studio Dry, Big Room, Crushed
- **Other formats:** SFZ: `Synthwave Kit.sfz`; Decent Sampler: `Synthwave Kit.dspreset` (in `SFZ/03 Band and Keys` and `Decent Sampler/03 Band and Keys`)
- **Tip:** 80s gated snares and big synth toms

### Trap Kit

Modern trap kit: long 808, snares, claps, hats with Note Repeat rolls, percs and vox.

- **File:** `Instruments/03 Band and Keys/Trap Kit.nki` (build with `Creator Tools/Build Trap Kit.lua`)
- **Engine:** Drum engine - one piece per key, velocity layers, round robins, choke groups, per-bus mixer.
- **Samples:** 56 zones in 4 groups (V1RR1, V1RR2, V2RR1, V2RR2), mono, 24-bit / 44.1 kHz, 5.7 MB
- **Key map:**

  | Key | MIDI | Piece | Bus |
  |---|---|---|---|
  | C1 | 36 | 808 Kick | Kick |
  | B0 | 35 | Punch Kick | Kick |
  | D1 | 38 | Trap Snare | Snare |
  | D#1 | 39 | Clap | Snare |
  | E1 | 40 | Snare + Clap | Snare |
  | C#1 | 37 | Rim | Snare |
  | F#1 | 42 | Hat | Hats |
  | G#1 | 44 | Hat Tight | Hats |
  | A#1 | 46 | Open Hat (choked by closed/pedal hat) | Hats |
  | C#2 | 49 | Crash | Perc |
  | D#2 | 51 | Perc Bell | Perc |
  | E2 | 52 | Snap | Perc |
  | F2 | 53 | Shaker | Perc |
  | G2 | 55 | Vox Chop | Perc |

- **Effects chain (built by the script):** Filter > Bus Compressor > Supercharger GT > Stereo Modeller > Raum Reverb
- **Presets:** Default, Studio Dry, Big Room, Crushed, Hat Rolls 1/32
- **Other formats:** SFZ: `Trap Kit.sfz`; Decent Sampler: `Trap Kit.dspreset` (in `SFZ/03 Band and Keys` and `Decent Sampler/03 Band and Keys`)
- **Tip:** Note Repeat (PLAY page) for hi-hat rolls

### Cinematic Mallets

Modal-synthesis marimba, vibraphone, celesta and glockenspiel.

- **File:** `Instruments/03 Band and Keys/Cinematic Mallets.nki` (build with `Creator Tools/Build Cinematic Mallets.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** A0 - E7 (MIDI 33-112)
- **Samples:** 34 zones in 4 groups (Marimba, Vibes, Celesta, Glock), mono, 24-bit / 44.1 kHz, 8.6 MB
- **Instruments (menu + layer):** Marimba, Vibraphone, Celesta, Glockenspiel
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Studio, Ambient Wash, Strummed Chords, Celesta + Glock
- **Other formats:** SFZ: `Cinematic Mallets - Celesta.sfz`, `Cinematic Mallets - Glockenspiel.sfz`, `Cinematic Mallets - Marimba.sfz`, `Cinematic Mallets - Vibraphone.sfz`; Decent Sampler: `Cinematic Mallets - Celesta.dspreset`, `Cinematic Mallets - Glockenspiel.dspreset`, `Cinematic Mallets - Marimba.dspreset`, `Cinematic Mallets - Vibraphone.dspreset` (in `SFZ/03 Band and Keys` and `Decent Sampler/03 Band and Keys`)
- **Tip:** Pick an instrument, layer a second one on top

## 04 Cinematic

### Braams and Hits

Trailer braams: brass-like saw walls and a ring-modulated, folded 'Blaster'.

- **File:** `Instruments/04 Cinematic/Braams and Hits.nki` (build with `Creator Tools/Build Braams and Hits.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** A-1 - C3 (MIDI 21-60)
- **Samples:** 10 zones in 2 groups (Braam, Blaster), stereo, 24-bit / 44.1 kHz, 11.6 MB
- **Instruments (menu + layer):** Braam, Blaster
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Studio, Ambient Wash, Strummed Chords, Inception Stack
- **Other formats:** SFZ: `Braams and Hits - Blaster.sfz`, `Braams and Hits - Braam.sfz`; Decent Sampler: `Braams and Hits - Blaster.dspreset`, `Braams and Hits - Braam.dspreset` (in `SFZ/04 Cinematic` and `Decent Sampler/04 Cinematic`)
- **Tip:** Low keys = biggest braams. Layer Braam + Blaster

### Drones and Textures

Eight evolving underscore beds: strings, air, choir, metal, rumble, ghost, tension, heartbeat.

- **File:** `Instruments/04 Cinematic/Drones and Textures.nki` (build with `Creator Tools/Build Drones and Textures.lua`)
- **Engine:** Synth engine - two blendable layers, attack/release, filter with tempo-synced Movement, octave layering, mono/glide.
- **Playable range:** C0 - C6 (MIDI 24-96)
- **Samples:** 8 zones in 8 groups (DarkStrings, GlassAir, ChoirDrone, MetalShimmer, SubRumble, GhostPad, TensionCluster, Heartbeat), stereo, 24-bit / 44.1 kHz, 9.9 MB
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Lush and Wide, Dark and Close, Epic Octaves, Tempo Pulse
- **Other formats:** SFZ: `Drones and Textures - ChoirDrone.sfz`, `Drones and Textures - DarkStrings.sfz`, `Drones and Textures - GhostPad.sfz`, `Drones and Textures - GlassAir.sfz`, `Drones and Textures - Heartbeat.sfz`, `Drones and Textures - MetalShimmer.sfz`, `Drones and Textures - SubRumble.sfz`, `Drones and Textures - TensionCluster.sfz`, `Drones and Textures.sfz`; Decent Sampler: `Drones and Textures - ChoirDrone.dspreset`, `Drones and Textures - DarkStrings.dspreset`, `Drones and Textures - GhostPad.dspreset`, `Drones and Textures - GlassAir.dspreset`, `Drones and Textures - Heartbeat.dspreset`, `Drones and Textures - MetalShimmer.dspreset`, `Drones and Textures - SubRumble.dspreset`, `Drones and Textures - TensionCluster.dspreset` (in `SFZ/04 Cinematic` and `Decent Sampler/04 Cinematic`)
- **Tip:** Pick two textures and blend them

### Dark Atmospheres

Eight dark beds: abyss, wind, bowed metal, haunted choir, machine hum, deep space, pulse, shimmer.

- **File:** `Instruments/04 Cinematic/Dark Atmospheres.nki` (build with `Creator Tools/Build Dark Atmospheres.lua`)
- **Engine:** Synth engine - two blendable layers, attack/release, filter with tempo-synced Movement, octave layering, mono/glide.
- **Playable range:** C0 - C6 (MIDI 24-96)
- **Samples:** 8 zones in 8 groups (Abyss, Wind, BowedMetal, HauntedChoir, MachineHum, DeepSpace, Pulse, Shimmer), stereo, 24-bit / 44.1 kHz, 10.0 MB
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Lush and Wide, Dark and Close, Epic Octaves, Tempo Pulse
- **Other formats:** SFZ: `Dark Atmospheres - Abyss.sfz`, `Dark Atmospheres - BowedMetal.sfz`, `Dark Atmospheres - DeepSpace.sfz`, `Dark Atmospheres - HauntedChoir.sfz`, `Dark Atmospheres - MachineHum.sfz`, `Dark Atmospheres - Pulse.sfz`, `Dark Atmospheres - Shimmer.sfz`, `Dark Atmospheres - Wind.sfz`, `Dark Atmospheres.sfz`; Decent Sampler: `Dark Atmospheres - Abyss.dspreset`, `Dark Atmospheres - BowedMetal.dspreset`, `Dark Atmospheres - DeepSpace.dspreset`, `Dark Atmospheres - HauntedChoir.dspreset`, `Dark Atmospheres - MachineHum.dspreset`, `Dark Atmospheres - Pulse.dspreset`, `Dark Atmospheres - Shimmer.dspreset`, `Dark Atmospheres - Wind.dspreset` (in `SFZ/04 Cinematic` and `Decent Sampler/04 Cinematic`)
- **Tip:** Horror and thriller beds. Blend any two

### Reverse Swells

Chromatic reversed piano, strings and pad swells for transitions.

- **File:** `Instruments/04 Cinematic/Reverse Swells.nki` (build with `Creator Tools/Build Reverse Swells.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** C0 - C6 (MIDI 24-96)
- **Samples:** 15 zones in 3 groups (RevPiano, RevStrings, RevPad), stereo, 24-bit / 44.1 kHz, 10.3 MB
- **Instruments (menu + layer):** Reverse Piano, Reverse Strings, Reverse Pad
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Studio, Ambient Wash, Strummed Chords
- **Other formats:** SFZ: `Reverse Swells - Reverse Pad.sfz`, `Reverse Swells - Reverse Piano.sfz`, `Reverse Swells - Reverse Strings.sfz`; Decent Sampler: `Reverse Swells - Reverse Pad.dspreset`, `Reverse Swells - Reverse Piano.dspreset`, `Reverse Swells - Reverse Strings.dspreset` (in `SFZ/04 Cinematic` and `Decent Sampler/04 Cinematic`)
- **Tip:** Pitched reverse swells: play them just before the beat

### Cinematic FX

Twenty trailer-style one-shots: impacts, risers, whooshes, downers and stingers.

- **File:** `Instruments/04 Cinematic/Cinematic FX.nki` (build with `Creator Tools/Build Cinematic FX.lua`)
- **Engine:** Drum engine - one piece per key, velocity layers, round robins, choke groups, per-bus mixer.
- **Samples:** 20 zones in 1 groups (FX), stereo, 24-bit / 44.1 kHz, 17.3 MB
- **Key map:**

  | Key | MIDI | Piece | Bus |
  |---|---|---|---|
  | C1 | 36 | Boom Impact | Impacts |
  | C#1 | 37 | Sub Drop | Impacts |
  | D1 | 38 | Trailer Hit | Impacts |
  | D#1 | 39 | Metal Impact | Impacts |
  | E1 | 40 | Low Hit | Impacts |
  | F1 | 41 | Glass Hit | Impacts |
  | F#1 | 42 | Noise Riser | Risers |
  | G1 | 43 | Tonal Riser | Risers |
  | G#1 | 44 | Tension Riser | Risers |
  | A1 | 45 | Reverse Cymbal | Risers |
  | A#1 | 46 | Reverse Hit | Risers |
  | B1 | 47 | Whoosh Fast | Whooshes |
  | C2 | 48 | Whoosh Slow | Whooshes |
  | C#2 | 49 | Downer | Downers |
  | D2 | 50 | Power Down | Downers |
  | D#2 | 51 | Braam Stab | Misc |
  | E2 | 52 | Heartbeat | Misc |
  | F2 | 53 | Clock Ticks | Misc |
  | F#2 | 54 | Glitch Stutter | Misc |
  | G2 | 55 | Distant Thunder | Misc |

- **Effects chain (built by the script):** Filter > Stereo Modeller > Replika Delay > Raum Reverb
- **Presets:** Default, Studio Dry, Big Room, Crushed
- **Other formats:** SFZ: `Cinematic FX.sfz`; Decent Sampler: `Cinematic FX.dspreset` (in `SFZ/04 Cinematic` and `Decent Sampler/04 Cinematic`)
- **Tip:** C2-G3: impacts, risers, whooshes, downers, stingers

### Hybrid Trailer Percussion

Hybrid trailer percussion: booms, slams, distorted toms, chains and glitch hits.

- **File:** `Instruments/04 Cinematic/Hybrid Trailer Percussion.nki` (build with `Creator Tools/Build Hybrid Trailer Percussion.lua`)
- **Engine:** Drum engine - one piece per key, velocity layers, round robins, choke groups, per-bus mixer.
- **Samples:** 32 zones in 2 groups (RR1, RR2), mono, 24-bit / 44.1 kHz, 7.9 MB
- **Key map:**

  | Key | MIDI | Piece | Bus |
  |---|---|---|---|
  | C1 | 36 | Epic Boom | Booms |
  | C#1 | 37 | Distorted Kick | Booms |
  | D1 | 38 | Hybrid Hit | Hits |
  | D#1 | 39 | Metal Slam | Metal |
  | E1 | 40 | Taiko Stack | Hits |
  | F1 | 41 | Dist Tom Low | Toms |
  | G1 | 43 | Dist Tom Mid | Toms |
  | A1 | 45 | Dist Tom High | Toms |
  | F#1 | 42 | Clap Stack | Hits |
  | G#1 | 44 | Snap Snare | Hits |
  | A#1 | 46 | Chain Slam | Metal |
  | B1 | 47 | Sub Hit | Booms |
  | C2 | 48 | Gong Hit | Metal |
  | C#2 | 49 | Whip Crack | Hits |
  | D2 | 50 | Glitch Hit | Hits |
  | D#2 | 51 | Rumble Hit | Booms |

- **Effects chain (built by the script):** Filter > Bus Compressor > Supercharger GT > Stereo Modeller > Raum Reverb
- **Presets:** Default, Studio Dry, Big Room, Crushed
- **Other formats:** SFZ: `Hybrid Trailer Percussion.sfz`; Decent Sampler: `Hybrid Trailer Percussion.dspreset` (in `SFZ/04 Cinematic` and `Decent Sampler/04 Cinematic`)
- **Tip:** Distorted booms, slams and toms. Try Note Repeat

### Sci-Fi FX

Eighteen sci-fi effects: lasers, alarms, robots, data, teleports, ships and warps.

- **File:** `Instruments/04 Cinematic/Sci-Fi FX.nki` (build with `Creator Tools/Build Sci-Fi FX.lua`)
- **Engine:** Drum engine - one piece per key, velocity layers, round robins, choke groups, per-bus mixer.
- **Samples:** 18 zones in 1 groups (FX), stereo, 24-bit / 44.1 kHz, 10.1 MB
- **Key map:**

  | Key | MIDI | Piece | Bus |
  |---|---|---|---|
  | C1 | 36 | Laser Zap | SciFi |
  | C#1 | 37 | Laser Burst | SciFi |
  | D1 | 38 | Phaser Blast | SciFi |
  | D#1 | 39 | Alarm | SciFi |
  | E1 | 40 | Robot Beeps | SciFi |
  | F1 | 41 | Data Stream | SciFi |
  | F#1 | 42 | Teleport | SciFi |
  | G1 | 43 | Power Up | SciFi |
  | G#1 | 44 | Shutdown | SciFi |
  | A1 | 45 | Force Field | SciFi |
  | A#1 | 46 | Servo | SciFi |
  | B1 | 47 | Ship Pass | SciFi |
  | C2 | 48 | Sonar Ping | SciFi |
  | C#2 | 49 | Radio Static | SciFi |
  | D2 | 50 | Energy Charge | SciFi |
  | D#2 | 51 | Zap Hit | SciFi |
  | E2 | 52 | Alien Voice | SciFi |
  | F2 | 53 | Warp | SciFi |

- **Effects chain (built by the script):** Filter > Stereo Modeller > Replika Delay > Raum Reverb
- **Presets:** Default, Studio Dry, Big Room, Crushed
- **Other formats:** SFZ: `Sci-Fi FX.sfz`; Decent Sampler: `Sci-Fi FX.dspreset` (in `SFZ/04 Cinematic` and `Decent Sampler/04 Cinematic`)
- **Tip:** C2 upwards: lasers, alarms, robots, teleports, ships

### Tension Toolkit

Suspense tools: clock, heartbeat and pulse loops, scrapes, clusters, stingers, breaths.

- **File:** `Instruments/04 Cinematic/Tension Toolkit.nki` (build with `Creator Tools/Build Tension Toolkit.lua`)
- **Engine:** Drum engine - one piece per key, velocity layers, round robins, choke groups, per-bus mixer.
- **Samples:** 12 zones in 1 groups (FX), stereo, 24-bit / 44.1 kHz, 8.3 MB
- **Key map:**

  | Key | MIDI | Piece | Bus |
  |---|---|---|---|
  | C1 | 36 | Clock Loop (hold = roll) | Loops |
  | C#1 | 37 | Heartbeat Loop (hold = roll) | Loops |
  | D1 | 38 | Sub Pulse Loop (hold = roll) | Loops |
  | D#1 | 39 | Ticking Bomb (hold = roll) | Loops |
  | E1 | 40 | String Scrape | Hits |
  | F1 | 41 | Col Legno | Hits |
  | F#1 | 42 | Bowed Cymbal | Textures |
  | G1 | 43 | Piano Cluster | Hits |
  | G#1 | 44 | Stinger High | Hits |
  | A1 | 45 | Stinger Low | Hits |
  | A#1 | 46 | Breath | Textures |
  | B1 | 47 | Metal Creak | Textures |

- **Effects chain (built by the script):** Filter > Stereo Modeller > Replika Delay > Raum Reverb
- **Presets:** Default, Studio Dry, Big Room, Crushed
- **Other formats:** SFZ: `Tension Toolkit.sfz`; Decent Sampler: `Tension Toolkit.dspreset` (in `SFZ/04 Cinematic` and `Decent Sampler/04 Cinematic`)
- **Tip:** C2-D#2 are loops: hold the key

## 05 World

### Hang Drum

Hand-played steel hang drum with soft, singing overtones.

- **File:** `Instruments/05 World/Hang Drum.nki` (build with `Creator Tools/Build Hang Drum.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** A1 - G#5 (MIDI 45-92)
- **Samples:** 14 zones in 2 groups (RR1, RR2), mono, 24-bit / 44.1 kHz, 5.6 MB
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Studio, Ambient Wash, Strummed Chords, Pentatonic Arp
- **Other formats:** SFZ: `Hang Drum.sfz`; Decent Sampler: `Hang Drum.dspreset` (in `SFZ/05 World` and `Decent Sampler/05 World`)
- **Tip:** 2 round robins, rings out naturally

### Steel Pan

Caribbean steel pan, bright and percussive.

- **File:** `Instruments/05 World/Steel Pan.nki` (build with `Creator Tools/Build Steel Pan.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** D2 - C6 (MIDI 50-96)
- **Samples:** 14 zones in 2 groups (RR1, RR2), mono, 24-bit / 44.1 kHz, 2.9 MB
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Studio, Ambient Wash, Strummed Chords, Pentatonic Arp
- **Other formats:** SFZ: `Steel Pan.sfz`; Decent Sampler: `Steel Pan.dspreset` (in `SFZ/05 World` and `Decent Sampler/05 World`)
- **Tip:** 2 round robins, rings out naturally

### Kalimba

Thumb piano tines on a wooden resonator box.

- **File:** `Instruments/05 World/Kalimba.nki` (build with `Creator Tools/Build Kalimba.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** D2 - C6 (MIDI 50-96)
- **Samples:** 14 zones in 2 groups (RR1, RR2), mono, 24-bit / 44.1 kHz, 3.6 MB
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Studio, Ambient Wash, Strummed Chords, Pentatonic Arp
- **Other formats:** SFZ: `Kalimba.sfz`; Decent Sampler: `Kalimba.dspreset` (in `SFZ/05 World` and `Decent Sampler/05 World`)
- **Tip:** 2 round robins, rings out naturally

### Gamelan Bells

Balinese-style metallophone with shimmering beating pairs.

- **File:** `Instruments/05 World/Gamelan Bells.nki` (build with `Creator Tools/Build Gamelan Bells.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** G1 - E6 (MIDI 43-100)
- **Samples:** 18 zones in 2 groups (RR1, RR2), stereo, 24-bit / 44.1 kHz, 13.8 MB
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Studio, Ambient Wash, Strummed Chords, Pentatonic Arp
- **Other formats:** SFZ: `Gamelan Bells.sfz`; Decent Sampler: `Gamelan Bells.dspreset` (in `SFZ/05 World` and `Decent Sampler/05 World`)
- **Tip:** 2 round robins, rings out naturally

### Sitar and Tanpura

Sitar with buzzing jawari bridge and sympathetic strings, plus a looping tanpura drone.

- **File:** `Instruments/05 World/Sitar and Tanpura.nki` (build with `Creator Tools/Build Sitar and Tanpura.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** C0 - C6 (MIDI 24-96)
- **Samples:** 15 zones in 3 groups (RR1, RR2, Tanpura), mono, 24-bit / 44.1 kHz, 5.3 MB
- **Instruments (menu + layer):** Sitar, Tanpura Drone
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Studio, Ambient Wash, Strummed Chords, Raga Drone
- **Other formats:** SFZ: `Sitar and Tanpura - Sitar.sfz`, `Sitar and Tanpura - Tanpura Drone.sfz`; Decent Sampler: `Sitar and Tanpura - Sitar.dspreset`, `Sitar and Tanpura - Tanpura Drone.dspreset` (in `SFZ/05 World` and `Decent Sampler/05 World`)
- **Tip:** Layer the Tanpura drone under the sitar

### Duduk

Mournful double-reed flute in the duduk style, with legato slides.

- **File:** `Instruments/05 World/Duduk.nki` (build with `Creator Tools/Build Duduk.lua`)
- **Engine:** Articulation engine - keyswitches, mod-wheel dynamics crossfade, legato with portamento, round-robin shorts.
- **Playable range:** C2 - A5 (MIDI 48-93)
- **Samples:** 21 zones in 3 groups (Sus, StacRR1, StacRR2), mono, 24-bit / 44.1 kHz, 3.1 MB
- **Articulations / keyswitches:**
  - `C0` **Sustain** - sustain, CC1 dynamics (Sus)
  - `C#0` **Staccato** - short, round robin, velocity (StacRR1 / StacRR2)
  - `D0` **Swell** - auto-swell, CC1 dynamics (Sus)
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Presets:** Default, Epic Legato, Soft Underscore, Ostinato 1/16, Desert Lament
- **Other formats:** SFZ: `Duduk.sfz`; Decent Sampler: `Duduk - Staccato.dspreset`, `Duduk - Sustain.dspreset`, `Duduk - Swell.dspreset` (in `SFZ/05 World` and `Decent Sampler/05 World`)
- **Tip:** Mournful double-reed lead, legato on

## Performer (PERFORM page, all melodic instruments)

- **Scale Lock:** Off (chromatic), Major, Natural Minor, Harmonic Minor, Melodic Minor, Dorian, Phrygian, Lydian, Mixolydian, Locrian, Major Pentatonic, Minor Pentatonic, Blues, Hungarian Minor, Phrygian Dominant, Whole Tone
- **Chord:** Off, Octave, Power (1-5-8), Major, Minor, Sus2, Sus4, Major 7, Minor 7, Add9, Minor Add9, Stacked Fifths, Epic Minor, Diminished, Augmented, Diatonic Triad, Diatonic 7th
- **Arpeggiator:** Up, Down, Up-Down, Random, As Played, Chord Repeat; rates 1/4, 1/8, 1/8 T, 1/16, 1/16 T, 1/32; 1-4 octaves, gate, swing, latch, accent
- **Strum** (0-150 ms) and **Humanize** (timing and velocity)
