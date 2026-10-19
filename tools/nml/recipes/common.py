"""Shared synthesis helpers for the recipes."""
import functools

import numpy as np

from .. import dsp
from ..dsp import SR


@functools.lru_cache(maxsize=None)
def hall_ir(seconds=2.2, seed=7, predelay=0.02, hi_ratio=0.45):
    rng = np.random.default_rng(seed)
    return dsp.make_ir(seconds, rng, predelay=predelay, hi_t60=seconds * hi_ratio)


@functools.lru_cache(maxsize=None)
def room_ir(seconds=0.9, seed=11):
    rng = np.random.default_rng(seed)
    return dsp.make_ir(seconds, rng, predelay=0.006, hi_t60=seconds * 0.4, density=2.0)


def unison(n, f0, rng, voices=7, spread_cents=14.0, drift=3.0, osc="saw", width=0.85,
           pw=0.5, os=2, detune_curve=None, center_gain=1.0, phase_rand=True):
    """Stereo stack of detuned oscillators rendered at os*SR."""
    sr = SR * os
    m = n * os
    if detune_curve is None:
        offs = np.linspace(-1.0, 1.0, voices) if voices > 1 else np.zeros(1)
    else:
        offs = np.asarray(detune_curve)
    out = np.zeros((m, 2))
    for i, o in enumerate(offs):
        cents = o * spread_cents + rng.normal(0, spread_cents * 0.06)
        dr = dsp.drift_cents(m, rng, drift, 0.35, sr)
        f = f0 * dsp.cents_to_ratio(cents + dr)
        ph = rng.uniform() if phase_rand else 0.0
        if osc == "saw":
            v = dsp.saw(f, sr, ph)
        elif osc == "pulse":
            v = dsp.pulse(f, pw, sr, ph)
        elif osc == "tri":
            v = dsp.triangle(f, sr, ph)
        else:
            v = dsp.sine(f, sr, ph)
        g = center_gain if abs(o) < 1e-9 else 1.0
        pos = o * width if voices > 1 else 0.0
        out += dsp.pan(v * g, pos)
    out /= np.sqrt(len(offs))
    from scipy import signal
    return np.stack([signal.resample_poly(out[:, c], 1, os)[:n] for c in range(2)], axis=1)


def sustain_loop(x, loop_start, loop_len, xfade):
    return dsp.make_looped(x, loop_start, loop_len, xfade)


def key_scale(root, lo=24, hi=108):
    """0 at the bottom of the range, 1 at the top."""
    return float(np.clip((root - lo) / (hi - lo), 0.0, 1.0))


def lerp(a, b, t):
    return a + (b - a) * t
