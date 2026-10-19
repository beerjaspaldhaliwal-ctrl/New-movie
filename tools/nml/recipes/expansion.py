"""Expansion pack: new synths, cinematic tools, world instruments, kits,
electric guitar, solo strings, horns, harp and felt piano."""
import numpy as np
from scipy import signal

from .. import dsp
from ..dsp import SR, mtof, secs, LN1000
from .common import hall_ir, room_ir, unison, sustain_loop, key_scale, lerp
from .band import drum_piece, _cymbal, _metal
from .cinematic import _membrane, perc_piece
from .orchestral import _bowed_section, _brass_section, _flute, _timp_hit
from .synths import _choir_source, FORMANTS


def _layer(z, default=1):
    """Velocity layer number from a group name like 'V2RR1' (1-based)."""
    g = z.group
    return int(g[1]) if len(g) > 1 and g[0] == "V" and g[1].isdigit() else default


def _rr(z):
    return int(z.group[-1]) if z.group[-1].isdigit() else 1


# ========================================================================== SYNTHS
def wavetable_pad(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    n = secs(2.6)
    t = dsp.tvec(n)
    if z.group == "Morph":
        # additive spectrum that morphs between a hollow (odd) and a vocal (formant) table
        nh = int(min(90, 0.42 * SR / f0))
        k = np.arange(1, nh + 1)
        table_a = np.where(k % 2 == 1, 1.0 / k, 0.08 / k)
        formant = np.exp(-((k * f0 - 1100.0) / 500.0) ** 2) * 1.6 + np.exp(-((k * f0 - 2600.0) / 700.0) ** 2) * 0.7
        table_b = (1.0 / k ** 1.3) * (0.4 + formant)
        x = np.zeros((n, 2))
        for v, (det, p) in enumerate([(-6, -0.8), (0, 0.0), (6, 0.8)]):
            fr = f0 * dsp.cents_to_ratio(det + dsp.drift_cents(n, rng, 2.5))
            base = 2 * np.pi * np.cumsum(fr) / SR
            w = 0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(0.15, 0.3) * t + rng.uniform(0, 6))
            out = np.zeros(n)
            for i, kk in enumerate(k):
                amp = (1 - w) * table_a[i] + w * table_b[i]
                out += amp * np.sin(kk * base + rng.uniform(0, 6))
            x += dsp.pan(out, p)
        x = dsp.butter(x, min(12000, 2500 + f0 * 10), "low", 2)
        x = dsp.chorus(x, rng, voices=3, rate=0.2, depth_ms=3.0, mix=0.35)
        x = dsp.reverb(x, hall_ir(2.6, 201), 0.3)
    else:  # Digital: wavefolded triangle with a slowly moving fold, rendered at 4x
        def render(m, sr):
            tt = np.arange(m) / sr
            out = np.zeros((m, 2))
            for det, p in [(-4, -0.6), (4, 0.6)]:
                fr = f0 * dsp.cents_to_ratio(det + dsp.drift_cents(m, rng, 2, 0.3, sr))
                tri = dsp.triangle(fr, sr, rng.uniform())
                amt = 1.2 + 1.0 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.23 * tt + rng.uniform(0, 6)))
                out += dsp.pan(dsp.fold(tri * 0.9, amt), p)
            return out
        x = dsp.oversampled(render, n, 4)
        x = dsp.butter(x, 9000, "low", 2)
        x = dsp.hp(x, 60)
        x = dsp.chorus(x, rng, voices=2, rate=0.3, depth_ms=2.0, mix=0.3)
        x = dsp.reverb(x, hall_ir(2.2, 203), 0.22)
    x = dsp.fade_edges(x, 0.01, 0.001)
    return sustain_loop(x, 0.95, 1.3, 0.45)


