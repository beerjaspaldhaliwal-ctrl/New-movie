"""DSP building blocks for the New Movie Library sample generator.

Everything renders at SR (44.1 kHz) in float64. Oscillators that can alias are
band-limited with PolyBLEP and, where it matters, rendered at 2x and
decimated. Numba is used for the per-sample loops (filters, strings, delays).
"""
import math

import numpy as np
from numba import njit
from scipy import signal

SR = 44100
LN1000 = math.log(1000.0)


# --------------------------------------------------------------------------
# basics
# --------------------------------------------------------------------------
def mtof(m):
    return 440.0 * 2.0 ** ((np.asarray(m, dtype=np.float64) - 69.0) / 12.0)


def db(x):
    return 10.0 ** (x / 20.0)


def secs(n, sr=SR):
    return int(round(n * sr))


def tvec(n, sr=SR):
    return np.arange(n, dtype=np.float64) / sr


def cents_to_ratio(c):
    return 2.0 ** (np.asarray(c, dtype=np.float64) / 1200.0)


def smooth_noise(n, rng, hz, sr=SR):
    """Band-limited random signal (approx -1..1) changing at roughly `hz`."""
    step = max(1.0, sr / max(hz, 0.01))
    pts = rng.uniform(-1.0, 1.0, int(n / step) + 3)
    pos = np.arange(n) / step
    i = pos.astype(np.int64)
    frac = pos - i
    w = 0.5 - 0.5 * np.cos(np.pi * frac)  # cosine interpolation: smooth, no overshoot
    return pts[i] * (1.0 - w) + pts[i + 1] * w


def vibrato_cents(n, rng, rate=5.2, depth=12.0, onset=0.35, jitter=0.12, sr=SR):
    """Natural vibrato: slightly wandering rate/depth with a delayed onset."""
    t = tvec(n, sr)
    r = rate * (1.0 + jitter * smooth_noise(n, rng, 0.7, sr))
    ph = 2.0 * np.pi * np.cumsum(r) / sr + rng.uniform(0, 2 * np.pi)
    d = depth * (1.0 + 0.25 * smooth_noise(n, rng, 0.5, sr))
    env = np.clip(t / max(onset, 1e-3), 0.0, 1.0) ** 1.5
    return d * env * np.sin(ph)


def drift_cents(n, rng, amount=3.0, hz=0.4, sr=SR):
    return amount * smooth_noise(n, rng, hz, sr)


# --------------------------------------------------------------------------
# oscillators
# --------------------------------------------------------------------------
@njit(cache=True)
def _saw_blep(freq, sr, phase0):
    n = freq.size
    out = np.empty(n)
    t = phase0
    for i in range(n):
        dt = freq[i] / sr
        v = 2.0 * t - 1.0
        if t < dt:
            x = t / dt
            v -= x + x - x * x - 1.0
        elif t > 1.0 - dt:
            x = (t - 1.0) / dt
            v -= x * x + x + x + 1.0
        out[i] = v
        t += dt
        if t >= 1.0:
            t -= 1.0
    return out


@njit(cache=True)
def _blep(t, dt):
    if t < dt:
        x = t / dt
        return x + x - x * x - 1.0
    elif t > 1.0 - dt:
        x = (t - 1.0) / dt
        return x * x + x + x + 1.0
    return 0.0


@njit(cache=True)
def _pulse_blep(freq, pw, sr, phase0):
    n = freq.size
    out = np.empty(n)
    t = phase0
    for i in range(n):
        dt = freq[i] / sr
        w = pw[i]
        v = 1.0 if t < w else -1.0
        v += _blep(t, dt)
        t2 = t - w
        if t2 < 0.0:
            t2 += 1.0
        v -= _blep(t2, dt)
        out[i] = v
        t += dt
        if t >= 1.0:
            t -= 1.0
    return out


def saw(freq, sr=SR, phase0=0.0):
    return _saw_blep(np.ascontiguousarray(freq, dtype=np.float64), float(sr), float(phase0))


