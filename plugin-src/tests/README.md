# Plugin tests

Run from `plugin-src/`. They need the rendered library in `../New Movie Library`.

```bash
LIB="../New Movie Library"
ENGINE="src/engine/Engine.cpp src/engine/Catalog.cpp src/engine/Samples.cpp src/generated/catalog_data.cpp"

# every instrument through the engine: levels, missing samples, NaNs (optionally writes WAVs)
g++ -std=c++17 -O2 -Isrc -Ithird_party tests/engine_render.cpp $ENGINE -o /tmp/engine_render -ldl
/tmp/engine_render "$LIB" all [out_dir]

# behaviour: arpeggiator, Note Repeat, strum, scale lock, pedal, glide, legato, keyswitches, mics,
# all-notes-off and stuck voices on all 45 instruments
g++ -std=c++17 -O2 -Isrc -Ithird_party tests/engine_features.cpp $ENGINE -o /tmp/engine_features -ldl
/tmp/engine_features "$LIB"

# a minimal CLAP host for the built plugin: render, state round trip, or open the editor
g++ -std=c++17 -O2 -Idpf/distrho/src tests/clap_host.cpp -o /tmp/clap_host -ldl -lpthread -lX11 /usr/lib/x86_64-linux-gnu/libXtst.so.6
NML_LIBRARY_PATH="$PWD/$LIB" /tmp/clap_host ../Plugin/Linux/NewMovieLibrary.clap render /tmp/out.wav
/tmp/clap_host ../Plugin/Linux/NewMovieLibrary.clap state
/tmp/clap_host ../Plugin/Linux/NewMovieLibrary.clap gui click 398 96 wait 500 shot /tmp/sound_page.png
```

`clap_host.cpp` also cross-compiles for Windows (`x86_64-w64-mingw32-g++-posix ... -static -lgdi32 -luser32`)
to test `Plugin/Windows/NewMovieLibrary.clap` under Wine.
