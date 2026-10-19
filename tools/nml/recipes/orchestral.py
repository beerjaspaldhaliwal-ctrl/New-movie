"""02 Orchestral: ensemble strings, brass, woodwinds, timpani."""
import numpy as np

from .. import dsp
from ..dsp import SR, mtof, secs
from .common import hall_ir, room_ir, sustain_loop, key_scale, lerp


# ---------------------------------------------------------------- Strings
def _string_body(x, bright):
    x = dsp.eq(x, "peak", 290, 2.5, 1.1)
    x = dsp.eq(x, "peak", 520, 1.5, 1.4)
    x = dsp.eq(x, "peak", 2600, 3.5 * bright, 0.9)
    x = dsp.eq(x, "highshelf", 7000, lerp(-10, -6, bright), 0.7)
    return dsp.hp(x, 45)


def _bowed_section(n, f0, rng, dyn, players=8, attack=0.15, vib=12.0, trem=False, length=None, body=None):
    t = dsp.tvec(n)
    out = np.zeros((n, 2))
    f = 1.0 if dyn == "f" else 0.0
    for p in range(players):
        cents = rng.normal(0, 5) + dsp.drift_cents(n, rng, 3.5, 0.35)
        if vib > 0:
            cents = cents + dsp.vibrato_cents(n, rng, rng.uniform(4.8, 6.1), vib * rng.uniform(0.7, 1.3), 0.3)
        fr = f0 * dsp.cents_to_ratio(cents)
        v = dsp.saw(fr, SR, rng.uniform())
        # slight bow-pressure flutter
        v *= 1 + 0.05 * dsp.smooth_noise(n, rng, 9.0)
        delay = rng.uniform(0, 0.03)
        a = attack * rng.uniform(0.8, 1.25)
        env = np.clip((t - delay) / a, 0, 1) ** 1.6
        if length is not None:
            rel = np.clip(1 - (t - length) / 0.09, 0, 1) ** 2
            env *= rel
        if trem:
            rate = rng.uniform(12.5, 15.5)
            ph = np.cumsum(rate * (1 + 0.06 * dsp.smooth_noise(n, rng, 2.0))) / SR + rng.uniform()
            stroke = 0.35 + 0.65 * (0.5 - 0.5 * np.cos(2 * np.pi * ph)) ** 0.7
            env *= stroke
        env *= 1 + 0.08 * dsp.smooth_noise(n, rng, 0.6)
        out += dsp.pan(v * env, (p / max(players - 1, 1) * 2 - 1) * 0.8 if players > 1 else 0.0)
    out /= np.sqrt(players)
    # bow noise
    noise = rng.standard_normal((n, 2))
    nb = dsp.bp(noise, 3800, 0.7) * lerp(0.025, 0.05, f)
    scratch = np.exp(-t / 0.04)[:, None] * dsp.bp(noise, 2200, 1.2) * lerp(0.05, 0.12, f)
    env_all = np.clip(t / max(attack, 0.01), 0, 1)[:, None]
    out = out + nb * env_all + scratch * (attack < 0.1)
    cut = lerp(1500, 3200, f) + f0 * lerp(2.5, 3.5, f)
    out = dsp.lp24(out, cut, 0.6)
    if f:
        out = dsp.saturate(dsp.norm_rms(out, 0.2), 1.25)
    return (body or _string_body)(out, f)


def _mic(x, mic, seed=31):
    """Close = the section with a little room; Hall = darker, wider, mostly reverb.
    Both are made from the same dry render, so they mix phase-coherently."""
    if mic == "hall":
        y = dsp.eq(x, "highshelf", 4500, -4.0, 0.7)
        y = dsp.eq(y, "lowshelf", 200, 1.5, 0.7)
        y = dsp.reverb(y, hall_ir(2.8, seed + 6, 0.035), 0.6)
        return dsp.width(y, 1.3)
    return dsp.reverb(x, hall_ir(1.8, seed), 0.12)


def _with_mics(z, dry, seed=31):
    """Close and Hall variants of a sustained sample share the same loop points."""
    close = dsp.fade_edges(_mic(dry, "close", seed), 0.002, 0.001)
    pts = dsp.loop_points(close, 0.95, 1.25, 0.45)
    y = close if not z.group.endswith("Hall") else dsp.fade_edges(_mic(dry, "hall", seed), 0.002, 0.001)
    return dsp.make_looped(y, 0, 0, points=pts)