def pulse(freq, pw=0.5, sr=SR, phase0=0.0):
    freq = np.ascontiguousarray(freq, dtype=np.float64)
    pw = np.broadcast_to(np.asarray(pw, dtype=np.float64), freq.shape).copy()
    return _pulse_blep(freq, pw, float(sr), float(phase0))


def phase_of(freq, sr=SR, phase0=0.0):
    return (phase0 + np.cumsum(np.asarray(freq, dtype=np.float64)) / sr) % 1.0


def sine(freq, sr=SR, phase0=0.0):
    return np.sin(2.0 * np.pi * phase_of(freq, sr, phase0))


def triangle(freq, sr=SR, phase0=0.0):
    p = phase_of(freq, sr, phase0)
    return 4.0 * np.abs(p - 0.5) - 1.0


def additive(freq, amps, sr=SR, phase0=None, rng=None):
    """Sum of harmonics k*freq with amplitudes amps[k-1]; harmonics above
    Nyquist*0.9 are dropped per sample, so it never aliases."""
    freq = np.asarray(freq, dtype=np.float64)
    base = 2.0 * np.pi * np.cumsum(freq) / sr
    out = np.zeros_like(freq)
    nyq = 0.45 * sr
    for k, a in enumerate(amps, start=1):
        if a == 0:
            continue
        ph = 0.0 if phase0 is None else phase0[k - 1]
        if rng is not None and phase0 is None:
            ph = rng.uniform(0, 2 * np.pi)
        mask = (freq * k) < nyq
        if not mask.any():
            break
        out += a * np.sin(k * base + ph) * mask
    return out


def oversampled(fn, n, factor=2):
    """Run fn(n_os, sr_os) at factor*SR and decimate back to SR."""
    y = fn(n * factor, SR * factor)
    if y.ndim == 1:
        return signal.resample_poly(y, 1, factor)[:n]
    return np.stack([signal.resample_poly(y[:, c], 1, factor)[:n] for c in range(y.shape[1])], axis=1)


# --------------------------------------------------------------------------
# filters
# --------------------------------------------------------------------------
@njit(cache=True)
def _svf(x, fc, q, sr, mode):
    n = x.size
    y = np.empty(n)
    ic1 = 0.0
    ic2 = 0.0
    for i in range(n):
        f = fc[i]
        if f > 0.49 * sr:
            f = 0.49 * sr
        if f < 5.0:
            f = 5.0
        g = math.tan(math.pi * f / sr)
        k = 1.0 / q[i]
        a1 = 1.0 / (1.0 + g * (g + k))
        a2 = g * a1
        a3 = g * a2
        v3 = x[i] - ic2
        v1 = a1 * ic1 + a2 * v3
        v2 = ic2 + a2 * ic1 + a3 * v3
        ic1 = 2.0 * v1 - ic1
        ic2 = 2.0 * v2 - ic2
        if mode == 0:
            y[i] = v2
        elif mode == 1:
            y[i] = v1
        elif mode == 2:
            y[i] = x[i] - k * v1 - v2
        else:
            y[i] = x[i] - k * v1  # notch
    return y


_SVF_MODES = {"lp": 0, "bp": 1, "hp": 2, "notch": 3}


def svf(x, fc, q=0.707, mode="lp", sr=SR):
    """Zero-delay-feedback state variable filter; fc and q may be arrays."""
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 2:
        return np.stack([svf(x[:, c], fc, q, mode, sr) for c in range(x.shape[1])], axis=1)
    fc = np.broadcast_to(np.asarray(fc, dtype=np.float64), x.shape).copy()
    q = np.broadcast_to(np.asarray(q, dtype=np.float64), x.shape).copy()
    return _svf(np.ascontiguousarray(x), fc, q, float(sr), _SVF_MODES[mode])


def lp24(x, fc, res=0.707, sr=SR):
    """4-pole low-pass: two cascaded SVFs, resonance on the second stage."""
    return svf(svf(x, fc, 0.54, "lp", sr), fc, res, "lp", sr)


def hp(x, fc, q=0.707, sr=SR):
    return svf(x, fc, q, "hp", sr)


