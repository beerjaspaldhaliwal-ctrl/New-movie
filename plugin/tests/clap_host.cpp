// Minimal CLAP host used to test the plugin binary (Linux, and Windows under Wine).
//
//   clap_host <plugin.clap> render <out.wav> [seconds]
//       plays a short phrase (chord + single notes) and writes the output
//   clap_host <plugin.clap> state
//       saves the plugin state, reloads it into a fresh instance and prints it
//   clap_host <plugin.clap> gui <script...>
//       opens the editor; script steps: wait <ms> | click <x> <y> | drag <x> <y> <dy> |
//       wheel <x> <y> <n> | note <key> <vel> <ms> | hold <key> <vel> | shot <file> (Linux, needs ImageMagick)
//
// The instrument is chosen with NML_DEFAULT_INSTRUMENT, the library folder with NML_LIBRARY_PATH.
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

#include "clap/entry.h"
#include "clap/ext/audio-ports.h"
#include "clap/ext/gui.h"
#include "clap/ext/params.h"
#include "clap/ext/state.h"
#include "clap/ext/timer-support.h"
#include "clap/plugin-factory.h"

#ifdef _WIN32
#include <windows.h>
#else
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <dlfcn.h>
extern "C" int XTestFakeMotionEvent(Display*, int, int, int, unsigned long);
extern "C" int XTestFakeButtonEvent(Display*, unsigned int, int, unsigned long);
#endif

static const double kSr = 48000.0;
static const uint32_t kBlock = 256;

// ---------------------------------------------------------------- host
struct Timer { clap_id id; uint32_t period; double next; };
static std::vector<Timer> gTimers;
static clap_id gNextTimer = 1;
static double nowMs() {
    using namespace std::chrono;
    return (double)duration_cast<microseconds>(steady_clock::now().time_since_epoch()).count() / 1000.0;
}

static bool hostRegisterTimer(const clap_host_t*, uint32_t period, clap_id* id) {
    *id = gNextTimer++;
    gTimers.push_back({*id, std::max<uint32_t>(period, 10), nowMs() + period});
    return true;
}
static bool hostUnregisterTimer(const clap_host_t*, clap_id id) {
    for (size_t i = 0; i < gTimers.size(); ++i) if (gTimers[i].id == id) { gTimers.erase(gTimers.begin() + i); return true; }
    return false;
}
static const clap_host_timer_support_t kTimerExt = {hostRegisterTimer, hostUnregisterTimer};

static void hostGuiResizeHints(const clap_host_t*) {}
static bool hostGuiRequestResize(const clap_host_t*, uint32_t w, uint32_t h) {
    std::printf("gui: plugin asks for %ux%u\n", w, h);
    return true;
}
static bool hostGuiRequest(const clap_host_t*) { return true; }
static void hostGuiClosed(const clap_host_t*, bool) {}
static const clap_host_gui_t kGuiExt = {hostGuiResizeHints, hostGuiRequestResize, hostGuiRequest, hostGuiRequest,
                                        hostGuiClosed};

static const void* hostGetExtension(const clap_host_t*, const char* id) {
    if (!std::strcmp(id, CLAP_EXT_TIMER_SUPPORT)) return &kTimerExt;
    if (!std::strcmp(id, CLAP_EXT_GUI)) return &kGuiExt;
    return nullptr;
}
static void hostNoop(const clap_host_t*) {}

static clap_host_t gHost = {CLAP_VERSION, nullptr, "nml-test-host", "New Movie Library", "", "1.0",
                            hostGetExtension, hostNoop, hostNoop, hostNoop};

// ---------------------------------------------------------------- events
struct InEvents {
    std::vector<clap_event_note_t> notes;
    static uint32_t size(const clap_input_events_t* l) { return (uint32_t)((InEvents*)l->ctx)->notes.size(); }
    static const clap_event_header_t* get(const clap_input_events_t* l, uint32_t i) {
        return &((InEvents*)l->ctx)->notes[i].header;
    }
};
static bool tryPush(const clap_output_events_t*, const clap_event_header_t*) { return true; }

