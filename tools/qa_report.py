#!/usr/bin/env python3
"""Quality checks for the rendered library.

    python3 tools/qa_report.py [--png OUTDIR]

Checks every sample listed in the manifest for clipping, DC offset, pitch
accuracy (pitched instruments), loop seam continuity and clean tails, and
optionally renders spectrogram sheets for visual inspection.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from nml.wav import read_wav24  # noqa: E402
from nml.library import LIB_NAME  # noqa: E402

LIB = os.path.join(os.path.dirname(HERE), LIB_NAME)
UNPITCHED = {"Drums", "OrchPerc", "FX", "Timpani", "Drones", "Braams", "SynthwaveKit", "TrapKit", "TrailerPerc",
             "SciFi", "TensionKit", "DarkAtmos", "ElecGuitar", "Gamelan"}
REVERSED = {"ReverseSwells"}  # end on purpose at the peak of the swell


def f0_error_cents(x, root, sr):
    m = x.mean(axis=1)
    n = min(m.size, 1 << 16)
    seg = m[m.size // 5: m.size // 5 + n] if m.size > n * 1.3 else m[:n]
    seg = seg * np.hanning(seg.size)
    N = 1 << 19
    X = np.abs(np.fft.rfft(seg, N))
    fr = np.fft.rfftfreq(N, 1 / sr)
    f0 = 440 * 2 ** ((root - 69) / 12)
    band = (fr > f0 * 0.97) & (fr < f0 * 1.03)
    if not band.any():
        return None
    fpk = fr[band][np.argmax(X[band])]
    return 1200 * np.log2(fpk / f0)


def loop_seam(x, loop):
    s, e = loop
    jump = np.abs(x[s] - x[e - 1])
    d = np.abs(np.diff(x[s:e], axis=0))
    typical = np.percentile(d, 99, axis=0) + 1e-9
    return float(np.max(jump / typical))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--png", default="")
    args = ap.parse_args()
    man = json.load(open(os.path.join(LIB, "Documentation", "manifest.json")))
    problems = 0
    for inst in man["instruments"]:
        peaks, worst_seam, worst_pitch, dc = [], 0.0, 0.0, 0.0
        sheet = []
        for g in inst["groups"]:
            for z in g["zones"]:
                info = read_wav24(os.path.join(LIB, z["file"]))
                x = info["audio"]
                sr = info["sr"]
                pk = float(np.max(np.abs(x)))
                peaks.append(pk)
                dc = max(dc, float(np.max(np.abs(x.mean(axis=0)))))
                if z["loop"]:
                    assert tuple(info["loop"]) == tuple(z["loop"]), (z["file"], info.get("loop"), z["loop"])
                    worst_seam = max(worst_seam, loop_seam(x, z["loop"]))
                elif inst["key"] not in REVERSED:
                    tail = float(np.max(np.abs(x[-int(0.005 * sr):])))
                    if tail > 0.01:
                        print(f"  ! {z['file']}: tail not silent ({tail:.3f})")
                        problems += 1
                if inst["key"] not in UNPITCHED:
                    err = f0_error_cents(x, z["root"], sr)
                    if err is not None:
                        worst_pitch = max(worst_pitch, abs(err))
                if pk > 0.95:
                    print(f"  ! {z['file']}: peak {pk:.3f}")
                    problems += 1
                if len(sheet) < 6 and z is g["zones"][len(g["zones"]) // 2]:
                    sheet.append((g["name"], x, sr))
        print(f"{inst['name']:26s} peak max {20 * np.log10(max(peaks)):6.1f} dBFS  "
              f"DC {dc:.4f}  loop seam {worst_seam:5.2f}x  pitch err {worst_pitch:5.1f} c")
        if worst_seam > 3.0:
            print("  ! loop seam larger than 3x the typical sample step")
            problems += 1
        if args.png and sheet:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            fig, axs = plt.subplots(len(sheet), 1, figsize=(10, 2.2 * len(sheet)), squeeze=False)
            for ax, (name, x, sr) in zip(axs[:, 0], sheet):
                ax.specgram(x.mean(axis=1), NFFT=2048, Fs=sr, noverlap=1536, cmap="magma", vmin=-140)
                ax.set_ylim(0, 16000)
                ax.set_title(f"{inst['name']} / {name}", fontsize=8)
            fig.tight_layout()
            os.makedirs(args.png, exist_ok=True)
            fig.savefig(os.path.join(args.png, inst["key"] + ".png"), dpi=70)
            plt.close(fig)
    print(f"{problems} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