def bp(x, fc, q=1.0, sr=SR):
    return svf(x, fc, q, "bp", sr)


def _rbj(kind, f, q, gain_db, sr):
    A = 10 ** (gain_db / 40.0)
    w = 2 * np.pi * f / sr
    cw, sw = np.cos(w), np.sin(w)
    alpha = sw / (2 * q)
    if kind == "peak":
        b = [1 + alpha * A, -2 * cw, 1 - alpha * A]
        a = [1 + alpha / A, -2 * cw, 1 - alpha / A]
    elif kind == "lowshelf":
        sa = 2 * np.sqrt(A) * alpha
        b = [A * ((A + 1) - (A - 1) * cw + sa), 2 * A * ((A - 1) - (A + 1) * cw), A * ((A + 1) - (A - 1) * cw - sa)]
        a = [(A + 1) + (A - 1) * cw + sa, -2 * ((A - 1) + (A + 1) * cw), (A + 1) + (A - 1) * cw - sa]
    elif kind == "highshelf":
        sa = 2 * np.sqrt(A) * alpha
        b = [A * ((A + 1) + (A - 1) * cw + sa), -2 * A * ((A - 1) + (A + 1) * cw), A * ((A + 1) + (A - 1) * cw - sa)]
        a = [(A + 1) - (A - 1) * cw + sa, 2 * ((A - 1) - (A + 1) * cw), (A + 1) - (A - 1) * cw - sa]
    else:
        raise ValueError(kind)
    b = np.array(b) / a[0]
    a = np.array(a) / a[0]
    return b, a


def eq(x, kind, f, gain_db, q=0.9, sr=SR):
    """Static RBJ peaking / shelving EQ."""
    if f >= 0.49 * sr:
        return x
    b, a = _rbj(kind, f, q, gain_db, sr)
    return signal.lfilter(b, a, x, axis=0)


def tilt(x, db_per_oct=-1.5, pivot=1000.0):
    """Gentle spectral tilt using two shelves."""
    x = eq(x, "lowshelf", pivot / 2, -db_per_oct * 2, 0.6)
    return eq(x, "highshelf", pivot * 2, db_per_oct * 2, 0.6)


def dc_block(x, fc=12.0):
    b, a = signal.butter(1, fc / (SR / 2), "high")
    return signal.lfilter(b, a, x, axis=0)


def butter(x, fc, kind="low", order=2, sr=SR):
    sos = signal.butter(order, np.clip(np.asarray(fc) / (sr / 2), 1e-5, 0.999), kind, output="sos")
    return signal.sosfilt(sos, x, axis=0)


def formant_bank(x, formants, sr=SR):
    """Parallel band-pass bank: formants = [(freq, bandwidth, gain_db), ...]."""
    out = np.zeros_like(x)
    for f, bw, g in formants:
        if f >= 0.45 * sr:
            continue
        out += db(g) * bp(x, f, max(f / bw, 0.5), sr)
    return out


# --------------------------------------------------------------------------
# physical / modal models
# --------------------------------------------------------------------------
def modal(n, freqs, amps, t60s, sr=SR, rng=None, attack=0.0005, beat_cents=None):
    """Bank of exponentially decaying sinusoids."""
    t = tvec(n, sr)
    out = np.zeros(n)
    rng = rng or np.random.default_rng(0)
    for i, (f, a, t60) in enumerate(zip(freqs, amps, t60s)):
        if f >= 0.45 * sr or a == 0:
            continue
        tau = t60 / LN1000
        ph = rng.uniform(0, 2 * np.pi)
        env = np.exp(-t / tau)
        part = np.sin(2 * np.pi * f * t + ph)
        if beat_cents:
            f2 = f * 2 ** (beat_cents[i % len(beat_cents)] / 1200.0)
            part = 0.5 * (part + np.sin(2 * np.pi * f2 * t + ph * 1.3))
        out += a * env * part
    if attack > 0:
        k = max(1, int(attack * sr))
        out[:k] *= np.linspace(0, 1, k)
    return out


