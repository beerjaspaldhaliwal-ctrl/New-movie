// New Movie Library player: DPF plugin wrapper around the engine.
#include "DistrhoPlugin.hpp"
#include "DistrhoPluginUtils.hpp"

#include <condition_variable>
#include <cstring>
#include <cstdlib>
#include <thread>
#include <vector>

#include "PluginShared.hpp"

START_NAMESPACE_DISTRHO

using namespace nml;

static const char* const kDefaultInstrument = "Strings";

class NMLPlugin : public Plugin, public SharedStatusProvider {
public:
    NMLPlugin()
        : Plugin((uint32_t)Catalog::get().params.size(), 0, 2) {
        const Catalog& cat = Catalog::get();
        const char* env = std::getenv("NML_DEFAULT_INSTRUMENT");
        instrumentKey_ = (env && cat.instrument(env) >= 0) ? env : kDefaultInstrument;
        params_.resize(cat.params.size());
        for (size_t i = 0; i < params_.size(); ++i) params_[i] = defaultValue((uint32_t)i);
        engine_.setParamPointer(params_.data());
        midi_.reserve(2048);
        engine_.setSampleRate(getSampleRate());
        status_.engine = &engine_;
        if (isDummyInstance()) return;  // hosts create one while scanning: no disk access, no threads

        setLibrary(paths::findLibrary(std::string()), false);
        worker_ = std::thread([this] { workerLoop(); });
        requestLoad(instrumentKey_);
    }

    ~NMLPlugin() override {
        {
            std::lock_guard<std::mutex> g(workerMutex_);
            quit_ = true;
        }
        workerCv_.notify_all();
        if (worker_.joinable()) worker_.join();
        delete pending_.exchange(nullptr);
        delete retired_.exchange(nullptr);
        delete engine_.setInstrument(nullptr);
    }

    SharedStatus& sharedStatus() override { return status_; }

protected:
    const char* getLabel() const override { return "NewMovieLibrary"; }
    const char* getDescription() const override {
        return "Player for the New Movie Library: synths, orchestra, band, cinematic and world instruments.";
    }
    const char* getMaker() const override { return "New Movie Library"; }
    const char* getHomePage() const override { return "https://github.com/beerjaspaldhaliwal-ctrl/New-movie"; }
    const char* getLicense() const override { return "ISC"; }
    uint32_t getVersion() const override { return d_version(1, 0, 0); }
    int64_t getUniqueId() const override { return d_cconst('N', 'M', 'L', 'p'); }

    void initParameter(uint32_t index, Parameter& p) override {
        const ParamDef& d = Catalog::get().params[index];
        p.hints = kParameterIsAutomatable;
        if (d.kind == "menu") p.hints |= kParameterIsInteger;
        if (d.kind == "switch") p.hints |= kParameterIsInteger | kParameterIsBoolean;
        p.name = d.name.c_str();
        p.symbol = d.var.c_str();
        p.ranges.min = d.lo;
        p.ranges.max = d.hi;
        p.ranges.def = defaultValue(index);
        if (index == 0) p.unit = "dB";
    }

    // Defaults follow the start-up instrument, so a fresh instance sounds like that instrument's patch.
    float defaultValue(uint32_t index) const {
        const Catalog& cat = Catalog::get();
        const int ii = cat.instrument(instrumentKey_.empty() ? kDefaultInstrument : instrumentKey_);
        if (ii >= 0)
            if (const ControlDef* c = cat.instruments[ii].control(cat.params[index].var)) return (float)c->def;
        return cat.params[index].def;
    }

    float getParameterValue(uint32_t index) const override { return index < params_.size() ? params_[index] : 0.f; }
    void setParameterValue(uint32_t index, float value) override {
        if (index < params_.size()) params_[index] = value;
    }

    void initState(uint32_t index, State& s) override {
        if (index == 0) {
            s.key = "instrument";
            s.defaultValue = kDefaultInstrument;
            s.label = "Instrument";
        } else {
            s.key = "library";
            s.defaultValue = "";
            s.label = "Library Folder";
        }
    }

    String getState(const char* key) const override {
        if (std::strcmp(key, "instrument") == 0) return String(instrumentKey_.c_str());
        if (std::strcmp(key, "library") == 0) return String(libraryDir_.c_str());
        return String();
    }

    void setState(const char* key, const char* value) override {
        if (!worker_.joinable()) return;
        if (std::strcmp(key, "instrument") == 0) {
            if (Catalog::get().instrument(value) < 0) return;
            instrumentKey_ = value;
            requestLoad(instrumentKey_);
        } else if (std::strcmp(key, "library") == 0) {
            // an empty or stale saved path falls back to auto-detection
            std::string lib = value && *value ? paths::libraryFromAnyPath(value) : std::string();
            if (lib.empty()) lib = paths::findLibrary(std::string());
            if (lib != libraryDir_) {
                setLibrary(lib, value && *value && !lib.empty());
                requestLoad(instrumentKey_);
            }
        }
    }

    void activate() override {
        std::lock_guard<std::mutex> g(engineMutex_);
        engine_.setSampleRate(getSampleRate());
        swapIn();
        active_.store(true);
    }

    void deactivate() override {
        std::lock_guard<std::mutex> g(engineMutex_);
        active_.store(false);
        engine_.allNotesOff();
    }

    void sampleRateChanged(double sr) override {
        std::lock_guard<std::mutex> g(engineMutex_);
        engine_.setSampleRate(sr);
    }

