// The New Movie Library playback engine: voices, the four instrument engines
// (synth, articulations, keys, drums), the Performer and the effect chain.
// Behaviour mirrors the generated Kontakt scripts (tools/nml/ksp_gen.py).
#pragma once

#include <atomic>
#include <cstdint>
#include <vector>

#include "Catalog.hpp"
#include "Effects.hpp"
#include "Samples.hpp"

namespace nml {

struct MidiMsg {
    uint32_t frame;
    uint8_t data[3];
};

struct TimeInfo {
    bool playing = false;
    bool bbtValid = false;
    double bpm = 120.0;
    double ppq = 0.0;  // quarter-note position at the start of the block
};

class Engine {
public:
    static constexpr int kMaxVoices = 256;
    static constexpr int kNumSources = 129;  // 128 keys + the arpeggiator
    static constexpr int kArpSource = 128;

    Engine();
    void setSampleRate(double sr);
    // Parameter values in "control units" (same as the Kontakt scripts), indexed like Catalog::params.
    void setParamPointer(const float* params) { P_ = params; }
    // Swap in a newly loaded instrument (audio thread). Returns the previous one for deferred deletion.
    LoadedInstrument* setInstrument(LoadedInstrument* li);
    const LoadedInstrument* instrument() const { return inst_; }
    void process(float* outL, float* outR, uint32_t frames, const MidiMsg* ev, uint32_t nev, const TimeInfo& ti);
    void allNotesOff();

    // status for the UI (read from another thread)
    std::atomic<int> activeVoices{0};
    std::atomic<int> currentArt{0};
    std::atomic<uint8_t> keyDown[128];
    std::atomic<float> peakL{0}, peakR{0};
    std::atomic<uint32_t> voicesStarted{0};  // running count, used by the tests

private:
    struct Voice {
        bool active = false;
        uint32_t id = 0;
        const Sample* s = nullptr;
        int note = 60;
        double pos = 0, step = 1;
        float tune = 0, tuneTarget = 0, tuneRate = 0;  // cents, cents per sample
        float gain = 1, gainTarget = 1;
        float panL = 1, panR = 1;
        float env = 0, envInc = 0;  // linear envelope 0..1
        int envState = 0;           // 0 attack, 1 hold, 2 release
        int role = 3;               // dynamic-volume role (see voiceDb)
        float base = 0;             // base level in dB for static roles
        uint64_t started = 0;
    };
    struct Source {
        std::vector<uint32_t> ids;
        bool held = false, sus = false;
    };
    struct Action {  // delayed note start (strum / humanise)
        uint64_t time;
        int src, index, vel;
        uint32_t generation;
    };
    struct Pending { uint32_t id; uint64_t tick; };

    // --- helpers
    // Value of a parameter, or dflt when the current instrument has no such control
    // (the Kontakt scripts hard-code the same fallbacks).
    float p(int idx, float dflt = 0.f) const { return (P_ && idx >= 0 && has_[idx]) ? P_[idx] : dflt; }
    float pv(const char* var, float dflt = 0.f) const;
    bool has(const char* var) const;  // control exists in the current instrument
    void resolveParams();

    uint32_t playVoice(int note, int group, float db, float tuneCents, float offsetSec, float fadeSec, float pan,
                       int role, float base);
    Voice* find(uint32_t id);
    void fadeOut(uint32_t id, float sec);
    void setVoiceDb(Voice& v, float db) { v.gainTarget = dbToLin(db); }
    void updatePitch(Voice& v);
    void renderVoices(float* l, float* r, int n);
    void releaseSrc(int src, float sec);
    void releaseAll(float sec);
    void registerNew(int src);
    void pendNew(uint64_t releaseTick);

    // --- events
    void handleMidi(const uint8_t* d);
    void noteOn(int note, int vel);
    void noteOff(int note);
    void controller(int cc, int val);
    void tickEvent();
    void runAction(const Action& a);

    // --- performer
    int scaleSnap(int note) const;
    void buildChord(int root, int src);
    void polyNoteOn(int note, int vel);
    void polyNoteOff(int note, bool letRing);
    void startChordNote(int src, int index, int vel);
    void arpAdd(int src);
    void arpRemove(int src);
    void arpSort();
    void arpFire();