@njit(cache=True)
def _ks(n, period, exc, gain, s, coef, stiff):
    # delay-line string: integer delay + one-zero damping + allpass tuning
    N = int(period)
    buf = np.zeros(N + 2)
    out = np.zeros(n)
    idx = 0
    prev = 0.0
    ap_x1 = 0.0
    ap_y1 = 0.0
    st_x1 = 0.0
    st_y1 = 0.0
    m = exc.size
    for i in range(n):
        rd = buf[idx]
        # damping filter (one-zero low-pass), brightness s in 0..0.5
        y = gain * ((1.0 - s) * rd + s * prev)
        prev = rd
        # stiffness (dispersion) allpass
        z = stiff * y + st_x1 - stiff * st_y1
        st_x1 = y
        st_y1 = z
        # fractional tuning allpass
        a = coef * z + ap_x1 - coef * ap_y1
        ap_x1 = z
        ap_y1 = a
        if i < m:
            a += exc[i]
        buf[idx] = a
        out[i] = a
        idx += 1
        if idx >= N:
            idx = 0
    return out


def ks_string(n, f0, exc, t60=3.0, bright=0.25, stiff=0.0, sr=SR):
    """Extended Karplus-Strong string, tuned with an allpass fractional delay."""
    s = float(np.clip(bright, 0.02, 0.5))
    stiff = float(np.clip(stiff, 0.0, 0.6))
    # phase delay of the damping filter is ~s samples; the dispersion allpass
    # (coefficient -stiff) adds (1+stiff)/(1-stiff) samples at low frequencies
    stiff_delay = (1 + stiff) / (1 - stiff)
    period = sr / f0
    N = int(np.floor(period - s - stiff_delay - 0.1))
    d = period - N - s - stiff_delay  # fractional part for the tuning allpass (0.1..1.1)
    coef = (1 - d) / (1 + d)
    gain = 10 ** (-3.0 / (f0 * t60))
    return _ks(int(n), float(N), np.ascontiguousarray(exc, dtype=np.float64), gain, s, coef, float(-stiff))


def pluck_excitation(n_period, rng, bright=0.6, position=0.18, length_periods=1.0):
    """Noise burst shaped like a finger/plectrum pluck."""
    L = max(8, int(n_period * length_periods))
    e = rng.uniform(-1, 1, L)
    # brightness: one-pole low-pass on the burst
    a = np.clip(1.0 - bright, 0.0, 0.97)
    e = signal.lfilter([1 - a], [1, -a], e)
    # pluck position comb
    d = max(1, int(n_period * position))
    e2 = e.copy()
    e2[d:] -= e[:-d]
    e2 *= np.hanning(L * 2)[:L] ** 0.3
    return e2 / (np.max(np.abs(e2)) + 1e-12)


def body_ir(rng, modes, n=None, sr=SR, direct=1.0):
    """Short resonant body response: list of (freq, t60, gain)."""
    n = n or int(0.25 * sr)
    t = tvec(n, sr)
    ir = np.zeros(n)
    ir[0] = direct
    for f, t60, g in modes:
        ir += g * np.exp(-t * LN1000 / t60) * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * 0.02
    return ir


# --------------------------------------------------------------------------
# envelopes
# --------------------------------------------------------------------------
def env_adsr(n, a, d, s, sr=SR, curve=2.0):
    """Attack/decay/sustain without release (release handled by the sampler)."""
    t = tvec(n, sr)
    e = np.full(n, float(s))
    if a > 0:
        m = t < a
        e[m] = (t[m] / a) ** (1.0 / curve)
    if d > 0:
        m = (t >= a) & (t < a + d)
        e[m] = s + (1 - s) * np.exp(-5.0 * (t[m] - a) / d)
        m2 = t >= a + d
        e[m2] = s + (1 - s) * np.exp(-5.0)
    return e


def env_exp(n, t60, sr=SR, attack=0.001):
    t = tvec(n, sr)
    e = np.exp(-t * LN1000 / max(t60, 1e-3))
    k = max(1, int(attack * sr))
    e[:k] *= np.linspace(0, 1, k)
    return e


