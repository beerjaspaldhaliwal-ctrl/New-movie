"""Orchestral percussion and 03 Cinematic (braams, drones, FX)."""
import numpy as np
from scipy import signal

from .. import dsp
from ..dsp import SR, mtof, secs
from .common import hall_ir, unison, sustain_loop, lerp
from .band import _cymbal, drum_piece
from .orchestral import _bowed_section, _timp_hit
from .synths import _choir_source, FORMANTS


# ---------------------------------------------------------------- membranes
def _membrane(n, rng, f0, t60=1.5, pitch_drop=0.15, slap=0.4, modes=None):
    t = dsp.tvec(n)
    modes = modes or [(1.0, 1.0, 1.0), (1.59, 0.5, 0.5), (2.14, 0.3, 0.35), (2.3, 0.2, 0.3), (2.65, 0.15, 0.25)]
    f = f0 * (1 + pitch_drop * np.exp(-t / 0.06))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.zeros(n)
    for r, a, d in modes:
        x += a * np.sin(r * ph + rng.uniform(0, 6)) * np.exp(-t * dsp.LN1000 / (t60 * d))
    noise = rng.standard_normal(n)
    x += dsp.butter(noise, 900, "low", 2) * np.exp(-t / 0.02) * slap
    x += dsp.bp(noise, 2500, 0.8) * np.exp(-t / 0.004) * slap * 0.5
    return dsp.saturate(x, 1.3)


def perc_piece(piece, n, rng, var):
    t = dsp.tvec(n)
    noise = rng.standard_normal(n)
    if piece == "grancassa":
        return _membrane(n, rng, 42 * var, t60=3.0, pitch_drop=0.08, slap=0.25)
    if piece == "taiko":
        return _membrane(n, rng, 72 * var, t60=1.4, pitch_drop=0.2, slap=0.7)
    if piece == "taikoens":
        x = np.zeros(n)
        for k in range(5):
            d = int(rng.uniform(0, 0.03) * SR)
            h = _membrane(n - d, rng, rng.uniform(58, 95) * var, t60=rng.uniform(1.2, 1.8), slap=0.6)
            x[d:] += h * rng.uniform(0.6, 1.0)
        return x
    if piece == "taikorim":
        x = dsp.modal(n, np.array([780, 1650, 2400]) * var, [1, 0.6, 0.3], [0.08, 0.05, 0.04], rng=rng)
        return x + dsp.hp(noise, 2000) * np.exp(-t / 0.003) * 0.6
    if piece == "boom":
        x = _membrane(n, rng, 36 * var, t60=4.0, pitch_drop=0.5, slap=0.9)
        sub = np.sin(2 * np.pi * np.cumsum(30 + 40 * np.exp(-t / 0.2)) / SR) * np.exp(-t * dsp.LN1000 / 3.0)
        return dsp.saturate(x + sub, 1.5)
    if piece == "osnare":
        return drum_piece("snare", n, rng, True, var * 1.1)
    if piece in ("gcroll", "sroll"):
        x = np.zeros(n)
        tt = 0.0
        rate = 13.0 if piece == "gcroll" else 22.0
        while tt < n / SR:
            s = int(tt * SR)
            m = min(n - s, secs(1.2))
            if piece == "gcroll":
                h = _membrane(m, rng, 42 * var, t60=2.0, pitch_drop=0.05, slap=0.15)
            else:
                h = drum_piece("snare", m, rng, False, var * 1.1) * 0.8
            x[s:s + m] += h[:m] * rng.uniform(0.6, 1.0)
            tt += 1 / rate * rng.uniform(0.85, 1.15)
        return x
    if piece == "piatti":
        x = _cymbal(n, rng, 500, 15000, 200, (1.6, 3.6), 0.2)
        return x + dsp.hp(noise, 3000) * np.exp(-t * dsp.LN1000 / 2.0) * 0.4
    if piece == "swell":
        roll = np.zeros(n)
        tt = 0.0
        while tt < n / SR:
            s = int(tt * SR)
            m = min(n - s, secs(2.0))
            roll[s:s + m] += _cymbal(m, rng, 700, 13000, 40, (1.0, 2.0), 0.2)[:m]
            tt += 0.045
        env = np.clip(t / (n / SR * 0.82), 0, 1) ** 2.4
        env[t > n / SR * 0.82] = np.exp(-(t[t > n / SR * 0.82] - n / SR * 0.82) / 0.25)
        return roll * env
    if piece == "suscym":
        return _cymbal(n, rng, 600, 14000, 120, (1.4, 3.0), 0.3) * np.clip(t / 0.004, 0, 1)
    if piece == "tamtam":
        x = _cymbal(n, rng, 70, 4500, 220, (3.5, 6.0), 0.1)
        bloom = 0.35 + 0.65 * (1 - np.exp(-t / 0.5))
        return x * bloom + _membrane(n, rng, 55, 2.0, 0.0, 0.5) * 0.3
    if piece == "triangle":
        f = 1180 * var
        return dsp.modal(n, [f, f * 2.66, f * 4.1, f * 5.5, f * 6.9], [1, 0.6, 0.5, 0.35, 0.25],
                         [3.0, 2.6, 2.2, 1.8, 1.5], rng=rng) + dsp.hp(noise, 5000) * np.exp(-t / 0.002) * 0.3
    if piece == "anvil":
        f = 1350 * var
        return dsp.modal(n, [f, f * 2.4, f * 3.7, f * 5.1], [1, 0.7, 0.4, 0.3], [1.3, 0.9, 0.6, 0.4], rng=rng) + \
            dsp.hp(noise, 3000) * np.exp(-t / 0.002)
    if piece == "woodblock":
        return dsp.modal(n, np.array([1050, 2400]) * var, [1, 0.3], [0.09, 0.05], rng=rng) + \
            dsp.hp(noise, 3000) * np.exp(-t / 0.0015) * 0.4
    if piece == "otamb":
        return drum_piece("tamb", n, rng, True, var)
    raise ValueError(piece)