    // --- engines
    void startNote(int note, int vel, float offsetSec, float fadeSec);
    void startSynth(int note, int vel, float offsetSec, float fadeSec);
    void startArtic(int note, int vel, float offsetSec, float fadeSec);
    void startKeys(int note, int vel, float offsetSec, float fadeSec);
    void playPatch(int patch, int note, int curvedVel, float db, float offsetSec, float fadeSec);
    void drumHit(int note, int vel);
    float velCurveDb(int vel, int& curved) const;
    void calcDyn();
    float voiceDb(int role, float base) const;
    void updateDyn();
    // mono / legato
    void monoNoteOn(int note, int vel);
    void monoNoteOff(int note);
    void monoGlideTo(int note, int vel);
    void legatoNoteOn(int note, int vel);
    void legatoNoteOff(int note);
    void legatoTo(int note, int vel);

    // --- effects
    void applyFx(float* l, float* r, int n);
    void resetFx();
    void updateFxParams();

    const float* P_ = nullptr;
    LoadedInstrument* inst_ = nullptr;
    const InstrumentDef* def_ = nullptr;
    double sr_ = 44100.0;
    double srRatio_ = 1.0;
    Voice voices_[kMaxVoices];
    uint32_t nextId_ = 1;
    uint64_t now_ = 0;  // absolute sample clock
    Source src_[kNumSources];
    std::vector<uint32_t> newIds_;
    std::vector<Action> actions_;
    std::vector<Pending> pending_;
    uint32_t generation_[128] = {0};

    // tempo ticks (24 per quarter note)
    uint64_t tick_ = 0;
    double samplesToTick_ = 0;
    double bpm_ = 120;
    bool wasPlaying_ = false;

    // controller state
    bool pedal_ = false;
    int keysDown_ = 0;
    float bendCents_ = 0;
    int cc1_ = 0, cc11_ = 127;
    int lastVel_ = 100;

    // performer
    std::vector<int> chord_[kNumSources];
    struct ArpNote { int note, src; };
    std::vector<ArpNote> arp_;
    std::vector<int> arpSorted_;
    uint64_t arpStep_ = 0, arpNext_ = 0;
    int arpVel_ = 100;

    // synth
    int lfoPos_ = 0;
    float cutLfo_ = 0;
    // mono / legato
    std::vector<uint32_t> monoIds_;
    std::vector<int> stack_;
    int monoBase_ = 60, monoCur_ = -1, monoVel_ = 100;
    float monoTune_ = 0;
    // articulations
    int art_ = 0;
    int rrPos_[64] = {0};
    float dynGp_ = 0, dynGf_ = 0, dynDb_ = 0, exprDb_ = 0, micDb_[2] = {0, 0};
    int dyn_ = 90;
    // keys
    int patchRr_[16][4] = {{0}};
    // drums
    std::vector<uint32_t> pieceVoices_[128];
    int pieceRr_[128][4] = {{0}};
    int repVel_[128] = {0};
    uint64_t repNext_[128] = {0};
    int repN_ = 0;

    // effects
    FilterFx filter_;
    DriveFx drive_;
    CompFx comp_;
    TremoloFx trem_;
    RotaryFx rotary_;
    WidthFx width_;
    ChorusFx chorus_;
    DelayFx delay_;
    ReverbFx reverb_;
    Smooth master_;
    std::vector<float> busL_, busR_;

    // resolved global parameter indices
    struct Idx {
        int volume, tone, reso, width, chorus, dly_mix, dly_time, dly_fb, dly_sync, rev_mix, rev_size, rev_decay,
            use_pedal, pb_range, scale_type, scale_key, chord, strum, hum_time, hum_vel, arp_mode, arp_rate,
            arp_oct, arp_gate, arp_swing, arp_latch, arp_accent, layer_a, layer_b, blend, attack, release, vsens,
            move_amt, oct_mode, oct_lvl, mono, glide, move_rate, modwheel, drive, patch, patch2, mix2, vrange,
            vcurve, repeat_damp, let_ring, art_menu, dyn_knob, dyn_src, dyn_range, swell_t, legato, leg_time,
            porta, mic_close, mic_hall, comp, tune, hum, spread, repeat, trem_amt, trem_rate, ep_drive, rot_fast,
            rot_mix, mw_rot;
        int bus[8];
    } I{};
    int lastArtParam_ = -1;
    float lastDynSig_[4] = {-1e9f, -1e9f, -1e9f, -1e9f};
    bool has_[256] = {false};
    bool fastRotary_ = false;
};

}  // namespace nml
