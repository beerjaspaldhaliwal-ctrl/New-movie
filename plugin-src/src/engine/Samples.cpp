#include "Samples.hpp"

#include <cstdio>
#include <cstdlib>
#include <cstring>

#define DR_WAV_IMPLEMENTATION
#define DR_WAV_NO_STDIO
#include "dr_wav.h"

#ifdef _WIN32
#include <windows.h>
#include <shlobj.h>
#else
#include <dlfcn.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace nml {
namespace paths {

#ifdef _WIN32
static std::wstring widen(const std::string& s) {
    if (s.empty()) return std::wstring();
    int n = MultiByteToWideChar(CP_UTF8, 0, s.c_str(), (int)s.size(), nullptr, 0);
    std::wstring w(n, 0);
    MultiByteToWideChar(CP_UTF8, 0, s.c_str(), (int)s.size(), &w[0], n);
    return w;
}
static std::string narrow(const wchar_t* w) {
    int n = WideCharToMultiByte(CP_UTF8, 0, w, -1, nullptr, 0, nullptr, nullptr);
    std::string s(n > 0 ? n - 1 : 0, 0);
    if (n > 1) WideCharToMultiByte(CP_UTF8, 0, w, -1, &s[0], n, nullptr, nullptr);
    return s;
}
static const char kSep = '\\';
#else
static const char kSep = '/';
#endif

std::string join(const std::string& a, const std::string& b) {
    if (a.empty()) return b;
    std::string out = a;
    if (out.back() != '/' && out.back() != '\\') out += kSep;
    for (char c : b) out += (c == '/' || c == '\\') ? kSep : c;
    return out;
}

static bool isDir(const std::string& p) {
#ifdef _WIN32
    const DWORD a = GetFileAttributesW(widen(p).c_str());
    return a != INVALID_FILE_ATTRIBUTES && (a & FILE_ATTRIBUTE_DIRECTORY);
#else
    struct stat st;
    return stat(p.c_str(), &st) == 0 && S_ISDIR(st.st_mode);
#endif
}

static std::string parent(const std::string& p) {
    std::string s = p;
    while (!s.empty() && (s.back() == '/' || s.back() == '\\')) s.pop_back();
    const size_t i = s.find_last_of("/\\");
    return i == std::string::npos ? std::string() : s.substr(0, i);
}

bool isLibraryFolder(const std::string& dir) {
    return !dir.empty() && isDir(join(dir, "Samples")) && isDir(join(dir, "Samples/02 Orchestral"));
}

std::string libraryFromAnyPath(const std::string& path) {
    std::string p = path;
    for (int i = 0; i < 6 && !p.empty(); ++i) {
        if (isLibraryFolder(p)) return p;
        const std::string inner = join(p, "New Movie Library");
        if (isLibraryFolder(inner)) return inner;
        p = parent(p);
    }
    return std::string();
}

static std::string envVar(const char* name) {
#ifdef _WIN32
    wchar_t buf[2048];
    const DWORD n = GetEnvironmentVariableW(widen(name).c_str(), buf, 2048);
    return (n > 0 && n < 2048) ? narrow(buf) : std::string();
#else
    const char* v = std::getenv(name);
    return v ? std::string(v) : std::string();
#endif
}

std::string settingsFile() {
#ifdef _WIN32
    std::string base = envVar("APPDATA");
    if (base.empty()) return std::string();
    const std::string dir = join(base, "NewMovieLibrary");
    CreateDirectoryW(widen(dir).c_str(), nullptr);
    return join(dir, "library_path.txt");
#else
    std::string base = envVar("XDG_CONFIG_HOME");
    if (base.empty()) base = join(envVar("HOME"), ".config");
    const std::string dir = join(base, "NewMovieLibrary");
    mkdir(base.c_str(), 0755);
    mkdir(dir.c_str(), 0755);
    return join(dir, "library_path.txt");
#endif
}

bool readFile(const std::string& path, std::vector<uint8_t>& out) {
#ifdef _WIN32
    FILE* f = _wfopen(widen(path).c_str(), L"rb");
#else
    FILE* f = std::fopen(path.c_str(), "rb");
#endif
    if (!f) return false;
    std::fseek(f, 0, SEEK_END);
    const long size = std::ftell(f);
    std::fseek(f, 0, SEEK_SET);
    if (size <= 0) { std::fclose(f); return false; }
    out.resize((size_t)size);
    const size_t got = std::fread(out.data(), 1, (size_t)size, f);
    std::fclose(f);
    return got == (size_t)size;
}

std::string loadSavedLibrary() {
    std::vector<uint8_t> data;
    const std::string sf = settingsFile();
    if (sf.empty() || !readFile(sf, data)) return std::string();
    std::string s(data.begin(), data.end());
    while (!s.empty() && (s.back() == '\n' || s.back() == '\r' || s.back() == ' ')) s.pop_back();
    return s;
}

void saveLibrary(const std::string& dir) {
    const std::string sf = settingsFile();
    if (sf.empty()) return;
#ifdef _WIN32
    FILE* f = _wfopen(widen(sf).c_str(), L"wb");
#else
    FILE* f = std::fopen(sf.c_str(), "wb");
#endif
    if (!f) return;
    std::fwrite(dir.data(), 1, dir.size(), f);
    std::fclose(f);
}

static std::string binaryDir() {
#ifdef _WIN32
    HMODULE mod = nullptr;
    GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                       (LPCWSTR)&binaryDir, &mod);
    wchar_t buf[2048];
    const DWORD n = GetModuleFileNameW(mod, buf, 2048);
    return n ? parent(narrow(buf)) : std::string();
#else
    Dl_info info;
    if (dladdr((void*)&binaryDir, &info) && info.dli_fname) return parent(info.dli_fname);
    return std::string();
#endif
}

