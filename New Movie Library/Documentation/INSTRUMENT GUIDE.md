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
- **Tip:** Mod wheel opens the filter, Blend mixes Warm and Air

### Glass Shimmer Pad

FM glass bells with an octave shimmer, chorus and a long hall.

- **File:** `Instruments/01 Synths and Pads/Glass Shimmer Pad.nki` (build with `Creator Tools/Build Glass Shimmer Pad.lua`)
- **Engine:** Synth engine - two blendable layers, attack/release, filter with tempo-synced Movement, octave layering, mono/glide.
- **Playable range:** C0 - C7 (MIDI 24-108)
- **Samples:** 11 zones in 1 groups (Glass), stereo, 24-bit / 44.1 kHz, 7.5 MB
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Tip:** FM bell attack into a shimmering sustain

### Supersaw Stack

Seven detuned saws, trance/trailer style. Poly, or mono with glide.

- **File:** `Instruments/01 Synths and Pads/Supersaw Stack.nki` (build with `Creator Tools/Build Supersaw Stack.lua`)
- **Engine:** Synth engine - two blendable layers, attack/release, filter with tempo-synced Movement, octave layering, mono/glide.
- **Playable range:** C0 - C7 (MIDI 24-108)
- **Samples:** 11 zones in 1 groups (Saw), stereo, 24-bit / 44.1 kHz, 4.9 MB
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Tip:** Mono / Glide for leads, Octave Layer for anthems

### Analog Mono Bass

Pure sub and a resonant, driven growl layer. Mono legato with glide.

- **File:** `Instruments/01 Synths and Pads/Analog Mono Bass.nki` (build with `Creator Tools/Build Analog Mono Bass.lua`)
- **Engine:** Synth engine - two blendable layers, attack/release, filter with tempo-synced Movement, octave layering, mono/glide.
- **Playable range:** C-1 - C4 (MIDI 12-72)
- **Samples:** 14 zones in 2 groups (Sub, Growl), mono, 24-bit / 44.1 kHz, 2.7 MB
- **Effects chain (built by the script):** Filter > Supercharger GT > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Tip:** Blend: clean sub to growl. Mono/Glide on by default

### Pluck Synth

Snappy filter-envelope pluck with round robins.