def orch_perc(z):
    rng = np.random.default_rng(z.seed)
    piece = z.p["piece"]
    var = 1 + rng.normal(0, 0.01)
    n = secs(z.p["len"])
    x = perc_piece(piece, n, rng, var)
    x = dsp.dc_block(x)
    x = dsp.mono(dsp.reverb(x, hall_ir(2.4, 71), 0.15))
    if z.p.get("hold"):
        x = dsp.fade_edges(x, 0.002, 0.001)
        return sustain_loop(x, 1.0, z.p["len"] - 1.4, 0.4)
    return dsp.fade_edges(x, 0.0002, 0.3), None


# ---------------------------------------------------------------- Braams
def braams(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    n = secs(3.4)
    t = dsp.tvec(n)
    amp = np.clip(t / 0.05, 0, 1) * np.exp(-np.clip(t - 1.8, 0, None) / 0.45) * (1 - 0.15 * t / 3.4)
    bend = -45 * np.clip((t - 1.6) / 1.4, 0, 1) ** 2
    if z.group == "Braam":
        x = unison(n, f0, rng, voices=6, spread_cents=12, osc="saw", width=0.9)
        x += unison(n, f0 * 2, rng, voices=3, spread_cents=9, osc="saw", width=0.6) * 0.5
        x += unison(n, f0 * 1.5, rng, voices=2, spread_cents=6, osc="saw") * 0.2
        cut = 160 + (2600 + f0 * 18) * np.clip(t / 0.35, 0, 1) ** 1.5 * np.exp(-np.clip(t - 0.35, 0, None) / 1.1) + 700
        x = dsp.lp24(x, cut, 1.4)
        x = dsp.saturate(x * 2.5, 2.4)
        x = dsp.butter(x, 6500, "low", 2)
    else:  # Blaster: ring-modulated, folded and distorted
        sq = unison(n, f0, rng, voices=3, spread_cents=8, osc="pulse", pw=0.4)
        sw = unison(n, f0 * 1.005, rng, voices=3, spread_cents=15, osc="saw")
        ring = np.sin(2 * np.pi * f0 * 1.414 * t)[:, None]
        x = sq * 0.6 + sw * 0.6 + sq * ring * 0.4
        x = dsp.fold(x * 0.8, 1.2)
        cut = 300 + 5000 * np.clip(t / 0.25, 0, 1) * np.exp(-np.clip(t - 0.25, 0, None) / 1.4)
        x = dsp.lp24(x, cut, 2.0)
        x = dsp.saturate(x * 3.0, 3.0)
    ratio = dsp.cents_to_ratio(bend)
    # apply the end-of-note pitch fall by resampling time
    idx = np.cumsum(ratio)
    idx = idx - idx[0]
    x = np.stack([np.interp(idx, np.arange(n), x[:, c]) for c in range(2)], axis=1)
    x = x * amp[:, None]
    x = dsp.hp(x, 28)
    x = dsp.fade_edges(x, 0.001, 0.25)  # dry tail must reach zero before the reverb tail takes over
    x = dsp.reverb_tail(x, hall_ir(3.0, 81), 0.25, extra=1.0)
    return dsp.fade_edges(x, 0.001, 0.4), None


# ---------------------------------------------------------------- Drones
def drones(z):
    rng = np.random.default_rng(z.seed)
    f0 = float(mtof(z.root))
    n = secs(5.6)
    t = dsp.tvec(n)
    g = z.group
    if g == "DarkStrings":
        x = _bowed_section(n, f0, rng, "p", attack=0.6, vib=6)
        x += _bowed_section(n, f0 * 1.5, rng, "p", attack=0.9, vib=6) * 0.5
        x += _bowed_section(n, f0 / 2, rng, "p", attack=0.9, vib=4) * 0.6
        x = dsp.butter(x, 2200, "low", 2)
        x = dsp.reverb(x, hall_ir(3.5, 91), 0.4)
    elif g == "GlassAir":
        x = np.zeros((n, 2))
        for k, r in enumerate([4.0, 6.02, 8.97, 11.1, 13.4]):
            tr = 0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(0.05, 0.2) * t + rng.uniform(0, 6))
            x += dsp.pan(np.sin(2 * np.pi * f0 * r * t) * tr / (k + 1), rng.uniform(-0.8, 0.8))
        sweep = 3000 + 2500 * np.sin(2 * np.pi * 0.11 * t)
        x += dsp.bp(rng.standard_normal((n, 2)), sweep, 3.0) * 0.08
        x = dsp.reverb(x, hall_ir(4.0, 93), 0.5)
    elif g == "ChoirDrone":
        src = _choir_source(n, f0, rng, singers=10, vib_depth=12)
        src += _choir_source(n, f0 * 1.5, rng, singers=6, vib_depth=12) * 0.5
        x = dsp.formant_bank(src, FORMANTS[("Ooh", "m")])
        x = dsp.reverb(x / (dsp.rms(x) + 1e-9), hall_ir(4.0, 95), 0.5)
    elif g == "MetalShimmer":
        exc = rng.standard_normal((n, 2))
        x = np.zeros((n, 2))
        for r in [1.0, 2.32, 3.86, 5.1, 6.92, 8.3]:
            x += dsp.bp(exc, f0 * r * 2, 120.0) * (1 + 0.5 * np.sin(2 * np.pi * rng.uniform(0.1, 0.4) * t))[:, None]
        x = dsp.butter(x, 9000, "low", 2)
        x = dsp.reverb(x, hall_ir(4.5, 97), 0.5)
    elif g == "SubRumble":
        x = dsp.stereo(np.sin(2 * np.pi * f0 * 0.5 * t) * 0.6 + np.sin(2 * np.pi * f0 * t) * 0.3)
        rum = dsp.butter(rng.standard_normal((n, 2)), 180, "low", 4) * 2.0
        x = x * (1 + 0.2 * np.sin(2 * np.pi * 0.17 * t))[:, None] + rum
        x = dsp.saturate(x, 1.3)
        x = dsp.reverb(x, hall_ir(3.0, 99), 0.3)
    elif g == "GhostPad":
        x = unison(n, f0, rng, voices=5, spread_cents=10, osc="tri")
        x += unison(n, f0 * 2.0, rng, voices=4, spread_cents=14, osc="saw") * 0.15
        x += unison(n, f0 * 3.0, rng, voices=2, spread_cents=8, osc="sine") * 0.2
        x = dsp.butter(x, 1800, "low", 2)
        x = dsp.reverb(x, hall_ir(6.0, 101, 0.05), 0.75)
    elif g == "TensionCluster":
        x = np.zeros((n, 2))
        for semi in [0, 1, 2, 6]:
            x += _bowed_section(n, f0 * 2 ** (semi / 12), rng, "p", players=5, attack=0.8, vib=3, trem=semi == 1)
        x = dsp.reverb(x, hall_ir(3.0, 103), 0.35)
    else:  # Heartbeat pulse: 1.4 Hz throb, loop length is a whole number of beats
        beat = 1 / 1.4
        ph = (t % beat) / beat

        def thump(p, at):
            q = p - at
            return np.where(q >= 0, (1 - np.exp(-q / 0.012)) * np.exp(-q / 0.08), 0.0)
        throb = thump(ph, 0.1) + 0.6 * thump(ph, 0.32)
        x = dsp.stereo(np.sin(2 * np.pi * f0 * t) * throb * 0.9)
        x += unison(n, f0 * 2, rng, voices=3, spread_cents=6, osc="tri") * 0.12
        x = dsp.saturate(x, 1.4)
        x = dsp.reverb(x, hall_ir(2.0, 105), 0.25)
        x = dsp.fade_edges(x, 0.01, 0.001)
        ls = int(round(2 * beat * SR))
        le = ls + int(round(4 * beat * SR))
        xf = int(0.05 * SR)
        return dsp.bake_loop(x, ls, le, xf), (ls, le)
    x = dsp.fade_edges(x, 0.05, 0.001)
    return sustain_loop(x, 1.4, 3.3, 0.9)