static clap_event_note_t makeNote(bool on, uint32_t time, int key, double vel) {
    clap_event_note_t n;
    std::memset(&n, 0, sizeof(n));
    n.header.size = sizeof(n);
    n.header.time = time;
    n.header.space_id = CLAP_CORE_EVENT_SPACE_ID;
    n.header.type = on ? CLAP_EVENT_NOTE_ON : CLAP_EVENT_NOTE_OFF;
    n.note_id = -1; n.port_index = 0; n.channel = 0; n.key = (int16_t)key; n.velocity = vel;
    return n;
}

// ---------------------------------------------------------------- plugin wrapper
struct Instance {
    const clap_plugin_t* p = nullptr;
    std::vector<float> l, r;
    std::mutex evMutex;
    std::vector<clap_event_note_t> queued;
    clap_event_transport_t transport{};
    double beats = 0;

    bool create(const clap_plugin_factory_t* f, const char* id) {
        p = f->create_plugin(f, &gHost, id);
        if (!p || !p->init(p)) { std::fprintf(stderr, "plugin init failed\n"); return false; }
        if (!p->activate(p, kSr, 1, kBlock)) { std::fprintf(stderr, "activate failed\n"); return false; }
        p->start_processing(p);
        l.resize(kBlock); r.resize(kBlock);
        return true;
    }
    void destroy() {
        if (!p) return;
        p->stop_processing(p);
        p->deactivate(p);
        p->destroy(p);
        p = nullptr;
    }
    // processes one block; events are block-relative
    void process(std::vector<clap_event_note_t> evs, float* outL, float* outR) {
        {
            std::lock_guard<std::mutex> g(evMutex);
            for (auto& e : queued) evs.push_back(e);
            queued.clear();
        }
        InEvents in{evs};
        clap_input_events_t inList{&in, InEvents::size, InEvents::get};
        clap_output_events_t outList{nullptr, tryPush};
        float* chans[2] = {outL, outR};
        clap_audio_buffer_t out{};
        out.data32 = chans; out.channel_count = 2;
        transport.header.size = sizeof(transport);
        transport.header.type = CLAP_EVENT_TRANSPORT;
        transport.flags = CLAP_TRANSPORT_HAS_TEMPO | CLAP_TRANSPORT_HAS_BEATS_TIMELINE | CLAP_TRANSPORT_IS_PLAYING;
        transport.tempo = 120.0;
        transport.song_pos_beats = (clap_beattime)std::llround(beats * CLAP_BEATTIME_FACTOR);
        transport.tsig_num = 4; transport.tsig_denom = 4;
        clap_process_t pr{};
        pr.steady_time = -1; pr.frames_count = kBlock; pr.transport = &transport;
        pr.audio_outputs = &out; pr.audio_outputs_count = 1;
        pr.in_events = &inList; pr.out_events = &outList;
        p->process(p, &pr);
        beats += kBlock / kSr * 2.0;
    }
};

static void writeWav(const char* path, const std::vector<float>& L, const std::vector<float>& R) {
    FILE* f = std::fopen(path, "wb");
    if (!f) return;
    const uint32_t n = (uint32_t)L.size(), data = n * 4;
    auto u32 = [&](uint32_t v) { std::fwrite(&v, 4, 1, f); };
    auto u16 = [&](uint16_t v) { std::fwrite(&v, 2, 1, f); };
    std::fwrite("RIFF", 1, 4, f); u32(36 + data); std::fwrite("WAVEfmt ", 1, 8, f);
    u32(16); u16(1); u16(2); u32((uint32_t)kSr); u32((uint32_t)kSr * 4); u16(4); u16(16);
    std::fwrite("data", 1, 4, f); u32(data);
    for (uint32_t i = 0; i < n; ++i) {
        const int16_t a = (int16_t)std::lround(std::max(-1.f, std::min(1.f, L[i])) * 32767.f);
        const int16_t b = (int16_t)std::lround(std::max(-1.f, std::min(1.f, R[i])) * 32767.f);
        std::fwrite(&a, 2, 1, f); std::fwrite(&b, 2, 1, f);
    }
    std::fclose(f);
}

