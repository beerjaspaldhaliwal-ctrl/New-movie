#include "Engine.hpp"

#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <cstring>

namespace nml {

namespace {

const int kScaleMask[16][12] = {
    {1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1}, {1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1}, {1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0},
    {1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1}, {1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1}, {1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0},
    {1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0}, {1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1}, {1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0},
    {1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0}, {1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0}, {1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0},
    {1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0}, {1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1}, {1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0},
    {1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0}};
const std::vector<std::vector<int>> kChords = {
    {0}, {0, 12}, {0, 7, 12}, {0, 4, 7}, {0, 3, 7}, {0, 2, 7}, {0, 5, 7}, {0, 4, 7, 11}, {0, 3, 7, 10},
    {0, 4, 7, 14}, {0, 3, 7, 14}, {0, 7, 14, 21}, {0, 7, 12, 15, 19}, {0, 3, 6}, {0, 4, 8}, {}, {}};
const int kDiaTriad = 15, kDia7th = 16;
const int kRateTicks[6] = {24, 12, 8, 6, 4, 3};
const int kLfoTicks[6] = {24, 48, 96, 192, 384, 768};
const int kRepeatTicks[6] = {0, 12, 8, 6, 4, 3};
const float kDelayBeats[13] = {0.125f, 1.f / 6, 0.25f, 1.f / 3, 0.375f, 0.5f, 2.f / 3, 0.75f, 1.f, 4.f / 3, 1.5f, 2.f, 4.f};

inline float rnd(float lo, float hi) { return lo + (hi - lo) * (float)std::rand() / (float)RAND_MAX; }
inline int rndi(int lo, int hi) { return hi <= lo ? lo : lo + std::rand() % (hi - lo + 1); }
inline float lin2db(float g) { return 20.f * std::log10(std::max(g, 1e-4f)); }

}  // namespace

Engine::Engine() {
    for (auto& k : keyDown) k.store(0);
    actions_.reserve(256);
    due_.reserve(256);
    pending_.reserve(512);
    newIds_.reserve(64);
    monoIds_.reserve(64);
    stack_.reserve(32);
    arp_.reserve(64);
    arpSorted_.reserve(64);
    for (auto& s : src_) s.ids.reserve(32);
    for (auto& c : chord_) c.reserve(8);
    for (auto& r : pieceVoices_) r.reserve(9);
    resolveParams();
    setSampleRate(44100.0);
}

void Engine::resolveParams() {
    const Catalog& c = Catalog::get();
#define R(x) I.x = c.param(#x)
    R(volume); R(tone); R(reso); R(width); R(chorus); R(dly_mix); R(dly_time); R(dly_fb); R(dly_sync); R(rev_mix);
    R(rev_size); R(rev_decay); R(use_pedal); R(pb_range); R(scale_type); R(scale_key); R(chord); R(strum);
    R(hum_time); R(hum_vel); R(arp_mode); R(arp_rate); R(arp_oct); R(arp_gate); R(arp_swing); R(arp_latch);
    R(arp_accent); R(layer_a); R(layer_b); R(blend); R(attack); R(release); R(vsens); R(move_amt); R(oct_mode);
    R(oct_lvl); R(mono); R(glide); R(move_rate); R(modwheel); R(drive); R(patch); R(patch2); R(mix2); R(vrange);
    R(vcurve); R(repeat_damp); R(let_ring); R(art_menu); R(dyn_knob); R(dyn_src); R(dyn_range); R(swell_t);
    R(legato); R(leg_time); R(porta); R(mic_close); R(mic_hall); R(comp); R(tune); R(hum); R(spread); R(repeat);
    R(trem_amt); R(trem_rate); R(ep_drive); R(rot_fast); R(rot_mix); R(mw_rot);
#undef R
    for (int b = 0; b < 8; ++b) I.bus[b] = c.param("bus" + std::to_string(b));
}

float Engine::pv(const char* var, float dflt) const { return p(Catalog::get().param(var), dflt); }

bool Engine::has(const char* var) const {
    const int idx = Catalog::get().param(var);
    return idx >= 0 && has_[idx];
}

void Engine::setSampleRate(double sr) {
    sr_ = sr;
    srRatio_ = 44100.0 / sr;
    resetFx();
    master_.setTime((float)sr, 0.05f);
    master_.reset(1.f);
}

void Engine::resetFx() {
    const float sr = (float)sr_;
    filter_.init(sr, def_ ? def_->ladder : true);
    drive_.init(sr);
    comp_.init(sr);
    trem_.init(sr);
    rotary_.init(sr);
    width_.init(sr);
    chorus_.init(sr);
    delay_.init(sr);
    reverb_.init(sr);
}

LoadedInstrument* Engine::setInstrument(LoadedInstrument* li) {
    LoadedInstrument* old = inst_;
    for (auto& v : voices_) v.active = false;
    for (auto& s : src_) { s.ids.clear(); s.held = false; s.sus = false; }
    for (auto& pv2 : pieceVoices_) pv2.clear();
    actions_.clear();
    pending_.clear();
    arp_.clear();
    monoIds_.clear();
    stack_.clear();
    monoCur_ = -1;
    repN_ = 0;
    std::memset(repVel_, 0, sizeof(repVel_));
    std::memset(rrPos_, 0, sizeof(rrPos_));
    keysDown_ = 0;
    inst_ = li;
    def_ = li ? li->def : nullptr;
    art_ = 0;
    lastArtParam_ = -1;
    for (auto& d : lastDynSig_) d = -1e9f;
    for (auto& m : lastModes_) m = -1;
    std::memset(has_, 0, sizeof(has_));
    has_[0] = true;  // master volume
    if (def_)
        for (auto& c : def_->controls)
            if (c.param >= 0 && c.param < 256) has_[c.param] = true;
    if (def_) {
        filter_.init((float)sr_, def_->ladder);
        dyn_ = (int)p(I.dyn_knob, def_->engine == EngineType::Drums ? 100 : 90);
        calcDyn();
    }
    return old;
}

// ===================================================================== voices
uint32_t Engine::playVoice(int note, int group, float db, float tuneCents, float offsetSec, float fadeSec, float pan,
                           int role, float base) {
    if (!inst_) return 0;
    const int z = inst_->zone(group, note);
    if (z < 0) return 0;
    const Sample& s = inst_->samples[z];
    if (s.frames < 8) return 0;
    Voice* v = nullptr;
    for (auto& c : voices_) if (!c.active) { v = &c; break; }
    if (!v) {  // steal the oldest voice
        v = &voices_[0];
        for (auto& c : voices_) if (c.started < v->started) v = &c;
    }
    v->active = true;
    v->id = nextId_++;
    if (nextId_ == 0) nextId_ = 1;
    v->s = &s;
    v->note = note;
    v->pos = std::min<double>(offsetSec * 44100.0, std::max(0, s.frames - 8));
    v->tune = v->tuneTarget = tuneCents;
    v->tuneRate = 0;
    v->gain = v->gainTarget = dbToLin(db);
    const float a = (clampf(pan, -1.f, 1.f) + 1.f) * kPi * 0.25f;
    v->panL = std::cos(a) * 1.41421356f;
    v->panR = std::sin(a) * 1.41421356f;
    if (fadeSec > 0.0005f) { v->env = 0; v->envInc = 1.f / (fadeSec * (float)sr_); v->envState = 0; }
    else { v->env = 0; v->envInc = 1.f / (0.0007f * (float)sr_); v->envState = 0; }
    v->role = role;
    v->base = base;
    v->started = now_;
    updatePitch(*v);
    newIds_.push_back(v->id);
    voicesStarted.fetch_add(1, std::memory_order_relaxed);
    return v->id;
}

Engine::Voice* Engine::find(uint32_t id) {
    if (!id) return nullptr;
    for (auto& v : voices_) if (v.active && v.id == id) return &v;
    return nullptr;
}

void Engine::fadeOut(uint32_t id, float sec) {
    Voice* v = find(id);
    if (!v || v->envState == 2) return;
    v->envState = 2;
    v->envInc = -std::max(v->env, 0.001f) / (std::max(sec, 0.001f) * (float)sr_);
}

void Engine::updatePitch(Voice& v) {
    const double semis = (v.note - v.s->root) + (v.tune + bendCents_) / 100.0;
    v.step = std::pow(2.0, semis / 12.0) * srRatio_;
}

void Engine::renderVoices(float* l, float* r, int n) {
    int count = 0;
    for (auto& v : voices_) {
        if (!v.active) continue;
        ++count;
        const Sample& s = *v.s;
        const float* dl = s.l.data();
        const float* dr = s.stereo() ? s.r.data() : dl;
        const bool loop = s.loopStart >= 0;
        const double loopLen = loop ? (double)(s.loopEnd - s.loopStart) : 0.0;
        const double end = loop ? (double)s.loopEnd : (double)(s.frames - 2);
        const float gcoef = 0.9985f;
        for (int i = 0; i < n; ++i) {
            if ((i & 31) == 0 && v.tuneRate != 0.f) {
                const float step = v.tuneRate * 32.f;
                if (std::fabs(v.tuneTarget - v.tune) <= std::fabs(step)) { v.tune = v.tuneTarget; v.tuneRate = 0; }
                else v.tune += step;
                updatePitch(v);
            }
            // envelope
            v.env += v.envInc;
            if (v.envState == 0 && v.env >= 1.f) { v.env = 1.f; v.envInc = 0; v.envState = 1; }
            if (v.envState == 2 && v.env <= 0.f) { v.active = false; break; }
            v.gain = v.gainTarget + (v.gain - v.gainTarget) * gcoef;
            // 4-point Hermite interpolation
            const int ip = (int)v.pos;
            const float f = (float)(v.pos - ip);
            const int i0 = ip > 0 ? ip - 1 : 0;
            auto herm = [&](const float* d) {
                const float xm1 = d[i0], x0 = d[ip], x1 = d[ip + 1], x2 = d[ip + 2];
                const float c1 = 0.5f * (x1 - xm1);
                const float c2 = xm1 - 2.5f * x0 + 2.f * x1 - 0.5f * x2;
                const float c3 = 0.5f * (x2 - xm1) + 1.5f * (x0 - x1);
                return ((c3 * f + c2) * f + c1) * f + x0;
            };
            const float g = v.gain * v.env;
            l[i] += herm(dl) * g * v.panL;
            r[i] += herm(dr) * g * v.panR;
            v.pos += v.step;
            if (v.pos >= end) {
                if (loop) { while (v.pos >= end) v.pos -= loopLen; }
                else { v.active = false; break; }
            }
        }
    }
    activeVoices.store(count);
}

void Engine::registerNew(int src) {
    auto& s = src_[src];
    for (uint32_t id : newIds_) s.ids.push_back(id);
}

void Engine::pendNew(uint64_t releaseTick) {
    for (uint32_t id : newIds_) pending_.push_back({id, releaseTick});
}

void Engine::releaseSrc(int src, float sec) {
    for (uint32_t id : src_[src].ids) fadeOut(id, sec);
    src_[src].ids.clear();
    src_[src].sus = false;
}

void Engine::releaseAll(float sec) {
    for (int s = 0; s < kNumSources; ++s) releaseSrc(s, sec);
    for (auto& pd : pending_) fadeOut(pd.id, sec);
    pending_.clear();
    for (uint32_t id : monoIds_) fadeOut(id, sec);
    monoIds_.clear();
    actions_.clear();
}

void Engine::pedalUp() {
    pedal_ = false;
    for (int s = 0; s < 128; ++s)
        if (src_[s].sus && !src_[s].held) releaseSrc(s, p(I.release, 300) / 1000.f);
}

void Engine::checkModes() {
    const int modes[5] = {(int)p(I.mono, 0), (int)p(I.legato, 0), p(I.arp_mode, 0) > 0.5f ? 1 : 0,
                          (int)p(I.arp_mode, 0), (int)p(I.arp_latch, 0)};
    if (lastModes_[0] < 0) { std::memcpy(lastModes_, modes, sizeof(modes)); return; }  // new instrument
    // switching mono, legato or the arpeggiator re-routes note-offs: release what is sounding
    // first, so no note can be left without its note-off (the scripts do the same)
    if (modes[0] != lastModes_[0] || modes[1] != lastModes_[1] || modes[3] != lastModes_[3]) {
        releaseAll(0.03f);
        arp_.clear();
        arpSorted_.clear();
        stack_.clear();
        monoCur_ = -1;
    }
    if (modes[4] == 0 && lastModes_[4] == 1 && keysDown_ == 0) { arp_.clear(); arpSorted_.clear(); }
    std::memcpy(lastModes_, modes, sizeof(modes));
    if (pedal_ && p(I.use_pedal, 1) < 0.5f) pedalUp();  // pedal switched off while held down
}

void Engine::rebaseTicks(uint64_t newTick) {
    auto shift = [&](uint64_t v) {
        const int64_t r = (int64_t)v - (int64_t)tick_ + (int64_t)newTick;
        return r < 0 ? (uint64_t)0 : (uint64_t)r;
    };
    arpNext_ = shift(arpNext_);
    for (auto& r : repNext_) r = shift(r);
    for (auto& pd : pending_) pd.tick = shift(pd.tick);
    tick_ = newTick;
}

void Engine::allNotesOff() {
    releaseAll(0.02f);
    pedal_ = false;
    arp_.clear();
    stack_.clear();
    monoCur_ = -1;
}

// ===================================================================== processing
void Engine::process(float* outL, float* outR, uint32_t frames, const MidiMsg* ev, uint32_t nev, const TimeInfo& ti) {
    std::memset(outL, 0, sizeof(float) * frames);
    std::memset(outR, 0, sizeof(float) * frames);
    if (busL_.size() < frames) { busL_.resize(frames); busR_.resize(frames); }
    if (!def_) {
        for (uint32_t i = 0; i < nev; ++i) handleMidi(ev[i].data);
        return;
    }
    // articulation menu changed by the user
    const int artParam = (int)p(I.art_menu, 0);
    if (def_->engine == EngineType::Artic && artParam != lastArtParam_) {
        lastArtParam_ = artParam;
        art_ = std::min(std::max(artParam, 0), (int)def_->arts.size() - 1);
        currentArt.store(art_);
    }
    // dynamics, dyn range and mic levels (the scripts' ui_control callbacks)
    const float sig[4] = {p(I.dyn_knob, -1), p(I.dyn_range, 20), p(I.mic_close, 0), p(I.mic_hall, -60)};
    if (std::memcmp(sig, lastDynSig_, sizeof(sig)) != 0) {
        if (sig[0] != lastDynSig_[0] && sig[0] >= 0) dyn_ = (int)sig[0];
        std::memcpy(lastDynSig_, sig, sizeof(sig));
        calcDyn();
        updateDyn();
    }
    checkModes();
    // tempo / tick alignment
    bpm_ = ti.bpm > 20 ? ti.bpm : 120.0;
    const double spt = sr_ * 60.0 / (bpm_ * 24.0);  // samples per tick
    if (ti.playing && ti.bbtValid) {
        const double tpos = ti.ppq * 24.0;
        double frac = std::ceil(tpos) - tpos;
        if (frac < 1e-9) frac = 0.0;
        const double want = frac * spt;
        if (!wasPlaying_) {
            // transport started: align the tick phase and count with the song position,
            // so arpeggiator accents and Note Repeat land on the host's beats
            samplesToTick_ = want;
            const double nextTick = std::ceil(tpos - 1e-9);
            rebaseTicks(nextTick >= 1.0 ? (uint64_t)nextTick - 1 : 0);
        } else {
            // keep the phase locked; the difference is wrapped to one tick, because a tick that
            // fell exactly on the block boundary has already fired at the end of the last block
            double d = samplesToTick_ - want;
            d -= spt * std::round(d / spt);
            if (std::fabs(d) > 0.25 * spt) samplesToTick_ -= d;
        }
    }
    wasPlaying_ = ti.playing;
    if (samplesToTick_ > spt) samplesToTick_ = spt;

    updateFxParams();
    uint32_t cursor = 0, evi = 0;
    while (cursor < frames) {
        uint32_t next = frames;
        if (evi < nev) next = std::min(next, std::max(ev[evi].frame, cursor));
        const uint32_t tickAt = cursor + (uint32_t)std::ceil(std::max(0.0, samplesToTick_));
        next = std::min(next, tickAt);
        for (auto& a : actions_) if (a.time < now_ + (next - cursor)) next = std::min<uint32_t>(next, cursor + (uint32_t)(a.time > now_ ? a.time - now_ : 0));
        if (next > cursor) {
            renderVoices(outL + cursor, outR + cursor, (int)(next - cursor));
            now_ += next - cursor;
            samplesToTick_ -= (double)(next - cursor);
            cursor = next;
        }
        while (evi < nev && ev[evi].frame <= cursor) handleMidi(ev[evi++].data);
        if (samplesToTick_ <= 0.0) {
            samplesToTick_ += spt;
            tickEvent();
        }
        if (!actions_.empty()) {
            due_.clear();
            for (size_t i = 0; i < actions_.size();) {
                if (actions_[i].time <= now_) { due_.push_back(actions_[i]); actions_[i] = actions_.back(); actions_.pop_back(); }
                else ++i;
            }
            for (auto& a : due_) runAction(a);
        }
    }
    applyFx(outL, outR, (int)frames);
    // Safety net: never let a NaN or a blow-up live on in the effect feedback loops.
    float sum = 0.f;
    for (uint32_t i = 0; i < frames; ++i) sum += outL[i] + outR[i];
    if (!std::isfinite(sum)) {
        resetFx();
        std::memset(outL, 0, sizeof(float) * frames);
        std::memset(outR, 0, sizeof(float) * frames);
    }
    // master volume and a soft safety limiter
    master_.target = dbToLin(p(I.volume, 0.f) + def_->gainDb);
    float pl = 0, pr = 0;
    for (uint32_t i = 0; i < frames; ++i) {
        const float g = master_.next();
        float a = outL[i] * g, b = outR[i] * g;
        if (std::fabs(a) > 0.9f) a = (a > 0 ? 1.f : -1.f) * (0.9f + 0.1f * std::tanh((std::fabs(a) - 0.9f) * 10.f));
        if (std::fabs(b) > 0.9f) b = (b > 0 ? 1.f : -1.f) * (0.9f + 0.1f * std::tanh((std::fabs(b) - 0.9f) * 10.f));
        outL[i] = a;
        outR[i] = b;
        pl = std::max(pl, std::fabs(a));
        pr = std::max(pr, std::fabs(b));
    }
    peakL.store(std::max(pl, peakL.load() * 0.9f));
    peakR.store(std::max(pr, peakR.load() * 0.9f));
}

void Engine::handleMidi(const uint8_t* d) {
    const uint8_t status = d[0] & 0xF0;
    if (status == 0x90 && d[2] > 0) { keyDown[d[1] & 127].store(1); noteOn(d[1] & 127, d[2]); }
    else if (status == 0x80 || (status == 0x90 && d[2] == 0)) { keyDown[d[1] & 127].store(0); noteOff(d[1] & 127); }
    else if (status == 0xB0) controller(d[1], d[2]);
    else if (status == 0xE0 && has("pb_range")) {
        const int v = ((d[2] << 7) | d[1]) - 8192;
        const float range = p(I.pb_range, 2.f);
        bendCents_ = (float)v / 8191.f * range * 100.f;
        for (auto& v2 : voices_) if (v2.active) updatePitch(v2);
    }
}

void Engine::controller(int cc, int val) {
    if (cc == 64 && p(I.use_pedal, 1) > 0.5f) {
        if (val >= 64) pedal_ = true;
        else if (pedal_) pedalUp();
    }
    if (cc == 120 || cc == 123) allNotesOff();
    if (cc == 1) {
        cc1_ = val;
        if (def_ && def_->engine == EngineType::Artic && p(I.dyn_src, 0) < 0.5f) { dyn_ = val; calcDyn(); updateDyn(); }
        if (def_ && def_->engine == EngineType::Drums) { dyn_ = val; calcDyn(); updateDyn(); }
        if (def_ && def_->hasFx(Fx::Rotator) && p(I.mw_rot, 1) > 0.5f) fastRotary_ = val >= 64;
    }
    if (cc == 11) { cc11_ = val; calcDyn(); updateDyn(); }
}

void Engine::tickEvent() {
    ++tick_;
    if (!pending_.empty()) {
        const float rel = p(I.release, 300) / 1000.f;
        for (size_t i = 0; i < pending_.size();) {
            if (pending_[i].tick <= tick_) { fadeOut(pending_[i].id, rel); pending_[i] = pending_.back(); pending_.pop_back(); }
            else ++i;
        }
    }
    if (!def_) return;
    if (def_->engine != EngineType::Drums) {
        const int mode = (int)p(I.arp_mode, 0);
        if (mode > 0 && !arp_.empty() && tick_ >= arpNext_) {
            arpFire();
            const int len = kRateTicks[std::min(std::max((int)p(I.arp_rate, 3), 0), 5)];
            const int sw = len * (int)p(I.arp_swing, 0) / 6;
            arpNext_ = tick_ + (arpStep_ % 2 == 1 ? len + sw : len - sw);
        }
    }
    if (def_->engine == EngineType::Synth && p(I.move_amt, 0) > 0) {
        const int len = kLfoTicks[std::min(std::max((int)p(I.move_rate, 3), 0), 5)];
        if (++lfoPos_ >= len) lfoPos_ = 0;
        cutLfo_ = std::sin(kTwoPi * (float)lfoPos_ / (float)len) * p(I.move_amt, 0) * 0.25f;
    } else {
        cutLfo_ = 0;
    }
    if (def_->engine == EngineType::Drums && repN_ > 0) {
        const int rate = kRepeatTicks[std::min(std::max((int)p(I.repeat, 0), 0), 5)];
        if (rate == 0) { std::memset(repVel_, 0, sizeof(repVel_)); repN_ = 0; }
        else
            for (int k = 0; k < 128; ++k)
                if (repVel_[k] > 0 && tick_ >= repNext_[k]) { drumHit(k, repVel_[k]); repNext_[k] = tick_ + rate; }
    }
}

// ===================================================================== note routing
void Engine::noteOn(int note, int vel) {
    if (!def_) return;
    lastVel_ = vel;
    if (def_->engine == EngineType::Drums) {
        bool isPiece = false;
        for (auto& pc : def_->pieces) if (pc.key == note) { isPiece = true; break; }
        if (!isPiece) return;
        ++keysDown_;
        src_[note].held = true;
        drumHit(note, vel);
        const int rep = (int)p(I.repeat, 0);
        bool hold = false;
        for (auto& pc : def_->pieces) if (pc.key == note) hold = pc.hold;
        if (rep > 0 && !hold) {
            if (repVel_[note] == 0) ++repN_;
            repVel_[note] = vel;
            repNext_[note] = tick_ + kRepeatTicks[std::min(rep, 5)];
        }
        return;
    }
    if (def_->engine == EngineType::Artic) {
        for (size_t a = 0; a < def_->arts.size(); ++a)
            if (def_->arts[a].ks == note) { art_ = (int)a; currentArt.store(art_); return; }
    }
    ++keysDown_;
    src_[note].held = true;
    ++generation_[note];
    if (def_->engine == EngineType::Synth && p(I.mono, 0) > 0.5f) { monoNoteOn(note, vel); return; }
    if (def_->engine == EngineType::Artic && p(I.legato, 0) > 0.5f && def_->arts[art_].type != 1) {
        legatoNoteOn(note, vel);
        return;
    }
    polyNoteOn(note, vel);
}

void Engine::noteOff(int note) {
    if (!def_) return;
    if (def_->engine == EngineType::Drums) {
        bool isPiece = false;
        for (auto& pc : def_->pieces) if (pc.key == note) { isPiece = true; break; }
        if (!isPiece) return;
        if (repVel_[note] > 0) { repVel_[note] = 0; --repN_; }
        keysDown_ = std::max(0, keysDown_ - 1);
        src_[note].held = false;
        if (!src_[note].ids.empty()) releaseSrc(note, p(I.release, 250) / 1000.f);
        return;
    }
    if (def_->engine == EngineType::Artic)
        for (auto& a : def_->arts) if (a.ks == note) return;
    keysDown_ = std::max(0, keysDown_ - 1);
    src_[note].held = false;
    if (def_->engine == EngineType::Synth && p(I.mono, 0) > 0.5f) { monoNoteOff(note); return; }
    if (def_->engine == EngineType::Artic && p(I.legato, 0) > 0.5f && !monoIds_.empty()) { legatoNoteOff(note); return; }
    bool letRing = false;
    if (def_->engine == EngineType::Keys && has("let_ring") && p(I.let_ring, 0) > 0.5f) {
        const int pi = def_->patches.size() > 1 ? (int)p(I.patch, 0) : 0;
        letRing = !def_->patches[std::min(std::max(pi, 0), (int)def_->patches.size() - 1)].loop;
    }
    polyNoteOff(note, letRing);
}

// ===================================================================== performer
int Engine::scaleSnap(int note) const {
    const int st = std::min(std::max((int)p(I.scale_type, 0), 0), 15);
    if (st == 0) return note;
    const int key = (int)p(I.scale_key, 0);
    const int pc = (note - key + 120) % 12;
    int d = 0;
    while (d < 11 && !kScaleMask[st][(pc - d + 12) % 12]) ++d;
    int out = note - d;
    if (out < 0) out += 12;
    return out;
}

void Engine::buildChord(int root, int src) {
    auto& ch = chord_[src];
    ch.clear();
    ch.push_back(root);
    const int c = std::min(std::max((int)p(I.chord, 0), 0), (int)kChords.size() - 1);
    if (c == kDiaTriad || c == kDia7th) {
        const int need = c == kDia7th ? 4 : 3;
        int st = (int)p(I.scale_type, 0);
        if (st <= 0) st = 1;
        const int key = (int)p(I.scale_key, 0);
        int step = 0;
        for (int n = root + 1; (int)ch.size() < need && n < root + 24 && n <= 127; ++n) {
            if (kScaleMask[st][(n - key + 120) % 12]) {
                ++step;
                if (step == 2 || step == 4 || step == 6) ch.push_back(n);
            }
        }
    } else {
        for (size_t i = 1; i < kChords[c].size(); ++i) {
            const int n = root + kChords[c][i];
            if (n <= 127) ch.push_back(n);
        }
    }
}

void Engine::polyNoteOn(int note, int vel) {
    int v = vel;
    const int hv = (int)p(I.hum_vel, 0);
    if (hv > 0) v = std::min(127, std::max(1, v + rndi(-hv, hv)));
    buildChord(scaleSnap(note), note);
    if (p(I.arp_mode, 0) > 0.5f) {
        arpVel_ = v;
        arpAdd(note);
        return;
    }
    if (!src_[note].ids.empty()) releaseSrc(note, (has("repeat_damp") ? p(I.repeat_damp, 60) : 40.f) / 1000.f);
    const int ht = (int)p(I.hum_time, 0);
    const float strum = p(I.strum, 0);
    const float delay0 = ht > 0 ? rnd(0.f, (float)ht) / 1000.f : 0.f;
    for (size_t i = 0; i < chord_[note].size(); ++i) {
        const float t = delay0 + (float)i * strum / 1000.f;
        if (t <= 0.f) startChordNote(note, (int)i, v);
        else actions_.push_back({now_ + (uint64_t)(t * sr_), note, (int)i, v, generation_[note]});
    }
}

void Engine::runAction(const Action& a) {
    if (a.generation != generation_[a.src]) return;
    startChordNote(a.src, a.index, a.vel);
}

void Engine::startChordNote(int src, int index, int vel) {
    if (!(src_[src].held || pedal_)) return;
    if (index >= (int)chord_[src].size()) return;
    newIds_.clear();
    startNote(chord_[src][index], vel, 0.f, -1.f);
    registerNew(src);
}

void Engine::polyNoteOff(int note, bool letRing) {
    if (p(I.arp_mode, 0) > 0.5f) {
        if (p(I.arp_latch, 0) < 0.5f) arpRemove(note);
        return;
    }
    if (pedal_) { src_[note].sus = true; return; }
    if (letRing) {  // one-shot voices ring out; a looping layer (e.g. a drone) still stops
        for (uint32_t id : src_[note].ids)
            if (Voice* v = find(id)) if (v->s->loopStart >= 0) fadeOut(id, p(I.release, 300) / 1000.f);
        src_[note].ids.clear();
        return;
    }
    releaseSrc(note, p(I.release, 300) / 1000.f);
}

void Engine::arpSort() {
    arpSorted_.clear();
    for (auto& a : arp_) arpSorted_.push_back(a.note);
    std::sort(arpSorted_.begin(), arpSorted_.end());
}

void Engine::arpAdd(int src) {
    if (p(I.arp_latch, 0) > 0.5f && keysDown_ <= 1) arp_.clear();
    const bool wasEmpty = arp_.empty();
    for (int n : chord_[src]) if (arp_.size() < 64) arp_.push_back({n, src});
    arpSort();
    if (wasEmpty) {
        arpStep_ = 0;
        arpFire();
        arpNext_ = tick_ + kRateTicks[std::min(std::max((int)p(I.arp_rate, 3), 0), 5)];
    }
}

void Engine::arpRemove(int src) {
    arp_.erase(std::remove_if(arp_.begin(), arp_.end(), [&](const ArpNote& a) { return a.src == src; }), arp_.end());
    arpSort();
}

void Engine::arpFire() {
    const int n = (int)arp_.size();
    const int oct = std::max(1, (int)p(I.arp_oct, 1));
    const int total = n * oct;
    if (total == 0) return;
    const int mode = (int)p(I.arp_mode, 0);
    const int len = kRateTicks[std::min(std::max((int)p(I.arp_rate, 3), 0), 5)];
    const int gate = std::max(1, len * (int)p(I.arp_gate, 60) / 100);
    int vel = arpVel_;
    if ((int)(tick_ % 24) < len) vel += (int)p(I.arp_accent, 10);
    vel = std::min(127, vel);
    if (mode == 6) {
        for (auto& a : arp_) {
            newIds_.clear();
            startNote(a.note, vel, 0.f, -1.f);
            pendNew(tick_ + gate);
        }
    } else {
        int idx = 0;
        switch (mode) {
            case 1: idx = (int)(arpStep_ % total); break;
            case 2: idx = total - 1 - (int)(arpStep_ % total); break;
            case 3:
                if (total == 1) idx = 0;
                else { const int per = 2 * total - 2; idx = (int)(arpStep_ % per); if (idx >= total) idx = per - idx; }
                break;
            case 4: idx = rndi(0, total - 1); break;
            default: idx = (int)(arpStep_ % total); break;
        }
        const int e = idx % n, o = idx / n;
        const int note = (mode == 5 ? arp_[e].note : arpSorted_[e]) + 12 * o;
        if (note <= 127) {
            newIds_.clear();
            startNote(note, vel, 0.f, -1.f);
            pendNew(tick_ + gate);
        }
    }
    ++arpStep_;
}

// ===================================================================== engines
void Engine::startNote(int note, int vel, float offsetSec, float fadeSec) {
    switch (def_->engine) {
        case EngineType::Synth: startSynth(note, vel, offsetSec, fadeSec); break;
        case EngineType::Artic: startArtic(note, vel, offsetSec, fadeSec); break;
        case EngineType::Keys: startKeys(note, vel, offsetSec, fadeSec); break;
        default: break;
    }
}

void Engine::startSynth(int note, int vel, float offsetSec, float fadeSec) {
    const auto& L = def_->layers;
    if (L.empty()) return;
    const float sv = p(I.vsens, 50) * 0.4f * std::log10((float)vel / 127.f);
    const int la = std::min(std::max((int)p(I.layer_a, 0), 0), (int)L.size() - 1);
    const int lbm = (int)p(I.layer_b, 0);
    const int ga = L[la];
    const int gb = (lbm > 0 && lbm - 1 < (int)L.size()) ? L[lbm - 1] : -1;
    const float b = p(I.blend, 350) / 1000.f;
    const float gaDb = lin2db(std::cos(b * kPi * 0.5f)), gbDb = lin2db(std::sin(b * kPi * 0.5f));
    int iv[3] = {0, 0, 0}, ivn = 1;
    switch ((int)p(I.oct_mode, 0)) {
        case 1: iv[1] = 12; ivn = 2; break;
        case 2: iv[1] = -12; ivn = 2; break;
        case 3: iv[1] = 12; iv[2] = -12; ivn = 3; break;
        case 4: iv[1] = 7; ivn = 2; break;
        case 5: iv[1] = 12; iv[2] = 19; ivn = 3; break;
        default: break;
    }
    const float fade = fadeSec >= 0 ? fadeSec : p(I.attack, 10) / 1000.f;
    const float octDb = p(I.oct_lvl, -60) / 10.f;
    for (int i = 0; i < ivn; ++i) {
        const int n = note + iv[i];
        if (n < 0 || n > 127) continue;
        float db = sv + (i > 0 ? octDb : 0.f);
        playVoice(n, ga, db + (gb >= 0 ? gaDb : 0.f), 0, offsetSec, fade, 0, 3, 0);
        if (gb >= 0) playVoice(n, gb, db + gbDb, 0, offsetSec, fade, 0, 3, 0);
    }
}

float Engine::velCurveDb(int vel, int& curved) const {
    float r = (float)vel / 127.f;
    r = std::pow(r, std::pow(2.f, -p(I.vcurve, 0) / 50.f));
    curved = std::max(1, (int)(r * 127.f));
    return p(I.vrange, 24) * (r - 1.f);
}

void Engine::calcDyn() {
    const float r = (float)dyn_ / 127.f;
    dynGp_ = lin2db(std::cos(r * kPi * 0.5f));
    dynGf_ = lin2db(std::sin(r * kPi * 0.5f));
    if (def_ && def_->engine == EngineType::Drums) dynDb_ = 20.f * std::log10(std::max(r, 0.001f)) * 1.2f;
    else dynDb_ = -p(I.dyn_range, 20) * std::pow(1.f - r, 1.3f);
    exprDb_ = 20.f * std::log10(std::max((float)cc11_ / 127.f, 0.001f)) * 0.9f;
    const float mc = p(I.mic_close, 0), mh = p(I.mic_hall, -60);
    micDb_[0] = has("mic_close") ? (mc <= -400 ? -100.f : mc / 10.f) : 0.f;
    micDb_[1] = has("mic_hall") ? (mh <= -400 ? -100.f : mh / 10.f) : 0.f;
}

float Engine::voiceDb(int role, float base) const {
    const int m = role / 10, r = role % 10;
    float db = 0;
    if (def_ && def_->engine == EngineType::Drums) return base + dynDb_;
    switch (r) {
        case 0: db = dynGp_ + dynDb_ + exprDb_; break;
        case 1: db = dynGf_ + dynDb_ + exprDb_; break;
        case 2: db = dynDb_ + exprDb_; break;
        default: db = base + exprDb_; break;
    }
    return db + micDb_[m & 1];
}

void Engine::updateDyn() {
    if (!def_) return;
    if (def_->engine == EngineType::Drums) {
        for (int s = 0; s < 128; ++s)
            for (uint32_t id : src_[s].ids) if (Voice* v = find(id)) setVoiceDb(*v, voiceDb(v->role, v->base));
        return;
    }
    if (def_->engine != EngineType::Artic) return;
    for (auto& v : voices_) if (v.active && v.envState != 2) setVoiceDb(v, voiceDb(v.role, v.base));
}

void Engine::startArtic(int note, int vel, float offsetSec, float fadeSec) {
    const ArtDef& a = def_->arts[art_];
    float fade = fadeSec >= 0 ? fadeSec : p(I.attack, 0) / 1000.f;
    if (a.type == 1) {  // short: round robin + velocity
        int& rr = rrPos_[art_];
        const int g = a.groups[rr % a.groups.size()];
        rr = (rr + 1) % (int)a.groups.size();
        int curved;
        const float base = velCurveDb(vel, curved) + rnd(-0.6f, 0.6f);
        playVoice(note, g, voiceDb(3, base), 0, offsetSec, 0, 0, 3, base);
        return;
    }
    if (a.type == 2) fade = p(I.swell_t, 1800) / 1000.f;
    const bool velDyn = p(I.dyn_src, 0) > 0.5f;
    for (size_t k = 0; k < a.groups.size(); ++k) {
        const int gi = a.groups[k];
        int role = a.groups.size() == 1 ? 2 : (int)k;
        float base = 0;
        if (velDyn) {
            const int saved = dyn_;
            dyn_ = vel; calcDyn();
            base = voiceDb(role, 0) - exprDb_ - micDb_[0];
            dyn_ = saved; calcDyn();
            role = 3;
        }
        for (int m = 0; m < 2; ++m) {
            int g = gi;
            if (m == 1) g = (gi < (int)def_->hallOf.size()) ? def_->hallOf[gi] : -1;
            if (g < 0 || micDb_[m] <= -100.f) continue;
            playVoice(note, g, voiceDb(role + 10 * m, base), 0, offsetSec, fade, 0, role + 10 * m, base);
        }
    }
}

void Engine::playPatch(int patch, int note, int curvedVel, float db, float offsetSec, float fadeSec) {
    const PatchDef& pd = def_->patches[patch];
    int layer = 0;
    while (layer < (int)pd.layers.size() - 1 && layer < (int)pd.splits.size() && curvedVel > pd.splits[layer]) ++layer;
    const auto& rrs = pd.layers[layer];
    if (rrs.empty()) return;
    int& rr = patchRr_[patch & 15][layer & 3];
    const int g = rrs[rr % rrs.size()];
    rr = (rr + 1) % (int)rrs.size();
    playVoice(note, g, db, 0, offsetSec, fadeSec, 0, 3, db);
}

void Engine::startKeys(int note, int vel, float offsetSec, float fadeSec) {
    int curved;
    const float vdb = velCurveDb(vel, curved);
    const float fade = fadeSec >= 0 ? fadeSec : p(I.attack, 0) / 1000.f;
    const int np = (int)def_->patches.size();
    const int pa = np > 1 ? std::min(std::max((int)p(I.patch, 0), 0), np - 1) : 0;
    playPatch(pa, note, curved, vdb + rnd(-0.25f, 0.25f), offsetSec, fade);
    if (np > 1) {
        const int pb = (int)p(I.patch2, 0);
        if (pb > 0 && pb - 1 < np) playPatch(pb - 1, note, curved, vdb + p(I.mix2, -60) / 10.f, offsetSec, fade);
    }
}

void Engine::drumHit(int note, int vel) {
    int pi = -1;
    for (size_t i = 0; i < def_->pieces.size(); ++i) if (def_->pieces[i].key == note) { pi = (int)i; break; }
    if (pi < 0) return;
    const PieceDef& pc = def_->pieces[pi];
    if (pc.cut > 0)
        for (auto& other : def_->pieces)
            if (other.cg == pc.cut && other.key != pc.key) {
                for (uint32_t id : pieceVoices_[other.key]) fadeOut(id, 0.045f);
                pieceVoices_[other.key].clear();
            }
    int curved;
    const float vdb = velCurveDb(vel, curved);
    int layer = 0;
    while (layer < (int)pc.layers.size() - 1 && layer < (int)pc.splits.size() && curved > pc.splits[layer]) ++layer;
    const auto& rrs = pc.layers[layer];
    int& rr = pieceRr_[note][layer & 3];
    int r = rr;
    if (rrs.size() > 1) rr = (r + 1 + rndi(0, (int)rrs.size() - 2)) % (int)rrs.size();
    const int g = rrs[r % rrs.size()];
    const float hum = p(I.hum, 25);
    const float busDb = (pc.bus < 8 && I.bus[pc.bus] >= 0) ? p(I.bus[pc.bus], 0) / 10.f : 0.f;
    const float base = vdb + busDb + rnd(-hum * 0.015f, hum * 0.015f);
    const float tune = p(I.tune, 0) + rnd(-hum * 0.04f, hum * 0.04f);
    const float pan = pc.pan * p(I.spread, 70) / 100.f;
    newIds_.clear();
    const float db = pc.hold ? base + dynDb_ : base;
    const uint32_t id = playVoice(note, g, db, tune, 0, 0, pan, 3, base);
    if (!id) return;
    auto& ring = pieceVoices_[note];
    ring.push_back(id);
    if (ring.size() > 8) ring.erase(ring.begin());
    if (pc.hold) registerNew(note);
}

// ===================================================================== mono synth (glide)
void Engine::monoNoteOn(int note, int vel) {
    monoVel_ = vel;
    stack_.erase(std::remove(stack_.begin(), stack_.end(), note), stack_.end());
    stack_.push_back(note);
    monoGlideTo(note, vel);
}

void Engine::monoGlideTo(int note, int vel) {
    if (!monoIds_.empty() && std::abs(note - monoBase_) <= 24) {
        monoCur_ = note;
        monoTune_ = (float)(note - monoBase_) * 100.f;
        const float glide = p(I.glide, 80) / 1000.f;
        for (uint32_t id : monoIds_)
            if (Voice* v = find(id)) {
                v->tuneTarget = monoTune_;
                v->tuneRate = glide <= 0.001f ? 0.f : (monoTune_ - v->tune) / (glide * (float)sr_);
                if (glide <= 0.001f) { v->tune = monoTune_; updatePitch(*v); }
            }
        return;
    }
    for (uint32_t id : monoIds_) fadeOut(id, 0.012f);
    newIds_.clear();
    startSynth(note, vel, 0, -1.f);
    monoIds_ = newIds_;
    monoBase_ = note;
    monoCur_ = note;
    monoTune_ = 0;
}

void Engine::monoNoteOff(int note) {
    stack_.erase(std::remove(stack_.begin(), stack_.end(), note), stack_.end());
    if (note != monoCur_) return;
    if (!stack_.empty()) { monoGlideTo(stack_.back(), monoVel_); return; }
    for (uint32_t id : monoIds_) fadeOut(id, p(I.release, 300) / 1000.f);
    monoIds_.clear();
    monoCur_ = -1;
}

// ===================================================================== legato (articulations)
void Engine::legatoNoteOn(int note, int vel) {
    monoVel_ = vel;
    stack_.erase(std::remove(stack_.begin(), stack_.end(), note), stack_.end());
    stack_.push_back(note);
    legatoTo(note, vel);
}

void Engine::legatoTo(int note, int vel) {
    if (!monoIds_.empty()) {
        const float lt = p(I.leg_time, 110) / 1000.f;
        const float from = (float)(monoCur_ - note) * p(I.porta, 25);  // cents
        for (uint32_t id : monoIds_) fadeOut(id, lt);
        newIds_.clear();
        startArtic(note, monoVel_, def_->legOffsetMs / 1000.f, lt);
        monoIds_ = newIds_;
        if (from != 0.f)
            for (uint32_t id : monoIds_)
                if (Voice* v = find(id)) {
                    v->tune = from;
                    v->tuneTarget = 0;
                    v->tuneRate = -from / (std::max(lt, 0.01f) * (float)sr_);
                    updatePitch(*v);
                }
        monoCur_ = note;
        return;
    }
    newIds_.clear();
    startArtic(note, vel, 0, -1.f);
    monoIds_ = newIds_;
    monoCur_ = note;
}

void Engine::legatoNoteOff(int note) {
    stack_.erase(std::remove(stack_.begin(), stack_.end(), note), stack_.end());
    if (note != monoCur_) return;
    if (!stack_.empty()) { legatoTo(stack_.back(), monoVel_); return; }
    for (uint32_t id : monoIds_) fadeOut(id, p(I.release, 350) / 1000.f);
    monoIds_.clear();
    monoCur_ = -1;
}

// ===================================================================== effects
void Engine::updateFxParams() {
    if (!def_) return;
    // filter: tone + mod wheel + movement, in control units 0..1000 -> 20 Hz .. 20 kHz
    float u = p(I.tone, 1000);
    if (def_->engine == EngineType::Synth) u += (float)cc1_ / 127.f * p(I.modwheel, 500) + cutLfo_;
    u = clampf(u, 0.f, 1000.f);
    const float hz = 20.f * std::pow(1000.f, u / 1000.f);
    const float q = has("reso") ? 0.5f + 7.5f * std::pow(p(I.reso, 120) / 1000.f, 1.5f) : 0.707f;
    filter_.set(hz, q);
    drive_.amt.target = p(I.drive, 0) / 1000.f;
    comp_.amount = p(I.comp, 0) / 1000.f;
    trem_.depth = p(I.trem_amt, 0) / 1000.f;
    trem_.rate = 0.5f + 9.5f * std::pow(p(I.trem_rate, 450) / 1000.f, 1.5f);
    trem_.drive = p(I.ep_drive, 0) / 1000.f;
    rotary_.fast = (p(I.rot_fast, 0) > 0.5f || fastRotary_) ? 1.f : 0.f;
    rotary_.mix = p(I.rot_mix, 1000) / 1000.f;
    width_.w.target = p(I.width, 500) / 500.f;
    chorus_.mix.target = p(I.chorus, 0) / 1000.f;
    delay_.mix.target = p(I.dly_mix, 0) / 1000.f * 0.8f;
    delay_.feedback = p(I.dly_fb, 350) / 1000.f * 0.92f;
    const float dt = p(I.dly_time, 450) / 1000.f;
    if (p(I.dly_sync, 1) > 0.5f) delay_.setTimeSeconds(kDelayBeats[(int)std::lround(dt * 12.f)] * 60.f / (float)bpm_);
    else delay_.setTimeSeconds(0.01f * std::pow(200.f, dt));
    reverb_.mix.target = p(I.rev_mix, 250) / 1000.f * 0.9f;
    reverb_.size = p(I.rev_size, 600) / 1000.f;
    reverb_.decay = 0.4f + 11.6f * std::pow(p(I.rev_decay, 550) / 1000.f, 2.f);
    reverb_.damping = 0.45f;
}

void Engine::applyFx(float* l, float* r, int n) {
    for (Fx f : def_->fx) {
        switch (f) {
            case Fx::Filter: filter_.process(l, r, n); break;
            case Fx::EpPre: trem_.process(l, r, n); break;
            case Fx::Rotator: rotary_.process(l, r, n); break;
            case Fx::SuperGt: drive_.process(l, r, n); break;
            case Fx::Comp: comp_.process(l, r, n); break;
            case Fx::Stereo: width_.process(l, r, n); break;
            case Fx::Choral: chorus_.process(l, r, n); break;
            case Fx::Replika: delay_.process(l, r, n); break;
            case Fx::Raum: reverb_.process(l, r, n); break;
        }
    }
}

}  // namespace nml
