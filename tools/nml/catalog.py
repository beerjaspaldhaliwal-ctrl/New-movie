"""The full instrument catalog of the New Movie Library."""
from .library import (Instrument, Zone, keymap, zones_for, add_hall_mics,
                      CAT_SYNTH, CAT_ORCH, CAT_BAND, CAT_CINE, CAT_WORLD)

SYNTH_FX = ["filter", "stereo", "choral", "replika", "raum"]
ACOUSTIC_FX = ["filter", "stereo", "choral", "replika", "raum"]
KIT_FX = ["filter", "comp", "supergt", "stereo", "raum"]


def _roots(lo, hi, step=6):
    return list(range(lo, hi + 1, step))


def _rr_zones(groups, roots, lo, hi, seed, **p):
    zs = zones_for(groups, roots, lo, hi, seed_base=seed, **p)
    for z in zs:
        if "RR" in z.group:
            z.p["rr"] = int(z.group[-1])
    return zs


def _vr(layers, rrs):
    """Group names V1RR1 ... for velocity layers x round robins."""
    return [f"V{v}RR{r}" for v in range(1, layers + 1) for r in range(1, rrs + 1)]


def _vr_layers(layers, rrs):
    return [[f"V{v}RR{r}" for r in range(1, rrs + 1)] for v in range(1, layers + 1)]


def _rrs(prefix, n):
    return [f"{prefix}RR{r}" for r in range(1, n + 1)]


def _kit_zones(pieces, groups, seed, extra=None):
    zs = []
    for gi, g in enumerate(groups):
        for pi, pc in enumerate(pieces):
            key, piece, ln = pc[0], pc[2], pc[3]
            p = dict(piece=piece, len=ln)
            if extra:
                p.update(extra(pc))
            zs.append(Zone(g, key, key, key, seed=seed + gi * 100 + pi, p=p))
    return zs


def _fx_zones(items, group, seed, keyname="fx"):
    return [Zone(group, k, k, k, seed=seed + i, p={keyname: kind, "len": ln}) for i, (k, _, kind, ln, *_) in enumerate(items)]


def _mics(groups):
    return {g: g + "Hall" for g in groups}


# ------------------------------------------------------------------ preset helpers (KSP control units)
def synth_presets(extra=()):
    return [("Lush and Wide", dict(rev_mix=450, chorus=350, width=850, rev_size=850, rev_decay=700)),
            ("Dark and Close", dict(tone=450, rev_mix=150, width=450, chorus=100)),
            ("Epic Octaves", dict(oct_mode=3, oct_lvl=-40, rev_mix=400, width=800)),
            ("Tempo Pulse", dict(arp_mode=1, arp_rate=3, arp_gate=50, dly_mix=300, release=250))] + list(extra)


def artic_presets(staccato_index=None, mics=False, extra=()):
    p = []
    if mics:
        p += [("Close Mics", dict(mic_close=0, mic_hall=-400, rev_mix=200)),
              ("Concert Hall", dict(mic_close=-80, mic_hall=0, rev_mix=150))]
    p += [("Epic Legato", dict(legato=1, porta=35, leg_time=140, rev_mix=350, art_menu=0)),
          ("Soft Underscore", dict(dyn_knob=45, attack=250, release=900, rev_mix=380, art_menu=0))]
    if staccato_index is not None:
        p.append(("Ostinato 1/16", dict(art_menu=staccato_index, arp_mode=1, arp_rate=3, arp_gate=40, legato=0)))
    return p + list(extra)


def keys_presets(extra=()):
    return [("Studio", dict(rev_mix=120, width=450, dly_mix=0)),
            ("Ambient Wash", dict(rev_mix=520, dly_mix=280, release=1500, rev_size=850)),
            ("Strummed Chords", dict(chord=15, strum=35, scale_type=1))] + list(extra)


def drum_presets(extra=()):
    return [("Studio Dry", dict(rev_mix=80, comp=200, drive=100)),
            ("Big Room", dict(rev_mix=420, rev_size=850, rev_decay=650)),
            ("Crushed", dict(drive=700, comp=800, tone=850))] + list(extra)