// state streams
struct Buf { std::vector<uint8_t> d; size_t pos = 0; };
static int64_t ostreamWrite(const clap_ostream_t* s, const void* b, uint64_t n) {
    auto* buf = (Buf*)s->ctx; buf->d.insert(buf->d.end(), (const uint8_t*)b, (const uint8_t*)b + n); return (int64_t)n;
}
static int64_t istreamRead(const clap_istream_t* s, void* b, uint64_t n) {
    auto* buf = (Buf*)s->ctx;
    const size_t k = std::min<size_t>((size_t)n, buf->d.size() - buf->pos);
    std::memcpy(b, buf->d.data() + buf->pos, k); buf->pos += k; return (int64_t)k;
}

static void sleepMs(int ms) { std::this_thread::sleep_for(std::chrono::milliseconds(ms)); }

int main(int argc, char** argv) {
    if (argc < 3) { std::fprintf(stderr, "usage: clap_host <plugin.clap> render|state|gui ...\n"); return 2; }
#ifdef _WIN32
    HMODULE lib = LoadLibraryA(argv[1]);
    if (!lib) { std::fprintf(stderr, "cannot load %s (%lu)\n", argv[1], GetLastError()); return 1; }
    auto* entry = (const clap_plugin_entry_t*)GetProcAddress(lib, "clap_entry");
#else
    void* lib = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL);
    if (!lib) { std::fprintf(stderr, "dlopen: %s\n", dlerror()); return 1; }
    auto* entry = (const clap_plugin_entry_t*)dlsym(lib, "clap_entry");