def ramp(n, points, sr=SR):
    """Piecewise-linear envelope from [(time_s, value), ...]."""
    ts = [p[0] for p in points]
    vs = [p[1] for p in points]
    return np.interp(tvec(n, sr), ts, vs)


def fade_edges(x, fin=0.0005, fout=0.02, sr=SR):
    x = x.copy()
    a = max(1, int(fin * sr))
    b = max(1, int(fout * sr))
    w_in = np.linspace(0, 1, a)
    w_out = np.linspace(1, 0, b) ** 2
    if x.ndim == 2:
        w_in = w_in[:, None]
        w_out = w_out[:, None]
    x[:a] *= w_in
    x[-b:] *= w_out
    return x


# --------------------------------------------------------------------------
# effects
# --------------------------------------------------------------------------
def saturate(x, drive=1.0, asym=0.0):
    """tanh waveshaper, run at 2x sample rate to keep the added harmonics
    from aliasing."""
    if drive <= 0:
        return x
    up = signal.resample_poly(x, 2, 1, axis=0)
    y = (np.tanh(drive * (up + asym)) - np.tanh(drive * asym)) / np.tanh(drive)
    return signal.resample_poly(y, 1, 2, axis=0)[: x.shape[0]]


def norm_rms(x, level=0.2):
    """Scale x to a given RMS (used before non-linear stages)."""
    return x * (level / (rms(x) + 1e-12))


def fold(x, amount=1.0):
    return np.sin(np.pi * 0.5 * x * (1 + amount))


def pan(x, pos):
    """Constant-power pan of a mono signal; pos -1..1 (scalar or array)."""
    a = (np.asarray(pos) + 1.0) * np.pi / 4.0
    return np.stack([x * np.cos(a), x * np.sin(a)], axis=1) * np.sqrt(2.0)


def stereo(x):
    return np.stack([x, x], axis=1) if x.ndim == 1 else x


def width(x, w):
    m = 0.5 * (x[:, 0] + x[:, 1])
    s = 0.5 * (x[:, 0] - x[:, 1]) * w
    return np.stack([m + s, m - s], axis=1)


def mono(x):
    return x if x.ndim == 1 else x.mean(axis=1)


def delay_read(x, delay_samples):
    """Read x at time-varying fractional delay (linear interpolation)."""
    n = x.size
    idx = np.arange(n) - delay_samples
    return np.interp(idx, np.arange(n), x, left=0.0, right=0.0)


def chorus(x, rng, voices=3, rate=0.35, depth_ms=3.5, base_ms=12.0, mix=0.5, sr=SR):
    """Multi-voice stereo chorus/ensemble."""
    x = stereo(x)
    n = x.shape[0]
    t = tvec(n, sr)
    wet = np.zeros_like(x)
    for v in range(voices):
        for c in range(2):
            ph = rng.uniform(0, 2 * np.pi)
            r = rate * rng.uniform(0.8, 1.25)
            d = (base_ms + depth_ms * np.sin(2 * np.pi * r * t + ph)) * sr / 1000.0
            d = d + 0.3 * depth_ms * sr / 1000.0 * smooth_noise(n, rng, 0.8, sr)
            wet[:, c] += delay_read(x[:, (c + v) % 2], d)
    wet /= voices
    return (1 - mix) * x + mix * wet * 1.2


