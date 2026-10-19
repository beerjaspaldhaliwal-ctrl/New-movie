// Effect processors used by the instrument effect chain.
#pragma once

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <vector>

namespace nml {

constexpr float kPi = 3.14159265358979f;
constexpr float kTwoPi = 6.28318530717959f;

inline float dbToLin(float db) { return db <= -120.f ? 0.f : std::pow(10.f, db * 0.05f); }
inline float clampf(float v, float lo, float hi) { return v < lo ? lo : (v > hi ? hi : v); }

// Parameter smoothing (one-pole).
struct Smooth {
    float v = 0, target = 0, coef = 0.999f;
    void setTime(float sr, float seconds) { coef = std::exp(-1.f / (std::max(seconds, 1e-4f) * sr)); }
    void reset(float x) { v = target = x; }
    float next() { v = target + (v - target) * coef; return v; }
};

// Zero-delay-feedback state variable filter (Zavalishin), one channel.
struct Svf {
    float ic1 = 0, ic2 = 0;
    void reset() { ic1 = ic2 = 0; }
    inline float lp(float x, float g, float k) {
        const float a1 = 1.f / (1.f + g * (g + k));
        const float a2 = g * a1, a3 = g * a2;
        const float v3 = x - ic2;
        const float v1 = a1 * ic1 + a2 * v3;
        const float v2 = ic2 + a2 * ic1 + a3 * v3;
        ic1 = 2.f * v1 - ic1;
        ic2 = 2.f * v2 - ic2;
        return v2;
    }
};

struct FilterFx {
    Svf s[2][2];
    Smooth cut, res;
    bool ladder = true;
    float sr = 44100;
    void init(float sampleRate, bool isLadder) {
        sr = sampleRate; ladder = isLadder;
        cut.setTime(sr, 0.02f); res.setTime(sr, 0.02f);
        cut.reset(20000.f); res.reset(0.7f);
        for (auto& c : s) for (auto& f : c) f.reset();
    }
    void set(float hz, float q) { cut.target = clampf(hz, 20.f, 0.45f * sr); res.target = q; }
    void process(float* l, float* r, int n) {
        if (cut.target >= 0.44f * sr && cut.v >= 0.44f * sr) return;  // fully open: bypass
        for (int i = 0; i < n; ++i) {
            const float fc = cut.next();
            const float q = res.next();
            const float g = std::tan(kPi * std::min(fc, 0.45f * sr) / sr);
            float* ch[2] = {l, r};
            for (int c = 0; c < 2; ++c) {
                float x = ch[c][i];
                if (ladder) {
                    x = s[c][0].lp(x, g, 1.f / 0.54f);
                    x = s[c][1].lp(x, g, 1.f / q);
                } else {
                    x = s[c][0].lp(x, g, 1.f / q);
                }
                ch[c][i] = x;
            }
        }
    }
};

struct DriveFx {
    Smooth amt;
    void init(float sr) { amt.setTime(sr, 0.03f); amt.reset(0); }
    void process(float* l, float* r, int n) {
        for (int i = 0; i < n; ++i) {
            const float a = amt.next();
            if (a < 0.001f) continue;
            const float g = 1.f + a * 9.f;
            const float comp = 1.f / std::tanh(g * 0.5f) * 0.5f;
            l[i] = std::tanh(l[i] * g) * comp;
            r[i] = std::tanh(r[i] * g) * comp;
        }
    }
};

struct CompFx {
    float env = 0, sr = 44100, amount = 0;
    void init(float s) { sr = s; env = 0; }
    void process(float* l, float* r, int n) {
        if (amount < 0.01f) return;
        const float thr = dbToLin(-6.f - 26.f * amount);
        const float ratio = 2.f + 4.f * amount;
        const float makeup = dbToLin(10.f * amount);
        const float att = std::exp(-1.f / (0.004f * sr)), rel = std::exp(-1.f / (0.12f * sr));
        for (int i = 0; i < n; ++i) {
            const float lev = std::max(std::fabs(l[i]), std::fabs(r[i]));
            env = lev > env ? lev + (env - lev) * att : lev + (env - lev) * rel;
            float gain = 1.f;
            if (env > thr) gain = std::pow(env / thr, 1.f / ratio - 1.f);
            l[i] *= gain * makeup;
            r[i] *= gain * makeup;
        }
    }
};

struct TremoloFx {
    float phase = 0, sr = 44100, depth = 0, rate = 4, drive = 0;
    void init(float s) { sr = s; phase = 0; }
    void process(float* l, float* r, int n) {
        const float inc = rate / sr;
        for (int i = 0; i < n; ++i) {
            phase += inc;
            if (phase >= 1.f) phase -= 1.f;
            const float m = std::sin(kTwoPi * phase);
            float a = l[i], b = r[i];
            if (drive > 0.01f) {
                const float g = 1.f + drive * 6.f;
                a = std::tanh(a * g + 0.1f * drive) / g * 1.6f;
                b = std::tanh(b * g + 0.1f * drive) / g * 1.6f;
            }
            l[i] = a * (1.f - depth * 0.5f * (1.f + m));
            r[i] = b * (1.f - depth * 0.5f * (1.f - m));
        }
    }
};

// Fractional delay line.
struct DelayLine {
    std::vector<float> buf;
    int w = 0;
    void init(int size) { buf.assign(size + 4, 0.f); w = 0; }
    inline void push(float x) { buf[w] = x; if (++w >= (int)buf.size()) w = 0; }
    inline float read(float delay) const {  // delay in samples (>= 1, < size)
        const int size = (int)buf.size();
        const int di = (int)delay;
        const float f = delay - (float)di;
        // integer index arithmetic: float wrap-around can round up to `size`
        int i1 = w - di;  // newer sample
        while (i1 < 0) i1 += size;
        int i0 = i1 - 1;  // older sample
        if (i0 < 0) i0 += size;
        return buf[i1] + (buf[i0] - buf[i1]) * f;
    }
};

struct RotaryFx {
    DelayLine dl[2];
    Svf split[2];
    float sr = 44100, hornPh = 0, drumPh = 0, hornRate = 0.8f, drumRate = 0.7f, mix = 1, fast = 0;
    void init(float s) { sr = s; dl[0].init((int)(0.01f * s)); dl[1].init((int)(0.01f * s)); }
    void process(float* l, float* r, int n) {
        if (mix < 0.01f) return;
        const float hornT = fast > 0.5f ? 6.7f : 0.8f, drumT = fast > 0.5f ? 5.9f : 0.67f;
        const float accH = 1.f / (0.7f * sr), accD = 1.f / (2.5f * sr);
        const float g = std::tan(kPi * 800.f / sr);
        for (int i = 0; i < n; ++i) {
            hornRate += (hornT - hornRate) * accH * 4.f;
            drumRate += (drumT - drumRate) * accD * 4.f;
            hornPh += hornRate / sr; if (hornPh >= 1) hornPh -= 1;
            drumPh += drumRate / sr; if (drumPh >= 1) drumPh -= 1;
            const float x = 0.5f * (l[i] + r[i]);
            const float lo = split[0].lp(x, g, 1.4f);
            const float hi = x - lo;
            dl[0].push(hi);
            dl[1].push(lo);
            const float hs = std::sin(kTwoPi * hornPh), ds = std::sin(kTwoPi * drumPh);
            const float hl = dl[0].read(2.f + 0.0006f * sr * (1 + hs)) * (1.f + 0.35f * hs);
            const float hr = dl[0].read(2.f + 0.0006f * sr * (1 - hs)) * (1.f - 0.35f * hs);
            const float dlv = dl[1].read(2.f + 0.0004f * sr * (1 + ds)) * (1.f + 0.15f * ds);
            const float drv = dl[1].read(2.f + 0.0004f * sr * (1 - ds)) * (1.f - 0.15f * ds);
            l[i] = l[i] * (1 - mix) + (hl + dlv) * mix;
            r[i] = r[i] * (1 - mix) + (hr + drv) * mix;
        }
    }
};

struct WidthFx {
    Smooth w;
    void init(float sr) { w.setTime(sr, 0.03f); w.reset(1); }
    void process(float* l, float* r, int n) {
        for (int i = 0; i < n; ++i) {
            const float k = w.next();
            const float m = 0.5f * (l[i] + r[i]), s = 0.5f * (l[i] - r[i]) * k;
            l[i] = m + s;
            r[i] = m - s;
        }
    }
};

struct ChorusFx {
    DelayLine dl[2];
    float sr = 44100, ph[3] = {0, 0.33f, 0.66f};
    Smooth mix;
    void init(float s) {
        sr = s; dl[0].init((int)(0.05f * s)); dl[1].init((int)(0.05f * s));
        mix.setTime(s, 0.03f); mix.reset(0);
    }
    void process(float* l, float* r, int n) {
        const float rates[3] = {0.31f, 0.43f, 0.57f};
        for (int i = 0; i < n; ++i) {
            const float m = mix.next();
            dl[0].push(l[i]);
            dl[1].push(r[i]);
            if (m < 0.001f) continue;
            float wl = 0, wr = 0;
            for (int v = 0; v < 3; ++v) {
                ph[v] += rates[v] / sr; if (ph[v] >= 1) ph[v] -= 1;
                const float d = (0.012f + 0.004f * std::sin(kTwoPi * ph[v])) * sr;
                const float d2 = (0.012f + 0.004f * std::sin(kTwoPi * (ph[v] + 0.25f))) * sr;
                wl += dl[v & 1].read(d);
                wr += dl[(v + 1) & 1].read(d2);
            }
            l[i] = l[i] * (1 - 0.5f * m) + wl * (0.4f * m);
            r[i] = r[i] * (1 - 0.5f * m) + wr * (0.4f * m);
        }
    }
};

struct DelayFx {
    DelayLine dl[2];
    Svf damp[2];
    float sr = 44100;
    Smooth time, mix;
    float feedback = 0.35f;
    void init(float s) {
        sr = s; dl[0].init((int)(2.6f * s)); dl[1].init((int)(2.6f * s));
        time.setTime(s, 0.25f); time.reset(0.3f * s);
        mix.setTime(s, 0.03f); mix.reset(0);
    }
    void setTimeSeconds(float sec) { time.target = clampf(sec, 0.01f, 2.5f) * sr; }
    void process(float* l, float* r, int n) {
        const float g = std::tan(kPi * 5500.f / sr);
        for (int i = 0; i < n; ++i) {
            const float t = time.next();
            const float m = mix.next();
            const float yl = dl[0].read(t), yr = dl[1].read(t * 1.0f);
            // ping-pong: each side feeds the other
            dl[0].push(l[i] + damp[0].lp(yr, g, 1.2f) * feedback);
            dl[1].push(r[i] + damp[1].lp(yl, g, 1.2f) * feedback);
            l[i] += yl * m;
            r[i] += yr * m;
        }
    }
};

// 8-line feedback delay network reverb with input diffusion and modulation.
struct ReverbFx {
    static constexpr int N = 8;
    DelayLine lines[N];
    DelayLine pre;
    struct Allpass { DelayLine d; float len = 100, g = 0.6f; } ap[4];
    float lp[N] = {0};
    float baseLen[N];
    float sr = 44100, size = 0.6f, decay = 2.5f, damping = 0.4f;
    float modPh = 0;
    Smooth mix;
    void init(float s) {
        sr = s;
        const float ms[N] = {37.1f, 41.9f, 47.3f, 53.9f, 59.3f, 67.1f, 73.7f, 79.9f};
        for (int i = 0; i < N; ++i) { baseLen[i] = ms[i] * 0.001f * s; lines[i].init((int)(baseLen[i] * 2.4f) + 64); lp[i] = 0; }
        pre.init((int)(0.12f * s));
        const float apms[4] = {4.77f, 3.59f, 2.73f, 1.89f};
        for (int i = 0; i < 4; ++i) { ap[i].len = apms[i] * 0.001f * s; ap[i].d.init((int)ap[i].len + 8); }
        mix.setTime(s, 0.05f); mix.reset(0);
    }
    void process(float* l, float* r, int n) {
        const float scale = 0.45f + 1.8f * size;
        float fb[N], len[N];
        for (int k = 0; k < N; ++k) {
            len[k] = baseLen[k] * scale;
            fb[k] = std::pow(10.f, -3.f * (len[k] / sr) / std::max(decay, 0.1f));
        }
        const float dampCoef = 0.15f + 0.8f * damping;
        const float predelay = 0.004f * sr + size * 0.03f * sr;
        for (int i = 0; i < n; ++i) {
            const float m = mix.next();
            const float in = 0.5f * (l[i] + r[i]);
            pre.push(in);
            if (m < 0.0005f) continue;
            float x = pre.read(predelay);
            for (auto& a : ap) {  // input diffusion
                const float d = a.d.read(a.len);
                const float y = -a.g * x + d;
                a.d.push(x + a.g * y);
                x = y;
            }
            modPh += 0.3f / sr; if (modPh >= 1) modPh -= 1;
            float o[N];
            for (int k = 0; k < N; ++k) {
                const float mod = (k & 1 ? 1.f : -1.f) * 6.f * std::sin(kTwoPi * (modPh + k * 0.125f));
                float v = lines[k].read(len[k] + mod);
                lp[k] += (v - lp[k]) * (1.f - dampCoef);
                o[k] = lp[k] * fb[k];
            }
            // Hadamard-style mixing (fast Walsh-Hadamard transform, normalised)
            for (int h = 1; h < N; h <<= 1)
                for (int a = 0; a < N; a += h << 1)
                    for (int b = a; b < a + h; ++b) { const float u = o[b], w2 = o[b + h]; o[b] = u + w2; o[b + h] = u - w2; }
            const float norm = 0.35355339f;  // 1/sqrt(8)
            for (int k = 0; k < N; ++k) lines[k].push(o[k] * norm + x * (k < 4 ? 0.5f : -0.5f));
            const float wl = (o[0] + o[2] + o[4] + o[6]) * norm;
            const float wr = (o[1] + o[3] + o[5] + o[7]) * norm;
            l[i] = l[i] + wl * m * 0.9f;
            r[i] = r[i] + wr * m * 0.9f;
        }
    }
};

}  // namespace nml