def synth_brass(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    n = secs(2.2)
    t = dsp.tvec(n)
    x = unison(n, f0, rng, voices=4, spread_cents=9, osc="saw", width=0.8)
    x += unison(n, f0 * 0.5, rng, voices=1, osc="pulse", pw=0.4) * 0.3 * (f0 > 70)
    env = np.clip(t / 0.07, 0, 1) ** 0.8
    fenv = env * (0.45 + 0.55 * np.exp(-np.clip(t - 0.07, 0, None) / 0.35))
    cut = f0 * 1.4 + (2600 + f0 * 4) * fenv
    x = dsp.lp24(x, cut, 0.9)
    x = dsp.saturate(dsp.norm_rms(x, 0.2), 1.3)
    x = dsp.chorus(x, rng, voices=2, rate=0.45, depth_ms=2.0, mix=0.3)
    x = dsp.reverb(x, hall_ir(1.8, 205), 0.15)
    x = dsp.fade_edges(x, 0.002, 0.001)
    return sustain_loop(x, 0.85, 1.0, 0.3)


def _tape(x, rng, sr=SR):
    """Wow, flutter, head saturation, band limits and hiss."""
    n = x.size
    t = np.arange(n) / sr
    wow = 0.0016 * np.sin(2 * np.pi * 0.55 * t + rng.uniform(0, 6)) + 0.0004 * np.sin(2 * np.pi * 7.1 * t)
    d = (0.004 + wow + 0.0005 * dsp.smooth_noise(n, rng, 2.0)) * sr
    y = dsp.delay_read(x, d)
    y = dsp.saturate(dsp.norm_rms(y, 0.25), 1.5)
    y = dsp.hp(y, 110)
    y = dsp.butter(y, 6200, "low", 2)
    return y + dsp.hp(rng.standard_normal(n), 3000) * 0.004


def tape_keys(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    n = secs(2.3)
    t = dsp.tvec(n)
    if z.group == "TapeFlute":
        x = _flute(n, f0, rng, attack=0.05) + _flute(n, f0 * dsp.cents_to_ratio(6), rng, attack=0.06) * 0.7
    elif z.group == "TapeStrings":
        x = dsp.mono(_bowed_section(n, f0, rng, "p", players=4, attack=0.08, vib=8))
    else:  # TapeChoir
        src = _choir_source(n, f0, rng, singers=6, vib_depth=15)
        x = dsp.mono(dsp.formant_bank(src, FORMANTS[("Aah", "f" if z.root >= 58 else "m")]))
    x = dsp.mono(x)
    x = _tape(x / (dsp.rms(x) + 1e-9) * 0.25, rng)
    x = x * np.clip(t / 0.03, 0, 1)
    x = dsp.fade_edges(x, 0.002, 0.001)
    return sustain_loop(x, 0.8, 1.15, 0.35)


def bass_808(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    n = secs(2.8)
    t = dsp.tvec(n)
    f = f0 * (1 + 0.6 * np.exp(-t / 0.025))
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) + 0.08 * np.sin(2 * ph)
    env = np.exp(-t * LN1000 / 3.2) * np.clip(t / 0.002, 0, 1)
    click = dsp.hp(rng.standard_normal(n), 2000) * np.exp(-t / 0.002) * 0.15
    x = body * env + click
    if z.group == "Dist":
        x = dsp.saturate(x * 3.0, 3.0)
        x = dsp.butter(x, 3800, "low", 2)
    else:
        x = dsp.saturate(x, 1.2)
    x = dsp.hp(x, 22)
    return dsp.fade_edges(x, 0.0005, 0.3), None


def seq_bass(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    n = secs(0.75)
    t = dsp.tvec(n)
    f = np.full(n, f0)
    x = 0.7 * dsp.saw(f * dsp.cents_to_ratio(-3), SR, rng.uniform()) + 0.6 * dsp.pulse(f * dsp.cents_to_ratio(4), 0.3, SR, rng.uniform())
    cut = f0 * 1.2 + 120 + (3800 + f0 * 2) * np.exp(-t / 0.06)
    x = dsp.lp24(x, cut, 2.4)
    x = dsp.saturate(dsp.norm_rms(x, 0.25), 1.8)
    x = x * dsp.env_exp(n, 0.9, attack=0.001)
    return dsp.fade_edges(x, 0.0005, 0.08), None


# ========================================================================== CINEMATIC
def trailer_perc(z):
    rng = np.random.default_rng(z.seed)
    piece = z.p["piece"]
    n = secs(z.p["len"])
    t = dsp.tvec(n)
    noise = rng.standard_normal(n)
    var = 1 + rng.normal(0, 0.012)
    if piece == "epicboom":
        x = perc_piece("boom", n, rng, var) + _membrane(n, rng, 55 * var, 2.2, 0.4, 1.0) * 0.6
        x += dsp.butter(noise, 900, "low", 2) * np.exp(-t / 0.08) * 0.8
        x = dsp.saturate(x, 2.2)
    elif piece == "distkick":
        x = drum_piece("kick", n, rng, 1.0, var)
        x = dsp.saturate(x * 2.5, 3.0) + np.sin(2 * np.pi * np.cumsum(40 + 60 * np.exp(-t / 0.1)) / SR) * np.exp(-t / 0.6) * 0.6
    elif piece == "hybridhit":
        x = perc_piece("taikoens", n, rng, var) * 0.8 + perc_piece("anvil", n, rng, 0.5 * var) * 0.3
        x += dsp.bp(noise, 1800, 0.6) * np.exp(-t / 0.05)
        x = dsp.saturate(x, 2.0)
    elif piece == "metalslam":
        f = 260 * var
        x = dsp.modal(n, [f, f * 1.73, f * 2.61, f * 3.9, f * 5.3, f * 7.2], [1, 0.8, 0.7, 0.5, 0.4, 0.3],
                      [1.2, 1.0, 0.8, 0.6, 0.5, 0.4], rng=rng, beat_cents=[8, -6, 11])
        x += dsp.hp(noise, 1500) * np.exp(-t / 0.02) * 1.5
        x = dsp.saturate(x, 2.0)
    elif piece == "taikostack":
        x = perc_piece("taikoens", n, rng, var) + perc_piece("taikoens", n, rng, 0.8 * var) * 0.7
    elif piece.startswith("disttom"):
        f0 = {"disttom1": 70, "disttom2": 95, "disttom3": 130}[piece] * var
        x = _membrane(n, rng, f0, 1.4, 0.35, 0.8)
        x = dsp.saturate(x * 2.0, 2.5)
    elif piece == "clapstack":
        x = sum(drum_piece("clap", n, rng, 1.0, var * rng.uniform(0.85, 1.2)) for _ in range(4))
        x = dsp.reverb(x, hall_ir(1.6, 211), 0.35)
        x = dsp.mono(x)
    elif piece == "snapsnare":
        x = drum_piece("snare", n, rng, 1.0, var * 1.15) + drum_piece("clap", n, rng, 1.0, var) * 0.7
        x = dsp.saturate(x, 1.8)
    elif piece == "chainslam":
        x = np.zeros(n)
        for k in range(14):
            off = int(rng.uniform(0, 0.12) * SR)
            m = n - off
            f = rng.uniform(1800, 6500)
            x[off:] += dsp.modal(m, [f, f * 1.4, f * 2.1], [1, 0.6, 0.3], [0.15, 0.1, 0.08], rng=rng)[:m] * rng.uniform(0.3, 1)
        x += dsp.hp(noise, 2500) * np.exp(-t / 0.03)
    elif piece == "subhit":
        x = np.sin(2 * np.pi * np.cumsum(28 + 45 * np.exp(-t / 0.12)) / SR) * np.exp(-t * LN1000 / 2.5)
        x = dsp.saturate(x * 1.3, 1.5)
    elif piece == "gonghit":
        x = perc_piece("tamtam", n, rng, var) * 0.8 + perc_piece("anvil", n, rng, 0.4) * 0.2
        x *= np.exp(-t / 1.2)
    elif piece == "whip":
        x = dsp.bp(noise, 3500, 0.9) * np.exp(-t / 0.012) * 2 + dsp.hp(noise, 6000) * np.exp(-t / 0.003)
    elif piece == "glitchhit":
        base = drum_piece("snare", n, rng, 1.0, var) + drum_piece("kick", n, rng, 1.0, var)
        x = np.zeros(n)
        seg = int(0.04 * SR)
        for k in range(6):
            s0 = k * seg
            x[s0:s0 + seg] = base[:seg] * (0.85 ** k)
        x[6 * seg:] = base[6 * seg:]
    else:  # rumblehit
        sw = np.clip(t / 0.8, 0, 1) ** 2
        x = dsp.butter(noise, 250, "low", 4) * sw * 4 * (t < 0.8)
        hit = perc_piece("boom", n - secs(0.8), rng, var)
        x[secs(0.8):] += hit
    x = dsp.dc_block(x)
    return dsp.fade_edges(x, 0.0003, min(0.4, z.p["len"] * 0.25)), None


def dark_atmos(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    n = secs(5.6)
    t = dsp.tvec(n)
    g = z.group
    if g == "Abyss":
        x = unison(n, f0 / 2, rng, voices=5, spread_cents=18, osc="saw", width=1.0)
        fc = 300 + 220 * np.sin(2 * np.pi * 0.09 * t)
        x = dsp.bp(x, fc, 2.5) * 2 + dsp.lp24(x, 160, 0.8)
        x = dsp.reverb(x, hall_ir(5.0, 221), 0.55)
    elif g == "Wind":
        nz = rng.standard_normal((n, 2))
        gust = 0.5 + 0.5 * dsp.smooth_noise(n, rng, 0.4)
        fc = 500 + 900 * gust
        x = dsp.bp(nz, fc, 3.0) * gust[:, None] + dsp.bp(nz, f0 * 4, 25.0) * 0.6
        x = dsp.reverb(x, hall_ir(3.5, 223), 0.4)
    elif g == "BowedMetal":
        exc = rng.standard_normal((n, 2)) * (0.6 + 0.4 * dsp.smooth_noise(n, rng, 0.5))[:, None]
        x = np.zeros((n, 2))
        for r in [1.0, 2.41, 3.9, 5.3, 7.1]:
            x += dsp.bp(exc, f0 * r, 180.0)
        x = dsp.reverb(x, hall_ir(4.5, 225), 0.5)
    elif g == "HauntedChoir":
        src = _choir_source(n, f0, rng, singers=8, vib_depth=30)
        src *= (1 + 0.3 * np.sin(2 * np.pi * 0.07 * t))[:, None]
        x = dsp.formant_bank(src, FORMANTS[("Ooh", "f")]) + dsp.formant_bank(src, FORMANTS[("Aah", "m")]) * 0.5
        x = dsp.reverb(x / (dsp.rms(x) + 1e-9), hall_ir(6.0, 227, 0.05), 0.7)
    elif g == "MachineHum":
        x = np.zeros((n, 2))
        for k, a in [(1, 1.0), (2, 0.6), (3, 0.4), (5, 0.25), (7, 0.15), (9, 0.1)]:
            am = 1 + 0.2 * np.sin(2 * np.pi * (0.5 + k * 0.13) * t)
            x += dsp.stereo(np.sin(2 * np.pi * f0 * k * t) * a * am)
        x += dsp.bp(rng.standard_normal((n, 2)), 2400, 2.0) * 0.05
        x = dsp.saturate(dsp.norm_rms(x, 0.25), 1.6)
        x = dsp.reverb(x, hall_ir(2.0, 229), 0.25)
    elif g == "DeepSpace":
        x = np.zeros((n, 2))
        for r in [1.0, 1.5, 2.0, 2.997, 4.01, 6.0]:
            tr = 0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(0.04, 0.12) * t + rng.uniform(0, 6))
            x += dsp.pan(np.sin(2 * np.pi * f0 * r * t + rng.uniform(0, 6)) * tr / r ** 0.5, rng.uniform(-0.9, 0.9))
        x = dsp.reverb(x, hall_ir(7.0, 231, 0.06), 0.75)
    elif g == "Pulse":
        rate = 1.25
        ph = (t * rate) % 1.0
        thump = np.where(ph < 0.5, np.sin(np.pi * ph / 0.5) ** 2, 0.0)
        x = dsp.stereo(np.sin(2 * np.pi * f0 * 0.5 * t) * thump)
        x += unison(n, f0, rng, voices=3, spread_cents=10, osc="saw") * 0.05
        x = dsp.butter(x, 900, "low", 2)
        x = dsp.reverb(x, hall_ir(2.5, 233), 0.3)
        x = dsp.fade_edges(x, 0.01, 0.001)
        beat = 1.0 / rate
        ls = int(round(2 * beat * SR))
        le = ls + int(round(4 * beat * SR))
        return dsp.bake_loop(x, ls, le, int(0.04 * SR)), (ls, le)
    else:  # Shimmer
        x = unison(n, f0 * 2, rng, voices=6, spread_cents=12, osc="tri", width=1.0)
        x += unison(n, f0 * 4, rng, voices=4, spread_cents=15, osc="sine", width=1.0) * 0.4
        x *= (1 + 0.3 * np.sin(2 * np.pi * 0.31 * t))[:, None]
        x = dsp.reverb(x, hall_ir(6.0, 235, 0.04), 0.7)
    x = dsp.fade_edges(x, 0.05, 0.001)
    return sustain_loop(x, 1.4, 3.3, 0.9)


def reverse_swells(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    T = 2.6
    n = secs(T)
    src_len = secs(1.6)
    if z.group == "RevPiano":
        s = felt_piano_note(f0, src_len, rng, 0.8, z.root)
        s = dsp.stereo(s)
    elif z.group == "RevStrings":
        s = _bowed_section(src_len, f0, rng, "f", players=6, attack=0.02, vib=6, length=0.4)
    else:  # RevPad
        s = unison(src_len, f0, rng, voices=5, spread_cents=12, osc="saw")
        s = dsp.lp24(s, 900 + f0 * 3, 0.8) * dsp.env_exp(src_len, 1.2, attack=0.002)[:, None]
    s = dsp.fade_edges(s, 0.0005, 0.2)
    wet = dsp.reverb_tail(s, hall_ir(3.0, 241, 0.02), 0.65, extra=T - 1.6)
    x = wet[:n][::-1].copy()
    x = dsp.fade_edges(x, 0.05, 0.03)  # the swell ends at its peak; a 30 ms cut keeps it click-free
    return x, None


SCIFI = ["laser", "laserburst", "phaserblast", "alarm", "robot", "datastream", "teleport", "powerup", "shutdown",
         "forcefield", "servo", "shippass", "sonar", "static", "charge", "zaphit", "alienvoice", "warp"]


def scifi(z):
    rng = np.random.default_rng(z.seed)
    kind = z.p["fx"]
    n = secs(z.p["len"])
    t = dsp.tvec(n)
    T = n / SR
    big = hall_ir(2.4, 251)
    if kind == "laser":
        f = 3200 * np.exp(-t / 0.08) + 180
        x = dsp.stereo(dsp.saw(f) * 0.6 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * 0.5) * np.exp(-t / 0.18)[:, None]
    elif kind == "laserburst":
        x = np.zeros((n, 2))
        for k in range(5):
            off = k * 0.11
            tt = np.clip(t - off, 0, None)
            f = 2600 * np.exp(-tt / 0.05) + 250
            x += dsp.pan(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.07) * (t >= off), (-1) ** k * 0.5)
    elif kind == "phaserblast":
        nz = rng.standard_normal((n, 2))
        d = (2 + 8 * (1 - np.exp(-t / 0.3))) * SR / 1000
        x = np.stack([nz[:, c] + dsp.delay_read(nz[:, c], d) for c in range(2)], axis=1)
        x = dsp.bp(x, 1500 + 1200 * np.sin(2 * np.pi * 3 * t), 1.0) * np.exp(-t / 0.4)[:, None]
    elif kind == "alarm":
        f = np.where((t * 2.5) % 1 < 0.5, 880, 660)
        x = dsp.stereo(dsp.butter(dsp.pulse(f, 0.5), 4000, "low", 2) * 0.4)
    elif kind == "robot":
        x = np.zeros(n)
        pos = 0
        while pos < n:
            L = int(rng.uniform(0.05, 0.14) * SR)
            f = rng.choice([440, 660, 880, 990, 1320, 1760])
            m = min(L, n - pos)
            x[pos:pos + m] = dsp.pulse(np.full(m, f), 0.5)[:m] * np.hanning(m) * 0.5
            pos += L + int(rng.uniform(0.0, 0.05) * SR)
        x = dsp.stereo(dsp.butter(x, 5000, "low", 2))
    elif kind == "datastream":
        x = np.zeros((n, 2))
        step = int(0.025 * SR)
        for k in range(n // step):
            f = rng.uniform(800, 4000)
            seg = np.sin(2 * np.pi * f * np.arange(step) / SR) * np.hanning(step) * rng.uniform(0.2, 0.6)
            x[k * step:(k + 1) * step] += dsp.pan(seg, rng.uniform(-0.8, 0.8))
    elif kind == "teleport":
        f = 300 * 2 ** (4 * t / T)
        car = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(2 * np.pi * np.cumsum(f * 1.41) / SR)
        sh = dsp.bp(rng.standard_normal(n), f * 3, 6.0)
        x = dsp.stereo((car * 0.6 + sh * 0.5) * np.sin(np.pi * t / T) ** 2)
    elif kind == "powerup":
        f = 60 * 2 ** (4.5 * (t / T) ** 1.5)
        x = dsp.stereo(dsp.saw(f) * 0.5 + dsp.pulse(f * 1.01, 0.3) * 0.3)
        x = dsp.lp24(x, 300 + 8000 * (t / T) ** 2, 1.4) * np.clip(t / 0.1, 0, 1)[:, None]
    elif kind == "shutdown":
        sp = np.clip(1 - t / (T * 0.85), 0, 1) ** 1.8
        f = 900 * sp + 20
        x = dsp.stereo(dsp.saw(f) * 0.5 + np.sin(2 * np.pi * np.cumsum(f * 0.5) / SR) * 0.4) * (sp > 0.005)[:, None]
        x = dsp.lp24(x, 200 + 6000 * sp, 1.2)
    elif kind == "forcefield":
        hum = sum(np.sin(2 * np.pi * 100 * k * t) / k for k in range(1, 8))
        am = 1 + 0.5 * np.sin(2 * np.pi * 7 * t)
        x = dsp.stereo(hum * am * 0.3) + dsp.bp(rng.standard_normal((n, 2)), 3000, 4.0) * 0.1
    elif kind == "servo":
        f = 400 + 300 * np.sin(np.pi * t / T)
        x = dsp.stereo(dsp.butter(dsp.saw(f) + dsp.saw(f * 2.02) * 0.5, 3500, "low", 2) * 0.4)
    elif kind == "shippass":
        env = np.exp(-((t - T * 0.5) / (T * 0.22)) ** 2)
        dop = 1 + 0.12 * np.tanh((T * 0.5 - t) * 3)
        rum = dsp.butter(rng.standard_normal(n), 200, "low", 4) * 3
        tone = dsp.saw(110 * dop) * 0.3
        mono_sig = (rum + tone) * env
        p = np.tanh((t - T * 0.5) * 2)
        x = dsp.pan(mono_sig, p)
    elif kind == "sonar":
        x = np.zeros(n)
        for k, a in enumerate([1.0, 0.45, 0.2, 0.09]):
            off = int(k * 0.42 * SR)
            m = n - off
            x[off:] += np.sin(2 * np.pi * 1250 * np.arange(m) / SR) * np.exp(-np.arange(m) / SR / 0.25) * a
        x = dsp.stereo(x)
    elif kind == "static":
        crack = (rng.random(n) < 0.004) * rng.standard_normal(n) * 4
        x = dsp.stereo(dsp.bp(rng.standard_normal(n) * (0.5 + 0.5 * dsp.smooth_noise(n, rng, 6)), 2200, 0.8) * 0.5 + crack)
    elif kind == "charge":
        f = 120 * 2 ** (3.5 * t / T)
        buzz = dsp.pulse(f, 0.15) * 0.4
        x = dsp.stereo(dsp.lp24(buzz, 500 + 6000 * (t / T), 2.0) * (t / T) ** 1.2)
    elif kind == "zaphit":
        f = 2500 * np.exp(-t / 0.04) + 120
        x = dsp.stereo(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.3) + perc_piece("boom", n, rng, 1.0) * 0.6)
    elif kind == "alienvoice":
        src = dsp.saw(140 * (1 + 0.3 * dsp.smooth_noise(n, rng, 3)))
        vow = [FORMANTS[("Aah", "m")], FORMANTS[("Ooh", "m")]]
        a = dsp.formant_bank(src, vow[0])
        b = dsp.formant_bank(src, vow[1])
        w = 0.5 + 0.5 * np.sin(2 * np.pi * 2.3 * t)
        x = dsp.stereo((a * w + b * (1 - w)) * np.sin(2 * np.pi * 37 * t)) * np.sin(np.pi * t / T)[:, None]
    else:  # warp
        f = 80 * 2 ** (6 * (t / T) ** 2)
        x = dsp.stereo(dsp.saw(f) * 0.3 + dsp.bp(rng.standard_normal(n), f * 4, 3.0) * 0.4) * np.sin(np.pi * t / T)[:, None]
    x = dsp.reverb(x, big, 0.25)
    x = dsp.dc_block(x)
    return dsp.fade_edges(x, 0.001, min(0.3, T * 0.2)), None


def tension_kit(z):
    rng = np.random.default_rng(z.seed)
    kind = z.p["fx"]
    n = secs(z.p["len"])
    t = dsp.tvec(n)
    T = n / SR
    room = hall_ir(2.0, 261)

    def tick(m, f=2500):
        return dsp.modal(m, [f, f * 2.1], [1, 0.4], [0.035, 0.025], rng=rng)

    if kind in ("clockloop", "bombloop"):
        period = 0.5 if kind == "clockloop" else 0.25
        x = np.zeros(n)
        k = 0
        while k * period < T:
            s0 = int(k * period * SR)
            m = min(n - s0, secs(0.15))
            x[s0:s0 + m] += tick(m, 2400 if k % 2 == 0 else 2900)[:m] * (1 if k % 2 == 0 else 0.75)
            k += 1
        x = dsp.mono(dsp.reverb(x, room, 0.2))
        x = dsp.stereo(x)
        ls, le = int(period * 2 * SR), int(period * 2 * SR) + int(period * 4 * SR)
        return dsp.bake_loop(x, ls, le, int(0.01 * SR)), (ls, le)
    if kind == "heartloop":
        beat = 1 / 1.25
        x = np.zeros(n)
        k = 0
        while k * beat < T:
            for off, a in [(0.0, 1.0), (0.24, 0.7)]:
                s0 = int((k * beat + off) * SR)
                if s0 < n:
                    m = n - s0
                    x[s0:] += _membrane(m, rng, 45, 0.5, 0.3, 0.3)[:m] * a
            k += 1
        x = dsp.stereo(dsp.butter(x, 400, "low", 2))
        ls, le = int(beat * 1 * SR), int(beat * 1 * SR) + int(beat * 3 * SR)
        return dsp.bake_loop(x, ls, le, int(0.02 * SR)), (ls, le)
    if kind == "subloop":
        rate = 2.0
        ph = (t * rate) % 1.0
        env = np.exp(-ph / 0.15) * (1 - np.exp(-ph / 0.01))
        x = dsp.stereo(np.sin(2 * np.pi * 42 * t) * env)
        ls, le = int(1.0 * SR), int(1.0 * SR) + int(2.0 * SR)
        return dsp.bake_loop(x, ls, le, int(0.01 * SR)), (ls, le)
    if kind == "scrape":
        sec = _bowed_section(n, 233.0, rng, "f", players=4, attack=0.3, vib=0)
        x = dsp.bp(sec, 2500, 1.2) * 2 + dsp.bp(rng.standard_normal((n, 2)), 3500, 2.0) * 0.3 * np.sin(np.pi * t / T)[:, None]
    elif kind == "collegno":
        x = np.zeros(n)
        for k in range(8):
            off = k * 0.012 + rng.uniform(0, 0.01)
            s0 = int(off * SR)
            m = n - s0
            x[s0:] += dsp.modal(m, np.array([700, 1650, 2900]) * rng.uniform(0.9, 1.1), [1, 0.5, 0.3], [0.06, 0.04, 0.03], rng=rng)[:m]
        x = dsp.stereo(x)
    elif kind == "bowedcym":
        x = dsp.stereo(_cymbal(n, rng, 900, 9000, 60, (3.0, 4.0), 0.0) * np.sin(np.pi * np.clip(t / T, 0, 1)) ** 2)
    elif kind == "pianocluster":
        x = sum(felt_piano_note(float(mtof(m)), n, rng, 1.0, m) for m in [24, 25, 27, 30, 31])
        x = dsp.stereo(x)
    elif kind == "stingerhigh":
        x = sum(_bowed_section(n, float(mtof(m)), rng, "f", players=4, attack=0.01, vib=0, length=0.3) for m in [84, 85, 90])
    elif kind == "stingerlow":
        x = sum(_brass_section(n, float(mtof(m)), rng, "f", players=3, attack=0.01, length=0.4) for m in [36, 37, 43])
        x += dsp.stereo(perc_piece("boom", n, rng, 1.0)) * 0.6
    elif kind == "breath":
        env = np.sin(np.pi * np.clip(t / (T * 0.8), 0, 1)) ** 2 * (t < T * 0.8)
        x = dsp.stereo(dsp.formant_bank(rng.standard_normal(n), FORMANTS[("Aah", "m")]) * env * 0.4)
    else:  # creak
        fc = 400 + 300 * dsp.smooth_noise(n, rng, 1.5)
        grains = (rng.random(n) < 0.02) * 1.0
        x = dsp.stereo(dsp.bp(grains + rng.standard_normal(n) * 0.05, fc, 8.0) * np.sin(np.pi * t / T))
    x = dsp.reverb(x, room, 0.25)
    x = dsp.dc_block(x)
    return dsp.fade_edges(x, 0.001, min(0.4, T * 0.25)), None


# ========================================================================== WORLD
def _tuned_modal(z, ratios, amps, t60_lo, t60_hi, lo, hi, t60_scale, click=0.002, stereo_beat=None, max_len=4.0):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root)) * (1 + rng.normal(0, 0.0004))
    ks = key_scale(z.root, lo, hi)
    base = lerp(t60_lo, t60_hi, ks)
    n = secs(min(base * 0.85 + 0.4, max_len))
    t = dsp.tvec(n)
    vel = 0.8 + 0.2 * (_rr(z) % 2)
    if stereo_beat:
        chans = []
        for c, sign in enumerate([-1, 1]):
            r = np.random.default_rng(z.seed + c)
            chans.append(dsp.modal(n, [f0 * q * (1 + sign * stereo_beat / (f0 * q)) for q in ratios], amps,
                                   [base * s for s in t60_scale], rng=r))
        x = np.stack(chans, axis=1)
    else:
        x = dsp.modal(n, [f0 * q for q in ratios], amps, [base * s for s in t60_scale], rng=rng)
    strike = dsp.bp(rng.standard_normal(n), min(f0 * 5, 8000), 1.0) * np.exp(-t / click) * 0.3 * vel
    if x.ndim == 2:
        strike = dsp.stereo(strike)
    return x * vel + strike, n, t, rng, f0


def hang(z):
    x, n, t, rng, f0 = _tuned_modal(z, [1.0, 2.0, 2.98, 3.6, 5.1], [1.0, 0.5, 0.35, 0.12, 0.06], 4.2, 2.0, 50, 86,
                                    [1.0, 0.7, 0.5, 0.3, 0.2], click=0.006)
    thump = dsp.butter(rng.standard_normal(n), 300, "low", 2) * np.exp(-t / 0.012) * 0.3
    x = x + thump
    x = dsp.mono(dsp.reverb(x, room_ir(1.2, 271), 0.12))
    return dsp.fade_edges(x, 0.0003, 0.3), None


def steel_pan(z):
    x, n, t, rng, f0 = _tuned_modal(z, [1.0, 2.0, 3.0, 4.02, 5.05], [1.0, 0.8, 0.45, 0.2, 0.08], 1.8, 1.0, 55, 91,
                                    [1.0, 0.8, 0.6, 0.45, 0.3], click=0.0015)
    x = dsp.mono(dsp.reverb(x, room_ir(1.0, 273), 0.12))
    return dsp.fade_edges(x, 0.0003, 0.2), None


def kalimba(z):
    x, n, t, rng, f0 = _tuned_modal(z, [1.0, 5.9, 10.1], [1.0, 0.22, 0.07], 2.4, 1.2, 55, 91, [1.0, 0.3, 0.15],
                                    click=0.0015)
    body = dsp.body_ir(rng, [(210, 0.06, 1.0), (460, 0.05, 0.7), (900, 0.03, 0.4)])
    x = signal.fftconvolve(x, body)[:n]
    buzz = dsp.hp(x, 3000) * (np.abs(x) > 0.2) * 0.1
    x = dsp.mono(dsp.reverb(x + buzz, room_ir(0.9, 275), 0.1))
    return dsp.fade_edges(x, 0.0003, 0.2), None


def gamelan(z):
    x, n, t, rng, f0 = _tuned_modal(z, [1.0, 2.76, 5.2, 8.1], [1.0, 0.45, 0.2, 0.08], 4.0, 2.2, 48, 96,
                                    [1.0, 0.5, 0.3, 0.2], click=0.002, stereo_beat=3.5, max_len=3.2)
    x = dsp.reverb(x, hall_ir(2.0, 277), 0.18)
    return dsp.fade_edges(x, 0.0003, 0.3), None


def _jawari(x, f0):
    """Sitar bridge buzz: emphasise and saturate the upper harmonics."""
    hi = dsp.hp(x, f0 * 6)
    return x + dsp.saturate(hi * 6, 2.0) * 0.12


def sitar(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    if z.group == "Tanpura":
        n = secs(6.4)
        x = np.zeros(n)
        cycle = 3.2
        notes = [f0 * 1.5 / 2, f0, f0, f0 / 2]  # Pa Sa Sa Sa (low)
        for c in range(2):
            for i, fr in enumerate(notes):
                s0 = int((c * cycle + i * 0.8) * SR)
                m = n - s0
                exc = dsp.pluck_excitation(SR / fr, rng, bright=0.5, position=0.12)
                s = dsp.ks_string(m, fr, exc, t60=6.0, bright=0.08, stiff=0.0)
                x[s0:] += _jawari(s, fr)[:m] * 0.6
        x = dsp.reverb(x, hall_ir(2.0, 281), 0.25)
        ls = int(cycle * 0.5 * SR)
        le = ls + int(cycle * SR)
        y = dsp.bake_loop(x, ls, le, int(0.08 * SR))
        return y, (ls, le)
    ks = key_scale(z.root, 48, 84)
    n = secs(lerp(3.0, 2.0, ks))
    exc = dsp.pluck_excitation(SR / f0, rng, bright=0.75, position=rng.uniform(0.08, 0.12))
    s = dsp.ks_string(n, f0, exc, t60=lerp(4.0, 2.2, ks), bright=0.1, stiff=0.0)
    x = _jawari(s, f0)
    # sympathetic strings (taraf) tuned to the Sa / Pa / Re / Ga of C
    for m in [48, 50, 52, 55, 60, 62, 64, 67]:
        fs = float(mtof(m))
        x += dsp.ks_string(n, fs, s[: secs(0.3)] * 0.02, t60=5.0, bright=0.05) * 0.5
    body = dsp.body_ir(rng, [(150, 0.08, 1.0), (300, 0.06, 0.8), (700, 0.04, 0.5), (1500, 0.03, 0.3)])
    x = signal.fftconvolve(x, body)[:n]
    x = dsp.hp(x, 80)
    x = dsp.mono(dsp.reverb(x, room_ir(1.2, 283), 0.15))
    return dsp.fade_edges(x, 0.0003, 0.3), None


def duduk(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    g = z.group

    def tone(n, length=None, attack=0.08):
        t = dsp.tvec(n)
        cents = dsp.vibrato_cents(n, rng, 5.2, 18, 0.45) + dsp.drift_cents(n, rng, 4)
        cents += -25 * np.exp(-t / 0.06)  # slide into the note
        fr = f0 * dsp.cents_to_ratio(cents)
        amps = [1.0, 0.65, 0.5, 0.32, 0.22, 0.14, 0.09, 0.06, 0.04, 0.03]
        v = dsp.additive(fr, amps, rng=rng)
        v = dsp.formant_bank(v, [(620, 120, 0), (1250, 150, -4), (2500, 250, -12)]) * 2 + v * 0.3
        breath = dsp.bp(rng.standard_normal(n), 1800, 1.2) * 0.05
        env = np.clip(t / attack, 0, 1) ** 1.3
        if length is not None:
            env *= np.clip(1 - (t - length) / 0.07, 0, 1) ** 2
        return (v + breath) * env

    room = room_ir(1.2, 291)
    if g == "Sus":
        n = secs(2.6)
        x = dsp.mono(dsp.reverb(tone(n), room, 0.15))
        x = dsp.fade_edges(x, 0.002, 0.001)
        return sustain_loop(x, 0.95, 1.25, 0.45)
    n = secs(0.6)
    x = dsp.mono(dsp.reverb(tone(n, length=0.14, attack=0.02), room, 0.18))
    return dsp.fade_edges(x, 0.0005, 0.08), None


# ========================================================================== BAND
def synthwave_kit(z):
    rng = np.random.default_rng(z.seed)
    piece = z.p["piece"]
    lvl = {1: 0.6, 2: 1.0}[_layer(z)]
    n = secs(z.p["len"])
    t = dsp.tvec(n)
    noise = rng.standard_normal(n)
    var = z.p.get("var", 1.0) * (1 + rng.normal(0, 0.006))
    gated = hall_ir(1.2, 301)

    def gate(x, close=0.28):
        wet = dsp.mono(dsp.reverb(x, gated, 1.0))
        g = np.clip(1 - (t - close) / 0.02, 0, 1)
        return x + wet * g * 1.5

    if piece == "kick":
        f = 50 * var + 90 * np.exp(-t / 0.04)
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * LN1000 / 0.5) + dsp.hp(noise, 3000) * np.exp(-t / 0.002) * 0.3
        x = dsp.saturate(x * lvl, 1.4)
    elif piece == "snare":
        x = drum_piece("snare", n, rng, lvl, var * 1.05)
        x = gate(x)
    elif piece == "snare2":
        x = drum_piece("rimshot", n, rng, lvl, var * 1.1)
        x = gate(x, 0.22)
    elif piece == "clap":
        x = gate(drum_piece("clap", n, rng, lvl, var), 0.3)
    elif piece == "rim":
        x = drum_piece("sidestick", n, rng, lvl, var * 1.2)
    elif piece == "tom":
        f = var * (1 + 0.6 * np.exp(-t / 0.18))
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * LN1000 / 0.9) + dsp.bp(noise, 900, 1.0) * np.exp(-t / 0.03) * 0.4
        x = gate(x * lvl, 0.45)
    elif piece in ("chh", "phh", "ohh"):
        x = drum_piece(piece, n, rng, lvl, var)
    elif piece == "crash":
        x = drum_piece("crash", n, rng, lvl, var)
    elif piece == "ride":
        x = drum_piece("ride", n, rng, lvl, var)
    elif piece == "tamb":
        x = drum_piece("tamb", n, rng, lvl, var)
    else:  # cowbell (two detuned squares through a band-pass)
        x = (dsp.pulse(np.full(n, 540.0 * var)) + dsp.pulse(np.full(n, 800.0 * var))) * 0.5
        x = dsp.bp(x, 900, 1.5) * np.exp(-t / 0.12) * lvl
    x = dsp.dc_block(x)
    return dsp.fade_edges(x, 0.0002, min(0.3, z.p["len"] * 0.3)), None


def trap_kit(z):
    rng = np.random.default_rng(z.seed)
    piece = z.p["piece"]
    lvl = {1: 0.6, 2: 1.0}[_layer(z)]
    n = secs(z.p["len"])
    t = dsp.tvec(n)
    noise = rng.standard_normal(n)
    var = 1 + rng.normal(0, 0.006)
    if piece == "808":
        f = 45 * (1 + 0.8 * np.exp(-t / 0.03))
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * LN1000 / 2.2)
        x = dsp.saturate(x * (1 + lvl), 1.8) + dsp.hp(noise, 3000) * np.exp(-t / 0.002) * 0.2 * lvl
    elif piece == "punchkick":
        x = drum_piece("kick", n, rng, lvl, var * 1.1)
        x = dsp.saturate(x * 1.5, 2.0)
    elif piece == "snare":
        x = drum_piece("snare", n, rng, lvl, var * 1.25)
        x = dsp.hp(x, 150)
    elif piece == "clap":
        x = drum_piece("clap", n, rng, lvl, var * 1.1)
        x = dsp.mono(dsp.reverb(x, room_ir(0.9, 311), 0.25))
    elif piece == "snareclap":
        x = drum_piece("snare", n, rng, lvl, var * 1.2) * 0.8 + drum_piece("clap", n, rng, lvl, var) * 0.8
    elif piece == "rim":
        x = drum_piece("sidestick", n, rng, lvl, var * 1.3)
    elif piece == "hat":
        x = drum_piece("chh", n, rng, lvl, var * 1.15)
    elif piece == "hattight":
        x = drum_piece("chh", n, rng, lvl, var * 1.2) * np.exp(-t / 0.02)
    elif piece == "ohh":
        x = drum_piece("ohh", n, rng, lvl, var * 1.1) * np.exp(-t / 0.35)
    elif piece == "crash":
        x = drum_piece("crash", n, rng, lvl, var)
    elif piece == "bell":
        f = 1240 * var
        x = dsp.modal(n, [f, f * 2.0, f * 3.01, f * 4.17], [1, 0.4, 0.2, 0.1], [0.8, 0.5, 0.4, 0.3], rng=rng) * lvl
    elif piece == "snap":
        x = dsp.bp(noise, 2600, 2.0) * np.exp(-t / 0.008) * 1.5 + dsp.bp(noise, 1200, 2.0) * np.exp(-t / 0.02) * 0.4
    elif piece == "shaker":
        x = drum_piece("shaker", n, rng, lvl, var)
    else:  # vox chop "hey"
        src = dsp.saw(np.full(n, 190.0 * var))
        x = dsp.formant_bank(src, FORMANTS[("Aah", "m")]) * np.clip(t / 0.01, 0, 1) * np.exp(-t / 0.12)
    x = dsp.dc_block(x)
    return dsp.fade_edges(x, 0.0002, min(0.3, z.p["len"] * 0.3)), None