static std::string documentsDir() {
#ifdef _WIN32
    wchar_t buf[MAX_PATH];
    if (SHGetFolderPathW(nullptr, CSIDL_PERSONAL, nullptr, 0, buf) == S_OK) return narrow(buf);
    return std::string();
#else
    return join(envVar("HOME"), "Documents");
#endif
}

std::string findLibrary(const std::string& hint) {
    std::vector<std::string> candidates;
    if (!hint.empty()) candidates.push_back(hint);
    candidates.push_back(envVar("NML_LIBRARY_PATH"));
    candidates.push_back(loadSavedLibrary());
    candidates.push_back(binaryDir());  // walks upwards from the plugin binary
    const std::string docs = documentsDir();
    if (!docs.empty()) candidates.push_back(join(docs, "New Movie Library"));
#ifdef _WIN32
    const std::string home = envVar("USERPROFILE");
    candidates.push_back(join(home, "Desktop\\New Movie Library"));
    candidates.push_back(join(home, "Downloads\\New Movie Library"));
    for (const char* drive : {"C:\\", "D:\\", "E:\\"}) {
        candidates.push_back(join(drive, "New Movie Library"));
        candidates.push_back(join(drive, "New-movie\\New Movie Library"));
    }
#else
    const std::string home = envVar("HOME");
    candidates.push_back(join(home, "New Movie Library"));
    candidates.push_back(join(home, "New-movie/New Movie Library"));
#endif
    for (auto& c : candidates) {
        if (c.empty()) continue;
        const std::string lib = libraryFromAnyPath(c);
        if (!lib.empty()) return lib;
    }
    return std::string();
}

}  // namespace paths

LoadedInstrument* loadInstrument(int index, const std::string& libraryDir, std::atomic<float>& progress) {
    const Catalog& cat = Catalog::get();
    auto* li = new LoadedInstrument();
    li->index = index;
    li->def = &cat.instruments[index];
    const InstrumentDef& d = *li->def;
    li->samples.resize(d.zones.size());
    li->zoneForKey.assign(d.groups.size(), std::vector<int>(128, -1));

    std::vector<uint8_t> bytes;
    for (size_t zi = 0; zi < d.zones.size(); ++zi) {
        const ZoneDef& z = d.zones[zi];
        for (int n = z.lo; n <= z.hi; ++n)
            if (n >= 0 && n < 128) li->zoneForKey[z.group][n] = (int)zi;
        Sample& s = li->samples[zi];
        s.root = z.root;
        s.loopStart = z.loopStart;
        s.loopEnd = z.loopEnd;
        const std::string path = paths::join(libraryDir, z.file);
        drwav wav;
        if (!paths::readFile(path, bytes) || !drwav_init_memory(&wav, bytes.data(), bytes.size(), nullptr)) {
            ++li->missing;
            if (li->error.empty()) li->error = "Missing sample: " + z.file;
            continue;
        }
        const drwav_uint64 frames = wav.totalPCMFrameCount;
        const unsigned ch = wav.channels;
        std::vector<float> inter((size_t)frames * ch);
        const drwav_uint64 got = drwav_read_pcm_frames_f32(&wav, frames, inter.data());
        drwav_uninit(&wav);
        s.frames = (int)got;
        s.l.resize(s.frames + 4, 0.f);  // padding for the interpolator
        if (ch > 1) s.r.resize(s.frames + 4, 0.f);
        for (int i = 0; i < s.frames; ++i) {
            s.l[i] = inter[(size_t)i * ch];
            if (ch > 1) s.r[i] = inter[(size_t)i * ch + 1];
        }
        if (s.loopEnd > s.frames) s.loopEnd = s.frames;
        if (s.loopStart >= 0 && s.loopEnd - s.loopStart < 16) s.loopStart = s.loopEnd = -1;
        if (s.loopStart >= 0) {
            // The interpolator reads up to two samples past the loop end: make them the loop start,
            // so the seam is continuous. A looping voice never plays the audio after loopEnd.
            for (int k = 0; k < 3; ++k) {
                s.l[s.loopEnd + k] = s.l[s.loopStart + k];
                if (ch > 1) s.r[s.loopEnd + k] = s.r[s.loopStart + k];
            }
        }
        progress.store((float)(zi + 1) / (float)d.zones.size());
    }
    progress.store(1.f);
    return li;
}

}  // namespace nml
