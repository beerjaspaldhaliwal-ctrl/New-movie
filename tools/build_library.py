#!/usr/bin/env python3
"""Build the New Movie Library.

    python3 tools/build_library.py              # render everything
    python3 tools/build_library.py --only Strings,Brass
    python3 tools/build_library.py --scripts-only   # regenerate KSP + Lua + docs

Renders every sample (24-bit / 44.1 kHz WAV with embedded root + loop),
writes the Kontakt performance scripts (KSP), the Creator Tools build scripts
(Lua) and a manifest describing every zone.
"""
import argparse
import importlib
import json
import multiprocessing as mp
import os
import shutil
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from nml import dsp  # noqa: E402
from nml.catalog import CATALOG, BY_KEY  # noqa: E402
from nml.library import LIB_NAME, note_name  # noqa: E402
from nml import ksp_gen, lua_gen  # noqa: E402
from nml.wav import write_wav24, read_wav24  # noqa: E402

ROOT = os.path.dirname(HERE)
LIB = os.path.join(ROOT, LIB_NAME)
PEAK_CEIL_DB = -1.0


def sample_rel(inst, z):
    name = f"{inst.key}_{z.group}_{z.root:03d}_{z.lo:03d}_{z.hi:03d}_{z.vlo:03d}_{z.vhi:03d}.wav"
    return "/".join(["Samples", inst.category, inst.name, z.group, name])


def _render_job(args):
    key, idx = args
    inst = BY_KEY[key]
    z = inst.zones[idx]
    mod, fn = inst.recipe.rsplit(".", 1)
    recipe = getattr(importlib.import_module("nml.recipes." + mod), fn)
    audio, loop = recipe(z)
    audio = np.asarray(audio, dtype=np.float64)
    if inst.channels == 1:
        audio = dsp.mono(audio)
    elif audio.ndim == 1:
        audio = dsp.stereo(audio)
    if not np.all(np.isfinite(audio)):
        raise RuntimeError(f"{key} zone {idx}: non-finite samples")
    # remove DC: a constant offset keeps baked loops seamless, one-shots get a 12 Hz high-pass
    if loop:
        audio = audio - audio[loop[0]:loop[1]].mean(axis=0)
    else:
        audio = dsp.dc_block(audio)
    return idx, audio, loop


def _level(audio, loop, norm):
    if norm == "rms":
        seg = audio[loop[0]:loop[1]] if loop else audio
        return dsp.rms(seg)
    return dsp.peak(audio)


