// Sample loading and library-folder discovery.
#pragma once

#include <atomic>
#include <cstdint>
#include <string>
#include <vector>

#include "Catalog.hpp"

namespace nml {

struct Sample {
    std::vector<float> l, r;  // r empty for mono
    int frames = 0;
    int loopStart = -1, loopEnd = -1;
    int root = 60;
    bool stereo() const { return !r.empty(); }
};

// A fully loaded instrument: catalog definition + audio + lookup tables.
struct LoadedInstrument {
    const InstrumentDef* def = nullptr;
    int index = -1;
    std::vector<Sample> samples;               // parallel to def->zones
    std::vector<std::vector<int>> zoneForKey;  // [group][note] -> zone index or -1
    int missing = 0;
    std::string error;

    int zone(int group, int note) const {
        if (group < 0 || group >= (int)zoneForKey.size() || note < 0 || note > 127) return -1;
        return zoneForKey[group][note];
    }
};

namespace paths {
std::string join(const std::string& a, const std::string& b);
bool isLibraryFolder(const std::string& dir);
// Finds the library folder: saved setting, env var, next to the plugin, Documents, drive roots.
std::string findLibrary(const std::string& hint);
// Normalises a user-chosen path (a file or folder anywhere inside the library) to the library root.
std::string libraryFromAnyPath(const std::string& path);
std::string settingsFile();
std::string loadSavedLibrary();
void saveLibrary(const std::string& dir);
bool readFile(const std::string& path, std::vector<uint8_t>& out);
}  // namespace paths

// Loads all samples of an instrument; progress is 0..1. Runs on a worker thread.
LoadedInstrument* loadInstrument(int index, const std::string& libraryDir, std::atomic<float>& progress);

}  // namespace nml