def _amp(x, drive):
    """Guitar amp + cabinet: pre-emphasis, saturation, cab low-pass."""
    if drive > 2:
        x = dsp.hp(x, 400) + x * 0.25
    y = dsp.saturate(dsp.norm_rms(x, 0.2), drive)
    y = dsp.eq(y, "peak", 1700, 3.0, 0.9)
    y = dsp.butter(y, 4800 if drive > 2 else 6500, "low", 2)
    return dsp.hp(y, 85)


def electric_guitar(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    ks = key_scale(z.root, 40, 76)
    g = z.group
    per = SR / f0
    if g.startswith("Mute"):
        n = secs(0.45)
        exc = dsp.pluck_excitation(per, rng, bright=0.7, position=0.1)
        s = dsp.ks_string(n, f0, exc, t60=0.22, bright=0.42, stiff=0.08)
        x = _amp(s, 6.0)
        return dsp.fade_edges(x, 0.0003, 0.08), None
    lvl = (_layer(z) - 1) if g.startswith("V") else 1
    n = secs(lerp(3.0, 2.0, ks))
    exc = dsp.pluck_excitation(per, rng, bright=0.55 + 0.3 * lvl, position=rng.uniform(0.1, 0.16))
    s = dsp.ks_string(n, f0, exc, t60=lerp(6.0, 3.0, ks), bright=0.12 - 0.04 * lvl, stiff=0.1)
    pick = max(1, int(per * 0.2))
    s = s - 0.7 * np.concatenate([np.zeros(pick), s[:-pick]])  # magnetic pickup position
    x = _amp(s, 7.0 if g.startswith("Drive") else 1.2)
    return dsp.fade_edges(x, 0.0003, 0.25), None


# ========================================================================== ORCHESTRAL
def _cello_body(x, bright):
    x = dsp.eq(x, "peak", 110, 3.0, 1.0)
    x = dsp.eq(x, "peak", 220, 2.0, 1.2)
    x = dsp.eq(x, "peak", 1400, 2.0 * bright, 0.9)
    x = dsp.eq(x, "highshelf", 5000, lerp(-12, -7, bright), 0.7)
    return dsp.hp(x, 40)


def _violin_body(x, bright):
    x = dsp.eq(x, "peak", 280, 3.0, 1.1)
    x = dsp.eq(x, "peak", 460, 2.0, 1.4)
    x = dsp.eq(x, "peak", 2800, 4.0 * bright + 1, 0.9)
    x = dsp.eq(x, "highshelf", 7500, lerp(-11, -6, bright), 0.7)
    return dsp.hp(x, 150)


def _solo(z, body, lo, hi):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    g = z.group
    ks = key_scale(z.root, lo, hi)
    room = hall_ir(1.6, 321)
    if g in ("SusP", "SusF"):
        n = secs(2.6)
        dyn = "f" if g == "SusF" else "p"
        x = _bowed_section(n, f0, rng, dyn, players=1, attack=0.16 if dyn == "p" else 0.08,
                           vib=lerp(16, 22, ks), body=body)
        x = dsp.mono(dsp.reverb(x, room, 0.12))
        x = dsp.fade_edges(x, 0.002, 0.001)
        return sustain_loop(x, 0.95, 1.25, 0.45)
    if g.startswith("Stac"):
        n = secs(0.55)
        x = _bowed_section(n, f0, rng, "f", players=1, attack=0.015, vib=0.0, length=0.13, body=body)
        x = dsp.mono(dsp.reverb(x, room, 0.15))
        return dsp.fade_edges(x, 0.0005, 0.08), None
    n = secs(lerp(1.3, 0.8, ks))
    exc = dsp.pluck_excitation(SR / f0, rng, bright=0.5, position=rng.uniform(0.15, 0.25))
    s = dsp.ks_string(n, f0, exc, t60=lerp(1.8, 0.8, ks), bright=0.3, stiff=0.03)
    x = body(dsp.stereo(s), 0.4)
    x = dsp.mono(dsp.reverb(x, room, 0.15))
    return dsp.fade_edges(x, 0.0003, 0.08), None


def solo_cello(z):
    return _solo(z, _cello_body, 36, 72)


def solo_violin(z):
    return _solo(z, _violin_body, 55, 91)


def horns(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    g = z.group
    room = hall_ir(2.2, 331)
    if g in ("SusP", "SusF"):
        n = secs(2.6)
        dyn = "f" if g == "SusF" else "p"
        x = _brass_section(n, f0, rng, dyn, players=4, attack=0.11 if dyn == "p" else 0.07, bright=0.55)
        x = dsp.eq(x, "highshelf", 3500, -5.0, 0.7)
        x = dsp.mono(dsp.reverb(x, room, 0.2))
        x = dsp.fade_edges(x, 0.002, 0.001)
        return sustain_loop(x, 0.95, 1.25, 0.45)
    n = secs(0.6)
    x = _brass_section(n, f0, rng, "f", players=4, attack=0.03, length=0.14, bright=0.6)
    x = dsp.eq(x, "highshelf", 3500, -5.0, 0.7)
    x = dsp.mono(dsp.reverb(x, room, 0.22))
    return dsp.fade_edges(x, 0.0005, 0.08), None


HARP_BODY = [(90, 0.1, 1.0), (180, 0.08, 0.8), (300, 0.06, 0.6), (520, 0.05, 0.4), (900, 0.03, 0.3), (1600, 0.02, 0.2)]


def harp(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    ks = key_scale(z.root, 24, 102)
    lvl = _layer(z) - 1
    n = secs(lerp(3.2, 1.0, ks))
    exc = dsp.pluck_excitation(SR / f0, rng, bright=0.45 + 0.35 * lvl, position=rng.uniform(0.4, 0.5),
                               length_periods=1.5)
    s = dsp.ks_string(n, f0, exc, t60=lerp(7.0, 1.4, ks), bright=0.2 - 0.06 * lvl, stiff=0.03)
    body = dsp.body_ir(rng, HARP_BODY)
    x = signal.fftconvolve(s, body)[:n]
    x = dsp.hp(x, 45)
    x = dsp.mono(dsp.reverb(x, hall_ir(2.0, 341), 0.15))
    return dsp.fade_edges(x, 0.0003, 0.25), None


def felt_piano_note(f0, n, rng, vel, midi):
    """Hammered string model: 1-3 detuned strings, felt hammer, soundboard."""
    ks = float(np.clip((midi - 21) / 87.0, 0, 1))
    strings = 1 if midi < 34 else (2 if midi < 48 else 3)
    out = np.zeros(n)
    per = SR / f0
    hammer_len = max(8, int(per * lerp(0.9, 0.35, vel)))
    ham = np.hanning(hammer_len * 2)[:hammer_len] ** 2
    ham = signal.lfilter([1 - 0.6], [1, -0.6], ham)
    for s in range(strings):
        det = (s - (strings - 1) / 2) * lerp(0.6, 0.25, ks)
        fs = f0 * 2 ** (det / 1200)
        exc = np.zeros(int(per) * 2)
        exc[:hammer_len] = ham
        exc += rng.standard_normal(exc.size) * 0.02 * vel
        out += dsp.ks_string(n, fs, exc, t60=lerp(9.0, 1.6, ks), bright=lerp(0.32, 0.18, vel),
                             stiff=lerp(0.25, 0.05, ks))
    sb_t = dsp.tvec(int(0.25 * SR))
    sb = rng.standard_normal(sb_t.size) * np.exp(-sb_t / 0.04)
    sb = dsp.butter(sb, 2500, "low", 2) * 0.05
    sb[0] = 1.0
    out = signal.fftconvolve(out, sb)[:n]
    out = dsp.butter(out, lerp(1800, 5000, vel) + f0 * 1.5, "low", 2)
    t = dsp.tvec(n)
    out += dsp.butter(rng.standard_normal(n), 200, "low", 2) * np.exp(-t / 0.02) * 0.02 * vel
    return out / (dsp.peak(out) + 1e-9)


def felt_piano(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    vel = {1: 0.25, 2: 0.6, 3: 1.0}[_layer(z)]
    ks = key_scale(z.root, 21, 108)
    n = secs(lerp(4.5, 1.6, ks))
    x = felt_piano_note(f0, n, rng, vel, z.root)
    x = dsp.mono(dsp.reverb(x, room_ir(1.3, 351), 0.12))
    return dsp.fade_edges(x, 0.0003, 0.3), None
