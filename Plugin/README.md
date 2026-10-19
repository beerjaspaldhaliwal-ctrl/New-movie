# New Movie Library player plugin (VST3 / CLAP)

A free-standing instrument plugin that plays the **New Movie Library** directly in
any DAW (Ableton Live, FL Studio, Cubase, Reaper, Studio One, Bitwig and others). It needs no Kontakt.
All 45 instruments, their articulations, effects, Performer and presets work
the same way as in the Kontakt version.

| Folder | Contents |
|---|---|
| `Windows/` | `New Movie Library Setup.exe` (setup wizard), `NewMovieLibrary.vst3`, `NewMovieLibrary.clap`, `Install.bat`, `Uninstall.bat` (64-bit Windows 10/11) |
| `Linux/` | `NewMovieLibrary.vst3`, `NewMovieLibrary.clap` (x86-64) |

## Install on Windows

1. Download the whole repository (**Code > Download ZIP** on GitHub) and unzip it.
   Keep the `New Movie Library` and `Plugin` folders side by side.
2. Open `Plugin\Windows` and double-click **`New Movie Library Setup.exe`**.
   Allow the administrator prompt, because the plugin folders are system folders.
3. Follow the wizard:
   - **Components:** the VST3 plugin, the CLAP plugin, and *Copy the samples*.
   - **Sample folder:** where the 470 MB of samples go. The default is
     `Documents\New Movie Library`, but any drive works. If you untick *Copy the samples*,
     the plugin uses them straight from the download folder.
   - The VST3 goes to `C:\Program Files\Common Files\VST3\` and the CLAP to
     `C:\Program Files\Common Files\CLAP\`.
   - The plugin remembers where the samples are.
4. In your DAW, rescan plugins and add **New Movie Library** as an instrument.

If Windows shows *"Windows protected your PC"*, choose **More info > Run anyway**. The setup
isn't code-signed, so Windows warns about any downloaded program like this.
To remove everything, use **Settings > Apps > New Movie Library > Uninstall**. It asks
before deleting the samples.

`Install.bat` / `Uninstall.bat` do the same job as a plain script, if you prefer that.

### Manual install (instead of the setup)

- Copy the folder `NewMovieLibrary.vst3` into `C:\Program Files\Common Files\VST3\`.
- Copy `NewMovieLibrary.clap` into `C:\Program Files\Common Files\CLAP\` if your DAW
  supports CLAP (Bitwig, Reaper, FL Studio 2024+, Studio One 7).
- Put the `New Movie Library` folder in your **Documents** folder, or anywhere you like.
  If it's somewhere else, the plugin asks for it the first time it opens.

### Uninstall

Run `Uninstall.bat`. It removes the plugin files and the saved sample location.
Your samples are left in place.

## Install on Linux

Copy `NewMovieLibrary.vst3` to `~/.vst3/` and/or `NewMovieLibrary.clap` to `~/.clap/`.
Put the `New Movie Library` folder in `~/Documents` or point the plugin at it.

## Finding the samples

The plugin looks for the `New Movie Library` folder (the one that contains `Samples`)
in this order:

1. The location you picked in the plugin, or that `Install.bat` saved, kept in
   `%APPDATA%\NewMovieLibrary\library_path.txt`.
2. The `NML_LIBRARY_PATH` environment variable.
3. Next to the plugin file, or a few folders above it.
4. `Documents\New Movie Library`, `Desktop`, `Downloads`, and `C:\`, `D:\`, `E:\`.

If it finds nothing, the plugin shows **Find the sample library**. Type or paste the
folder path, or press **Browse...** and pick any file inside the library folder,
such as `README.md` or any `.wav`. The choice is remembered for every project.

## Using the plugin

![Plugin window](../docs/plugin.png)

- **Browser (left):** the five categories. Click one to open it, then click an
  instrument to load it. Search finds names and descriptions.
  Loading a new instrument resets its controls to that instrument's own defaults.
- **Preset (top):** each instrument's presets. Use the arrows to step through them.
  *Default* resets every control.
- **PLAY / SOUND / PERFORM pages:** the same controls as the Kontakt version.
  [CONTROLS.md](../New%20Movie%20Library/Documentation/CONTROLS.md) explains them all.
  - Drag a knob up or down to turn it; hold **Shift** to fine-tune.
  - Double-click a knob to reset it.
  - The mouse wheel also turns knobs.
  - Hover over any control to see what it does in the help line.
- **Keyboard (bottom):** click to play.
  - Blue keys are the playable range.
  - Red keys are articulation keyswitches; the active one is gold.
  - On drum kits, each piece is colored by its mixer bus.
  - Keys light up while notes play.
- **Master** knob and level meters (top right). Instruments are level-matched, so
  switching between them doesn't jump in volume.
- All controls appear in your DAW as automatable parameters. Mod wheel (CC1),
  expression (CC11), sustain (CC64) and pitch bend work as in Kontakt.
- The DAW project saves the instrument, every control and the sample location.

Each loaded instrument uses between 1 and 80 MB of RAM. Samples load in the
background, shown as a progress bar in the browser and "Loading..." at the top of the panel.

## Building it yourself

The source is in [`plugin-src/`](../plugin-src). It is built with
[DPF](https://github.com/DISTRHO/DPF) and [Dear ImGui](https://github.com/ocornut/imgui).

```bash
sh tools/build_plugin.sh            # Linux + Windows (cross-compiled with mingw-w64)
```

- **Linux:** needs `g++`, `make`, `libgl1-mesa-dev`, `libx11-dev`, `libxcursor-dev`,
  `libxrandr-dev` and `libdbus-1-dev`.
- **Windows:** cross-compiled with the `x86_64-w64-mingw32-g*-posix` compilers.
- **macOS:** run `make` in `plugin-src/` on a Mac with the Xcode command-line tools.
  That build is untested.

**What was tested:** both Linux builds and the Windows CLAP build load in a
minimal CLAP test host (`plugin-src/tests/clap_host.cpp`, the Windows build under
Wine). Each one played every instrument, saved and restored its state, opened its
window, and had its tabs, browser and keyboard clicked. The Linux VST3 was also
loaded in a JUCE-based host (Spotify's `pedalboard`), which checked rendering and
parameter automation. Two offline engine tests run clean under Valgrind:
`plugin-src/tests/engine_render.cpp` plays all 45 instruments, and `engine_features.cpp`
runs 24 behaviour checks. Those cover arpeggiator and Note Repeat timing against the host
clock, strum, scale lock, pedal, glide, legato, keyswitches, mic faders, mode switches while
notes are held, loop seams, and no stuck voices on any instrument. The plugin was also checked
for correct pitch at 44.1, 48 and 96 kHz. **Not tested:** the Windows VST3
in a real DAW, because no Windows DAW was available here. If a DAW
misbehaves, note the DAW, its version and what happened.

## Licenses

The plugin code is ISC-licensed. It includes:

- DPF (ISC)
- Dear ImGui and the DPF-Widgets glue (MIT)
- dr_wav (public domain / MIT-0)
- the DejaVu Sans font (Bitstream Vera license)

Their license files are next to their sources in `plugin-src/`.
