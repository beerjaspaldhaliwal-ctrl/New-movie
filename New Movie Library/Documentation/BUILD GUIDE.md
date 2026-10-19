# New Movie Library: Build Guide

Kontakt instruments (`.nki`) are a Kontakt-only file format, so this library
ships everything an instrument needs: the samples, mapping, loops and scripts.
Kontakt assembles them into `.nki` files once. After that you load them like
any other library.

You need Kontakt 8 (7.10 or newer also works) and Creator Tools, which installs
with Kontakt. Building all 21 instruments takes about 20 minutes.

---

## Method A: Creator Tools (recommended, fully automatic)

Repeat for each instrument:

1. **Create an empty instrument.** In Kontakt, double-click the empty rack area
   (or choose *File > New instrument*).
2. **Connect Creator Tools.** Start Creator Tools. In the **Instrument Editor**
   (F2), pick the new instrument from the drop-down at the top.
3. **Run the build script.** Open the **Lua Script** panel (Shift+F3) and load
   `New Movie Library/Creator Tools/Build <Instrument>.lua` (double-click it in
   the file browser, or drag it in). Press **Run** (Ctrl/Cmd+R). The console
   prints something like
   `Ensemble Strings: 84 zones in 7 groups. Performance script attached.`
4. **Push.** Press **Push** (Ctrl/Cmd+Alt+Up) to send the result to Kontakt.
5. **Check the script.** Click the instrument header in Kontakt. The
   performance view (PLAY / SOUND / PERFORM) should appear. If it doesn't,
   open *Script Editor*, select slot 1 and press **Apply**.
6. **Save.** Choose *File > Save as...* and save to
   `New Movie Library/Instruments/<Category>/<Instrument>.nki`.
   Choose **Patch only** and leave *absolute sample paths* off, so the library
   keeps working when you move the folder.

The script builds the effects chain (filter, width, chorus, delay, reverb...)
the first time it runs. It's then saved inside the `.nki`.

### Which script for which file

| Build script | Save as |
|---|---|
| `Build Warm Analog Pad.lua` | `Instruments/01 Synths and Pads/Warm Analog Pad.nki` |
| `Build Glass Shimmer Pad.lua` | `Instruments/01 Synths and Pads/Glass Shimmer Pad.nki` |
| `Build Supersaw Stack.lua` | `Instruments/01 Synths and Pads/Supersaw Stack.nki` |
| `Build Analog Mono Bass.lua` | `Instruments/01 Synths and Pads/Analog Mono Bass.nki` |
| `Build Pluck Synth.lua` | `Instruments/01 Synths and Pads/Pluck Synth.nki` |
| `Build Pulse Arp.lua` | `Instruments/01 Synths and Pads/Pulse Arp.nki` |
| `Build Ethereal Choir.lua` | `Instruments/01 Synths and Pads/Ethereal Choir.nki` |
| `Build Ensemble Strings.lua` | `Instruments/02 Orchestral and Band/Ensemble Strings.nki` |
| `Build Brass Ensemble.lua` | `Instruments/02 Orchestral and Band/Brass Ensemble.nki` |
| `Build Woodwind Ensemble.lua` | `Instruments/02 Orchestral and Band/Woodwind Ensemble.nki` |
| `Build Cinematic Timpani.lua` | `Instruments/02 Orchestral and Band/Cinematic Timpani.nki` |
| `Build Electric Piano.lua` | `Instruments/02 Orchestral and Band/Electric Piano.nki` |
| `Build Nylon Guitar.lua` | `Instruments/02 Orchestral and Band/Nylon Guitar.nki` |
| `Build Finger Bass.lua` | `Instruments/02 Orchestral and Band/Finger Bass.nki` |
| `Build Studio Drum Kit.lua` | `Instruments/02 Orchestral and Band/Studio Drum Kit.nki` |
| `Build Drawbar Organ.lua` | `Instruments/02 Orchestral and Band/Drawbar Organ.nki` |
| `Build Cinematic Mallets.lua` | `Instruments/02 Orchestral and Band/Cinematic Mallets.nki` |
| `Build Orchestral Percussion.lua` | `Instruments/02 Orchestral and Band/Orchestral Percussion.nki` |
| `Build Braams and Hits.lua` | `Instruments/03 Cinematic/Braams and Hits.nki` |
| `Build Drones and Textures.lua` | `Instruments/03 Cinematic/Drones and Textures.nki` |
| `Build Cinematic FX.lua` | `Instruments/03 Cinematic/Cinematic FX.nki` |

---

## Method B: by hand, without Creator Tools

Every instrument can also be built in Kontakt's own editors. The
[Instrument Guide](INSTRUMENT%20GUIDE.md) and `manifest.json` list the groups
and zones.

1. Create an empty instrument and open **Edit** mode (wrench icon).
2. **Groups.** In the Group Editor, create one group per sample folder and name
   it **exactly** like the folder (for example `SusP`, `SusF`, `StacRR1`). The
   script finds groups by name, so the names must match; their order doesn't
   matter. In each group's Source module choose **Sampler** mode.
3. **Samples.** Select one group, then drag all WAVs from its folder
   (`Samples/<Category>/<Instrument>/<Group>/`) into the Mapping Editor.
4. **Auto-map.** With the new zones selected, open *Edit > Auto-map: Setup*.
   File names look like `Strings_SusP_069_067_071_001_127.wav`. Set token 3 =
   *Root Key*, token 4 = *Low Key*, token 5 = *High Key*, token 6 = *Low
   Velocity*, token 7 = *High Velocity* and the others to *Ignore*. Then run
   *Auto-map selected*. Repeat steps 3-4 for every group.
5. **Loops.** Loop points are embedded in the WAV files, and Kontakt reads them
   on import. If a sustained sound stops instead of holding, open the Loop
   Editor and check that loop 1 is set to **Until End** (no crossfade needed:
   it's baked into the audio).
6. **Script.** Open the *Script Editor*, select slot 1, paste the contents of
   `Resources/scripts/NML <Instrument>.txt` and press **Apply**.
7. Save as described in Method A, step 6.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Creator Tools prints `MISSING SAMPLE` | The `.lua` file must stay inside `New Movie Library/Creator Tools`. It finds the samples relative to its own folder. On Windows, avoid paths with non-English characters (a Creator Tools limitation). |
| Status bar shows `NML: group not found: ...` | A group was renamed or not created. Rebuild with the Lua script, or rename the group to match exactly. |
| No sound, but keys light up | Check that the script in slot 1 is applied, and that you aren't playing a keyswitch (red keys). |
| Sustained notes stop after ~2 seconds | Loops aren't enabled. Set loop 1 to *Until End* (Method B, step 5). |
| Effects missing | Re-apply the script once: it re-creates the effects chain in the instrument insert slots. |
| "Content missing" when reopening | The library folder moved and the instrument was saved with absolute paths. Use *Browse for folder* and point Kontakt to `New Movie Library`, then re-save. |

If the script editor reports an error, note the error text and the instrument
name. The scripts are generated by `tools/nml/ksp_gen.py`, so one fix there
updates all of them.
