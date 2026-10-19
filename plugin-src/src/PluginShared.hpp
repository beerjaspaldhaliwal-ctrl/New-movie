// State shared between the DSP and the UI (DISTRHO_PLUGIN_WANT_DIRECT_ACCESS).
#pragma once

#include <atomic>
#include <mutex>
#include <string>

#include "engine/Engine.hpp"

namespace nml {

struct SharedStatus {
    std::atomic<int> loadedIndex{-1};   // instrument currently playing
    std::atomic<int> loadingIndex{-1};  // instrument being loaded (-1 = idle)
    std::atomic<float> progress{0.f};
    std::atomic<int> missing{0};
    std::atomic<bool> libraryFound{false};
    std::atomic<uint32_t> revision{0};  // bumped whenever the strings below change
    std::mutex mutex;
    std::string library, error;
    Engine* engine = nullptr;           // UI reads its atomics only

    std::string libraryPath() { std::lock_guard<std::mutex> g(mutex); return library; }
    std::string errorText() { std::lock_guard<std::mutex> g(mutex); return error; }
};

// Implemented by the plugin; the UI finds it with dynamic_cast on the plugin instance pointer.
class SharedStatusProvider {
public:
    virtual ~SharedStatusProvider() {}
    virtual SharedStatus& sharedStatus() = 0;
};

}  // namespace nml