- **File:** `Instruments/01 Synths and Pads/Pluck Synth.nki` (build with `Creator Tools/Build Pluck Synth.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** C0 - C7 (MIDI 24-108)
- **Samples:** 22 zones in 2 groups (RR1, RR2), stereo, 24-bit / 44.1 kHz, 7.0 MB
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Tip:** Try PERFORM > Arpeggiator

### Pulse Arp

The Pluck Synth preset as a ready-to-go tempo-synced arpeggiator.

- **File:** `Instruments/01 Synths and Pads/Pulse Arp.nki` (build with `Creator Tools/Build Pulse Arp.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** C0 - C7 (MIDI 24-108)
- **Samples:** 22 zones in 2 groups (RR1, RR2), stereo, 24-bit / 44.1 kHz, 7.0 MB (shared with Pluck)
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Tip:** Hold a chord: 1/16 arpeggio synced to tempo

### Ethereal Choir

Formant-synthesised mixed choir, Aah and Ooh vowels, morphable.

- **File:** `Instruments/01 Synths and Pads/Ethereal Choir.nki` (build with `Creator Tools/Build Ethereal Choir.lua`)
- **Engine:** Synth engine - two blendable layers, attack/release, filter with tempo-synced Movement, octave layering, mono/glide.
- **Playable range:** A0 - C6 (MIDI 33-96)
- **Samples:** 18 zones in 2 groups (Aah, Ooh), stereo, 24-bit / 44.1 kHz, 12.1 MB
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Tip:** Blend morphs the vowel from Aah to Ooh

## 02 Orchestral and Band

### Ensemble Strings

Eight-player bowed ensemble: sustain (2 dynamics), tremolo, staccato, pizzicato, swell.

- **File:** `Instruments/02 Orchestral and Band/Ensemble Strings.nki` (build with `Creator Tools/Build Ensemble Strings.lua`)
- **Engine:** Articulation engine - keyswitches, mod-wheel dynamics crossfade, legato with portamento, round-robin shorts.
- **Playable range:** G0 - G6 (MIDI 31-103)
- **Samples:** 84 zones in 7 groups (SusP, SusF, Trem, StacRR1, StacRR2, PizzRR1, PizzRR2), stereo, 24-bit / 44.1 kHz, 30.7 MB
- **Articulations / keyswitches:**
  - `C0` **Sustain** - sustain, CC1 dynamics (SusP / SusF)
  - `C#0` **Tremolo** - sustain, CC1 dynamics (Trem)
  - `D0` **Staccato** - short, round robin, velocity (StacRR1 / StacRR2)
  - `D#0` **Pizzicato** - short, round robin, velocity (PizzRR1 / PizzRR2)
  - `E0` **Swell** - auto-swell, CC1 dynamics (SusP / SusF)
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Tip:** CC1 = dynamics, keyswitches C0-E0

### Brass Ensemble

Horn/trombone section with loudness-driven brightness, swells and shorts.

- **File:** `Instruments/02 Orchestral and Band/Brass Ensemble.nki` (build with `Creator Tools/Build Brass Ensemble.lua`)
- **Engine:** Articulation engine - keyswitches, mod-wheel dynamics crossfade, legato with portamento, round-robin shorts.
- **Playable range:** F0 - F#5 (MIDI 29-90)
- **Samples:** 36 zones in 4 groups (SusP, SusF, StacRR1, StacRR2), stereo, 24-bit / 44.1 kHz, 13.1 MB
- **Articulations / keyswitches:**
  - `C0` **Sustain** - sustain, CC1 dynamics (SusP / SusF)
  - `C#0` **Swell** - auto-swell, CC1 dynamics (SusP / SusF)
  - `D0` **Staccato** - short, round robin, velocity (StacRR1 / StacRR2)
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Tip:** CC1 = dynamics (soft to blaring), keyswitches C0-D0

### Woodwind Ensemble

Breathy flute pair, clarinet pair and a woodwind staccato.

- **File:** `Instruments/02 Orchestral and Band/Woodwind Ensemble.nki` (build with `Creator Tools/Build Woodwind Ensemble.lua`)
- **Engine:** Articulation engine - keyswitches, mod-wheel dynamics crossfade, legato with portamento, round-robin shorts.
- **Playable range:** E1 - E6 (MIDI 40-100)
- **Samples:** 36 zones in 4 groups (Flute, Clarinet, StacRR1, StacRR2), mono, 24-bit / 44.1 kHz, 6.4 MB
- **Articulations / keyswitches:**
  - `C0` **Flute Sustain** - sustain, CC1 dynamics (Flute)
  - `C#0` **Clarinet Sustain** - sustain, CC1 dynamics (Clarinet)
  - `D0` **Staccato** - short, round robin, velocity (StacRR1 / StacRR2)
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Tip:** Flutes, clarinets and staccato, keyswitches C0-D0

### Cinematic Timpani

Pitched timpani hits with round robins and looped rolls with crescendo control.

- **File:** `Instruments/02 Orchestral and Band/Cinematic Timpani.nki` (build with `Creator Tools/Build Cinematic Timpani.lua`)
- **Engine:** Articulation engine - keyswitches, mod-wheel dynamics crossfade, legato with portamento, round-robin shorts.
- **Playable range:** C1 - A2 (MIDI 36-57)
- **Samples:** 16 zones in 4 groups (HitRR1, HitRR2, RollP, RollF), mono, 24-bit / 44.1 kHz, 5.2 MB
- **Articulations / keyswitches:**
  - `C0` **Hits** - short, round robin, velocity (HitRR1 / HitRR2)
  - `C#0` **Roll** - sustain, CC1 dynamics (RollP / RollF)
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Tip:** C0 hits, C#0 rolls (CC1 = roll dynamics)

### Electric Piano

FM tine electric piano with velocity-dependent bark, tremolo preamp.

- **File:** `Instruments/02 Orchestral and Band/Electric Piano.nki` (build with `Creator Tools/Build Electric Piano.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** A-1 - C7 (MIDI 21-108)
- **Samples:** 39 zones in 3 groups (V1, V2, V3), mono, 24-bit / 44.1 kHz, 13.2 MB
- **Tine EP velocity layers:** 3 (splits at velocity 52, 98), 1 round robin(s) each
- **Effects chain (built by the script):** Filter > EP Preamp > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Tip:** 3 velocity layers, tremolo and drive on the SOUND page

### Nylon Guitar

Physically modelled nylon-string guitar with body resonance, 2 layers x 2 round robins.

- **File:** `Instruments/02 Orchestral and Band/Nylon Guitar.nki` (build with `Creator Tools/Build Nylon Guitar.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** D1 - C5 (MIDI 38-84)
- **Samples:** 28 zones in 4 groups (V1RR1, V1RR2, V2RR1, V2RR2), mono, 24-bit / 44.1 kHz, 8.9 MB
- **Nylon velocity layers:** 2 (splits at velocity 88), 2 round robin(s) each
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Tip:** Use PERFORM > Chord + Strum for strummed chords

### Finger Bass

Fingered electric bass model with pickup comb filtering and thump.

- **File:** `Instruments/02 Orchestral and Band/Finger Bass.nki` (build with `Creator Tools/Build Finger Bass.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** B-1 - E3 (MIDI 23-64)
- **Samples:** 24 zones in 4 groups (V1RR1, V1RR2, V2RR1, V2RR2), mono, 24-bit / 44.1 kHz, 6.2 MB
- **Finger velocity layers:** 2 (splits at velocity 90), 2 round robin(s) each
- **Effects chain (built by the script):** Filter > Supercharger GT > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Tip:** 2 velocity layers x 2 round robins

### Studio Drum Kit

Synthesised acoustic/hybrid kit: 20 pieces, 2 velocity layers x 2 round robins.

- **File:** `Instruments/02 Orchestral and Band/Studio Drum Kit.nki` (build with `Creator Tools/Build Studio Drum Kit.lua`)
- **Engine:** Drum engine - one piece per key, velocity layers, round robins, choke groups, per-bus mixer.
- **Samples:** 80 zones in 4 groups (V1RR1, V1RR2, V2RR1, V2RR2), mono, 24-bit / 44.1 kHz, 12.5 MB
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
- **Tip:** General MIDI layout, open hat choked by closed/pedal hat

### Drawbar Organ

Tonewheel-style additive organ with key click, rotary speaker and drive.

- **File:** `Instruments/02 Orchestral and Band/Drawbar Organ.nki` (build with `Creator Tools/Build Drawbar Organ.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** C0 - C7 (MIDI 24-108)
- **Samples:** 22 zones in 2 groups (Full, Soft), mono, 24-bit / 44.1 kHz, 4.6 MB
- **Instruments (menu + layer):** Full Drawbars, Soft Flutes
- **Effects chain (built by the script):** Filter > Rotator > Supercharger GT > Replika Delay > Raum Reverb
- **Tip:** Mod wheel up = fast rotary

### Cinematic Mallets

Modal-synthesis marimba, vibraphone, celesta and glockenspiel.

- **File:** `Instruments/02 Orchestral and Band/Cinematic Mallets.nki` (build with `Creator Tools/Build Cinematic Mallets.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** A0 - E7 (MIDI 33-112)
- **Samples:** 34 zones in 4 groups (Marimba, Vibes, Celesta, Glock), mono, 24-bit / 44.1 kHz, 8.6 MB
- **Instruments (menu + layer):** Marimba, Vibraphone, Celesta, Glockenspiel
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Tip:** Pick an instrument, layer a second one on top

### Orchestral Percussion

Gran cassa, taiko, snare, cymbals, tam-tam and metals with round robins and rolls.

- **File:** `Instruments/02 Orchestral and Band/Orchestral Percussion.nki` (build with `Creator Tools/Build Orchestral Percussion.lua`)
- **Engine:** Drum engine - one piece per key, velocity layers, round robins, choke groups, per-bus mixer.
- **Samples:** 32 zones in 2 groups (RR1, RR2), mono, 24-bit / 44.1 kHz, 10.3 MB
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
- **Tip:** Hold C#2 / G2 for rolls, CC1 = roll level

## 03 Cinematic

### Braams and Hits

Trailer braams: brass-like saw walls and a ring-modulated, folded 'Blaster'.

- **File:** `Instruments/03 Cinematic/Braams and Hits.nki` (build with `Creator Tools/Build Braams and Hits.lua`)
- **Engine:** Keys engine - velocity layers, round robins, velocity curve, sustain pedal, layering.
- **Playable range:** A-1 - C3 (MIDI 21-60)
- **Samples:** 10 zones in 2 groups (Braam, Blaster), stereo, 24-bit / 44.1 kHz, 11.6 MB
- **Instruments (menu + layer):** Braam, Blaster
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Tip:** Low keys = biggest braams. Layer Braam + Blaster

### Drones and Textures

Eight evolving underscore beds: strings, air, choir, metal, rumble, ghost, tension, heartbeat.

- **File:** `Instruments/03 Cinematic/Drones and Textures.nki` (build with `Creator Tools/Build Drones and Textures.lua`)
- **Engine:** Synth engine - two blendable layers, attack/release, filter with tempo-synced Movement, octave layering, mono/glide.
- **Playable range:** C0 - C6 (MIDI 24-96)
- **Samples:** 8 zones in 8 groups (DarkStrings, GlassAir, ChoirDrone, MetalShimmer, SubRumble, GhostPad, TensionCluster, Heartbeat), stereo, 24-bit / 44.1 kHz, 9.9 MB
- **Effects chain (built by the script):** Filter > Stereo Modeller > Choral > Replika Delay > Raum Reverb
- **Tip:** Pick two textures and blend them

### Cinematic FX

Twenty trailer-style one-shots: impacts, risers, whooshes, downers and stingers.

- **File:** `Instruments/03 Cinematic/Cinematic FX.nki` (build with `Creator Tools/Build Cinematic FX.lua`)
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
- **Tip:** C2-G3: impacts, risers, whooshes, downers, stingers

## Performer (PERFORM page, all melodic instruments)

- **Scale Lock:** Off (chromatic), Major, Natural Minor, Harmonic Minor, Melodic Minor, Dorian, Phrygian, Lydian, Mixolydian, Locrian, Major Pentatonic, Minor Pentatonic, Blues, Hungarian Minor, Phrygian Dominant, Whole Tone
- **Chord:** Off, Octave, Power (1-5-8), Major, Minor, Sus2, Sus4, Major 7, Minor 7, Add9, Minor Add9, Stacked Fifths, Epic Minor, Diminished, Augmented, Diatonic Triad, Diatonic 7th
- **Arpeggiator:** Up, Down, Up-Down, Random, As Played, Chord Repeat; rates 1/4, 1/8, 1/8 T, 1/16, 1/16 T, 1/32; 1-4 octaves, gate, swing, latch, accent
- **Strum** (0-150 ms) and **Humanize** (timing and velocity)