def build_catalog():
    I = []

    # ================================================================== 01 Synths and Pads
    I.append(Instrument(
        "WarmPad", "Warm Analog Pad", CAT_SYNTH, "synth", "synths.warm_pad",
        zones_for(["Warm", "Air"], _roots(33, 93), 24, 108, seed_base=100),
        cfg=dict(layers=["Warm", "Air"], layer_a=0, layer_b=2, blend=300, attack=650, release=2200, vsens=30,
                 movement=250, range=(24, 108), resonance=True, filter_type="$FILTER_TYPE_LDR_LP4", fx=SYNTH_FX,
                 fx_defaults=dict(tone=820, reso=120, reverb=380, chorus=250, width=600, rev_size=750, rev_decay=650),
                 info="Warm Analog Pad  |  Mod wheel opens the filter, Blend mixes Warm and Air"),
        presets=synth_presets(), blurb="Seven-voice detuned analog stack (Warm) and a breathy, tonal-noise shimmer (Air)."))
    I.append(Instrument(
        "GlassPad", "Glass Shimmer Pad", CAT_SYNTH, "synth", "synths.glass_pad",
        zones_for(["Glass"], _roots(33, 93), 24, 108, seed_base=200),
        cfg=dict(layers=["Glass"], layer_a=0, layer_b=0, attack=250, release=2600, vsens=35, movement=150,
                 range=(24, 108), resonance=True, filter_type="$FILTER_TYPE_LDR_LP4", fx=SYNTH_FX,
                 fx_defaults=dict(tone=950, reverb=420, chorus=200, width=650, delay=120, rev_size=800, rev_decay=700),
                 info="Glass Shimmer Pad  |  FM bell attack into a shimmering sustain"),
        presets=synth_presets(), blurb="FM glass bells with an octave shimmer, chorus and a long hall."))
    I.append(Instrument(
        "WavetablePad", "Wavetable Pad", CAT_SYNTH, "synth", "expansion.wavetable_pad",
        zones_for(["Morph", "Digital"], _roots(33, 93), 24, 108, seed_base=2100),
        cfg=dict(layers=["Morph", "Digital"], layer_a=0, layer_b=2, blend=250, attack=400, release=1800, vsens=30,
                 movement=300, range=(24, 108), resonance=True, filter_type="$FILTER_TYPE_LDR_LP4", fx=SYNTH_FX,
                 fx_defaults=dict(tone=880, reso=150, reverb=380, chorus=200, width=700, rev_size=750),
                 info="Wavetable Pad  |  Morphing additive tables (Morph) and wavefolded Digital layer"),
        presets=synth_presets(), blurb="Slowly morphing wavetable pad plus a wavefolded digital layer."))
    I.append(Instrument(
        "Supersaw", "Supersaw Stack", CAT_SYNTH, "synth", "synths.supersaw",
        zones_for(["Saw"], _roots(33, 93), 24, 108, seed_base=300),
        cfg=dict(layers=["Saw"], layer_a=0, layer_b=0, attack=3, release=380, vsens=40, glide=90, modwheel=600,
                 range=(24, 108), resonance=True, filter_type="$FILTER_TYPE_LDR_LP4", fx=SYNTH_FX,
                 fx_defaults=dict(tone=900, reso=150, reverb=220, delay=180, width=700),
                 info="Supersaw Stack  |  Mono / Glide for leads, Octave Layer for anthems"),
        presets=synth_presets([("Mono Lead", dict(mono=1, glide=120, dly_mix=250, rev_mix=200))]),
        blurb="Seven detuned saws, trance/trailer style. Poly, or mono with glide."))
    I.append(Instrument(
        "SynthBrass", "Analog Brass Synth", CAT_SYNTH, "synth", "expansion.synth_brass",
        zones_for(["Brass"], _roots(33, 93), 24, 108, seed_base=2200),
        cfg=dict(layers=["Brass"], layer_a=0, layer_b=0, attack=5, release=350, vsens=55, modwheel=500,
                 range=(24, 108), resonance=True, filter_type="$FILTER_TYPE_LDR_LP4", fx=SYNTH_FX,
                 fx_defaults=dict(tone=900, reso=100, reverb=250, chorus=200, width=650),
                 info="Analog Brass Synth  |  80s poly brass with a filter-envelope 'bwaa'"),
        presets=synth_presets(), blurb="Classic polysynth brass: detuned saws with a swelling filter envelope."))
    I.append(Instrument(
        "MonoBass", "Analog Mono Bass", CAT_SYNTH, "synth", "synths.mono_bass",
        zones_for(["Sub", "Growl"], _roots(24, 60), 12, 72, seed_base=400), channels=1,
        cfg=dict(layers=["Sub", "Growl"], layer_a=0, layer_b=2, blend=550, attack=2, release=140, vsens=45,
                 mono=1, glide=45, modwheel=700, range=(12, 72), resonance=True, filter_type="$FILTER_TYPE_LDR_LP4",
                 fx=["filter", "supergt", "stereo", "choral", "replika", "raum"],
                 fx_defaults=dict(tone=700, reso=200, drive=250, reverb=0, width=0),
                 info="Analog Mono Bass  |  Blend: clean sub to growl. Mono/Glide on by default"),
        presets=synth_presets(), blurb="Pure sub and a resonant, driven growl layer. Mono legato with glide."))
    I.append(Instrument(
        "Bass808", "808 Bass", CAT_SYNTH, "synth", "expansion.bass_808",
        zones_for(["Clean", "Dist"], _roots(24, 60), 12, 72, seed_base=2300), channels=1, norm="peak",
        cfg=dict(layers=["Clean", "Dist"], layer_a=0, layer_b=0, blend=500, attack=0, release=200, vsens=40,
                 mono=1, glide=70, modwheel=300, range=(12, 72), resonance=False, fx=["filter", "supergt", "stereo", "raum"],
                 fx_defaults=dict(tone=1000, drive=200, reverb=0, width=0),
                 info="808 Bass  |  Mono glide slides like trap 808s. Layer B adds distortion"),
        presets=synth_presets([("Distorted Slide", dict(layer_b=2, blend=600, glide=110, drive=500))]),
        blurb="Long trap 808 with pitch punch; clean and distorted layers, mono slide."))
    I.append(Instrument(
        "TapeKeys", "Tape Keys", CAT_SYNTH, "keys", "expansion.tape_keys",
        zones_for(["TapeFlute", "TapeStrings", "TapeChoir"], _roots(43, 91), 36, 96, seed_base=2400), channels=1,
        cfg=dict(patches=[dict(name="Tape Flute", layers=[["TapeFlute"]], loop=True),
                          dict(name="Tape Strings", layers=[["TapeStrings"]], loop=True),
                          dict(name="Tape Choir", layers=[["TapeChoir"]], loop=True)],
                 range=(36, 96), attack=10, release=400, vrange=12, restrike=30, fx=SYNTH_FX,
                 fx_defaults=dict(tone=1000, reverb=280, chorus=150, width=600),
                 info="Tape Keys  |  Vintage tape-replay flutes, strings and choir with wow and flutter"),
        presets=keys_presets(), blurb="Tape-replay keyboard: flute, strings and choir with wow, flutter and hiss."))
    pluck_zones = _rr_zones(_rrs("", 3), _roots(33, 93), 24, 108, 500)
    I.append(Instrument(
        "Pluck", "Pluck Synth", CAT_SYNTH, "keys", "synths.pluck", pluck_zones, norm="peak",
        cfg=dict(patches=[dict(name="Pluck", layers=[_rrs("", 3)])], range=(24, 108), attack=0, release=300,
                 vrange=20, let_ring=1, fx=SYNTH_FX, filter_type="$FILTER_TYPE_LDR_LP4", resonance=True,
                 fx_defaults=dict(tone=1000, delay=220, reverb=250, width=650),
                 info="Pluck Synth  |  Try PERFORM > Arpeggiator"),
        presets=keys_presets(), blurb="Snappy filter-envelope pluck with three round robins."))
    I.append(Instrument(
        "PulseArp", "Pulse Arp", CAT_SYNTH, "keys", "synths.pluck", pluck_zones, norm="peak", samples_from="Pluck",
        cfg=dict(patches=[dict(name="Pluck", layers=[_rrs("", 3)])], range=(24, 108), attack=0, release=200,
                 vrange=12, let_ring=0, arp_default=1, arp_rate=3, fx=SYNTH_FX, filter_type="$FILTER_TYPE_LDR_LP4",
                 resonance=True, fx_defaults=dict(tone=850, reso=250, delay=300, delay_fb=420, reverb=300, width=700),
                 info="Pulse Arp  |  Hold a chord: 1/16 arpeggio synced to tempo"),
        presets=keys_presets(), blurb="The Pluck Synth preset as a ready-to-go tempo-synced arpeggiator."))
    I.append(Instrument(
        "SeqBass", "Sequencer Bass", CAT_SYNTH, "keys", "expansion.seq_bass",
        zones_for(["Seq"], _roots(24, 72), 12, 84, seed_base=2500), channels=1, norm="peak",
        cfg=dict(patches=[dict(name="Seq Bass", layers=[["Seq"]])], range=(12, 84), attack=0, release=120,
                 vrange=14, let_ring=0, arp_default=1, arp_rate=3, fx=["filter", "supergt", "stereo", "replika", "raum"],
                 resonance=True, filter_type="$FILTER_TYPE_LDR_LP4",
                 fx_defaults=dict(tone=800, reso=300, drive=250, delay=150, reverb=100, width=0),
                 info="Sequencer Bass  |  Hold notes for a pulsing 1/16 bass line (arp on)"),
        presets=keys_presets(), blurb="Punchy resonant sequence bass, arpeggiator on by default."))
    I.append(Instrument(
        "Choir", "Ethereal Choir", CAT_SYNTH, "synth", "synths.choir",
        zones_for(["Aah", "Ooh"], _roots(40, 88), 33, 96, seed_base=600),
        cfg=dict(layers=["Aah", "Ooh"], layer_a=0, layer_b=2, blend=250, attack=380, release=1600, vsens=25,
                 range=(33, 96), resonance=False, fx=SYNTH_FX,
                 fx_defaults=dict(tone=1000, reverb=420, width=600, rev_size=800, rev_decay=700),
                 info="Ethereal Choir  |  Blend morphs the vowel from Aah to Ooh"),
        presets=synth_presets(), blurb="Formant-synthesised mixed choir, Aah and Ooh vowels, morphable."))

    # ================================================================== 02 Orchestral
    sus = ["SusP", "SusF", "Trem"]
    str_groups = sus + _rrs("Stac", 4) + _rrs("Pizz", 4)
    I.append(Instrument(
        "Strings", "Ensemble Strings", CAT_ORCH, "artic", "orchestral.strings",
        add_hall_mics(_rr_zones(str_groups, _roots(33, 99), 31, 103, 700), sus),
        cfg=dict(arts=[dict(name="Sustain", type="sus", groups=["SusP", "SusF"], ks=24),
                       dict(name="Tremolo", type="sus", groups=["Trem"], ks=25),
                       dict(name="Staccato", type="short", groups=_rrs("Stac", 4), ks=26),
                       dict(name="Pizzicato", type="short", groups=_rrs("Pizz", 4), ks=27),
                       dict(name="Swell", type="swell", groups=["SusP", "SusF"], ks=28)],
                 mics=_mics(sus), range=(31, 103), attack=0, release=380, fx=ACOUSTIC_FX,
                 fx_defaults=dict(tone=1000, reverb=250, width=550, rev_size=750, rev_decay=600),
                 info="Ensemble Strings  |  CC1 = dynamics, keyswitches C0-E0, Close/Hall mics"),
        presets=artic_presets(2, mics=True),
        blurb="Eight-player bowed ensemble: sustain (2 dynamics, 2 mics), tremolo, staccato, pizzicato, swell."))
    I.append(Instrument(
        "SoloViolin", "Solo Violin", CAT_ORCH, "artic", "expansion.solo_violin",
        _rr_zones(["SusP", "SusF"] + _rrs("Stac", 2) + _rrs("Pizz", 2), _roots(55, 91), 55, 100, 2600), channels=1,
        cfg=dict(arts=[dict(name="Sustain", type="sus", groups=["SusP", "SusF"], ks=24),
                       dict(name="Staccato", type="short", groups=_rrs("Stac", 2), ks=25),
                       dict(name="Pizzicato", type="short", groups=_rrs("Pizz", 2), ks=26),
                       dict(name="Swell", type="swell", groups=["SusP", "SusF"], ks=27)],
                 range=(55, 100), attack=0, release=300, legato=1, fx=ACOUSTIC_FX,
                 fx_defaults=dict(tone=1000, reverb=300, width=350, rev_size=700),
                 info="Solo Violin  |  Legato on by default, CC1 = dynamics"),
        presets=artic_presets(1), blurb="Expressive single violin with legato, staccato and pizzicato."))
    I.append(Instrument(
        "SoloCello", "Solo Cello", CAT_ORCH, "artic", "expansion.solo_cello",
        _rr_zones(["SusP", "SusF"] + _rrs("Stac", 2) + _rrs("Pizz", 2), _roots(36, 72), 36, 79, 2700), channels=1,
        cfg=dict(arts=[dict(name="Sustain", type="sus", groups=["SusP", "SusF"], ks=24),
                       dict(name="Staccato", type="short", groups=_rrs("Stac", 2), ks=25),
                       dict(name="Pizzicato", type="short", groups=_rrs("Pizz", 2), ks=26),
                       dict(name="Swell", type="swell", groups=["SusP", "SusF"], ks=27)],
                 range=(36, 79), attack=0, release=320, legato=1, fx=ACOUSTIC_FX,
                 fx_defaults=dict(tone=1000, reverb=300, width=350, rev_size=700),
                 info="Solo Cello  |  Legato on by default, CC1 = dynamics"),
        presets=artic_presets(1), blurb="Warm single cello with legato, staccato and pizzicato."))
    bsus = ["SusP", "SusF"]
    I.append(Instrument(
        "Brass", "Brass Ensemble", CAT_ORCH, "artic", "orchestral.brass",
        add_hall_mics(_rr_zones(bsus + _rrs("Stac", 4), _roots(36, 84), 29, 90, 800), bsus),
        cfg=dict(arts=[dict(name="Sustain", type="sus", groups=bsus, ks=24),
                       dict(name="Swell", type="swell", groups=bsus, ks=25),
                       dict(name="Staccato", type="short", groups=_rrs("Stac", 4), ks=26)],
                 mics=_mics(bsus), range=(29, 90), attack=0, release=300, fx=ACOUSTIC_FX,
                 fx_defaults=dict(tone=1000, reverb=280, width=500, rev_size=750, rev_decay=600),
                 info="Brass Ensemble  |  CC1 = dynamics (soft to blaring), keyswitches C0-D0, Close/Hall mics"),
        presets=artic_presets(2, mics=True), blurb="Horn/trombone section with loudness-driven brightness, swells and shorts."))
    I.append(Instrument(
        "Horns", "French Horns", CAT_ORCH, "artic", "expansion.horns",
        _rr_zones(["SusP", "SusF"] + _rrs("Stac", 2), _roots(34, 76), 31, 81, 2800), channels=1,
        cfg=dict(arts=[dict(name="Sustain", type="sus", groups=["SusP", "SusF"], ks=24),
                       dict(name="Swell", type="swell", groups=["SusP", "SusF"], ks=25),
                       dict(name="Staccato", type="short", groups=_rrs("Stac", 2), ks=26)],
                 range=(31, 81), attack=0, release=350, fx=ACOUSTIC_FX,
                 fx_defaults=dict(tone=1000, reverb=350, width=400, rev_size=800),
                 info="French Horns  |  Warm, heroic horn section. CC1 = dynamics"),
        presets=artic_presets(2), blurb="Four-horn section, mellow to heroic, with swells and shorts."))
    I.append(Instrument(
        "Woodwinds", "Woodwind Ensemble", CAT_ORCH, "artic", "orchestral.woodwinds",
        _rr_zones(["Flute", "Clarinet"] + _rrs("Stac", 4), _roots(48, 96), 40, 100, 900), channels=1,
        cfg=dict(arts=[dict(name="Flute Sustain", type="sus", groups=["Flute"], ks=24),
                       dict(name="Clarinet Sustain", type="sus", groups=["Clarinet"], ks=25),
                       dict(name="Staccato", type="short", groups=_rrs("Stac", 4), ks=26)],
                 range=(40, 100), attack=0, release=250, fx=ACOUSTIC_FX,
                 fx_defaults=dict(tone=1000, reverb=320, width=300, rev_size=650, rev_decay=550),
                 info="Woodwind Ensemble  |  Flutes, clarinets and staccato, keyswitches C0-D0"),
        presets=artic_presets(2), blurb="Breathy flute pair, clarinet pair and a woodwind staccato."))
    harp_groups = _vr(2, 2)
    I.append(Instrument(
        "Harp", "Concert Harp", CAT_ORCH, "keys", "expansion.harp",
        zones_for(harp_groups, _roots(24, 102), 23, 104, seed_base=2900), channels=1, norm="peak",
        cfg=dict(patches=[dict(name="Harp", layers=_vr_layers(2, 2), splits=[85])], range=(23, 104), attack=0,
                 release=500, vrange=24, let_ring=1, fx=ACOUSTIC_FX,
                 fx_defaults=dict(tone=1000, reverb=350, width=500, rev_size=800),
                 info="Concert Harp  |  For glissandi: PERFORM > Scale Lock + Arp Up 1/32"),
        presets=keys_presets([("Glissando", dict(scale_type=1, chord=11, arp_mode=3, arp_rate=5, arp_oct=3,
                                                 arp_gate=90))]),
        blurb="Plucked concert harp, 2 velocity layers x 2 round robins, rings out naturally."))
    I.append(Instrument(
        "Timpani", "Cinematic Timpani", CAT_ORCH, "artic", "orchestral.timpani",
        _rr_zones(_rrs("Hit", 4) + ["RollP", "RollF"], [38, 43, 48, 53], 36, 57, 1000), channels=1,
        cfg=dict(arts=[dict(name="Hits", type="short", groups=_rrs("Hit", 4), ks=24),
                       dict(name="Roll", type="sus", groups=["RollP", "RollF"], ks=25)],
                 range=(36, 57), attack=0, release=600, fx=ACOUSTIC_FX, pedal=0, vrange=30,
                 fx_defaults=dict(tone=1000, reverb=300, width=400, rev_size=850, rev_decay=650),
                 info="Cinematic Timpani  |  C0 hits, C#0 rolls (CC1 = roll dynamics)"),
        presets=artic_presets(None), blurb="Pitched timpani hits with 4 round robins and looped rolls with crescendo control."))
    perc = [
        (36, "Gran Cassa", "grancassa", 3.0, "Drums", 0.0, False),
        (37, "Gran Cassa Roll", "gcroll", 3.2, "Drums", 0.0, True),
        (38, "Taiko", "taiko", 2.2, "Taiko", -0.2, False),
        (39, "Taiko Ensemble", "taikoens", 2.6, "Taiko", 0.0, False),
        (40, "Taiko Rim", "taikorim", 0.5, "Taiko", -0.2, False),
        (41, "Boom Drum", "boom", 3.5, "Drums", 0.0, False),
        (42, "Orch Snare", "osnare", 1.0, "Snare", 0.15, False),
        (43, "Snare Roll", "sroll", 3.0, "Snare", 0.15, True),
        (45, "Piatti", "piatti", 3.5, "Cymbals", 0.3, False),
        (46, "Cymbal Swell", "swell", 3.5, "Cymbals", 0.35, False),
        (47, "Sus Cymbal", "suscym", 3.0, "Cymbals", 0.35, False),
        (48, "Tam-tam", "tamtam", 5.0, "Metals", -0.3, False),
        (50, "Triangle", "triangle", 3.0, "Metals", 0.4, False),
        (52, "Anvil", "anvil", 1.6, "Metals", -0.25, False),
        (53, "Woodblock", "woodblock", 0.3, "Metals", 0.2, False),
        (54, "Tambourine", "otamb", 0.8, "Snare", 0.3, False),
    ]
    I.append(Instrument(
        "OrchPerc", "Orchestral Percussion", CAT_ORCH, "drums", "cinematic.orch_perc",
        _kit_zones(perc, _rrs("", 3), 1700, lambda pc: {"hold": pc[6]}), channels=1, norm="peak",
        cfg=dict(buses=["Drums", "Taiko", "Snare", "Cymbals", "Metals"],
                 pieces=[dict(key=k, name=nm, bus=b, pan=pn, hold=h, layers=[_rrs("", 3)], splits=[127])
                         for (k, nm, _, _, b, pn, h) in perc],
                 fx=["filter", "comp", "stereo", "raum"], pedal=0, spread=60,
                 fx_defaults=dict(tone=1000, comp=150, reverb=320, width=600, rev_size=850, rev_decay=650),
                 info="Orchestral Percussion  |  Hold C#2 / G2 for rolls, CC1 = roll level"),
        presets=drum_presets(), blurb="Gran cassa, taiko, snare, cymbals, tam-tam and metals with 3 round robins and rolls."))

    # ================================================================== 03 Band and Keys
    I.append(Instrument(
        "FeltPiano", "Felt Piano", CAT_BAND, "keys", "expansion.felt_piano",
        zones_for(["V1", "V2", "V3"], _roots(21, 105), 21, 108, seed_base=3000), channels=1, norm="peak",
        cfg=dict(patches=[dict(name="Felt Piano", layers=[["V1"], ["V2"], ["V3"]], splits=[50, 98])], range=(21, 108),
                 attack=0, release=250, vrange=30, fx=ACOUSTIC_FX,
                 fx_defaults=dict(tone=1000, reverb=280, width=450, rev_size=700),
                 info="Felt Piano  |  Soft hammered-string piano, 3 velocity layers"),
        presets=keys_presets([("Intimate", dict(tone=650, rev_mix=180, width=300))]),
        blurb="Physically modelled felt piano: hammer, 1-3 strings per note and a soundboard."))
    I.append(Instrument(
        "EPiano", "Electric Piano", CAT_BAND, "keys", "band.epiano",
        zones_for(["V1", "V2", "V3"], _roots(28, 100), 21, 108, seed_base=1100), channels=1, norm="peak",
        cfg=dict(patches=[dict(name="Tine EP", layers=[["V1"], ["V2"], ["V3"]], splits=[52, 98])], range=(21, 108),
                 attack=0, release=180, vrange=28, fx=["filter", "eppre", "stereo", "choral", "replika", "raum"],
                 fx_defaults=dict(tone=1000, trem=300, reverb=200, chorus=150, width=500),
                 info="Electric Piano  |  3 velocity layers, tremolo and drive on the SOUND page"),
        presets=keys_presets(), blurb="FM tine electric piano with velocity-dependent bark, tremolo preamp."))
    I.append(Instrument(
        "Organ", "Drawbar Organ", CAT_BAND, "keys", "band.organ",
        zones_for(["Full", "Soft"], _roots(36, 96), 24, 108, seed_base=1500), channels=1,
        cfg=dict(patches=[dict(name="Full Drawbars", layers=[["Full"]], loop=True),
                          dict(name="Soft Flutes", layers=[["Soft"]], loop=True)],
                 range=(24, 108), attack=3, release=45, vrange=0, restrike=20,
                 fx=["filter", "rotator", "supergt", "replika", "raum"],
                 fx_defaults=dict(tone=1000, drive=180, reverb=180),
                 info="Drawbar Organ  |  Mod wheel up = fast rotary"),
        presets=[("Gospel Fast", dict(rot_fast=1, drive=350, rev_mix=150)), ("Church Soft", dict(patch=1, rev_mix=450))],
        blurb="Tonewheel-style additive organ with key click, rotary speaker and drive."))
    gtr_g = _vr(3, 2)
    I.append(Instrument(
        "Guitar", "Nylon Guitar", CAT_BAND, "keys", "band.guitar",
        zones_for(gtr_g, _roots(40, 76), 38, 84, seed_base=1200), channels=1, norm="peak",
        cfg=dict(patches=[dict(name="Nylon", layers=_vr_layers(3, 2), splits=[60, 100])],
                 range=(38, 84), attack=0, release=450, vrange=24, let_ring=0, fx=ACOUSTIC_FX,
                 fx_defaults=dict(tone=1000, reverb=220, width=400),
                 info="Nylon Guitar  |  Use PERFORM > Chord + Strum for strummed chords"),
        presets=keys_presets(), blurb="Physically modelled nylon-string guitar with body resonance, 3 layers x 2 round robins."))
    eg = _vr(2, 2) + _rrs("Drive", 2) + _rrs("Mute", 2)
    I.append(Instrument(
        "ElecGuitar", "Electric Guitar", CAT_BAND, "keys", "expansion.electric_guitar",
        zones_for(eg, _roots(40, 76), 38, 86, seed_base=3100), channels=1, norm="peak",
        cfg=dict(patches=[dict(name="Clean", layers=_vr_layers(2, 2), splits=[90]),
                          dict(name="Drive", layers=[_rrs("Drive", 2)]),
                          dict(name="Palm Mute", layers=[_rrs("Mute", 2)])],
                 range=(38, 86), attack=0, release=300, vrange=20, let_ring=0,
                 fx=["filter", "supergt", "stereo", "choral", "replika", "raum"],
                 fx_defaults=dict(tone=1000, drive=100, reverb=200, chorus=0, width=450),
                 info="Electric Guitar  |  Clean, Drive and Palm Mute. Power chords: PERFORM > Chord > Power"),
        presets=keys_presets([("Power Chords", dict(patch=1, chord=2, rev_mix=200)),
                              ("Chugs", dict(patch=2, chord=2, rev_mix=80))]),
        blurb="Electric guitar model with pickup, amp and cabinet: clean, overdrive and palm mutes."))
    I.append(Instrument(
        "Bass", "Finger Bass", CAT_BAND, "keys", "band.finger_bass",
        zones_for(gtr_g, _roots(28, 58), 23, 64, seed_base=1300), channels=1, norm="peak",
        cfg=dict(patches=[dict(name="Finger", layers=_vr_layers(3, 2), splits=[60, 100])],
                 range=(23, 64), attack=0, release=120, vrange=20,
                 fx=["filter", "supergt", "stereo", "choral", "replika", "raum"],
                 fx_defaults=dict(tone=1000, drive=150, reverb=0, width=0),
                 info="Finger Bass  |  3 velocity layers x 2 round robins"),
        presets=keys_presets(), blurb="Fingered electric bass model with pickup comb filtering and thump."))
    kit = [
        (36, "Kick", "kick", 0.8, 1.0, "Kick", 0.0, 0, 0),
        (37, "Side Stick", "sidestick", 0.35, 1.0, "Snare", -0.05, 0, 0),
        (38, "Snare", "snare", 0.9, 1.0, "Snare", -0.08, 0, 0),
        (39, "Clap", "clap", 0.7, 1.0, "Perc", 0.1, 0, 0),
        (40, "Rimshot", "rimshot", 0.9, 1.0, "Snare", -0.08, 0, 0),
        (41, "Floor Tom 2", "tom", 1.3, 82.0, "Toms", 0.45, 0, 0),
        (42, "Closed Hat", "chh", 0.35, 1.0, "Hats", -0.35, 0, 1),
        (43, "Floor Tom 1", "tom", 1.3, 98.0, "Toms", 0.35, 0, 0),
        (44, "Pedal Hat", "phh", 0.4, 1.0, "Hats", -0.35, 0, 1),
        (45, "Low Tom", "tom", 1.3, 117.0, "Toms", 0.2, 0, 0),
        (46, "Open Hat", "ohh", 1.4, 1.0, "Hats", -0.35, 1, 0),
        (47, "Mid Tom", "tom", 1.3, 139.0, "Toms", 0.05, 0, 0),
        (48, "Hi-Mid Tom", "tom", 1.3, 165.0, "Toms", -0.1, 0, 0),
        (49, "Crash", "crash", 2.6, 1.0, "Cymbals", -0.5, 0, 0),
        (50, "High Tom", "tom", 1.3, 196.0, "Toms", -0.2, 0, 0),
        (51, "Ride", "ride", 2.2, 1.0, "Cymbals", 0.5, 0, 0),
        (53, "Ride Bell", "bell", 1.8, 1.0, "Cymbals", 0.5, 0, 0),
        (54, "Tambourine", "tamb", 0.6, 1.0, "Perc", 0.3, 0, 0),
        (57, "Crash 2", "crash2", 2.4, 1.0, "Cymbals", 0.55, 0, 0),
        (70, "Shaker", "shaker", 0.35, 1.0, "Perc", 0.25, 0, 0),
    ]
    kit_g = _vr(3, 3)
    I.append(Instrument(
        "Drums", "Studio Drum Kit", CAT_BAND, "drums", "band.drums",
        _kit_zones(kit, kit_g, 1400, lambda pc: {"var": pc[4]}), channels=1, norm="peak",
        cfg=dict(buses=["Kick", "Snare", "Toms", "Hats", "Cymbals", "Perc"],
                 pieces=[dict(key=k, name=nm, bus=b, pan=pn, cg=cg, cut=cut, layers=_vr_layers(3, 3), splits=[60, 100])
                         for (k, nm, _, _, _, b, pn, cg, cut) in kit],
                 fx=KIT_FX, pedal=0,
                 fx_defaults=dict(tone=1000, comp=300, drive=150, reverb=180, width=500, rev_size=450, rev_decay=400),
                 info="Studio Drum Kit  |  GM layout, 3 velocity layers x 3 round robins, Note Repeat"),
        presets=drum_presets(), blurb="Synthesised acoustic/hybrid kit: 20 pieces, 3 velocity layers x 3 round robins."))
    swk = [
        (36, "Kick", "kick", 0.7, 1.0, "Kick", 0.0, 0, 0), (37, "Rim", "rim", 0.3, 1.0, "Snare", -0.05, 0, 0),
        (38, "Gated Snare", "snare", 0.6, 1.0, "Snare", -0.05, 0, 0), (39, "Gated Clap", "clap", 0.6, 1.0, "Snare", 0.1, 0, 0),
        (40, "Snare 2", "snare2", 0.6, 1.0, "Snare", -0.05, 0, 0),
        (41, "Tom 1", "tom", 1.0, 70.0, "Toms", 0.45, 0, 0), (43, "Tom 2", "tom", 1.0, 90.0, "Toms", 0.25, 0, 0),
        (45, "Tom 3", "tom", 1.0, 115.0, "Toms", 0.0, 0, 0), (47, "Tom 4", "tom", 1.0, 145.0, "Toms", -0.25, 0, 0),
        (48, "Tom 5", "tom", 1.0, 180.0, "Toms", -0.45, 0, 0),
        (42, "Closed Hat", "chh", 0.3, 1.0, "Hats", -0.3, 0, 1), (44, "Pedal Hat", "phh", 0.35, 1.0, "Hats", -0.3, 0, 1),
        (46, "Open Hat", "ohh", 1.0, 1.0, "Hats", -0.3, 1, 0), (49, "Crash", "crash", 2.2, 1.0, "Cymbals", -0.4, 0, 0),
        (51, "Ride", "ride", 1.8, 1.0, "Cymbals", 0.4, 0, 0), (54, "Tambourine", "tamb", 0.5, 1.0, "Perc", 0.3, 0, 0),
        (56, "Cowbell", "cowbell", 0.4, 1.0, "Perc", 0.2, 0, 0),
    ]
    I.append(Instrument(
        "SynthwaveKit", "Synthwave Kit", CAT_BAND, "drums", "expansion.synthwave_kit",
        _kit_zones(swk, _vr(2, 2), 3200, lambda pc: {"var": pc[4]}), channels=1, norm="peak",
        cfg=dict(buses=["Kick", "Snare", "Toms", "Hats", "Cymbals", "Perc"],
                 pieces=[dict(key=k, name=nm, bus=b, pan=pn, cg=cg, cut=cut, layers=_vr_layers(2, 2), splits=[90])
                         for (k, nm, _, _, _, b, pn, cg, cut) in swk],
                 fx=KIT_FX, pedal=0,
                 fx_defaults=dict(tone=1000, comp=350, drive=150, reverb=250, width=550, rev_size=600),
                 info="Synthwave Kit  |  80s gated snares and big synth toms"),
        presets=drum_presets(), blurb="80s drum machine kit with gated snares, Simmons-style toms and cowbell."))
    trap = [
        (36, "808 Kick", "808", 2.2, "Kick", 0.0, 0, 0), (35, "Punch Kick", "punchkick", 0.6, "Kick", 0.0, 0, 0),
        (38, "Trap Snare", "snare", 0.6, "Snare", 0.0, 0, 0), (39, "Clap", "clap", 0.8, "Snare", 0.05, 0, 0),
        (40, "Snare + Clap", "snareclap", 0.7, "Snare", 0.0, 0, 0), (37, "Rim", "rim", 0.3, "Snare", -0.1, 0, 0),
        (42, "Hat", "hat", 0.25, "Hats", -0.25, 0, 1), (44, "Hat Tight", "hattight", 0.15, "Hats", -0.25, 0, 1),
        (46, "Open Hat", "ohh", 0.9, "Hats", -0.25, 1, 0), (49, "Crash", "crash", 2.2, "Perc", 0.4, 0, 0),
        (51, "Perc Bell", "bell", 1.0, "Perc", 0.35, 0, 0), (52, "Snap", "snap", 0.3, "Perc", 0.15, 0, 0),
        (53, "Shaker", "shaker", 0.3, "Perc", 0.3, 0, 0), (55, "Vox Chop", "vox", 0.5, "Perc", 0.0, 0, 0),
    ]
    I.append(Instrument(
        "TrapKit", "Trap Kit", CAT_BAND, "drums", "expansion.trap_kit",
        _kit_zones(trap, _vr(2, 2), 3300), channels=1, norm="peak",
        cfg=dict(buses=["Kick", "Snare", "Hats", "Perc"],
                 pieces=[dict(key=k, name=nm, bus=b, pan=pn, cg=cg, cut=cut, layers=_vr_layers(2, 2), splits=[90])
                         for (k, nm, _, _, b, pn, cg, cut) in trap],
                 fx=KIT_FX, pedal=0, repeat=0,
                 fx_defaults=dict(tone=1000, comp=300, drive=200, reverb=150, width=500),
                 info="Trap Kit  |  Note Repeat (PLAY page) for hi-hat rolls"),
        presets=drum_presets([("Hat Rolls 1/32", dict(repeat=5))]),
        blurb="Modern trap kit: long 808, snares, claps, hats with Note Repeat rolls, percs and vox."))
    I.append(Instrument(
        "Mallets", "Cinematic Mallets", CAT_BAND, "keys", "band.mallets",
        [Zone(g, r, zlo, zhi, seed=1600 + gi * 100 + zi)
         for gi, (g, lo, hi, klo, khi) in enumerate([("Marimba", 36, 96, 33, 99), ("Vibes", 53, 89, 50, 92),
                                                     ("Celesta", 60, 108, 57, 112), ("Glock", 72, 108, 70, 112)])
         for zi, (r, zlo, zhi) in enumerate(keymap(_roots(lo, hi), klo, khi))], channels=1, norm="peak",
        cfg=dict(patches=[dict(name="Marimba", layers=[["Marimba"]]), dict(name="Vibraphone", layers=[["Vibes"]]),
                          dict(name="Celesta", layers=[["Celesta"]]), dict(name="Glockenspiel", layers=[["Glock"]])],
                 range=(33, 112), attack=0, release=400, vrange=24, let_ring=1, fx=ACOUSTIC_FX,
                 fx_defaults=dict(tone=1000, reverb=320, width=500, rev_size=750, rev_decay=650),
                 info="Cinematic Mallets  |  Pick an instrument, layer a second one on top"),
        presets=keys_presets([("Celesta + Glock", dict(patch=2, patch2=4, mix2=-30, rev_mix=400))]),
        blurb="Modal-synthesis marimba, vibraphone, celesta and glockenspiel."))

    # ================================================================== 04 Cinematic
    I.append(Instrument(
        "Braams", "Braams and Hits", CAT_CINE, "keys", "cinematic.braams",
        zones_for(["Braam", "Blaster"], _roots(24, 48), 21, 60, seed_base=1800), norm="peak",
        cfg=dict(patches=[dict(name="Braam", layers=[["Braam"]]), dict(name="Blaster", layers=[["Blaster"]])],
                 range=(21, 60), attack=0, release=900, vrange=18, let_ring=1, fx=SYNTH_FX,
                 filter_type="$FILTER_TYPE_LDR_LP4", resonance=True,
                 fx_defaults=dict(tone=1000, reverb=300, width=600, rev_size=900, rev_decay=750),
                 info="Braams and Hits  |  Low keys = biggest braams. Layer Braam + Blaster"),
        presets=keys_presets([("Inception Stack", dict(patch=0, patch2=2, mix2=-40, chord=2, rev_mix=420))]),
        blurb="Trailer braams: brass-like saw walls and a ring-modulated, folded 'Blaster'."))
    drones = ["DarkStrings", "GlassAir", "ChoirDrone", "MetalShimmer", "SubRumble", "GhostPad", "TensionCluster", "Heartbeat"]
    I.append(Instrument(
        "Drones", "Drones and Textures", CAT_CINE, "synth", "cinematic.drones",
        [Zone(g, 48, 24, 96, seed=1900 + i) for i, g in enumerate(drones)],
        cfg=dict(layers=drones, layer_a=0, layer_b=6, blend=200, attack=1500, release=3500, vsens=10, movement=350,
                 range=(24, 96), resonance=True, filter_type="$FILTER_TYPE_LDR_LP4", fx=SYNTH_FX,
                 fx_defaults=dict(tone=850, reverb=450, width=700, delay=100, rev_size=900, rev_decay=800),
                 info="Drones and Textures  |  Pick two textures and blend them"),
        presets=synth_presets(), blurb="Eight evolving underscore beds: strings, air, choir, metal, rumble, ghost, tension, heartbeat."))
    atm = ["Abyss", "Wind", "BowedMetal", "HauntedChoir", "MachineHum", "DeepSpace", "Pulse", "Shimmer"]
    I.append(Instrument(
        "DarkAtmos", "Dark Atmospheres", CAT_CINE, "synth", "expansion.dark_atmos",
        [Zone(g, 48, 24, 96, seed=3400 + i) for i, g in enumerate(atm)],
        cfg=dict(layers=atm, layer_a=0, layer_b=5, blend=300, attack=1800, release=4000, vsens=10, movement=400,
                 range=(24, 96), resonance=True, filter_type="$FILTER_TYPE_LDR_LP4", fx=SYNTH_FX,
                 fx_defaults=dict(tone=850, reverb=500, width=750, delay=120, rev_size=950, rev_decay=850),
                 info="Dark Atmospheres  |  Horror and thriller beds. Blend any two"),
        presets=synth_presets(), blurb="Eight dark beds: abyss, wind, bowed metal, haunted choir, machine hum, deep space, pulse, shimmer."))
    I.append(Instrument(
        "ReverseSwells", "Reverse Swells", CAT_CINE, "keys", "expansion.reverse_swells",
        zones_for(["RevPiano", "RevStrings", "RevPad"], [36, 48, 60, 72, 84], 24, 96, seed_base=3500), norm="peak",
        cfg=dict(patches=[dict(name="Reverse Piano", layers=[["RevPiano"]]),
                          dict(name="Reverse Strings", layers=[["RevStrings"]]),
                          dict(name="Reverse Pad", layers=[["RevPad"]])],
                 range=(24, 96), attack=0, release=300, vrange=12, let_ring=1, fx=SYNTH_FX,
                 fx_defaults=dict(tone=1000, reverb=250, width=650),
                 info="Reverse Swells  |  Pitched reverse swells: play them just before the beat"),
        presets=keys_presets(), blurb="Chromatic reversed piano, strings and pad swells for transitions."))
    fxl = [
        (36, "Boom Impact", "boom", 4.0, "Impacts"), (37, "Sub Drop", "subdrop", 4.0, "Impacts"),
        (38, "Trailer Hit", "trailer", 4.0, "Impacts"), (39, "Metal Impact", "metal", 3.5, "Impacts"),
        (40, "Low Hit", "lowhit", 3.5, "Impacts"), (41, "Glass Hit", "glasshit", 3.5, "Impacts"),
        (42, "Noise Riser", "riser_noise", 4.5, "Risers"), (43, "Tonal Riser", "riser_tonal", 4.5, "Risers"),
        (44, "Tension Riser", "riser_tension", 4.5, "Risers"), (45, "Reverse Cymbal", "revcymbal", 3.0, "Risers"),
        (46, "Reverse Hit", "revhit", 3.0, "Risers"), (47, "Whoosh Fast", "whoosh_fast", 1.8, "Whooshes"),
        (48, "Whoosh Slow", "whoosh_slow", 3.0, "Whooshes"), (49, "Downer", "downer", 3.5, "Downers"),
        (50, "Power Down", "powerdown", 2.5, "Downers"), (51, "Braam Stab", "braamstab", 2.5, "Misc"),
        (52, "Heartbeat", "heartbeat", 2.0, "Misc"), (53, "Clock Ticks", "ticks", 2.0, "Misc"),
        (54, "Glitch Stutter", "glitch", 1.5, "Misc"), (55, "Distant Thunder", "thunder", 4.5, "Misc"),
    ]
    I.append(Instrument(
        "FX", "Cinematic FX", CAT_CINE, "drums", "cinematic.fx", _fx_zones(fxl, "FX", 2000), norm="peak",
        cfg=dict(buses=["Impacts", "Risers", "Whooshes", "Downers", "Misc"],
                 pieces=[dict(key=k, name=nm, bus=b, layers=[["FX"]], splits=[127]) for (k, nm, _, _, b) in fxl],
                 fx=["filter", "stereo", "replika", "raum"], pedal=0, humanize=0, spread=0, vrange=18,
                 fx_defaults=dict(tone=1000, reverb=200, width=500, rev_size=900, rev_decay=700),
                 info="Cinematic FX  |  C2-G3: impacts, risers, whooshes, downers, stingers"),
        presets=drum_presets(), blurb="Twenty trailer-style one-shots: impacts, risers, whooshes, downers and stingers."))
    tp = [
        (36, "Epic Boom", "epicboom", 3.5, "Booms", 0.0), (37, "Distorted Kick", "distkick", 1.5, "Booms", 0.0),
        (38, "Hybrid Hit", "hybridhit", 2.5, "Hits", 0.0), (39, "Metal Slam", "metalslam", 2.0, "Metal", -0.2),
        (40, "Taiko Stack", "taikostack", 2.5, "Hits", 0.0), (41, "Dist Tom Low", "disttom1", 1.5, "Toms", 0.3),
        (43, "Dist Tom Mid", "disttom2", 1.3, "Toms", 0.0), (45, "Dist Tom High", "disttom3", 1.2, "Toms", -0.3),
        (42, "Clap Stack", "clapstack", 1.2, "Hits", 0.1), (44, "Snap Snare", "snapsnare", 1.0, "Hits", -0.1),
        (46, "Chain Slam", "chainslam", 1.5, "Metal", 0.25), (47, "Sub Hit", "subhit", 2.5, "Booms", 0.0),
        (48, "Gong Hit", "gonghit", 3.0, "Metal", -0.25), (49, "Whip Crack", "whip", 0.6, "Hits", 0.3),
        (50, "Glitch Hit", "glitchhit", 1.0, "Hits", 0.0), (51, "Rumble Hit", "rumblehit", 3.0, "Booms", 0.0),
    ]
    I.append(Instrument(
        "TrailerPerc", "Hybrid Trailer Percussion", CAT_CINE, "drums", "expansion.trailer_perc",
        _kit_zones(tp, _rrs("", 2), 3600), channels=1, norm="peak",
        cfg=dict(buses=["Booms", "Hits", "Toms", "Metal"],
                 pieces=[dict(key=k, name=nm, bus=b, pan=pn, layers=[_rrs("", 2)], splits=[127]) for (k, nm, _, _, b, pn) in tp],
                 fx=KIT_FX, pedal=0, spread=50,
                 fx_defaults=dict(tone=1000, comp=350, drive=250, reverb=380, width=650, rev_size=900, rev_decay=700),
                 info="Hybrid Trailer Percussion  |  Distorted booms, slams and toms. Try Note Repeat"),
        presets=drum_presets(), blurb="Hybrid trailer percussion: booms, slams, distorted toms, chains and glitch hits."))
    sfx = [(36 + i, nm, kind, ln, "SciFi") for i, (nm, kind, ln) in enumerate([
        ("Laser Zap", "laser", 1.0), ("Laser Burst", "laserburst", 1.2), ("Phaser Blast", "phaserblast", 1.6),
        ("Alarm", "alarm", 2.0), ("Robot Beeps", "robot", 2.0), ("Data Stream", "datastream", 2.0),
        ("Teleport", "teleport", 2.5), ("Power Up", "powerup", 2.5), ("Shutdown", "shutdown", 2.5),
        ("Force Field", "forcefield", 2.0), ("Servo", "servo", 1.5), ("Ship Pass", "shippass", 3.5),
        ("Sonar Ping", "sonar", 2.5), ("Radio Static", "static", 2.0), ("Energy Charge", "charge", 2.5),
        ("Zap Hit", "zaphit", 2.0), ("Alien Voice", "alienvoice", 2.0), ("Warp", "warp", 3.0)])]
    I.append(Instrument(
        "SciFi", "Sci-Fi FX", CAT_CINE, "drums", "expansion.scifi", _fx_zones(sfx, "FX", 3700), norm="peak",
        cfg=dict(buses=["SciFi"], pieces=[dict(key=k, name=nm, bus=b, layers=[["FX"]], splits=[127]) for (k, nm, _, _, b) in sfx],
                 fx=["filter", "stereo", "replika", "raum"], pedal=0, humanize=0, spread=0, vrange=18,
                 fx_defaults=dict(tone=1000, reverb=200, width=550, delay=150),
                 info="Sci-Fi FX  |  C2 upwards: lasers, alarms, robots, teleports, ships"),
        presets=drum_presets(), blurb="Eighteen sci-fi effects: lasers, alarms, robots, data, teleports, ships and warps."))
    tk = [(36, "Clock Loop", "clockloop", 3.5, "Loops", True), (37, "Heartbeat Loop", "heartloop", 4.0, "Loops", True),
          (38, "Sub Pulse Loop", "subloop", 3.5, "Loops", True), (39, "Ticking Bomb", "bombloop", 2.5, "Loops", True),
          (40, "String Scrape", "scrape", 2.5, "Hits", False), (41, "Col Legno", "collegno", 1.0, "Hits", False),
          (42, "Bowed Cymbal", "bowedcym", 4.0, "Textures", False), (43, "Piano Cluster", "pianocluster", 3.5, "Hits", False),
          (44, "Stinger High", "stingerhigh", 2.0, "Hits", False), (45, "Stinger Low", "stingerlow", 2.5, "Hits", False),
          (46, "Breath", "breath", 2.0, "Textures", False), (47, "Metal Creak", "creak", 3.0, "Textures", False)]
    I.append(Instrument(
        "TensionKit", "Tension Toolkit", CAT_CINE, "drums", "expansion.tension_kit",
        [Zone("FX", k, k, k, seed=3800 + i, p={"fx": kind, "len": ln, "hold": h}) for i, (k, _, kind, ln, _, h) in enumerate(tk)],
        norm="peak",
        cfg=dict(buses=["Loops", "Hits", "Textures"],
                 pieces=[dict(key=k, name=nm, bus=b, hold=h, layers=[["FX"]], splits=[127]) for (k, nm, _, _, b, h) in tk],
                 fx=["filter", "stereo", "replika", "raum"], pedal=0, humanize=0, spread=0, vrange=18,
                 fx_defaults=dict(tone=1000, reverb=250, width=550),
                 info="Tension Toolkit  |  C2-D#2 are loops: hold the key"),
        presets=drum_presets(), blurb="Suspense tools: clock, heartbeat and pulse loops, scrapes, clusters, stingers, breaths."))

    # ================================================================== 05 World
    for key, name, recipe, lo, hi, klo, khi, seed, blurb, rel in [
        ("Hang", "Hang Drum", "expansion.hang", 50, 86, 45, 92, 3900, "Hand-played steel hang drum with soft, singing overtones.", 600),
        ("SteelPan", "Steel Pan", "expansion.steel_pan", 55, 91, 50, 96, 4000, "Caribbean steel pan, bright and percussive.", 300),
        ("Kalimba", "Kalimba", "expansion.kalimba", 55, 91, 50, 96, 4100, "Thumb piano tines on a wooden resonator box.", 300),
        ("Gamelan", "Gamelan Bells", "expansion.gamelan", 48, 96, 43, 100, 4200, "Balinese-style metallophone with shimmering beating pairs.", 800),
    ]:
        I.append(Instrument(
            key, name, CAT_WORLD, "keys", recipe,
            _rr_zones(_rrs("", 2), _roots(lo, hi), klo, khi, seed), channels=2 if key == "Gamelan" else 1, norm="peak",
            cfg=dict(patches=[dict(name=name, layers=[_rrs("", 2)])], range=(klo, khi), attack=0, release=rel,
                     vrange=24, let_ring=1, fx=ACOUSTIC_FX,
                     fx_defaults=dict(tone=1000, reverb=320, width=500, rev_size=750),
                     info=f"{name}  |  2 round robins, rings out naturally"),
            presets=keys_presets([("Pentatonic Arp", dict(scale_type=10, arp_mode=3, arp_rate=3, arp_oct=2, dly_mix=250))]),
            blurb=blurb))
    sit = _rr_zones(_rrs("", 2), _roots(48, 84), 43, 90, 4300) + [Zone("Tanpura", 48, 24, 96, seed=4399)]
    I.append(Instrument(
        "Sitar", "Sitar and Tanpura", CAT_WORLD, "keys", "expansion.sitar", sit, channels=1, norm="peak",
        cfg=dict(patches=[dict(name="Sitar", layers=[_rrs("", 2)]), dict(name="Tanpura Drone", layers=[["Tanpura"]], loop=True)],
                 range=(24, 96), attack=0, release=400, vrange=20, let_ring=1, fx=ACOUSTIC_FX,
                 fx_defaults=dict(tone=1000, reverb=280, width=450),
                 info="Sitar and Tanpura  |  Layer the Tanpura drone under the sitar"),
        presets=keys_presets([("Raga Drone", dict(patch=0, patch2=2, mix2=-80, scale_type=14))]),
        blurb="Sitar with buzzing jawari bridge and sympathetic strings, plus a looping tanpura drone."))
    I.append(Instrument(
        "Duduk", "Duduk", CAT_WORLD, "artic", "expansion.duduk",
        _rr_zones(["Sus"] + _rrs("Stac", 2), _roots(52, 88), 48, 93, 4400), channels=1,
        cfg=dict(arts=[dict(name="Sustain", type="sus", groups=["Sus"], ks=24),
                       dict(name="Staccato", type="short", groups=_rrs("Stac", 2), ks=25),
                       dict(name="Swell", type="swell", groups=["Sus"], ks=26)],
                 range=(48, 93), attack=0, release=300, legato=1, fx=ACOUSTIC_FX,
                 fx_defaults=dict(tone=1000, reverb=380, width=350, rev_size=800),
                 info="Duduk  |  Mournful double-reed lead, legato on"),
        presets=artic_presets(1, extra=[("Desert Lament", dict(scale_type=14, porta=45, rev_mix=480))]),
        blurb="Mournful double-reed flute in the duduk style, with legato slides."))
    return I


CATALOG = build_catalog()
BY_KEY = {i.key: i for i in CATALOG}