def render_instrument(inst, pool):
    t0 = time.time()
    jobs = [(inst.key, i) for i in range(len(inst.zones))]
    results = {}
    for idx, audio, loop in pool.imap_unordered(_render_job, jobs):
        results[idx] = (audio, loop)
    # per-zone normalisation, then one common gain so the loudest peak sits at the ceiling
    target = dsp.db(inst.level_db if inst.norm == "rms" else -1.0)
    gains = {}
    for idx, (audio, loop) in results.items():
        gains[idx] = target / (_level(audio, loop, inst.norm) + 1e-12)
    top = max(dsp.peak(results[i][0]) * gains[i] for i in results)
    common = min(1.0, dsp.db(PEAK_CEIL_DB) / top)
    total_bytes = 0
    for idx, z in enumerate(inst.zones):
        audio, loop = results[idx]
        audio = audio * gains[idx] * common
        rel = sample_rel(inst, z)
        path = os.path.join(LIB, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        write_wav24(path, audio, dsp.SR, root=z.root, loop=loop)
        z.file, z.frames, z.loop = rel, audio.shape[0], (tuple(int(v) for v in loop) if loop else None)
        total_bytes += os.path.getsize(path)
    print(f"  {inst.name:28s} {len(inst.zones):4d} zones  {total_bytes / 1e6:6.1f} MB  {time.time() - t0:5.1f}s",
          flush=True)
    return total_bytes


def load_existing(inst):
    """Fill zone file/frames/loop from samples already on disk."""
    for z in inst.zones:
        rel = sample_rel(BY_KEY[inst.samples_from] if inst.samples_from else inst, z)
        path = os.path.join(LIB, *rel.split("/"))
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        info = read_wav24(path)
        z.file, z.frames, z.loop = rel, info["audio"].shape[0], info.get("loop")


def write_scripts(insts):
    sdir = os.path.join(LIB, "Resources", "scripts")
    ldir = os.path.join(LIB, "Creator Tools")
    os.makedirs(sdir, exist_ok=True)
    os.makedirs(ldir, exist_ok=True)
    for inst in insts:
        ksp = ksp_gen.generate(inst)
        sname = f"NML {inst.name}.txt"
        with open(os.path.join(sdir, sname), "w", newline="\n") as f:
            f.write(ksp)
        lua = lua_gen.generate(inst, ksp, sname)
        with open(os.path.join(ldir, f"Build {inst.name}.lua"), "w", newline="\n") as f:
            f.write(lua)


def write_manifest(insts):
    data = {"library": LIB_NAME, "sample_rate": dsp.SR, "bit_depth": 24, "instruments": []}
    for inst in insts:
        data["instruments"].append({
            "key": inst.key, "name": inst.name, "category": inst.category, "engine": inst.engine,
            "nki": f"Instruments/{inst.category}/{inst.name}.nki",
            "script": f"Resources/scripts/NML {inst.name}.txt",
            "build_script": f"Creator Tools/Build {inst.name}.lua",
            "description": inst.blurb,
            "groups": [{"name": g, "zones": [{
                "file": z.file, "root": z.root, "root_name": note_name(z.root), "lo": z.lo, "hi": z.hi,
                "vel": [z.vlo, z.vhi], "frames": z.frames, "loop": list(z.loop) if z.loop else None}
                for z in inst.zones if z.group == g]} for g in inst.groups],
        })
    path = os.path.join(LIB, "Documentation", "manifest.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n") as f:
        json.dump(data, f, indent=1)


def write_extras():
    """Convolution IRs for Kontakt's Convolution effect, and the instruments folder skeleton."""
    from nml.recipes.common import hall_ir
    irdir = os.path.join(LIB, "Resources", "ir_samples")
    os.makedirs(irdir, exist_ok=True)
    for name, secs, seed, pre in [("NML Scoring Stage", 2.2, 401, 0.018), ("NML Chamber", 1.1, 402, 0.008),
                                  ("NML Cathedral", 5.5, 403, 0.035), ("NML Plate", 1.8, 404, 0.0)]:
        ir = hall_ir(secs, seed, pre)
        ir = ir / (dsp.peak(ir) + 1e-12) * dsp.db(-3)
        write_wav24(os.path.join(irdir, name + ".wav"), ir, dsp.SR)
    for cat in sorted({i.category for i in CATALOG}):
        d = os.path.join(LIB, "Instruments", cat)
        os.makedirs(d, exist_ok=True)
        names = [i.name for i in CATALOG if i.category == cat]
        with open(os.path.join(d, "SAVE NKI FILES HERE.txt"), "w", newline="\n") as f:
            f.write("Save the instruments for this category here (see Documentation/BUILD GUIDE):\n\n")
            f.write("\n".join(f"  {n}.nki" for n in names) + "\n")


def write_formats(insts):
    """SFZ + Decent Sampler versions, the MIDI phrase pack and the wallpapers."""
    from nml import artwork, formats, midi_pack
    for sub in ("SFZ", "Decent Sampler", "MIDI"):
        shutil.rmtree(os.path.join(LIB, sub), ignore_errors=True)
    counts = formats.export(insts, LIB)
    n_mid = midi_pack.export(LIB)
    n_pic = artwork.export(LIB)
    os.makedirs(os.path.join(LIB, "Multis"), exist_ok=True)
    with open(os.path.join(LIB, "Multis", "SAVE MULTIS HERE.txt"), "w", newline="\n") as f:
        f.write("Save Kontakt multis (.nkm) here. Documentation/MULTIS AND MIDI.md lists ready-made combinations.\n")
    print(f"{counts['SFZ']} SFZ files, {counts['Decent Sampler']} Decent Sampler presets, {n_mid} MIDI files, "
          f"{n_pic} pictures")


def write_docs(insts):
    from nml.docs_gen import instrument_guide
    sizes = {}
    for inst in insts:
        if inst.samples_from:
            continue
        d = os.path.join(LIB, "Samples", inst.category, inst.name)
        sizes[inst.key] = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(d) for f in fs)
    path = os.path.join(LIB, "Documentation", "INSTRUMENT GUIDE.md")
    with open(path, "w", newline="\n") as f:
        f.write(instrument_guide(insts, sizes))
    from nml.docs_gen import build_guide, multis_and_midi
    from nml import midi_pack
    with open(os.path.join(LIB, "Documentation", "BUILD GUIDE.md"), "w", newline="\n") as f:
        f.write(build_guide(insts))
    with open(os.path.join(LIB, "Documentation", "MULTIS AND MIDI.md"), "w", newline="\n") as f:
        f.write(multis_and_midi(insts, midi_pack.build()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="comma-separated instrument keys to render")
    ap.add_argument("--scripts-only", action="store_true", help="do not render audio, reuse samples on disk")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    args = ap.parse_args()
    only = {k.strip() for k in args.only.split(",") if k.strip()}

    print(f"{LIB_NAME} -> {LIB}")
    total = 0
    t0 = time.time()
    if not args.scripts_only:
        with mp.get_context("fork").Pool(args.jobs) as pool:
            for inst in CATALOG:
                if inst.samples_from:
                    continue
                if only and inst.key not in only:
                    continue
                gdir = os.path.join(LIB, "Samples", inst.category, inst.name)
                if os.path.isdir(gdir):
                    shutil.rmtree(gdir)
                total += render_instrument(inst, pool)
        print(f"rendered {total / 1e6:.1f} MB in {time.time() - t0:.0f}s")
    for inst in CATALOG:
        if not inst.zones[0].file:
            load_existing(inst)
    write_scripts(CATALOG)
    write_manifest(CATALOG)
    write_extras()
    write_formats(CATALOG)
    write_docs(CATALOG)
    from nml import plugin_gen
    n, p, size = plugin_gen.export(CATALOG, os.path.join(ROOT, "plugin-src", "src", "generated"))
    print(f"plugin catalog: {n} instruments, {p} host parameters, {size / 1024:.0f} KB")
    print("scripts, build scripts, manifest and extras written")


if __name__ == "__main__":
    main()