    void run(const float**, float** outputs, uint32_t frames, const MidiEvent* ev, uint32_t nev) override {
        // Only contended in the moment the worker installs an instrument while the host is inactive.
        std::unique_lock<std::mutex> lk(engineMutex_, std::try_to_lock);
        if (!lk.owns_lock()) {
            std::memset(outputs[0], 0, sizeof(float) * frames);
            std::memset(outputs[1], 0, sizeof(float) * frames);
            return;
        }
        swapIn();
        midi_.clear();
        for (uint32_t i = 0; i < nev; ++i) {
            if (ev[i].size > 3 || ev[i].size == 0) continue;
            MidiMsg m;
            m.frame = ev[i].frame;
            m.data[0] = ev[i].data[0];
            m.data[1] = ev[i].size > 1 ? ev[i].data[1] : 0;
            m.data[2] = ev[i].size > 2 ? ev[i].data[2] : 0;
            midi_.push_back(m);
        }
        const TimePosition& tp = getTimePosition();
        TimeInfo ti;
        ti.playing = tp.playing;
        ti.bbtValid = tp.bbt.valid;
        if (tp.bbt.valid) {
            ti.bpm = tp.bbt.beatsPerMinute;
            const double tpb = tp.bbt.ticksPerBeat > 0 ? tp.bbt.ticksPerBeat : 1920.0;
            ti.ppq = (tp.bbt.barStartTick + (tp.bbt.beat - 1) * tpb + tp.bbt.tick) / tpb;
            // DPF's VST3 wrapper counts beats in time-signature units (eighths in 6/8); CLAP counts quarters
            if (isVst3_ && tp.bbt.beatType > 0) ti.ppq *= 4.0 / tp.bbt.beatType;
        }
        engine_.process(outputs[0], outputs[1], frames, midi_.data(), (uint32_t)midi_.size(), ti);
    }

private:
    void setLibrary(const std::string& lib, bool remember) {
        libraryDir_ = lib;
        if (remember) paths::saveLibrary(lib);
        status_.libraryFound.store(!lib.empty());
        {
            std::lock_guard<std::mutex> g(status_.mutex);
            status_.library = lib;
            if (lib.empty()) status_.error = "Library folder not found";
        }
        ++status_.revision;
    }

    void requestLoad(const std::string& key) {
        const int idx = Catalog::get().instrument(key);
        if (idx < 0) return;
        {
            std::lock_guard<std::mutex> g(workerMutex_);
            request_ = idx;
            requestLib_ = libraryDir_;
            ++requestSerial_;
        }
        status_.loadingIndex.store(idx);
        status_.progress.store(0.f);
        workerCv_.notify_all();
    }

    // Audio thread: install a freshly loaded instrument once the previous one has been collected.
    void swapIn() {
        if (retired_.load() != nullptr) return;
        LoadedInstrument* li = pending_.exchange(nullptr);
        if (!li) return;
        retired_.store(engine_.setInstrument(li));
        status_.loadedIndex.store(li->index);
        status_.missing.store(li->missing);
        if (status_.loadingIndex.load() == li->index) status_.loadingIndex.store(-1);
        workerCv_.notify_all();
    }

    void workerLoop() {
        int doneSerial = 0;
        std::unique_lock<std::mutex> lk(workerMutex_);
        while (!quit_) {
            workerCv_.wait_for(lk, std::chrono::milliseconds(100));
            delete retired_.exchange(nullptr);
            if (quit_) break;
            if (requestSerial_ == doneSerial) continue;
            doneSerial = requestSerial_;
            const int idx = request_;
            const std::string lib = requestLib_;
            lk.unlock();
            LoadedInstrument* li = nullptr;
            if (!lib.empty()) {
                li = loadInstrument(idx, lib, status_.progress);
                {
                    std::lock_guard<std::mutex> g(status_.mutex);
                    status_.error = li->missing ? li->error : std::string();
                }
                ++status_.revision;
            } else {
                // no library: install an empty instrument so the UI still shows its controls
                li = new LoadedInstrument();
                li->index = idx;
                li->def = &Catalog::get().instruments[idx];
                li->zoneForKey.assign(li->def->groups.size(), std::vector<int>(128, -1));
                li->missing = (int)li->def->zones.size();
            }
            delete pending_.exchange(li);  // drop a load that was superseded before it played
            if (!active_.load()) {
                // the host is not running audio: install directly so the UI is never stuck on "loading"
                std::lock_guard<std::mutex> g(engineMutex_);
                if (!active_.load()) {
                    swapIn();
                    delete retired_.exchange(nullptr);
                }
            }
            lk.lock();
        }
    }

    Engine engine_;
    SharedStatus status_;
    std::vector<float> params_;
    std::vector<MidiMsg> midi_;
    const bool isVst3_ = std::strcmp(getPluginFormatName(), "VST3") == 0;
    std::string instrumentKey_, libraryDir_;

    std::thread worker_;
    std::mutex workerMutex_;
    std::condition_variable workerCv_;
    bool quit_ = false;
    int request_ = -1, requestSerial_ = 0;
    std::string requestLib_;
    std::mutex engineMutex_;
    std::atomic<bool> active_{false};
    std::atomic<LoadedInstrument*> pending_{nullptr};
    std::atomic<LoadedInstrument*> retired_{nullptr};

    DISTRHO_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(NMLPlugin)
};

Plugin* createPlugin() { return new NMLPlugin(); }

END_NAMESPACE_DISTRHO

namespace nml {
SharedStatus* sharedStatusFromPlugin(void* plugin) {
    if (!plugin) return nullptr;
    return &static_cast<DISTRHO_NAMESPACE::NMLPlugin*>(static_cast<DISTRHO_NAMESPACE::Plugin*>(plugin))->sharedStatus();
}
}  // namespace nml