def make_ir(seconds, rng, sr=SR, predelay=0.012, lo_t60=None, hi_t60=None, er=True, density=1.0):
    """Synthetic stereo reverb impulse response (frequency-dependent decay)."""
    n = int((seconds * 1.15 + predelay) * sr)
    t = tvec(n, sr)
    lo_t60 = lo_t60 or seconds
    hi_t60 = hi_t60 or seconds * 0.45
    out = np.zeros((n, 2))
    bands = [(0, 250, lo_t60 * 1.1), (250, 1500, lo_t60), (1500, 5000, (lo_t60 + hi_t60) / 2), (5000, 20000, hi_t60)]
    for c in range(2):
        noise = rng.standard_normal(n)
        acc = np.zeros(n)
        for lo, hi_f, t60 in bands:
            if lo == 0:
                b = butter(noise, hi_f, "low", 2)
            elif hi_f >= 20000:
                b = butter(noise, lo, "high", 2)
            else:
                b = butter(noise, [lo, hi_f], "band", 2)
            acc += b * np.exp(-t * LN1000 / t60)
        # build-up of density
        acc *= 1 - np.exp(-t / (0.018 / density))
        out[:, c] = acc
    pd = int(predelay * sr)
    out = np.roll(out, pd, axis=0)
    out[:pd] = 0
    if er:
        for _ in range(14):
            tap = int(rng.uniform(predelay * 0.6, predelay + 0.07) * sr)
            g = rng.uniform(0.2, 0.6) * np.exp(-tap / sr * 12)
            out[tap, rng.integers(0, 2)] += g * 8
    out /= np.sqrt(np.sum(out ** 2) / 2) + 1e-12
    return out


def reverb(x, ir, mix=0.25):
    x = stereo(x)
    n = x.shape[0]
    wet = np.stack([signal.fftconvolve(x[:, c], ir[:, c])[:n] for c in range(2)], axis=1)
    return (1 - mix) * x + mix * wet


def reverb_tail(x, ir, mix=0.25, extra=0.0, sr=SR):
    """Like reverb() but extends the output so the tail is kept."""
    x = stereo(x)
    n = x.shape[0] + int(extra * sr)
    xp = np.zeros((n, 2))
    xp[: x.shape[0]] = x
    wet = np.stack([signal.fftconvolve(xp[:, c], ir[:, c])[:n] for c in range(2)], axis=1)
    return (1 - mix) * xp + mix * wet


# --------------------------------------------------------------------------
# loops, levels
# --------------------------------------------------------------------------
def best_loop_end(x, ls, le_target, search, win=1024):
    """Pick the loop end near le_target whose lead-in best matches the
    material just before the loop start (maximises correlation)."""
    m = mono(x)
    ref = m[ls - win:ls]
    ref = ref - ref.mean()
    best, best_c = le_target, -2.0
    lo = max(ls + win * 2, le_target - search)
    hi = min(m.size, le_target + search)
    for le in range(lo, hi, 2):
        seg = m[le - win:le]
        seg = seg - seg.mean()
        c = float(np.dot(ref, seg) / (np.linalg.norm(ref) * np.linalg.norm(seg) + 1e-12))
        if c > best_c:
            best, best_c = le, c
    return best, best_c


def bake_loop(x, ls, le, xf):
    """Bake a crossfade into x so that the region [ls, le) loops seamlessly
    without any sampler crossfade. Returns audio truncated at le."""
    assert ls >= xf and le - ls >= xf, (ls, le, xf)
    y = x[:le].copy()
    pre = x[ls - xf:ls]
    end = x[le - xf:le]
    c = float(np.corrcoef(mono(pre), mono(end))[0, 1]) if xf > 16 else 0.0
    w = np.linspace(0.0, 1.0, xf)
    if c > 0.7:
        fo, fi = 1 - w, w
    else:
        fo, fi = np.cos(w * np.pi / 2), np.sin(w * np.pi / 2)
    if y.ndim == 2:
        fo, fi = fo[:, None], fi[:, None]
    y[le - xf:le] = end * fo + pre * fi
    return y


def make_looped(x, loop_start_s, loop_len_s, xfade_s=0.35, sr=SR):
    """Given a rendered sustain (long enough), return (audio, (ls, le))."""
    ls = int(loop_start_s * sr)
    le_t = ls + int(loop_len_s * sr)
    le, _ = best_loop_end(x, ls, le_t, int(0.02 * sr))
    xf = min(int(xfade_s * sr), ls, le - ls)
    y = bake_loop(x, ls, le, xf)
    return y, (ls, le)


def rms(x):
    return float(np.sqrt(np.mean(np.square(x)) + 1e-20))


def peak(x):
    return float(np.max(np.abs(x)) + 1e-20)
