# tools/: the New Movie Library generator

Everything in `New Movie Library/` is produced by this code: the samples, the
Kontakt scripts, the Creator Tools build scripts, the manifest and the
Instrument Guide. Change a recipe or a setting, run one command, and the whole
library is rebuilt consistently.

```bash
pip install -r tools/requirements.txt
python3 tools/build_library.py                    # everything (about 30 s on 4 cores)
python3 tools/build_library.py --only Strings,FX  # re-render some instruments
python3 tools/build_library.py --scripts-only     # only KSP / Lua / docs
python3 tools/qa_report.py [--png OUTDIR]         # audio QA (+ spectrogram sheets)
python3 tools/test_build_scripts.py               # dry-run all Creator Tools scripts
```

## Layout

| File | Purpose |
|---|---|
| `nml/catalog.py` | **The catalog.** Every instrument: groups, zones, key ranges, articulations, keyswitches, drum maps, engine settings and effect defaults. |
| `nml/recipes/` | The synthesis recipes, one function per instrument (`synths.py`, `orchestral.py`, `band.py`, `cinematic.py`). |
| `nml/dsp.py` | DSP toolkit: PolyBLEP oscillators, zero-delay-feedback SVF filters, Karplus-Strong strings with dispersion, modal synthesis, formants, chorus, synthetic reverb IRs, oversampled saturation, loop baking. |
| `nml/wav.py` | 24-bit WAV writer and reader with `smpl` chunk (root key + loop). |
| `nml/ksp_gen.py` | Generates the vanilla-KSP performance script of each instrument (UI pages, effects chain, Performer, engines). |
| `nml/lua_gen.py` | Generates the Creator Tools Lua build script of each instrument. |
| `nml/docs_gen.py` | Generates `Documentation/INSTRUMENT GUIDE.md`. |
| `build_library.py` | Renders, normalizes and writes everything. |
| `qa_report.py` | Checks peaks, DC, pitch, loop seams and tails. |
| `test_build_scripts.py` | Runs every `.lua` build script against a mock Creator Tools API and checks it against the manifest. |

## How the samples are made

- **Pads and synths:** detuned PolyBLEP oscillator stacks rendered at 2x and
  decimated; SVF/ladder-style filtering; chorus and synthetic halls.
- **Choir:** glottal-tilted sources with individual vibrato per singer,
  through vowel formant banks (male/female formants by register).
- **Strings and brass:** ensembles of individually detuned players with
  natural vibrato, bow or lip noise, loudness-dependent brightness and body
  resonances. Pizzicato uses Karplus-Strong strings convolved with a body
  response.
- **Guitar and bass:** extended Karplus-Strong (allpass-tuned, with
  dispersion), pluck-position and pickup comb filtering, body impulse
  responses.
- **EP:** FM tine model with velocity-dependent "bark" from an asymmetric
  pickup non-linearity.
- **Mallets, timpani, metals:** modal synthesis with measured-style mode
  ratios.
- **Drums:** synthesized kick/snare/toms/hats/cymbals (inharmonic partial
  clouds) with velocity layers and round-robin variation.
- **Loops:** sustained samples get loop points chosen by correlation search and
  a crossfade baked into the audio, so they loop seamlessly with no sampler
  crossfade.

All randomness is seeded, so builds are reproducible.

## Script validation

The KSP is plain vanilla KSP. To syntax-check it, the
[SublimeKSP](https://github.com/nojanath/SublimeKSP) compiler works well:

```bash
python3 path/to/sublimeksp/compiler/ksp_compiler.py -e "New Movie Library/Resources/scripts/NML Ensemble Strings.txt" /dev/null
```
