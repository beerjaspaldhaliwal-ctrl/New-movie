"""02 Orchestral and Band: keys, plucked strings, drums, organ, mallets."""
import numpy as np
from scipy import signal

from .. import dsp
from ..dsp import SR, mtof, secs
from .common import room_ir, sustain_loop, key_scale, lerp


# ---------------------------------------------------------------- Electric Piano
def epiano(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    ks = key_scale(z.root, 28, 100)
    vel = {"V1": 0.25, "V2": 0.6, "V3": 1.0}[z.group]
    n = secs(lerp(3.6, 1.5, ks))
    t = dsp.tvec(n)
    t60 = lerp(9.0, 2.2, ks)
    amp = np.exp(-t * dsp.LN1000 / t60) * (0.75 + 0.25 * np.exp(-t / 0.25))
    i0 = lerp(0.5, 3.2, vel) * lerp(1.0, 0.55, ks)
    index = i0 * np.exp(-t / lerp(0.5, 0.18, ks)) + lerp(0.08, 0.3, vel)
    mod = np.sin(2 * np.pi * f0 * t + rng.uniform(0, 6))
    car = np.sin(2 * np.pi * f0 * t + index * mod)
    # second, slightly detuned tine partial gives the slow "bell" beating
    car2 = np.sin(2 * np.pi * f0 * 2.0 * dsp.cents_to_ratio(0.8) * t + 0.4 * index * mod) * 0.08 * np.exp(-t / 1.2)
    ding_f = f0 * 14.1
    ding = np.sin(2 * np.pi * ding_f * t) * np.exp(-t / 0.012) * 0.25 * vel if ding_f < 18000 else 0
    x = (car + car2) * amp + ding
    # pickup non-linearity: velocity dependent "bark"
    x = dsp.saturate(x * lerp(0.8, 2.2, vel), lerp(0.8, 1.8, vel), 0.12)
    x = dsp.dc_block(x)
    thump = dsp.butter(rng.standard_normal(n), 400, "low", 2) * np.exp(-t / 0.012) * 0.05 * (0.5 + vel)
    x = x + thump
    x = dsp.butter(x, lerp(5500, 12000, vel), "low", 2)
    return dsp.fade_edges(x, 0.0005, 0.25), None


# ---------------------------------------------------------------- Nylon Guitar
GUITAR_BODY = [(98, 0.09, 1.0), (196, 0.12, 0.9), (290, 0.06, 0.5), (420, 0.05, 0.45), (560, 0.04, 0.3),
               (750, 0.03, 0.3), (1050, 0.03, 0.2), (1500, 0.02, 0.15), (2200, 0.015, 0.1)]


def guitar(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    ks = key_scale(z.root, 40, 76)
    lvl = (int(z.group[1]) - 1) / 2.0  # V1..V3 -> 0..1
    hard = lvl > 0.6
    n = secs(lerp(3.0, 1.8, ks))
    per = SR / f0
    exc = dsp.pluck_excitation(per, rng, bright=lerp(0.3, 0.85, lvl), position=rng.uniform(0.13, 0.2))
    x = dsp.ks_string(n, f0, exc, t60=lerp(4.5, 1.6, ks), bright=lerp(0.36, 0.15, lvl), stiff=0.06)
    body = dsp.body_ir(rng, GUITAR_BODY)
    x = signal.fftconvolve(x, body)[:n]
    t = dsp.tvec(n)
    finger = dsp.bp(rng.standard_normal(n), 3000, 1.0) * np.exp(-t / 0.006) * lerp(0.06, 0.22, lvl)
    x = x / (dsp.peak(x) + 1e-9) + finger
    x = dsp.hp(x, 70)
    x = dsp.eq(x, "highshelf", 5000, -3.0)
    return dsp.fade_edges(x, 0.0003, 0.25), None


# ---------------------------------------------------------------- Finger Bass
def finger_bass(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    ks = key_scale(z.root, 28, 58)
    lvl = (int(z.group[1]) - 1) / 2.0  # V1..V3 -> 0..1
    hard = lvl > 0.6
    n = secs(lerp(2.3, 1.6, ks))
    per = SR / f0
    exc = dsp.pluck_excitation(per, rng, bright=lerp(0.25, 0.65, lvl), position=0.25, length_periods=1.2)
    x = dsp.ks_string(n, f0, exc, t60=lerp(3.8, 2.4, ks), bright=lerp(0.3, 0.15, lvl), stiff=0.08)
    pick = int(per * 0.12)
    x = x - 0.6 * np.concatenate([np.zeros(pick), x[:-pick]])  # pickup position comb
    t = dsp.tvec(n)
    thump = dsp.butter(rng.standard_normal(n), 250, "low", 2) * np.exp(-t / 0.015) * lerp(0.25, 0.65, lvl)
    x = x / (dsp.peak(x) + 1e-9) + thump
    x = dsp.saturate(x * 1.2, 1.2)
    x = dsp.butter(x, lerp(2800, 4800, lvl), "low", 2)
    x = dsp.hp(x, 30)
    return dsp.fade_edges(x, 0.0005, 0.2), None


# ---------------------------------------------------------------- Drum Kit
HAT_FREQS = np.array([205.3, 304.4, 369.6, 522.7, 540.0, 800.0])


def _metal(n, rng, scale=1.7):
    x = np.zeros(n)
    for f in HAT_FREQS * scale * rng.uniform(0.99, 1.01):
        x += dsp.pulse(np.full(n, f), 0.5, SR, rng.uniform())
    return x / 6


def _cymbal(n, rng, lo=300, hi=14000, count=140, t60=(1.2, 3.2), tilt=0.3):
    t = dsp.tvec(n)
    freqs = np.exp(rng.uniform(np.log(lo), np.log(hi), count))
    x = np.zeros(n)
    for f in freqs:
        d = lerp(t60[1], t60[0], (np.log(f) - np.log(lo)) / (np.log(hi) - np.log(lo)))
        x += (1 / f ** tilt) * np.exp(-t * dsp.LN1000 / d) * np.sin(2 * np.pi * f * t + rng.uniform(0, 6))
    return x / (dsp.peak(x) + 1e-9)


def drum_piece(piece, n, rng, hard, var):
    t = dsp.tvec(n)
    v = 1.0 if hard is True else (0.55 if hard is False else float(hard))
    noise = rng.standard_normal(n)
    if piece == "kick":
        f = 46 * var + 120 * v * np.exp(-t / 0.032)
        body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * dsp.LN1000 / 0.55)
        click = dsp.hp(noise, 3000) * np.exp(-t / 0.0025) * 0.5 * v + np.sin(2 * np.pi * 3200 * t) * np.exp(-t / 0.002) * 0.3 * v
        x = dsp.saturate(body * 1.0 + click, lerp(1.2, 2.2, v))
    elif piece in ("snare", "rimshot"):
        f = np.array([185, 330, 455]) * var
        shell = dsp.modal(n, f * (1 + 0.03 * 0), [1, 0.6, 0.35], [0.22, 0.14, 0.09], rng=rng)
        wires = dsp.bp(noise, 5200, 0.55) * np.exp(-t * dsp.LN1000 / lerp(0.28, 0.42, v))
        stick = dsp.hp(noise, 2500) * np.exp(-t / 0.003) * 0.6
        x = shell * 0.7 + wires * lerp(0.6, 1.0, v) + stick * v
        if piece == "rimshot":
            x += dsp.modal(n, [920 * var, 1730 * var], [1, 0.5], [0.12, 0.08], rng=rng) * 0.9
            x = dsp.saturate(x * 1.2, 1.4)
    elif piece == "sidestick":
        x = dsp.modal(n, np.array([520, 1230, 1820]) * var, [1, 0.7, 0.4], [0.06, 0.04, 0.03], rng=rng)
        x += dsp.hp(noise, 2000) * np.exp(-t / 0.002) * 0.7
    elif piece == "clap":
        x = np.zeros(n)
        for k, off in enumerate([0, 0.009, 0.019, 0.03]):
            s = int((off + rng.uniform(0, 0.002)) * SR)
            e = np.exp(-np.clip(t - off, 0, None) / (0.006 if k < 3 else 0.12)) * (t >= off)
            x += e * dsp.bp(noise, 1200 * var, 1.1) * (1 if k < 3 else 1.2)
    elif piece in ("chh", "phh", "ohh"):
        m = _metal(n, rng)
        m = dsp.hp(dsp.bp(m, 9500, 1.0), 7000)
        nz = dsp.hp(noise, 8000) * 0.4
        d = {"chh": 0.07, "phh": 0.11, "ohh": 0.95}[piece] * lerp(0.8, 1.1, v)
        x = (m + nz) * np.exp(-t * dsp.LN1000 / d)
        if piece == "phh":
            x += dsp.bp(noise, 1100, 1.5) * np.exp(-t / 0.01) * 0.6
        x *= lerp(0.7, 1.0, v)
    elif piece == "tom":
        f0 = var
        f = f0 * (1 + 0.28 * np.exp(-t / 0.05))
        ph = 2 * np.pi * np.cumsum(f) / SR
        x = (np.sin(ph) * np.exp(-t * dsp.LN1000 / 0.9) + 0.35 * np.sin(1.59 * ph) * np.exp(-t * dsp.LN1000 / 0.4)
             + 0.2 * np.sin(2.14 * ph) * np.exp(-t * dsp.LN1000 / 0.25))
        x += dsp.hp(noise, 1500) * np.exp(-t / 0.004) * 0.5 * v + dsp.bp(noise, 600, 0.8) * np.exp(-t / 0.04) * 0.2
        x = dsp.saturate(x, 1.2)
    elif piece in ("crash", "crash2"):
        x = _cymbal(n, rng, 350, 14000, 160, (lerp(0.9, 1.3, v), lerp(2.2, 3.0, v)), 0.25)
        x += dsp.hp(noise, 4000) * np.exp(-t * dsp.LN1000 / 1.6) * 0.35
        x *= np.clip(t / 0.003, 0, 1)
        if piece == "crash2":
            x = dsp.eq(x, "peak", 5000, 3, 1.0)
    elif piece == "ride":
        x = _cymbal(n, rng, 400, 12000, 90, (1.4, 2.4), 0.4) * 0.6
        x += dsp.modal(n, [3100 * var, 4300 * var, 5600 * var], [1, 0.7, 0.4], [0.25, 0.2, 0.15], rng=rng) * lerp(0.4, 0.7, v)
        x += dsp.hp(noise, 6000) * np.exp(-t / 0.004) * 0.5
    elif piece == "bell":
        x = dsp.modal(n, np.array([730, 1530, 2270, 3080, 4400]) * var, [1, 0.8, 0.6, 0.4, 0.3], [1.8, 1.4, 1.1, 0.9, 0.7], rng=rng)
        x += _cymbal(n, rng, 600, 10000, 50, (1.0, 1.6), 0.3) * 0.3
    elif piece == "tamb":
        x = np.zeros(n)
        for k in range(5):
            off = k * rng.uniform(0.012, 0.02)
            e = np.exp(-np.clip(t - off, 0, None) / 0.05) * (t >= off) * (0.8 ** k)
            x += e * dsp.bp(noise, rng.uniform(6500, 8500), 2.0)
        x += dsp.bp(noise, 400, 1.0) * np.exp(-t / 0.02) * 0.2
    elif piece == "shaker":
        env = np.clip(t / 0.03, 0, 1) * np.exp(-np.clip(t - 0.03, 0, None) / 0.06)
        x = dsp.bp(noise, 6000, 1.2) * env
    else:
        raise ValueError(piece)
    return x


def drums(z):
    rng = np.random.default_rng(z.seed)
    piece = z.p["piece"]
    hard = {1: 0.4, 2: 0.7, 3: 1.0}[int(z.group[1])]
    var = z.p.get("var", 1.0) * (1 + rng.normal(0, 0.008))
    n = secs(z.p["len"])
    x = drum_piece(piece, n, rng, hard, var)
    x = dsp.dc_block(x)
    return dsp.fade_edges(x, 0.0002, min(0.3, z.p["len"] * 0.3)), None


# ---------------------------------------------------------------- Organ
DRAWBAR_RATIOS = [0.5, 1, 1.5, 2, 3, 4, 5, 6, 8]
REGISTRATIONS = {"Full": [8, 8, 8, 6, 0, 6, 0, 0, 6], "Soft": [0, 8, 6, 4, 0, 0, 0, 0, 0]}


def organ(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    n = secs(1.9)
    t = dsp.tvec(n)
    x = np.zeros(n)
    for r, lvl in zip(DRAWBAR_RATIOS, REGISTRATIONS[z.group]):
        if lvl == 0:
            continue
        f = f0 * r
        while f > 6500:  # tonewheel foldback
            f /= 2
        f *= dsp.cents_to_ratio(rng.uniform(-0.6, 0.6))
        a = 10 ** ((lvl - 8) * 3 / 20)
        x += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6))
    x /= 3.0
    click = dsp.bp(rng.standard_normal(n), 2500, 0.7) * np.exp(-t / 0.004) * 0.25
    leak = dsp.bp(rng.standard_normal(n), 800, 2) * 0.002
    x = dsp.saturate(x + click + leak, 1.35 if z.group == "Full" else 1.1)
    x = dsp.fade_edges(x, 0.001, 0.001)
    return sustain_loop(x, 0.4, 1.2, 0.12)


# ---------------------------------------------------------------- Mallets
MALLETS = {
    #           ratios                 amps                  t60 scale         base t60 (low, high)
    "Marimba": ([1.0, 3.98, 9.9], [1.0, 0.35, 0.12], [1.0, 0.4, 0.15], (1.4, 0.35), 0.0015),
    "Vibes": ([1.0, 4.0, 10.0], [1.0, 0.25, 0.05], [1.0, 0.35, 0.12], (5.0, 2.4), 0.0008),
    "Celesta": ([1.0, 2.0, 2.76, 5.4], [1.0, 0.18, 0.12, 0.04], [1.0, 0.5, 0.3, 0.15], (2.0, 0.9), 0.0015),
    "Glock": ([1.0, 2.76, 5.40, 8.93], [1.0, 0.5, 0.25, 0.1], [1.0, 0.35, 0.18, 0.1], (3.2, 1.8), 0.0004),
}
MALLET_RANGE = {"Marimba": (36, 96), "Vibes": (53, 89), "Celesta": (60, 108), "Glock": (72, 108)}


def mallets(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    ratios, amps, t60s, (tlo, thi), click = MALLETS[z.group]
    lo, hi = MALLET_RANGE[z.group]
    ks = key_scale(z.root, lo, hi)
    base = lerp(tlo, thi, ks)
    n = secs(min(base * 0.8 + 0.4, 3.6))
    t = dsp.tvec(n)
    x = dsp.modal(n, [f0 * r for r in ratios], amps, [base * s for s in t60s], rng=rng)
    if z.group in ("Marimba", "Vibes"):
        # resonator tube reinforces the fundamental with a slower bloom
        res = np.sin(2 * np.pi * f0 * t) * (1 - np.exp(-t / 0.01)) * np.exp(-t * dsp.LN1000 / (base * 1.2)) * 0.4
        x += res
    strike = dsp.bp(rng.standard_normal(n), min(f0 * 6, 9000), 1.2) * np.exp(-t / click) * 0.4
    x = x + strike
    return dsp.fade_edges(x, 0.0003, 0.2), None
