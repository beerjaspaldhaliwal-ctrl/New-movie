#!/usr/bin/env python3
"""Measure every instrument through the plugin engine and store output trims.

    python3 tools/measure_plugin_levels.py

Builds plugin-src/tests/engine_render.cpp, plays the same short test phrase on every
instrument at default settings, and writes tools/nml/plugin_levels.json: one gain
(dB) per instrument that brings the phrase to a common loudness without pushing
its peaks into the limiter. Then regenerates the plugin catalog so the trims are
compiled in. Needs g++ and the rendered samples.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PLUGIN = os.path.join(ROOT, "plugin-src")
LIBRARY = os.path.join(ROOT, "New Movie Library")
OUT = os.path.join(HERE, "nml", "plugin_levels.json")

TARGET_RMS = -18.0   # dBFS, test phrase at master 0 dB
PEAK_CEIL = -1.0     # dBFS, keep the phrase out of the safety limiter
MIN_GAIN, MAX_GAIN = -9.0, 18.0


def main():
    with tempfile.TemporaryDirectory() as tmp:
        exe = os.path.join(tmp, "engine_render")
        src = ["tests/engine_render.cpp", "src/engine/Engine.cpp", "src/engine/Catalog.cpp",
               "src/engine/Samples.cpp", "src/generated/catalog_data.cpp"]
        subprocess.run(["g++", "-std=c++17", "-O2", "-Isrc", "-Ithird_party", *src, "-o", exe, "-ldl"],
                       cwd=PLUGIN, check=True)
        res = subprocess.run([exe, LIBRARY, "all"], env=dict(os.environ, NML_MEASURE="1"),
                             capture_output=True, text=True)
    levels = {}
    for line in res.stdout.splitlines():
        if not line.startswith("LEVEL "):
            continue
        _, key, peak, rms = line.split()
        peak, rms = float(peak), float(rms)
        gain = min(TARGET_RMS - rms, PEAK_CEIL - peak)
        levels[key] = round(max(MIN_GAIN, min(MAX_GAIN, gain)), 1)
        print(f"{key:15s} peak {peak:6.1f}  rms {rms:6.1f}  ->  trim {levels[key]:+5.1f} dB")
    if not levels:
        sys.exit("no measurements - is the library rendered?\n" + res.stdout + res.stderr)
    with open(OUT, "w") as f:
        json.dump(levels, f, indent=1, sort_keys=True)
        f.write("\n")
    print(f"wrote {OUT}")
    subprocess.run([sys.executable, os.path.join(HERE, "build_library.py"), "--scripts-only"], check=True)


if __name__ == "__main__":
    main()
