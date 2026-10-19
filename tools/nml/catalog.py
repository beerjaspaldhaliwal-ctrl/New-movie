"""The full instrument catalog of the New Movie Library."""
from .library import Instrument, Zone, keymap, zones_for, CAT_SYNTH, CAT_ORCH, CAT_CINE

SYNTH_FX = ["filter", "stereo", "choral", "replika", "raum"]
ACOUSTIC_FX = ["filter", "stereo", "choral", "replika", "raum"]


def _roots(lo, hi, step=6):
    return list(range(lo, hi + 1, step))


def _rr_zones(groups, roots, lo, hi, seed, **p):
    zs = zones_for(groups, roots, lo, hi, seed_base=seed, **p)
    for z in zs:
        if "RR" in z.group:
            z.p["rr"] = int(z.group[-1])
    return zs


def build_catalog():
    I = []

    # ------------------------------------------------------------------ 01 Synths and Pads
    I.append(Instrument(
        "WarmPad", "Warm Analog Pad", CAT_SYNTH, "synth", "synths.warm_pad",
        zones_for(["Warm", "Air"], _roots(33, 93), 24, 108, seed_base=100),
        cfg=dict(layers=["Warm", "Air"], layer_a=0, layer_b=2, blend=300, attack=650, release=2200, vsens=30,
                 movement=250, range=(24, 108), resonance=True, filter_type="$FILTER_TYPE_LDR_LP4", fx=SYNTH_FX,
                 fx_defaults=dict(tone=820, reso=120, reverb=380, chorus=250, width=600, rev_size=750, rev_decay=650),
                 info="Warm Analog Pad  |  Mod wheel opens the filter, Blend mixes Warm and Air"),
        blurb="Seven-voice detuned analog stack (Warm) and a breathy, tonal-noise shimmer (Air)."))
    I.append(Instrument(
        "GlassPad", "Glass Shimmer Pad", CAT_SYNTH, "synth", "synths.glass_pad",
        zones_for(["Glass"], _roots(33, 93), 24, 108, seed_base=200),
        cfg=dict(layers=["Glass"], layer_a=0, layer_b=0, attack=250, release=2600, vsens=35, movement=150,
                 range=(24, 108), resonance=True, filter_type="$FILTER_TYPE_LDR_LP4", fx=SYNTH_FX,
                 fx_defaults=dict(tone=950, reverb=420, chorus=200, width=650, delay=120, rev_size=800, rev_decay=700),
                 info="Glass Shimmer Pad  |  FM bell attack into a shimmering sustain"),
        blurb="FM glass bells with an octave shimmer, chorus and a long hall."))
    I.append(Instrument(
        "Supersaw", "Supersaw Stack", CAT_SYNTH, "synth", "synths.supersaw",
        zones_for(["Saw"], _roots(33, 93), 24, 108, seed_base=300),
        cfg=dict(layers=["Saw"], layer_a=0, layer_b=0, attack=3, release=380, vsens=40, glide=90, modwheel=600,
                 range=(24, 108), resonance=True, filter_type="$FILTER_TYPE_LDR_LP4", fx=SYNTH_FX,
                 fx_defaults=dict(tone=900, reso=150, reverb=220, delay=180, width=700),
                 info="Supersaw Stack  |  Mono / Glide for leads, Octave Layer for anthems"),
        blurb="Seven detuned saws, trance/trailer style. Poly, or mono with glide."))
    I.append(Instrument(
        "MonoBass", "Analog Mono Bass", CAT_SYNTH, "synth", "synths.mono_bass",
        zones_for(["Sub", "Growl"], _roots(24, 60), 12, 72, seed_base=400), channels=1,
        cfg=dict(layers=["Sub", "Growl"], layer_a=0, layer_b=2, blend=550, attack=2, release=140, vsens=45,
                 mono=1, glide=45, modwheel=700, range=(12, 72), resonance=True, filter_type="$FILTER_TYPE_LDR_LP4",
                 fx=["filter", "supergt", "stereo", "choral", "replika", "raum"],
                 fx_defaults=dict(tone=700, reso=200, drive=250, reverb=0, width=0),
                 info="Analog Mono Bass  |  Blend: clean sub to growl. Mono/Glide on by default"),
        blurb="Pure sub and a resonant, driven growl layer. Mono legato with glide."))
    pluck_zones = _rr_zones(["RR1", "RR2"], _roots(33, 93), 24, 108, 500)
    I.append(Instrument(
        "Pluck", "Pluck Synth", CAT_SYNTH, "keys", "synths.pluck", pluck_zones, norm="peak",
        cfg=dict(patches=[dict(name="Pluck", layers=[["RR1", "RR2"]])], range=(24, 108), attack=0, release=300,
                 vrange=20, let_ring=1, fx=SYNTH_FX, filter_type="$FILTER_TYPE_LDR_LP4", resonance=True,
                 fx_defaults=dict(tone=1000, delay=220, reverb=250, width=650),
                 info="Pluck Synth  |  Try PERFORM > Arpeggiator"),
        blurb="Snappy filter-envelope pluck with round robins."))
    I.append(Instrument(
        "PulseArp", "Pulse Arp", CAT_SYNTH, "keys", "synths.pluck", pluck_zones, norm="peak", samples_from="Pluck",
        cfg=dict(patches=[dict(name="Pluck", layers=[["RR1", "RR2"]])], range=(24, 108), attack=0, release=200,
                 vrange=12, let_ring=0, arp_default=1, arp_rate=3, fx=SYNTH_FX, filter_type="$FILTER_TYPE_LDR_LP4",
                 resonance=True, fx_defaults=dict(tone=850, reso=250, delay=300, delay_fb=420, reverb=300, width=700),
                 info="Pulse Arp  |  Hold a chord: 1/16 arpeggio synced to tempo"),
        blurb="The Pluck Synth preset as a ready-to-go tempo-synced arpeggiator."))
    I.append(Instrument(
        "Choir", "Ethereal Choir", CAT_SYNTH, "synth", "synths.choir",
        zones_for(["Aah", "Ooh"], _roots(40, 88), 33, 96, seed_base=600),
        cfg=dict(layers=["Aah", "Ooh"], layer_a=0, layer_b=2, blend=250, attack=380, release=1600, vsens=25,
                 range=(33, 96), resonance=False, fx=SYNTH_FX,
                 fx_defaults=dict(tone=1000, reverb=420, width=600, rev_size=800, rev_decay=700),
                 info="Ethereal Choir  |  Blend morphs the vowel from Aah to Ooh"),
        blurb="Formant-synthesised mixed choir, Aah and Ooh vowels, morphable."))

    # ------------------------------------------------------------------ 02 Orchestral and Band
    str_groups = ["SusP", "SusF", "Trem", "StacRR1", "StacRR2", "PizzRR1", "PizzRR2"]
    I.append(Instrument(
        "Strings", "Ensemble Strings", CAT_ORCH, "artic", "orchestral.strings",
        _rr_zones(str_groups, _roots(33, 99), 31, 103, 700),
        cfg=dict(arts=[dict(name="Sustain", type="sus", groups=["SusP", "SusF"], ks=24),
                       dict(name="Tremolo", type="sus", groups=["Trem"], ks=25),
                       dict(name="Staccato", type="short", groups=["StacRR1", "StacRR2"], ks=26),
                       dict(name="Pizzicato", type="short", groups=["PizzRR1", "PizzRR2"], ks=27),
                       dict(name="Swell", type="swell", groups=["SusP", "SusF"], ks=28)],
                 range=(31, 103), attack=0, release=380, fx=ACOUSTIC_FX,
                 fx_defaults=dict(tone=1000, reverb=300, width=550, rev_size=750, rev_decay=600),
                 info="Ensemble Strings  |  CC1 = dynamics, keyswitches C0-E0"),
        blurb="Eight-player bowed ensemble: sustain (2 dynamics), tremolo, staccato, pizzicato, swell."))
    I.append(Instrument(
        "Brass", "Brass Ensemble", CAT_ORCH, "artic", "orchestral.brass",
        _rr_zones(["SusP", "SusF", "StacRR1", "StacRR2"], _roots(36, 84), 29, 90, 800),
        cfg=dict(arts=[dict(name="Sustain", type="sus", groups=["SusP", "SusF"], ks=24),
                       dict(name="Swell", type="swell", groups=["SusP", "SusF"], ks=25),
                       dict(name="Staccato", type="short", groups=["StacRR1", "StacRR2"], ks=26)],
                 range=(29, 90), attack=0, release=300, fx=ACOUSTIC_FX,
                 fx_defaults=dict(tone=1000, reverb=320, width=500, rev_size=750, rev_decay=600),
                 info="Brass Ensemble  |  CC1 = dynamics (soft to blaring), keyswitches C0-D0"),
        blurb="Horn/trombone section with loudness-driven brightness, swells and shorts."))
    I.append(Instrument(
        "Woodwinds", "Woodwind Ensemble", CAT_ORCH, "artic", "orchestral.woodwinds",
        _rr_zones(["Flute", "Clarinet", "StacRR1", "StacRR2"], _roots(48, 96), 40, 100, 900), channels=1,
        cfg=dict(arts=[dict(name="Flute Sustain", type="sus", groups=["Flute"], ks=24),
                       dict(name="Clarinet Sustain", type="sus", groups=["Clarinet"], ks=25),
                       dict(name="Staccato", type="short", groups=["StacRR1", "StacRR2"], ks=26)],
                 range=(40, 100), attack=0, release=250, fx=ACOUSTIC_FX,
                 fx_defaults=dict(tone=1000, reverb=320, width=300, rev_size=650, rev_decay=550),
                 info="Woodwind Ensemble  |  Flutes, clarinets and staccato, keyswitches C0-D0"),
        blurb="Breathy flute pair, clarinet pair and a woodwind staccato."))
    I.append(Instrument(
        "Timpani", "Cinematic Timpani", CAT_ORCH, "artic", "orchestral.timpani",
        _rr_zones(["HitRR1", "HitRR2", "RollP", "RollF"], [38, 43, 48, 53], 36, 57, 1000), channels=1,
        cfg=dict(arts=[dict(name="Hits", type="short", groups=["HitRR1", "HitRR2"], ks=24),
                       dict(name="Roll", type="sus", groups=["RollP", "RollF"], ks=25)],
                 range=(36, 57), attack=0, release=600, fx=ACOUSTIC_FX, pedal=0, vrange=30,
                 fx_defaults=dict(tone=1000, reverb=300, width=400, rev_size=850, rev_decay=650),
                 info="Cinematic Timpani  |  C0 hits, C#0 rolls (CC1 = roll dynamics)"),
        blurb="Pitched timpani hits with round robins and looped rolls with crescendo control."))
    I.append(Instrument(
        "EPiano", "Electric Piano", CAT_ORCH, "keys", "band.epiano",
        zones_for(["V1", "V2", "V3"], _roots(28, 100), 21, 108, seed_base=1100), channels=1, norm="peak",
        cfg=dict(patches=[dict(name="Tine EP", layers=[["V1"], ["V2"], ["V3"]], splits=[52, 98])], range=(21, 108),
                 attack=0, release=180, vrange=28, fx=["filter", "eppre", "stereo", "choral", "replika", "raum"],
                 fx_defaults=dict(tone=1000, trem=300, reverb=200, chorus=150, width=500),
                 info="Electric Piano  |  3 velocity layers, tremolo and drive on the SOUND page"),
        blurb="FM tine electric piano with velocity-dependent bark, tremolo preamp."))
    gtr_g = ["V1RR1", "V1RR2", "V2RR1", "V2RR2"]
    I.append(Instrument(
        "Guitar", "Nylon Guitar", CAT_ORCH, "keys", "band.guitar",
        zones_for(gtr_g, _roots(40, 76), 38, 84, seed_base=1200), channels=1, norm="peak",
        cfg=dict(patches=[dict(name="Nylon", layers=[["V1RR1", "V1RR2"], ["V2RR1", "V2RR2"]], splits=[88])],
                 range=(38, 84), attack=0, release=450, vrange=24, let_ring=0, fx=ACOUSTIC_FX,
                 fx_defaults=dict(tone=1000, reverb=220, width=400),
                 info="Nylon Guitar  |  Use PERFORM > Chord + Strum for strummed chords"),
        blurb="Physically modelled nylon-string guitar with body resonance, 2 layers x 2 round robins."))
    I.append(Instrument(
        "Bass", "Finger Bass", CAT_ORCH, "keys", "band.finger_bass",
        zones_for(gtr_g, _roots(28, 58), 23, 64, seed_base=1300), channels=1, norm="peak",
        cfg=dict(patches=[dict(name="Finger", layers=[["V1RR1", "V1RR2"], ["V2RR1", "V2RR2"]], splits=[90])],
                 range=(23, 64), attack=0, release=120, vrange=20, fx=["filter", "supergt", "stereo", "choral", "replika", "raum"],
                 fx_defaults=dict(tone=1000, drive=150, reverb=0, width=0),
                 info="Finger Bass  |  2 velocity layers x 2 round robins"),
        blurb="Fingered electric bass model with pickup comb filtering and thump."))

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
    kz = []
    for gi, g in enumerate(gtr_g):
        for pi, (key, name, piece, ln, var, bus, pan, cg, cut) in enumerate(kit):
            kz.append(Zone(g, key, key, key, seed=1400 + gi * 100 + pi, p=dict(piece=piece, len=ln, var=var)))
    I.append(Instrument(
        "Drums", "Studio Drum Kit", CAT_ORCH, "drums", "band.drums", kz, channels=1, norm="peak",
        cfg=dict(buses=["Kick", "Snare", "Toms", "Hats", "Cymbals", "Perc"],
                 pieces=[dict(key=k, name=nm, bus=b, pan=pn, cg=cg, cut=cut,
                              layers=[["V1RR1", "V1RR2"], ["V2RR1", "V2RR2"]], splits=[90])
                         for (k, nm, _, _, _, b, pn, cg, cut) in kit],
                 fx=["filter", "comp", "supergt", "stereo", "raum"], pedal=0,
                 fx_defaults=dict(tone=1000, comp=300, drive=150, reverb=180, width=500, rev_size=450, rev_decay=400),
                 info="Studio Drum Kit  |  General MIDI layout, open hat choked by closed/pedal hat"),
        blurb="Synthesised acoustic/hybrid kit: 20 pieces, 2 velocity layers x 2 round robins."))
    I.append(Instrument(
        "Organ", "Drawbar Organ", CAT_ORCH, "keys", "band.organ",
        zones_for(["Full", "Soft"], _roots(36, 96), 24, 108, seed_base=1500), channels=1,
        cfg=dict(patches=[dict(name="Full Drawbars", layers=[["Full"]], loop=True),
                          dict(name="Soft Flutes", layers=[["Soft"]], loop=True)],
                 range=(24, 108), attack=3, release=45, vrange=0, restrike=20,
                 fx=["filter", "rotator", "supergt", "replika", "raum"],
                 fx_defaults=dict(tone=1000, drive=180, reverb=180),
                 info="Drawbar Organ  |  Mod wheel up = fast rotary"),
        blurb="Tonewheel-style additive organ with key click, rotary speaker and drive."))
    mal = []
    for gi, (g, lo, hi, klo, khi) in enumerate([("Marimba", 36, 96, 33, 99), ("Vibes", 53, 89, 50, 92),
                                                ("Celesta", 60, 108, 57, 112), ("Glock", 72, 108, 70, 112)]):
        for zi, (r, zlo, zhi) in enumerate(keymap(_roots(lo, hi), klo, khi)):
            mal.append(Zone(g, r, zlo, zhi, seed=1600 + gi * 100 + zi))
    I.append(Instrument(
        "Mallets", "Cinematic Mallets", CAT_ORCH, "keys", "band.mallets", mal, channels=1, norm="peak",
        cfg=dict(patches=[dict(name="Marimba", layers=[["Marimba"]]), dict(name="Vibraphone", layers=[["Vibes"]]),
                          dict(name="Celesta", layers=[["Celesta"]]), dict(name="Glockenspiel", layers=[["Glock"]])],
                 range=(33, 112), attack=0, release=400, vrange=24, let_ring=1, fx=ACOUSTIC_FX,
                 fx_defaults=dict(tone=1000, reverb=320, width=500, rev_size=750, rev_decay=650),
                 info="Cinematic Mallets  |  Pick an instrument, layer a second one on top"),
        blurb="Modal-synthesis marimba, vibraphone, celesta and glockenspiel."))
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
    pz = []
    for gi, g in enumerate(["RR1", "RR2"]):
        for pi, (key, name, piece, ln, bus, pan, hold) in enumerate(perc):
            pz.append(Zone(g, key, key, key, seed=1700 + gi * 100 + pi, p=dict(piece=piece, len=ln, hold=hold)))
    I.append(Instrument(
        "OrchPerc", "Orchestral Percussion", CAT_ORCH, "drums", "cinematic.orch_perc", pz, channels=1, norm="peak",
        cfg=dict(buses=["Drums", "Taiko", "Snare", "Cymbals", "Metals"],
                 pieces=[dict(key=k, name=nm, bus=b, pan=pn, hold=h, layers=[["RR1", "RR2"]], splits=[127])
                         for (k, nm, _, _, b, pn, h) in perc],
                 fx=["filter", "comp", "stereo", "raum"], pedal=0, spread=60,
                 fx_defaults=dict(tone=1000, comp=150, reverb=320, width=600, rev_size=850, rev_decay=650),
                 info="Orchestral Percussion  |  Hold C#2 / G2 for rolls, CC1 = roll level"),
        blurb="Gran cassa, taiko, snare, cymbals, tam-tam and metals with round robins and rolls."))

    # ------------------------------------------------------------------ 03 Cinematic
    I.append(Instrument(
        "Braams", "Braams and Hits", CAT_CINE, "keys", "cinematic.braams",
        zones_for(["Braam", "Blaster"], _roots(24, 48), 21, 60, seed_base=1800), norm="peak",
        cfg=dict(patches=[dict(name="Braam", layers=[["Braam"]]), dict(name="Blaster", layers=[["Blaster"]])],
                 range=(21, 60), attack=0, release=900, vrange=18, let_ring=1, fx=SYNTH_FX,
                 filter_type="$FILTER_TYPE_LDR_LP4", resonance=True,
                 fx_defaults=dict(tone=1000, reverb=300, width=600, rev_size=900, rev_decay=750),
                 info="Braams and Hits  |  Low keys = biggest braams. Layer Braam + Blaster"),
        blurb="Trailer braams: brass-like saw walls and a ring-modulated, folded 'Blaster'."))
    drones = ["DarkStrings", "GlassAir", "ChoirDrone", "MetalShimmer", "SubRumble", "GhostPad", "TensionCluster", "Heartbeat"]
    dz = [Zone(g, 48, 24, 96, seed=1900 + i) for i, g in enumerate(drones)]
    I.append(Instrument(
        "Drones", "Drones and Textures", CAT_CINE, "synth", "cinematic.drones", dz,
        cfg=dict(layers=drones, layer_a=0, layer_b=6, blend=200, attack=1500, release=3500, vsens=10, movement=350,
                 range=(24, 96), resonance=True, filter_type="$FILTER_TYPE_LDR_LP4", fx=SYNTH_FX,
                 fx_defaults=dict(tone=850, reverb=450, width=700, delay=100, rev_size=900, rev_decay=800),
                 info="Drones and Textures  |  Pick two textures and blend them"),
        blurb="Eight evolving underscore beds: strings, air, choir, metal, rumble, ghost, tension, heartbeat."))
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
    fz = [Zone("FX", k, k, k, seed=2000 + i, p=dict(fx=kind, len=ln)) for i, (k, _, kind, ln, _) in enumerate(fxl)]
    I.append(Instrument(
        "FX", "Cinematic FX", CAT_CINE, "drums", "cinematic.fx", fz, norm="peak",
        cfg=dict(buses=["Impacts", "Risers", "Whooshes", "Downers", "Misc"],
                 pieces=[dict(key=k, name=nm, bus=b, layers=[["FX"]], splits=[127]) for (k, nm, _, _, b) in fxl],
                 fx=["filter", "stereo", "replika", "raum"], pedal=0, humanize=0, spread=0, vrange=18,
                 fx_defaults=dict(tone=1000, reverb=200, width=500, rev_size=900, rev_decay=700),
                 info="Cinematic FX  |  C2-G3: impacts, risers, whooshes, downers, stingers"),
        blurb="Twenty trailer-style one-shots: impacts, risers, whooshes, downers and stingers."))
    return I


CATALOG = build_catalog()
BY_KEY = {i.key: i for i in CATALOG}