def strings(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    g = z.group.replace("Hall", "")
    ks = key_scale(z.root, 30, 96)
    if g in ("SusP", "SusF"):
        n = secs(2.6)
        dyn = "f" if g == "SusF" else "p"
        x = _bowed_section(n, f0, rng, dyn, attack=0.22 if dyn == "p" else 0.11, vib=lerp(10, 14, ks))
        return _with_mics(z, x)
    if g == "Trem":
        n = secs(2.6)
        x = _bowed_section(n, f0, rng, "f", attack=0.08, vib=4.0, trem=True)
        return _with_mics(z, x)
    if g.startswith("Stac"):
        n = secs(0.6)
        x = _bowed_section(n, f0, rng, "f", attack=0.018, vib=0.0, length=0.13)
        x = dsp.reverb(x, hall_ir(1.8, 31), 0.2)
        return dsp.fade_edges(x, 0.0005, 0.08), None
    # pizzicato: ensemble of plucked strings
    n = secs(lerp(1.15, 0.75, ks))
    x = np.zeros((n, 2))
    body = dsp.body_ir(rng, [(280, 0.05, 1.0), (450, 0.04, 0.8), (750, 0.03, 0.5), (1300, 0.02, 0.4)])
    players = 6
    for p in range(players):
        fr = f0 * dsp.cents_to_ratio(rng.normal(0, 6))
        per = SR / fr
        exc = dsp.pluck_excitation(per, rng, bright=0.45, position=rng.uniform(0.12, 0.25))
        s = dsp.ks_string(n, fr, exc, t60=lerp(1.6, 0.6, ks), bright=0.32, stiff=0.02)
        d = int(rng.uniform(0, 0.022) * SR)
        s = np.concatenate([np.zeros(d), s[:n - d]])
        x += dsp.pan(s, (p / (players - 1) * 2 - 1) * 0.8)
    from scipy import signal
    x = np.stack([signal.fftconvolve(x[:, c], body)[:n] for c in range(2)], axis=1)
    x = _string_body(x, 0.4)
    x = dsp.reverb(x, hall_ir(1.8, 31), 0.2)
    return dsp.fade_edges(x, 0.0003, 0.08), None


# ---------------------------------------------------------------- Brass
def _brass_section(n, f0, rng, dyn, players=4, attack=0.06, length=None, bright=1.0):
    t = dsp.tvec(n)
    out = np.zeros((n, 2))
    f = 1.0 if dyn == "f" else 0.0
    for p in range(players):
        delay = rng.uniform(0, 0.025)
        a = attack * rng.uniform(0.85, 1.2)
        tt = np.clip(t - delay, 0, None)
        amp = np.clip(tt / a, 0, 1) ** 1.3
        if f:
            amp *= 1 + 0.25 * np.exp(-tt / 0.12) * (tt > a)  # 'blat' overshoot
        if length is not None:
            amp *= np.clip(1 - (t - length) / 0.07, 0, 1) ** 2
        amp *= 1 + 0.05 * dsp.smooth_noise(n, rng, 1.0)
        scoop = -38 * np.exp(-tt / 0.045) * (1 if f else 0.6)
        cents = rng.normal(0, 5) + scoop + dsp.drift_cents(n, rng, 3, 0.4)
        cents += dsp.vibrato_cents(n, rng, 5.0, 4.0, 0.8)
        fr = f0 * dsp.cents_to_ratio(cents)
        v = 0.8 * dsp.saw(fr, SR, rng.uniform()) + 0.3 * dsp.pulse(fr, 0.45, SR, rng.uniform())
        # brightness follows loudness: the essence of a brass tone
        cut = (f0 * lerp(1.6, 2.6, f) + (lerp(800, 3500, f) + f0 * lerp(2, 5, f)) * amp ** 2) * bright
        v = dsp.svf(dsp.svf(v, cut, 0.55, "lp"), cut * 1.1, 0.9, "lp")
        out += dsp.pan(v * amp, (p / max(players - 1, 1) * 2 - 1) * 0.6 if players > 1 else 0.0)
    out /= np.sqrt(players)
    out += dsp.bp(rng.standard_normal((n, 2)), f0 * 3, 4.0) * 0.01 * np.clip(t / 0.05, 0, 1)[:, None]
    if f:
        out = dsp.saturate(dsp.norm_rms(out, 0.25), 1.6)
    out = dsp.eq(out, "peak", lerp(600, 1200, f), 3.0, 0.9)
    out = dsp.eq(out, "highshelf", 7000, lerp(-8, -2, f), 0.7)
    return dsp.hp(out, 40)


def brass(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    g = z.group.replace("Hall", "")
    if g in ("SusP", "SusF"):
        n = secs(2.6)
        dyn = "f" if g == "SusF" else "p"
        x = _brass_section(n, f0, rng, dyn, attack=0.09 if dyn == "p" else 0.05)
        return _with_mics(z, x, seed=41)
    n = secs(0.55)
    x = _brass_section(n, f0, rng, "f", attack=0.022, length=0.12)
    x = dsp.reverb(x, hall_ir(2.0, 41), 0.2)
    return dsp.fade_edges(x, 0.0005, 0.08), None


# ---------------------------------------------------------------- Woodwinds
def _flute(n, f0, rng, length=None, attack=0.06):
    t = dsp.tvec(n)
    cents = dsp.vibrato_cents(n, rng, 5.0, 14, 0.35) + dsp.drift_cents(n, rng, 3)
    fr = f0 * dsp.cents_to_ratio(cents)
    amps = [1.0, 0.32, 0.12, 0.06, 0.03, 0.015]
    v = dsp.additive(fr, amps, rng=rng)
    trem = 1 + 0.07 * np.sin(2 * np.pi * np.cumsum(np.full(n, 5.0)) / SR)
    env = np.clip(t / attack, 0, 1) ** 1.4
    chiff = np.exp(-t / 0.03) * 0.6
    if length is not None:
        env *= np.clip(1 - (t - length) / 0.06, 0, 1) ** 2
    breath = dsp.bp(rng.standard_normal(n), f0 * 2, 1.5) * 0.06 + dsp.hp(rng.standard_normal(n), 3000) * 0.012
    over = dsp.sine(fr * 2) * chiff * 0.3
    return (v * trem + breath + over) * env


def _clarinet(n, f0, rng, length=None, attack=0.05):
    t = dsp.tvec(n)
    fr = f0 * dsp.cents_to_ratio(dsp.drift_cents(n, rng, 2.5) + dsp.vibrato_cents(n, rng, 4.8, 3, 0.6))
    high = f0 > 520
    amps = []
    for k in range(1, 25):
        if k % 2 == 1:
            amps.append(1.0 / k ** 0.9)
        else:
            amps.append((0.25 if high else 0.04) / k)
    v = dsp.additive(fr, amps, rng=rng)
    v = dsp.svf(v, 1800 + f0 * 2, 0.7, "lp") * 1.6
    env = np.clip(t / attack, 0, 1) ** 1.3
    if length is not None:
        env *= np.clip(1 - (t - length) / 0.06, 0, 1) ** 2
    breath = dsp.bp(rng.standard_normal(n), 1500, 0.8) * 0.01
    return (v + breath) * env


def woodwinds(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    g = z.group
    room = room_ir(1.0, 51)
    if g in ("Flute", "Clarinet"):
        n = secs(2.6)
        fn = _flute if g == "Flute" else _clarinet
        x = fn(n, f0, rng) + fn(n, f0 * dsp.cents_to_ratio(rng.uniform(4, 7)), rng) * 0.8
        x = dsp.mono(dsp.reverb(x, room, 0.12))
        x = dsp.fade_edges(x, 0.002, 0.001)
        return sustain_loop(x, 0.95, 1.25, 0.45)
    n = secs(0.5)
    x = _flute(n, f0, rng, length=0.1, attack=0.015) + _clarinet(n, f0, rng, length=0.1, attack=0.012) * 0.8
    x = dsp.mono(dsp.reverb(x, room, 0.15))
    return dsp.fade_edges(x, 0.0005, 0.06), None


# ---------------------------------------------------------------- Timpani
def _timp_hit(n, f0, rng, vel=1.0):
    t = dsp.tvec(n)
    ratios = [1.0, 1.504, 1.742, 2.0, 2.245, 2.494, 2.8]
    amps = [1.0, 0.55, 0.32, 0.25, 0.15, 0.1, 0.06]
    t60 = [3.2, 1.6, 1.2, 1.0, 0.8, 0.6, 0.5]
    pitch = 1 + 0.012 * np.exp(-t / 0.08) * vel  # head tension glide
    x = np.zeros(n)
    for r, a, d in zip(ratios, amps, t60):
        ph = 2 * np.pi * np.cumsum(f0 * r * pitch) / SR + rng.uniform(0, 6)
        x += a * np.exp(-t * dsp.LN1000 / d) * np.sin(ph)
    thump = dsp.butter(rng.standard_normal(n), 300, "low", 2) * np.exp(-t / 0.03) * 1.2 * vel
    felt = dsp.bp(rng.standard_normal(n), 1200, 0.8) * np.exp(-t / 0.008) * 0.3 * vel
    x = (x + thump + felt) * np.clip(t / 0.002, 0, 1)
    return x


def timpani(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    g = z.group
    room = hall_ir(2.2, 61)
    if g.startswith("Hit"):
        n = secs(2.6)
        x = _timp_hit(n, f0, rng, 1.0)
        x = dsp.mono(dsp.reverb(x, room, 0.14))
        return dsp.fade_edges(x, 0.0003, 0.15), None
    # roll: rapid alternating strokes
    n = secs(2.7)
    x = np.zeros(n)
    rate = 15.0 if g == "RollF" else 12.5
    vel = 1.0 if g == "RollF" else 0.55
    tt = 0.0
    while tt < 2.7:
        s = int(tt * SR)
        m = min(n - s, secs(1.4))
        x[s:s + m] += _timp_hit(m, f0, rng, vel * rng.uniform(0.75, 1.0))[:m] * rng.uniform(0.7, 1.0)
        tt += 1.0 / rate * rng.uniform(0.88, 1.12)
    x = dsp.mono(dsp.reverb(x, room, 0.14))
    x = dsp.fade_edges(x, 0.002, 0.001)
    return sustain_loop(x, 1.0, 1.3, 0.45)