# ---------------------------------------------------------------- FX
def _noise_sweep(n, rng, f_from, f_to, q=1.5, shape=1.0):
    t = dsp.tvec(n)
    k = (t / t[-1]) ** shape
    fc = f_from * (f_to / f_from) ** k
    return dsp.bp(rng.standard_normal((n, 2)), fc, q)


def fx(z):
    rng = np.random.default_rng(z.seed)
    kind = z.p["fx"]
    n = secs(z.p["len"])
    t = dsp.tvec(n)
    T = n / SR
    big = hall_ir(3.2, 111)
    if kind == "boom":
        sub = np.sin(2 * np.pi * np.cumsum(28 + 70 * np.exp(-t / 0.15)) / SR) * np.exp(-t * dsp.LN1000 / 3.0)
        crack = dsp.butter(rng.standard_normal(n), 2500, "low", 2) * np.exp(-t / 0.03)
        x = dsp.stereo(dsp.saturate(sub * 1.2 + crack * 0.8, 1.6))
        x = dsp.reverb(x, big, 0.3)
    elif kind == "subdrop":
        f = 25 + 70 * np.exp(-t / 0.7)
        x = dsp.stereo(dsp.saturate(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * dsp.LN1000 / 3.8), 1.4))
    elif kind == "trailer":
        x = dsp.stereo(perc_piece("taikoens", n, rng, 0.9)) * 0.8
        x += dsp.stereo(perc_piece("boom", n, rng, 1.0)) * 0.6
        x += dsp.stereo(_cymbal(n, rng, 600, 14000, 120, (1.2, 2.6), 0.2)) * 0.25
        x = dsp.reverb(dsp.saturate(x, 1.5), big, 0.35)
    elif kind == "metal":
        x = dsp.stereo(perc_piece("anvil", n, rng, 0.45) + _cymbal(n, rng, 150, 6000, 120, (1.5, 3.0), 0.1) * 0.6)
        x = dsp.reverb(x, big, 0.4)
    elif kind == "lowhit":
        x = dsp.stereo(_membrane(n, rng, 48, 2.5, 0.35, 1.0) * 0.8 + perc_piece("boom", n, rng, 1.2) * 0.4)
        x = dsp.reverb(x, big, 0.35)
    elif kind == "glasshit":
        f = 1400
        x = dsp.modal(n, [f, f * 2.76, f * 5.4, f * 7.1, f * 9.3], [1, 0.7, 0.5, 0.3, 0.2], [2.5, 2.0, 1.5, 1.0, 0.8], rng=rng)
        x = dsp.stereo(x + dsp.hp(rng.standard_normal(n), 6000) * np.exp(-t / 0.01) * 0.4)
        x = dsp.reverb(x, big, 0.45)
    elif kind == "riser_noise":
        env = (t / T) ** 2.2 * np.exp(-np.clip(t - T * 0.85, 0, None) / 0.05)
        x = _noise_sweep(n, rng, 300, 9000, 2.0, 1.5) * env[:, None] * 2
        x += dsp.stereo(dsp.saw(110 * 2 ** (3 * t / T)) * env * 0.15)
        x = dsp.reverb(x, big, 0.3)
    elif kind == "riser_tonal":
        env = (t / T) ** 2.0 * np.exp(-np.clip(t - T * 0.85, 0, None) / 0.05)
        x = np.zeros((n, 2))
        for k in range(6):  # Shepard-like rising stack
            f = 55 * 2 ** (k + 2.5 * t / T)
            w = np.exp(-((np.log2(f) - np.log2(440)) ** 2) / 4)
            x += dsp.pan(dsp.saw(f, SR, rng.uniform()) * w, rng.uniform(-0.6, 0.6))
        x = dsp.lp24(x, 600 + 9000 * (t / T) ** 2, 1.2) * env[:, None]
        x = dsp.reverb(x, big, 0.35)
    elif kind == "riser_tension":
        x = np.zeros((n, 2))
        for semi in [0, 1, 5, 6]:
            f0 = 196 * 2 ** (semi / 12)
            sec = _bowed_section(n, f0, rng, "f", players=5, attack=0.4, vib=2, trem=True)
            gl = 2 ** (2.0 * (t / T) ** 1.6)
            idx = np.cumsum(gl)
            sec = np.stack([np.interp(idx, np.arange(n), sec[:, c], right=0) for c in range(2)], axis=1)
            x += sec
        env = (t / T) ** 1.5 * np.exp(-np.clip(t - T * 0.88, 0, None) / 0.06)
        x = dsp.reverb(x * env[:, None], big, 0.3)
    elif kind == "revcymbal":
        c = _cymbal(n, rng, 500, 15000, 160, (1.2, 2.8), 0.2)
        x = dsp.stereo(c[::-1] * np.clip((T - t) / 0.01, 0, 1))
        x = dsp.reverb(x, big, 0.2)
    elif kind == "revhit":
        dry = dsp.fade_edges(perc_piece("boom", secs(1.0), rng, 1.0), 0.0005, 0.3)
        hit = dsp.reverb_tail(dsp.stereo(dry), hall_ir(3.0, 113), 0.7, extra=T - 1.0)
        x = hit[:n][::-1].copy()
        x[-secs(0.02):] *= np.linspace(1, 0, secs(0.02))[:, None]
    elif kind in ("whoosh_fast", "whoosh_slow"):
        env = np.sin(np.pi * np.clip(t / T, 0, 1)) ** 3
        x = _noise_sweep(n, rng, 400, 5000, 1.2, 0.8) * env[:, None]
        p = np.linspace(-1, 1, n)
        x = np.stack([x[:, 0] * np.cos((p + 1) * np.pi / 4), x[:, 1] * np.sin((p + 1) * np.pi / 4)], axis=1) * 2
        x = dsp.reverb(x, big, 0.3)
    elif kind == "downer":
        f = 880 * 2 ** (-4 * (t / T) ** 0.8)
        x = dsp.stereo(dsp.saw(f) * 0.5 + np.sin(2 * np.pi * np.cumsum(f / 2) / SR))
        x = dsp.lp24(x, 300 + 6000 * (1 - t / T) ** 2, 1.5) * np.exp(-t / (T * 0.5))[:, None]
        x = dsp.reverb(x, big, 0.35)
    elif kind == "powerdown":
        sp = np.clip(1 - t / (T * 0.8), 0.0, 1) ** 1.5
        f = 110 * sp + 1
        x = dsp.stereo(dsp.saw(f) * 0.6 + dsp.pulse(f * 2, 0.3) * 0.3) * (sp > 0.01)[:, None]
        x = dsp.lp24(x, 200 + 5000 * sp, 1.0)
        x = dsp.reverb(x, big, 0.25)
    elif kind == "braamstab":
        x = unison(n, 55, rng, voices=6, spread_cents=14, osc="saw") + unison(n, 110, rng, voices=3, osc="saw") * 0.5
        env = np.clip(t / 0.02, 0, 1) * np.exp(-t / 0.5)
        x = dsp.lp24(dsp.saturate(x * 2, 2.2), 400 + 4000 * np.exp(-t / 0.4), 1.2) * env[:, None]
        x = dsp.reverb(x, big, 0.35)
    elif kind == "heartbeat":
        x = np.zeros(n)
        for off in [0.0, 0.28, 1.05, 1.33]:
            s = int(off * SR)
            m = n - s
            x[s:] += _membrane(m, rng, 45, 0.6, 0.3, 0.3)[:m] * (1.0 if off in (0.0, 1.05) else 0.7)
        x = dsp.stereo(dsp.butter(x, 400, "low", 2))
        x = dsp.reverb(x, big, 0.2)
    elif kind == "ticks":
        x = np.zeros(n)
        for k in range(int(T * 2)):
            s = int(k * 0.5 * SR)
            m = min(n - s, secs(0.2))
            x[s:s + m] += dsp.modal(m, [2400, 5100], [1, 0.4], [0.04, 0.03], rng=rng) * (1 if k % 2 == 0 else 0.7)
        x = dsp.reverb(dsp.stereo(x), big, 0.25)
    elif kind == "glitch":
        x = np.zeros((n, 2))
        src = unison(n, 220, rng, 3, 10, osc="pulse") + dsp.stereo(rng.standard_normal(n)) * 0.3
        pos = 0
        while pos < n:
            L = int(rng.choice([0.03, 0.06, 0.09]) * SR)
            seg = src[pos:pos + L] * rng.uniform(0.3, 1.0)
            if rng.random() < 0.4:
                seg = seg[::2].repeat(2, axis=0)[:L]
            x[pos:pos + seg.shape[0]] = seg * np.hanning(seg.shape[0] * 2 + 2)[1:seg.shape[0] + 1, None] ** 0.1
            pos += L
        x = dsp.saturate(dsp.bp(x, 1800, 0.7) * 3, 2.0)
    elif kind == "thunder":
        rum = dsp.butter(rng.standard_normal((n, 2)), 300, "low", 4)
        tc = np.clip(t - 0.3, 0, None)
        crack = dsp.bp(rng.standard_normal((n, 2)), 2500, 0.6) * ((1 - np.exp(-tc / 0.03)) * np.exp(-tc / 0.3))[:, None]
        env = (1 - np.exp(-t / 0.4)) * np.exp(-t / 1.6)
        x = (rum * 3 + crack * 0.6) * env[:, None]
        x = dsp.reverb(x, big, 0.4)
    else:
        raise ValueError(kind)
    x = dsp.dc_block(x)
    return dsp.fade_edges(x, 0.0005, min(0.4, T * 0.15)), None
