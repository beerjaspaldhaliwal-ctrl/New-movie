# New Movie Library: Controls

Every instrument has the same three pages. The tabs are at the top left; the
line next to them shows a tip for the loaded instrument, and the **Preset** menu
is at the top right. Hover over any control to see its help text in Kontakt's
info pane.

The [player plugin](../../Plugin/README.md) has exactly the same controls, with the
same names, ranges and defaults, so everything below applies to it too.

## PLAY

### Synth engine (pads, choir, supersaw, brass synth, mono bass, 808, drones, atmospheres)

| Control | What it does |
|---|---|
| Layer A / Layer B | Pick the two sound layers. Layer B can be *Off*. |
| Blend A/B | Constant-power mix between the two layers (in the choir it morphs the vowel). |
| Attack / Release | Fade-in and fade-out time of each note. |
| Velocity | How much velocity changes the volume. |
| Movement + Move Rate | Slow filter sweep, synced to the host tempo (1 beat to 8 bars). Needs *Tone* below 100%. |
| Octave Layer + Oct Level | Adds +1 octave, -1 octave, both, a fifth, or octave + fifth on every note. |
| Mono / Glide + Glide | Monophonic legato with portamento, for leads and bass. Bypasses chords and arp. |
| Mod > Tone | How far the mod wheel (CC1) opens the filter. |

### Articulation engine (strings, solo violin and cello, brass, horns, woodwinds, timpani, duduk)

| Control | What it does |
|---|---|
| Articulation | Current articulation; also switched by the red keyswitches (yellow = active). |
| Dynamics | Mirrors the mod wheel (CC1). Crossfades the soft and loud recorded layers and sets the level. |
| Dyn Source | Mod wheel (default) or Velocity for the sustain dynamics. |
| Dyn Range | Level difference between softest and loudest dynamics. |
| Attack / Release | Extra fade-in and the release time. |
| Swell Time | Fade-in length of the *Swell* articulation. |
| Legato + Leg. Speed + Portamento | Monophonic legato for sustained articulations: overlapping notes crossfade, with an optional slide into the new note. |
| Vel Range / Vel Curve | Velocity response of the short articulations. |
| Close Mic / Hall Mic | (Ensemble Strings, Brass Ensemble) Levels of the close and the distant hall microphones on the sustained articulations. All the way down = that mic is off and uses no voices. Short articulations use the close mics. |

CC11 (expression) scales the overall level on top of the dynamics.

### Keys engine (pianos, EP, guitars, bass, organ, mallets, harp, pluck, tape keys, braams, reverse swells, world instruments)

| Control | What it does |
|---|---|
| Instrument / Layer / Layer Level | Choose the sound and optionally layer a second one (mallets, organ, braams, tape keys, electric guitar, sitar + tanpura). |
| Attack / Release | Fade-in and release time. |
| Vel Range / Vel Curve | Velocity to volume range and curve. Velocity also picks the sample layer. |
| Let Ring | Notes ring out naturally instead of stopping on key release. |
| Re-strike | How fast a ringing note fades when the same key is played again. |
| Wheel = Fast | (Organ) Mod wheel above half switches the rotary speaker to fast. |

### Drum engine (drum kits, orchestral and trailer percussion, cinematic and sci-fi FX, tension toolkit)

| Control | What it does |
|---|---|
| Bus knobs | Level per group of pieces (for example Kick, Snare, Toms, Hats, Cymbals, Perc). |
| Tune | Tunes every piece, ±12 semitones. |
| Vel Range / Vel Curve | Velocity response. Velocity also picks the soft/hard layer. |
| Humanize | Small random level and pitch changes per hit, on top of the round robins. |
| Kit Spread | Stereo placement of the pieces (drummer's perspective). |
| Roll Release / Roll Dyn | Release time and level (also CC1) of held rolls and loops. |
| Note Repeat | Held keys retrigger in time with the host tempo: 1/8, 1/8 T, 1/16, 1/16 T or 1/32. Great for hi-hat rolls and fills. Velocity of the held key is kept. Held rolls and loops are not repeated. |

## SOUND

The script builds this effects chain in the instrument insert slots the first
time it runs. It's saved with the instrument.

| Control | Effect |
|---|---|
| Tone, Resonance | Filter low-pass (100% = open) and resonance (synths). |
| Tremolo, Trem Rate, Drive | EP Preamp (Electric Piano). |
| Rotary Fast, Rotary Mix | Rotator (Organ). |
| Drive | Supercharger GT saturation. |
| Glue Comp | Bus compressor (drums, percussion). |
| Width | Stereo Modeller: 0% mono, 100% as recorded, 200% extra wide. |
| Chorus | Choral, ensemble mode. |
| Delay, Time, Feedback, Delay Sync | Replika delay (tape mode). With Sync on, Time steps through note values. |
| Reverb, Size, Decay | Raum reverb. |
| Sustain Pedal | Follow CC64. |
| PB Range | Pitch-bend range in semitones. |

## PERFORM (melodic instruments)

| Control | What it does |
|---|---|
| Scale Lock + Key | Every note snaps down to the nearest note of the scale. 16 scales including Harmonic Minor, Hungarian Minor and Phrygian Dominant for cinematic colours. |
| Chord | One key plays a chord: octave, power, major, minor, sus, 7ths, add9, stacked fifths, epic minor, diminished, augmented, or **diatonic** triads / 7ths built from the selected scale. |
| Strum | Delay between chord notes (0-150 ms). |
| Hum. Time / Hum. Velo | Random timing and velocity per note. |
| Arpeggiator | Up, Down, Up-Down, Random, As Played, Chord Repeat. |
| Rate | 1/4, 1/8, 1/8 T, 1/16, 1/16 T, 1/32, synced to the host tempo (runs even when the transport is stopped). |
| Octaves, Gate, Swing, Latch, Accent | Octave range, note length, swing feel, hold after release, and a boost on the first step of every beat. |

Chords feed the arpeggiator, and Scale Lock applies to both. For example, Scale
Lock *Natural Minor* + Chord *Diatonic Triad* + Arp *Up 1/16* turns single
notes into in-key arpeggiated chords.

## Presets

The **Preset** menu (top right) recalls complete snapshots of every control:

- **Default** resets the instrument to how it was built.
- **Pads and synths:** Lush and Wide, Dark and Close, Epic Octaves, Tempo Pulse, plus a few specials
  (Supersaw *Mono Lead*, 808 *Distorted Slide*).
- **Orchestral:** Close Mics, Concert Hall (mic mixes), Epic Legato, Soft Underscore, Ostinato 1/16.
- **Keys and world:** Studio, Ambient Wash, Strummed Chords, plus specials such as Harp *Glissando*,
  Felt Piano *Intimate*, Electric Guitar *Power Chords* / *Chugs*, Braams *Inception Stack*,
  world instruments *Pentatonic Arp*, Sitar *Raga Drone*, Duduk *Desert Lament*.
- **Drums and FX:** Studio Dry, Big Room, Crushed, and Trap Kit *Hat Rolls 1/32*.

The [Instrument Guide](INSTRUMENT%20GUIDE.md) lists the presets of every instrument. Picking a preset
changes the controls the same way as moving them by hand, so you can tweak further and save
the result with your project (Kontakt saves it in the instrument or multi).
