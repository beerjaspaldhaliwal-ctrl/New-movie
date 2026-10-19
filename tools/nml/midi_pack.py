"""MIDI phrase pack: chord progressions, ostinatos, bass lines, drum grooves,
cinematic percussion, melodies and hits written for the library's instruments.

Every file is a type-0 Standard MIDI File on channel 1 (480 ticks per quarter)
with the tempo and time signature set. Drum files use the key maps of the kits
named in their file names; melodic files stay inside the target instrument's
range. String and brass phrases carry mod-wheel (CC1) dynamics.
"""
import os
import random
import struct

PPQ = 480
Q, E, S, H, W = PPQ, PPQ // 2, PPQ // 4, PPQ * 2, PPQ * 4
BAR = 4 * Q

NOTE = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
        "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
QUAL = {"": (0, 4, 7), "m": (0, 3, 7), "sus4": (0, 5, 7), "sus2": (0, 2, 7), "dim": (0, 3, 6), "aug": (0, 4, 8),
        "7": (0, 4, 7, 10), "m7": (0, 3, 7, 10), "maj7": (0, 4, 7, 11), "add9": (0, 4, 7, 14), "5": (0, 7)}


def chord(name):
    """'Dm' -> (root pitch class, intervals)."""
    root = name[:2] if len(name) > 1 and name[1] in "#b" else name[:1]
    return NOTE[root], QUAL[name[len(root):]]


# ----------------------------------------------------------------------------- SMF writer
def _vlq(n):
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.append((n & 0x7F) | 0x80)
        n >>= 7
    return bytes(reversed(out))


