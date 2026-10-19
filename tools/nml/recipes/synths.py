"""01 Synths and Pads."""
import numpy as np

from .. import dsp
from ..dsp import SR, mtof, secs
from .common import hall_ir, room_ir, unison, sustain_loop, key_scale, lerp


# ---------------------------------------------------------------- Warm Pad
def warm_pad(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    n = secs(3.0)
    t = dsp.tvec(n)
    ks = key_scale(z.root, 30, 96)
    if z.group == "Warm":
        x = unison(n, f0, rng, voices=7, spread_cents=13, drift=3.5, osc="saw", width=0.9)
        if f0 > 45:
            sub = dsp.triangle(f0 * 0.5 * dsp.cents_to_ratio(dsp.drift_cents(n, rng, 2)), SR, rng.uniform())
            x += dsp.stereo(sub) * 0.28
        x += unison(n, f0 * 2, rng, voices=2, spread_cents=6, osc="pulse", pw=0.3) * 0.18
        cut = (520 + f0 * 4.5) * (1 + 0.18 * dsp.smooth_noise(n, rng, 0.25)) * lerp(1.0, 1.6, ks)
        x = dsp.lp24(x, cut, 0.95)
        x = dsp.saturate(dsp.norm_rms(x, 0.2), 1.3)
        x = dsp.chorus(x, rng, voices=3, rate=0.27, depth_ms=3.0, mix=0.35)
        x = dsp.reverb(x, hall_ir(2.0, 3), 0.18)
        x = dsp.eq(x, "lowshelf", 160, 1.5)
    else:  # Air: breathy, tonal noise and an octave-up shimmer
        noise = rng.standard_normal((n, 2))
        tonal = np.zeros((n, 2))
        for k in range(1, 13):
            fk = f0 * k
            if fk > 15000:
                break
            g = 1.0 / k ** 0.6
            tonal += g * dsp.bp(noise, fk, 45.0)
        tonal *= 0.6
        sh = unison(n, f0 * 2, rng, voices=4, spread_cents=8, osc="tri", width=1.0)
        trem = 1 + 0.15 * np.sin(2 * np.pi * 0.21 * t + rng.uniform(0, 6))
        x = tonal / (dsp.rms(tonal) + 1e-9) * 0.1 + sh * trem[:, None] * 0.35
        x += dsp.butter(dsp.hp(unison(n, f0 * 4, rng, voices=3, spread_cents=10, osc="saw"), 2400), 6500, "low", 2) * 0.04
        x = dsp.hp(x, 120)
        x = dsp.chorus(x, rng, voices=3, rate=0.18, depth_ms=4.0, mix=0.4)
        x = dsp.butter(x, 8000, "low", 2)
        x = dsp.reverb(x, hall_ir(3.2, 5), 0.42)
    x = dsp.fade_edges(x, 0.02, 0.001)
    return sustain_loop(x, 1.0, 1.55, 0.45)


# ---------------------------------------------------------------- Glass Pad
def glass_pad(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    n = secs(3.0)
    t = dsp.tvec(n)
    x = np.zeros((n, 2))
    for v, (det, p) in enumerate([(-5, -0.7), (0, 0.0), (5, 0.7)]):
        fc = f0 * dsp.cents_to_ratio(det + dsp.drift_cents(n, rng, 2))
        idx = 0.55 + 2.4 * np.exp(-t / 0.22) + 0.2 * dsp.smooth_noise(n, rng, 0.3)
        mod = np.sin(2 * np.pi * np.cumsum(fc * 2.0) / SR + rng.uniform(0, 6))
        mod2 = np.sin(2 * np.pi * np.cumsum(fc * 3.51) / SR + rng.uniform(0, 6))
        ph = 2 * np.pi * np.cumsum(fc) / SR + idx * mod + 0.25 * np.exp(-t / 0.6) * mod2
        x += dsp.pan(np.sin(ph), p)
    octv = dsp.sine(f0 * 2 * dsp.cents_to_ratio(dsp.drift_cents(n, rng, 3)), SR, rng.uniform())
    swell = 1 - np.exp(-t / 0.6)
    x += dsp.pan(octv * swell * 0.35, 0.3 * np.sin(2 * np.pi * 0.13 * t))
    x = dsp.butter(x, 9000, "low", 2)
    x = dsp.chorus(x, rng, voices=3, rate=0.22, depth_ms=3.0, mix=0.45)
    x = dsp.reverb(x, hall_ir(3.5, 9), 0.38)
    x = dsp.fade_edges(x, 0.003, 0.001)
    return sustain_loop(x, 1.05, 1.5, 0.45)


# ---------------------------------------------------------------- Supersaw
SUPER_DETUNE = [-1.0, -0.62, -0.3, 0.0, 0.31, 0.6, 0.98]


def supersaw(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    n = secs(2.0)
    x = unison(n, f0, rng, spread_cents=24, drift=1.5, osc="saw", width=1.0,
               detune_curve=SUPER_DETUNE, center_gain=1.6)
    x += dsp.stereo(dsp.saw(f0 * 0.5 * np.ones(n), SR, rng.uniform())) * 0.25 * (f0 > 60)
    x = dsp.hp(x, max(40.0, f0 * 0.6), 0.6)
    x = dsp.butter(x, 11000, "low", 2)
    x = dsp.chorus(x, rng, voices=2, rate=0.5, depth_ms=1.5, mix=0.25)
    x = dsp.fade_edges(x, 0.002, 0.001)
    return sustain_loop(x, 0.45, 1.25, 0.35)


# ---------------------------------------------------------------- Mono Bass
def mono_bass(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    n = secs(1.7)
    t = dsp.tvec(n)
    if z.group == "Sub":
        ph = dsp.phase_of(np.full(n, f0))
        x = np.sin(2 * np.pi * ph) + 0.12 * np.sin(4 * np.pi * ph) + 0.05 * dsp.triangle(np.full(n, f0))
        x = dsp.saturate(x * 0.9, 1.3, 0.05)
        x = dsp.dc_block(x)
    else:  # Growl
        f = np.full(n, f0)
        x = 0.7 * dsp.saw(f * dsp.cents_to_ratio(-4)) + 0.55 * dsp.pulse(f * dsp.cents_to_ratio(5), 0.33)
        x += 0.35 * np.sin(2 * np.pi * dsp.phase_of(f * 0.5)) * (f0 > 40)
        cut = 180 + f0 * 3.2 + 2400 * np.exp(-t / 0.09)
        x = dsp.lp24(x, cut, 2.1)
        x = dsp.saturate(x * 1.6, 1.8)
        x = dsp.hp(x, 28)
        x = dsp.butter(x, 7000, "low", 2)
    x = dsp.fade_edges(x, 0.003, 0.001)
    return sustain_loop(x, 0.45, 1.0, 0.18)


# ---------------------------------------------------------------- Pluck
def pluck(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    rr = z.p.get("rr", 1)
    ks = key_scale(z.root, 30, 96)
    n = secs(lerp(1.5, 0.9, ks))
    t = dsp.tvec(n)
    x = unison(n, f0, rng, voices=2, spread_cents=7 + rr, osc="saw", width=0.6)
    x += unison(n, f0, rng, voices=1, osc="pulse", pw=0.42) * 0.45
    x += unison(n, f0 * 2, rng, voices=1, osc="sine") * 0.15
    tau = 0.11 + 0.015 * rr
    cut = f0 * 1.3 + 200 + (5200 + f0 * 2.5) * np.exp(-t / tau)
    x = dsp.lp24(x, cut, 1.6)
    amp = dsp.env_exp(n, lerp(1.3, 0.7, ks), attack=0.0015)
    x = x * amp[:, None]
    x = dsp.chorus(x, rng, voices=2, rate=0.6, depth_ms=1.2, mix=0.25)
    x = dsp.reverb(x, room_ir(0.8, 21 + rr), 0.1)
    return dsp.fade_edges(x, 0.0005, 0.05), None


# ---------------------------------------------------------------- Choir
FORMANTS = {
    ("Aah", "f"): [(800, 80, 0), (1150, 90, -4), (2900, 120, -20), (3900, 130, -36), (4950, 140, -38)],
    ("Aah", "m"): [(650, 70, 0), (1080, 80, -6), (2650, 110, -7), (2900, 120, -8), (3250, 130, -22)],
    ("Ooh", "f"): [(350, 50, 0), (750, 60, -12), (2700, 170, -30), (3800, 180, -40), (4950, 200, -50)],
    ("Ooh", "m"): [(400, 40, 0), (800, 80, -10), (2600, 100, -28), (2800, 120, -29), (3000, 120, -32)],
}


def _choir_source(n, f0, rng, singers=8, vib_depth=22.0):
    out = np.zeros((n, 2))
    for s in range(singers):
        cents = rng.normal(0, 7) + dsp.vibrato_cents(n, rng, rng.uniform(4.8, 5.9), vib_depth * rng.uniform(0.7, 1.2),
                                                    0.5) + dsp.drift_cents(n, rng, 5, 0.3)
        f = f0 * dsp.cents_to_ratio(cents)
        v = dsp.saw(f, SR, rng.uniform())
        amp = 1 + 0.12 * dsp.smooth_noise(n, rng, 2.0)
        out += dsp.pan(v * amp, (s / (singers - 1) * 2 - 1) * 0.85)
    # glottal tilt: extra -6 dB/oct above ~700 Hz
    return dsp.butter(out, 700, "low", 1) * 2 + out * 0.08


def choir(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    n = secs(3.0)
    voice = "f" if z.root >= 58 else "m"
    form = FORMANTS[(z.group, voice)]
    src = _choir_source(n, f0, rng)
    x = dsp.formant_bank(src, form)
    x /= dsp.rms(x) + 1e-9
    breath = dsp.formant_bank(rng.standard_normal((n, 2)), form)
    breath /= dsp.rms(breath) + 1e-9
    x += breath * 0.07 * (1 + 0.4 * dsp.smooth_noise(n, rng, 1.5))[:, None]
    x = dsp.hp(x, 90)
    x = dsp.eq(x, "peak", 3000, 2.0, 0.8)
    x = dsp.butter(x, 7500, "low", 2)
    x = dsp.reverb(x, hall_ir(2.8, 13), 0.32)
    x = dsp.fade_edges(x, 0.05, 0.001)
    return sustain_loop(x, 1.05, 1.5, 0.5)