#endif
    if (!entry || !entry->init(argv[1])) { std::fprintf(stderr, "no clap_entry\n"); return 1; }
    auto* factory = (const clap_plugin_factory_t*)entry->get_factory(CLAP_PLUGIN_FACTORY_ID);
    const clap_plugin_descriptor_t* desc = factory->get_plugin_descriptor(factory, 0);
    std::printf("plugin: %s (%s) v%s by %s\n", desc->name, desc->id, desc->version, desc->vendor);
    const std::string mode = argv[2];

    Instance inst;
    if (!inst.create(factory, desc->id)) return 1;
    auto* params = (const clap_plugin_params_t*)inst.p->get_extension(inst.p, CLAP_EXT_PARAMS);
    if (params) std::printf("parameters: %u\n", params->count(inst.p));
    // give the background loader time to read the samples
    for (int i = 0; i < 400; ++i) {
        inst.process({}, inst.l.data(), inst.r.data());
        sleepMs(10);
    }

    int rc = 0;
    if (mode == "render") {
        const double secs = argc > 4 ? std::atof(argv[4]) : 5.0;
        const uint32_t total = (uint32_t)(secs * kSr);
        std::vector<float> L(total), R(total);
        struct Ev { uint32_t t; bool on; int key; double vel; };
        std::vector<Ev> evs = {{0, true, 60, 0.7}, {0, true, 64, 0.6}, {0, true, 67, 0.6},
                               {(uint32_t)(1.6 * kSr), false, 60, 0}, {(uint32_t)(1.6 * kSr), false, 64, 0},
                               {(uint32_t)(1.6 * kSr), false, 67, 0}, {(uint32_t)(2.2 * kSr), true, 62, 0.95},
                               {(uint32_t)(2.6 * kSr), false, 62, 0}, {(uint32_t)(2.7 * kSr), true, 65, 0.45},
                               {(uint32_t)(3.1 * kSr), false, 65, 0}};
        if (const char* drums = std::getenv("NML_TEST_DRUMS")) {
            (void)drums;
            evs.clear();
            const int keys[] = {36, 38, 42, 46, 36, 38, 42, 49};
            for (int i = 0; i < 8; ++i) {
                evs.push_back({(uint32_t)(i * 0.4 * kSr), true, keys[i], 0.85});
                evs.push_back({(uint32_t)((i * 0.4 + 0.2) * kSr), false, keys[i], 0});
            }
        }
        size_t e = 0;
        for (uint32_t pos = 0; pos + kBlock <= total; pos += kBlock) {
            std::vector<clap_event_note_t> blockEv;
            while (e < evs.size() && evs[e].t < pos + kBlock) {
                blockEv.push_back(makeNote(evs[e].on, evs[e].t - pos, evs[e].key, evs[e].vel));
                ++e;
            }
            inst.process(blockEv, &L[pos], &R[pos]);
        }
        double peak = 0, sum = 0;
        bool finite = true;
        for (uint32_t i = 0; i < total; ++i) {
            if (!std::isfinite(L[i]) || !std::isfinite(R[i])) finite = false;
            peak = std::max(peak, (double)std::max(std::fabs(L[i]), std::fabs(R[i])));
            sum += (double)L[i] * L[i] + (double)R[i] * R[i];
        }
        const double rms = 10 * std::log10(sum / (2.0 * total) + 1e-12);
        std::printf("render: peak %.1f dBFS, rms %.1f dBFS, finite %s\n", 20 * std::log10(peak + 1e-12), rms,
                    finite ? "yes" : "NO");
        writeWav(argv[3], L, R);
        rc = (finite && peak > 0.01) ? 0 : 1;
    } else if (mode == "state") {
        auto* st = (const clap_plugin_state_t*)inst.p->get_extension(inst.p, CLAP_EXT_STATE);
        Buf buf;
        clap_ostream_t os{&buf, ostreamWrite};
        if (!st || !st->save(inst.p, &os)) { std::fprintf(stderr, "state save failed\n"); return 1; }
        std::printf("state: %zu bytes\n", buf.d.size());
        Instance second;
        if (!second.create(factory, desc->id)) return 1;
        auto* st2 = (const clap_plugin_state_t*)second.p->get_extension(second.p, CLAP_EXT_STATE);
        clap_istream_t is{&buf, istreamRead};
        const bool ok = st2->load(second.p, &is);
        Buf again;
        clap_ostream_t os2{&again, ostreamWrite};
        st2->save(second.p, &os2);
        std::printf("reload: %s, round trip %s\n", ok ? "ok" : "FAILED", again.d == buf.d ? "identical" : "different");
        std::string text(buf.d.begin(), buf.d.end());
        for (auto& ch : text) if (ch == 0) ch = '|';
        std::printf("%.400s\n", text.c_str());
        second.destroy();
        rc = ok ? 0 : 1;
    } else if (mode == "gui") {
        auto* gui = (const clap_plugin_gui_t*)inst.p->get_extension(inst.p, CLAP_EXT_GUI);
        auto* timer = (const clap_plugin_timer_support_t*)inst.p->get_extension(inst.p, CLAP_EXT_TIMER_SUPPORT);
#ifdef _WIN32
        const char* api = CLAP_WINDOW_API_WIN32;
#else
        const char* api = CLAP_WINDOW_API_X11;
#endif
        if (!gui || !gui->is_api_supported(inst.p, api, false) || !gui->create(inst.p, api, false)) {
            std::fprintf(stderr, "gui create failed\n");
            return 1;
        }
        uint32_t w = 0, h = 0;
        gui->get_size(inst.p, &w, &h);
        std::printf("gui: %ux%u\n", w, h);
        clap_window_t win{};
        win.api = api;
#ifdef _WIN32
        WNDCLASSA wc{};
        wc.lpfnWndProc = DefWindowProcA;
        wc.hInstance = GetModuleHandleA(nullptr);
        wc.lpszClassName = "NMLTestHost";
        RegisterClassA(&wc);
        RECT rc2{0, 0, (LONG)w, (LONG)h};
        AdjustWindowRect(&rc2, WS_OVERLAPPEDWINDOW, FALSE);
        HWND hwnd = CreateWindowA("NMLTestHost", "NML test host", WS_OVERLAPPEDWINDOW | WS_VISIBLE, 0, 0,
                                  rc2.right - rc2.left, rc2.bottom - rc2.top, nullptr, nullptr, wc.hInstance, nullptr);
        win.win32 = hwnd;
#else
        Display* dpy = XOpenDisplay(nullptr);
        if (!dpy) { std::fprintf(stderr, "no X display\n"); return 1; }
        Window xw = XCreateSimpleWindow(dpy, DefaultRootWindow(dpy), 0, 0, w, h, 0, 0, 0);
        XMapWindow(dpy, xw);
        XFlush(dpy);
        win.x11 = xw;
#endif
        gui->set_parent(inst.p, &win);
        gui->show(inst.p);

        std::atomic<bool> running{true};
        std::thread audio([&] {
            std::vector<float> L(kBlock), R(kBlock);
            float peak = 0;
            int n = 0;
            while (running) {
                inst.process({}, L.data(), R.data());
                for (uint32_t i = 0; i < kBlock; ++i) peak = std::max(peak, std::max(std::fabs(L[i]), std::fabs(R[i])));
                if (++n % 100 == 0) { std::printf("audio peak %.1f dBFS\n", 20 * std::log10(peak + 1e-9f)); peak = 0; }
                sleepMs(5);
            }
        });
        auto pump = [&](int ms) {
            const double end = nowMs() + ms;
            while (nowMs() < end) {
#ifdef _WIN32
                MSG msg;
                while (PeekMessageA(&msg, nullptr, 0, 0, PM_REMOVE)) { TranslateMessage(&msg); DispatchMessageA(&msg); }
#else
                while (XPending(dpy)) { XEvent ev; XNextEvent(dpy, &ev); }
#endif
                const double t = nowMs();
                for (auto& tm : gTimers)
                    if (t >= tm.next) { tm.next = t + tm.period; if (timer) timer->on_timer(inst.p, tm.id); }
                sleepMs(5);
            }
        };
#ifndef _WIN32
        auto mouse = [&](int x, int y, int button, bool press) {
            XTestFakeMotionEvent(dpy, -1, x, y, 0);
            if (button) XTestFakeButtonEvent(dpy, (unsigned)button, press, 0);
            XFlush(dpy);
        };
#endif
        pump(600);
        for (int i = 3; i < argc; ++i) {
            const std::string cmd = argv[i];
            if (cmd == "wait" && i + 1 < argc) pump(std::atoi(argv[++i]));
            else if (cmd == "note" && i + 3 < argc) {
                const int key = std::atoi(argv[i + 1]); const double vel = std::atoi(argv[i + 2]) / 127.0;
                const int ms = std::atoi(argv[i + 3]); i += 3;
                { std::lock_guard<std::mutex> g(inst.evMutex); inst.queued.push_back(makeNote(true, 0, key, vel)); }
                pump(ms);
                { std::lock_guard<std::mutex> g(inst.evMutex); inst.queued.push_back(makeNote(false, 0, key, 0)); }
            } else if (cmd == "hold" && i + 2 < argc) {
                const int key = std::atoi(argv[i + 1]); const double vel = std::atoi(argv[i + 2]) / 127.0; i += 2;
                std::lock_guard<std::mutex> g(inst.evMutex);
                inst.queued.push_back(makeNote(true, 0, key, vel));
            }
#ifndef _WIN32
            else if (cmd == "click" && i + 2 < argc) {
                const int x = std::atoi(argv[i + 1]), y = std::atoi(argv[i + 2]); i += 2;
                mouse(x, y, 0, false); pump(80); mouse(x, y, 1, true); pump(80); mouse(x, y, 1, false); pump(250);
            } else if (cmd == "drag" && i + 3 < argc) {
                const int x = std::atoi(argv[i + 1]), y = std::atoi(argv[i + 2]), dy = std::atoi(argv[i + 3]); i += 3;
                mouse(x, y, 0, false); pump(80); mouse(x, y, 1, true); pump(60);
                for (int s = 1; s <= 10; ++s) { mouse(x, y + dy * s / 10, 0, false); pump(30); }
                mouse(x, y + dy, 1, false); pump(250);
            } else if (cmd == "wheel" && i + 3 < argc) {
                const int x = std::atoi(argv[i + 1]), y = std::atoi(argv[i + 2]), n = std::atoi(argv[i + 3]); i += 3;
                mouse(x, y, 0, false); pump(60);
                for (int s = 0; s < std::abs(n); ++s) { mouse(x, y, n > 0 ? 4 : 5, true); mouse(x, y, n > 0 ? 4 : 5, false); pump(40); }
                pump(200);
            } else if (cmd == "shot" && i + 1 < argc) {
                pump(300);
                const std::string c = std::string("import -window root ") + argv[++i];
                if (std::system(c.c_str()) != 0) std::fprintf(stderr, "screenshot failed\n");
                else std::printf("screenshot: %s\n", argv[i]);
            }
#endif
        }
        running = false;
        audio.join();
        gui->hide(inst.p);
        gui->destroy(inst.p);
    }
    inst.destroy();
    entry->deinit();
    return rc;
}