class Clip:
    def __init__(self, name, bpm, num=4, den=4):
        self.name, self.bpm, self.num, self.den = name, bpm, num, den
        self.events = []  # (tick, order, bytes)

    def note(self, t, key, length, vel=96):
        key = int(key)
        if not 0 <= key <= 127 or length <= 0:
            return
        vel = max(1, min(127, int(vel)))
        self.events.append((int(t), 1, bytes([0x90, key, vel])))
        self.events.append((int(t + length), 0, bytes([0x80, key, 0])))

    def cc(self, t, num, val):
        self.events.append((int(t), 2, bytes([0xB0, num, max(0, min(127, int(val)))])))

    def ramp(self, t0, t1, num, v0, v1, step=Q // 4):
        t = t0
        while t <= t1:
            self.cc(t, num, v0 + (v1 - v0) * (t - t0) / max(1, t1 - t0))
            t += step

    def bytes(self):
        tempo = int(round(60_000_000 / self.bpm))
        meta = [(0, -3, b"\xff\x03" + _vlq(len(self.name.encode())) + self.name.encode()),
                (0, -2, b"\xff\x51\x03" + tempo.to_bytes(3, "big")),
                (0, -1, bytes([0xFF, 0x58, 0x04, self.num, {2: 1, 4: 2, 8: 3}[self.den], 24, 8]))]
        evs = sorted(meta + self.events, key=lambda e: (e[0], e[1]))
        data, last = b"", 0
        for t, _, msg in evs:
            data += _vlq(t - last) + msg
            last = t
        data += _vlq(0) + b"\xff\x2f\x00"
        return b"MThd" + struct.pack(">IHHH", 6, 0, 1, PPQ) + b"MTrk" + struct.pack(">I", len(data)) + data


# ----------------------------------------------------------------------------- harmony helpers
def voice(prev, name, lo=55, hi=76, n=4):
    """Upper voices for a chord, as close as possible to the previous voicing."""
    root, iv = chord(name)
    pcs = [(root + i) % 12 for i in iv]
    cands = [k for k in range(lo, hi + 1) if k % 12 in pcs]
    best, best_cost = None, None
    import itertools
    for combo in itertools.combinations(cands, n):
        if set(k % 12 for k in combo) != set(pcs) and len(pcs) <= n:
            continue
        if max(combo) - min(combo) > 14:
            continue
        cost = sum(min(abs(a - b) for b in prev) for a in combo) if prev else abs(sum(combo) / n - (lo + hi) / 2)
        if best is None or cost < best_cost:
            best, best_cost = combo, cost
    return list(best)


def bass_note(name, lo=36):
    root, _ = chord(name)
    k = lo + (root - lo) % 12
    return k


def progression(clip, chords, bars_per=1, lo=55, hi=76, vel=80, bass=True, swell=True, start=0):
    prev = None
    t = start
    for c in chords:
        v = voice(prev, c, lo, hi)
        prev = v
        length = BAR * bars_per
        for k in v:
            clip.note(t, k, length - 10, vel)
        if bass:
            clip.note(t, bass_note(c), length - 10, vel)
        if swell:  # CC1 dynamics: breathe up into each chord change
            clip.ramp(t, t + length // 2, 1, 55, 95)
            clip.ramp(t + length // 2, t + length - Q // 4, 1, 95, 60)
        t += length
    return t


# ----------------------------------------------------------------------------- the pack
def build():
    files = {}
    rnd = random.Random(7)

    def add(folder, name, clip):
        files[os.path.join(folder, name + ".mid")] = clip.bytes()

    # 01 chord progressions --------------------------------------------------
    F = "01 Chord Progressions"
    progs = [
        ("Epic Minor i-VI-III-VII (Dm, 90 BPM)", 90, ["Dm", "Bb", "F", "C"] * 2),
        ("Heroic I-V-vi-IV (C, 96 BPM)", 96, ["C", "G", "Am", "F"] * 2),
        ("Dark Tension i-VI-iv-V (Am, 80 BPM)", 80, ["Am", "F", "Dm", "E"] * 2),
        ("Mystery Phrygian i-bII (Em, 70 BPM)", 70, ["Em", "F", "Em", "F", "Em", "F", "Em", "Em"]),
        ("Wonder Lydian I-II (D, 84 BPM)", 84, ["D", "E", "D", "E", "Bm", "G", "D", "E"]),
        ("Sad Strings vi-IV-I-V (C, 72 BPM)", 72, ["Am", "F", "C", "G"] * 2),
        ("Chromatic Mediants (C, 76 BPM)", 76, ["C", "Ab", "C", "E", "C", "Ab", "Fm", "C"]),
        ("Trailer Rise (Dm, 100 BPM)", 100, ["Dm", "Dm", "Bb", "Bb", "Gm", "Gm", "Asus4", "A"]),
        ("Space Drift maj7 (F, 64 BPM)", 64, ["Fmaj7", "Em7", "Dm7", "Cmaj7"] * 2),
    ]
    for name, bpm, chs in progs:
        c = Clip(name, bpm)
        progression(c, chs)
        add(F, name + " - Strings Pads Choir", c)

    # 02 ostinatos and arpeggios ----------------------------------------------
    F = "02 Ostinatos and Arps"
    c = Clip("String Ostinato 16ths", 120)
    pat = [0, 0, -5, 0, 3, 0, -5, 0]  # relative to the chord root, 16ths
    t = 0
    for ch in ["Dm", "Bb", "F", "C"] * 2:
        root = 62 + (chord(ch)[0] - 62) % 12
        if root > 67:
            root -= 12
        third = chord(ch)[1][1]
        for rep in range(2):
            for i, iv in enumerate(pat):
                k = root + (third if iv == 3 else iv)
                c.note(t, k, S - 20, 100 if i % 4 == 0 else 78)
                t += S
        t += BAR - 16 * S
    add(F, "String Ostinato 16ths (Dm, 120 BPM) - Strings Staccato", c)

    c = Clip("Gallop", 132)
    t = 0
    for ch in ["Dm", "Dm", "Bb", "C"] * 2:
        k = 38 + (chord(ch)[0] - 2) % 12
        if k > 45:
            k -= 12
        for b in range(4):
            c.note(t, k, E - 20, 112)
            c.note(t + E, k, S - 20, 84)
            c.note(t + E + S, k, S - 20, 90)
            t += Q
    add(F, "Gallop 8th-16th-16th (Dm, 132 BPM) - Strings Staccato or Brass Staccato", c)

    c = Clip("Broken Chords", 100)
    t, prev = 0, None
    for ch in ["Am", "F", "C", "G"] * 2:
        v = voice(prev, ch, 57, 76, 3)
        prev = v
        seq = [bass_note(ch, 45), v[0], v[1], v[2], v[1] + 12 if v[1] + 12 <= 88 else v[2], v[2], v[1], v[0]]
        for i, k in enumerate(seq):
            c.note(t + i * E, k, E * 2, 88 if i == 0 else 70)
        t += BAR
    add(F, "Broken Chords 8ths (Am, 100 BPM) - Harp Piano Pluck", c)

    c = Clip("Synth Pulse", 118)
    t, prev = 0, None
    for ch in ["Em", "C", "G", "D"] * 2:
        v = voice(prev, ch, 52, 71, 3)
        prev = v
        for i in range(16):
            for k in v:
                c.note(t + i * S, k, S - 30, 96 if i % 4 == 0 else 72)
        t += BAR
    add(F, "Synth Pulse 16ths (Em, 118 BPM) - Supersaw Pluck Tape Keys", c)

    c = Clip("Rising Spiccato", 140)
    t = 0
    scale = [0, 2, 3, 5, 7, 8, 10]
    for b in range(8):
        base = 50 + (b // 2) * 2
        for i in range(16):
            deg = (i + b) % 7
            k = base + scale[deg] + 12 * ((i + b) // 7 % 2)
            c.note(t + i * S, k, S - 15, 70 + i * 3)
        t += BAR
    add(F, "Rising Spiccato Run (Dm, 140 BPM) - Strings Staccato", c)

    c = Clip("Pizzicato Walk", 108)
    t = 0
    walk = [45, 48, 52, 55, 53, 52, 50, 48, 46, 50, 53, 57, 55, 53, 52, 50]
    for rep in range(2):
        for i, k in enumerate(walk):
            c.note(t, k, E, 92 if i % 2 == 0 else 74)
            t += E
    add(F, "Pizzicato Walk (Am, 108 BPM) - Strings Pizzicato or Solo Cello Pizzicato", c)

    # 03 bass lines -----------------------------------------------------------
    F = "03 Bass Lines"
    c = Clip("Sub Roots", 90)
    for i, ch in enumerate(["Dm", "Bb", "F", "C"] * 2):
        c.note(i * BAR, bass_note(ch, 26), BAR - 20, 100)
    add(F, "Sustained Roots (Dm, 90 BPM) - Analog Mono Bass 808 Bass", c)

    c = Clip("Synthwave Octaves", 105)
    t = 0
    for ch in ["Am", "F", "C", "G"] * 2:
        k = bass_note(ch, 33)
        for i in range(8):
            c.note(t + i * E, k + (12 if i % 2 else 0), E - 30, 100 if i % 2 == 0 else 80)
        t += BAR
    add(F, "Synthwave Octaves 8ths (Am, 105 BPM) - Analog Mono Bass Seq Bass", c)

    c = Clip("Trap 808", 140)
    pattern = [(0, 0, Q + E), (Q + E, 0, E), (2 * Q + E, 0, Q), (3 * Q + E, 3, E)]
    for b in range(8):
        root = [25, 25, 30, 28][b % 4]
        for off, iv, ln in pattern:
            c.note(b * BAR + off, root + iv, ln - 10, 110)
    add(F, "Trap 808 Pattern (C#m, 140 BPM) - 808 Bass", c)

    c = Clip("Cinematic Pulse", 120)
    for b in range(8):
        k = [38, 38, 34, 36][b % 4]
        for i in range(8):
            c.note(b * BAR + i * E, k, E - 40, 108 if i in (0, 3, 6) else 84)
    add(F, "Cinematic Pulse 8ths (Dm, 120 BPM) - Finger Bass Seq Bass", c)

    # 04 drum grooves ---------------------------------------------------------
    F = "04 Drum Grooves"
    K, SN, CH, OH, CR, RD, PH = 36, 38, 42, 46, 49, 51, 44

    def groove(name, bpm, bars, fn):
        c = Clip(name, bpm)
        for b in range(bars):
            fn(c, b * BAR, b)
        return c

    def rock(c, t, b):
        for i in range(8):
            c.note(t + i * E, CH, E // 2, 100 if i % 2 == 0 else 72 + rnd.randint(-6, 6))
        for off in (0, 2 * Q + E):
            c.note(t + off, K, E, 112)
        for off in (Q, 3 * Q):
            c.note(t + off, SN, E, 110)
        if b == 0:
            c.note(t, CR, Q, 108)
        if b == 3:  # tom fill
            for i, tom in enumerate([50, 50, 48, 48, 47, 45, 43, 41]):
                c.note(t + 2 * Q + i * S, tom, S, 100 + i * 2)
    add(F, "Rock 8ths with Fill (100 BPM) - Studio Drum Kit", groove("Rock 8ths", 100, 4, rock))

    def ballad(c, t, b):
        for i in range(4):
            c.note(t + i * Q, RD, E, 86)
        c.note(t, K, E, 108)
        c.note(t + 2 * Q + E, K, E, 90)
        c.note(t + 2 * Q, SN, E, 104)
        if b % 2 == 1:
            c.note(t + 3 * Q + E, 37, S, 70)
    add(F, "Halftime Ballad (70 BPM) - Studio Drum Kit", groove("Halftime Ballad", 70, 4, ballad))

    def disco(c, t, b):
        for i in range(4):
            c.note(t + i * Q, K, E, 112)
            c.note(t + i * Q + E, OH, E, 90)
            c.note(t + i * Q, CH, S, 80)
        for off in (Q, 3 * Q):
            c.note(t + off, 39, E, 104)
    add(F, "Four on the Floor (120 BPM) - Studio Drum Kit", groove("Four on the Floor", 120, 4, disco))

    def synthwave(c, t, b):
        for i in range(16):
            c.note(t + i * S, CH, S // 2, 92 if i % 4 == 0 else 64)
        for off in (0, 2 * Q):
            c.note(t + off, K, E, 115)
        for off in (Q, 3 * Q):
            c.note(t + off, SN, E, 112)
        if b == 0:
            c.note(t, CR, Q, 100)
        if b == 3:
            for i, tom in enumerate([48, 47, 45, 43, 41, 41]):
                c.note(t + 2 * Q + i * (2 * Q // 6), tom, E, 108)
    add(F, "Synthwave Gated (105 BPM) - Synthwave Kit", groove("Synthwave Gated", 105, 4, synthwave))

    def trap(c, t, b):
        c.note(t, 36, Q, 118)
        c.note(t + Q + E + S, 36, E, 104)
        c.note(t + 3 * Q + E, 36, E, 100)
        c.note(t + 2 * Q, 38, E, 115)
        c.note(t + 2 * Q, 39, E, 100)
        i = 0
        while i < 16:
            if i in (6, 14) and b % 2 == 1:  # 1/32 roll
                for r in range(4):
                    c.note(t + i * S + r * (S // 2), 42, S // 3, 70 + r * 10)
                i += 2
                continue
            if i == 11 and b == 3:  # triplet roll
                for r in range(3):
                    c.note(t + i * S + r * (2 * S // 3), 42, S // 3, 80 + r * 8)
                i += 2
                continue
            c.note(t + i * S, 42 if i % 2 == 0 else 44, S // 2, 96 if i % 4 == 0 else 74)
            i += 1
        if b == 3:
            c.note(t + 3 * Q, 46, Q, 90)
    add(F, "Trap Hats and Rolls (140 BPM) - Trap Kit", groove("Trap Hats and Rolls", 140, 4, trap))

    def shuffle(c, t, b):
        trip = Q // 3
        for i in range(4):
            c.note(t + i * Q, RD, trip, 88)
            c.note(t + i * Q + 2 * trip, RD, trip, 70)
        c.note(t, K, E, 106)
        c.note(t + 2 * Q + 2 * trip, K, E, 92)
        for off in (Q, 3 * Q):
            c.note(t + off, SN, E, 108)
        c.note(t + Q, PH, E, 70)
        c.note(t + 3 * Q, PH, E, 70)
    add(F, "Shuffle Ride (110 BPM) - Studio Drum Kit", groove("Shuffle Ride", 110, 4, shuffle))

    # 05 cinematic percussion -------------------------------------------------
    F = "05 Cinematic Percussion"
    c = Clip("Trailer Build", 120)
    t = 0
    c.note(t, 36, BAR, 127)
    c.note(t, 48, BAR, 100)
    for b in range(1, 7):
        t = b * BAR
        sub = [Q, Q, E, E, S, S][b - 1]
        n = BAR // sub
        for i in range(n):
            vel = 70 + int(50 * (b / 6)) + (10 if i % 4 == 0 else 0)
            c.note(t + i * sub, 40 if i % 2 == 0 else [41, 43, 45][i % 3], sub, vel)
        c.note(t, 37, Q, 110)
    t = 7 * BAR
    c.note(t, 39, Q, 127)
    c.note(t, 36, BAR, 127)
    c.note(t, 51, BAR, 110)
    add(F, "Trailer Build 8 bars (120 BPM) - Hybrid Trailer Percussion", c)

    c = Clip("Taiko Ensemble", 90)
    pattern = [(0, 39, 120), (E, 38, 80), (Q + E, 38, 96), (2 * Q, 39, 116), (3 * Q, 38, 90), (3 * Q + E, 40, 84)]
    for b in range(8):
        for off, k, v in pattern:
            c.note(b * BAR + off, k, E, v + (8 if b >= 4 else 0))
        if b % 4 == 3:
            for i in range(4):
                c.note(b * BAR + 3 * Q + i * S, 38, S, 90 + i * 8)
    c.note(0, 36, BAR, 110)
    c.note(4 * BAR, 48, BAR, 100)
    add(F, "Taiko Ensemble (90 BPM) - Orchestral Percussion", c)

    c = Clip("Timpani", 80)
    c.note(0, 24, E, 100)  # keyswitch: Hits
    for b in range(3):
        for off, k in ((0, 38), (Q + E, 38), (2 * Q, 45), (3 * Q, 38)):
            c.note(b * BAR + off + 1, k, E, 100 if off == 0 else 82)
    c.note(3 * BAR - E, 25, E, 100)  # keyswitch: Roll
    c.note(3 * BAR, 38, BAR, 90)
    c.ramp(3 * BAR, 4 * BAR - Q, 1, 30, 127)
    c.note(4 * BAR - 2, 24, 1, 100)
    c.note(4 * BAR, 38, Q, 127)
    add(F, "Timpani Hits into Roll Crescendo (80 BPM) - Cinematic Timpani", c)

    c = Clip("Tension", 100)
    c.note(0, 36, 8 * BAR, 100)  # clock loop
    c.note(2 * BAR, 37, 6 * BAR, 90)  # heartbeat loop
    c.note(4 * BAR, 42, 2 * BAR, 90)  # bowed cymbal
    c.note(6 * BAR, 40, 2 * BAR, 100)  # string scrape
    c.note(8 * BAR, 45, BAR, 120)  # stinger low
    add(F, "Tension Bed 8 bars + Stinger (100 BPM) - Tension Toolkit", c)

    # 06 melodies -------------------------------------------------------------
    F = "06 Melodies"

    def melody(name, bpm, notes, cc=True, vel=96):
        c = Clip(name, bpm)
        t = 0
        for k, d in notes:
            if k is not None:
                c.note(t, k, d - 15, vel)
                if cc and d >= H:
                    c.ramp(t, t + d - Q // 2, 1, 60, 110)
            t += d
        return c

    hero = [(55, Q + E), (60, E), (62, Q), (64, Q), (67, H + Q), (65, E), (64, E), (62, H), (60, H),
            (55, Q + E), (60, E), (62, Q), (64, Q), (69, H + Q), (67, Q), (72, W)]
    add(F, "Heroic Theme (C, 92 BPM) - French Horns Brass", melody("Heroic Theme", 92, hero))
    sad = [(76, H), (74, Q), (72, Q), (71, H + Q), (69, Q), (72, H), (71, Q), (69, Q), (68, W),
           (69, H), (71, Q), (72, Q), (74, H + Q), (76, Q), (69, W)]
    add(F, "Lament Theme (Am, 66 BPM) - Solo Violin Solo Cello", melody("Lament Theme", 66, sad))
    duduk = [(62, H), (63, Q), (62, E), (60, E), (62, H + Q), (None, Q), (65, Q), (63, Q), (62, Q), (60, Q),
             (58, H), (57, Q), (58, E), (60, E), (62, W)]
    add(F, "Desert Lament (D Phrygian, 60 BPM) - Duduk", melody("Desert Lament", 60, duduk))
    lull = [(72, Q), (76, Q), (79, Q), (76, Q), (74, Q), (77, Q), (81, H), (79, Q), (76, Q), (72, Q), (74, Q),
            (76, H), (72, H)] * 2
    add(F, "Lullaby (C, 84 BPM) - Kalimba Celesta Hang", melody("Lullaby", 84, lull, cc=False, vel=84))
    sitar = [(62, E), (63, E), (66, Q), (67, E), (66, E), (63, Q), (62, H), (60, E), (62, E), (63, Q), (66, Q),
             (67, H + Q), (None, Q)]
    add(F, "Raga Phrase (D Bhairav, 76 BPM) - Sitar", melody("Raga Phrase", 76, sitar, cc=False))

    # 07 braams and hits ------------------------------------------------------
    F = "07 Braams and Hits"
    c = Clip("Braams", 70)
    for b, k in enumerate([26, 26, 22, 24]):
        c.note(b * 2 * BAR, k, int(1.5 * BAR), 120)
        c.note(b * 2 * BAR, k + 12, int(1.5 * BAR), 110)
    add(F, "Braam Hits (Dm, 70 BPM) - Braams and Hits", c)
    c = Clip("Riser to Hit", 100)
    c.note(0, 44, 2 * BAR, 110)  # tension riser
    c.note(BAR, 45, BAR, 100)  # reverse cymbal
    c.note(2 * BAR, 38, BAR, 127)  # trailer hit
    c.note(2 * BAR, 37, BAR, 120)  # sub drop
    c.note(3 * BAR + 2 * Q, 47, Q, 110)  # whoosh
    add(F, "Riser into Trailer Hit (100 BPM) - Cinematic FX", c)
    return files


def export(lib_dir):
    root = os.path.join(lib_dir, "MIDI")
    files = build()
    for rel, data in files.items():
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
    return len(files)
