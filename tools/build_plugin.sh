#!/bin/sh
# Builds the player plugin (VST3 + CLAP) for Linux and Windows and copies the
# results into Plugin/Linux and Plugin/Windows.
#
#   sh tools/build_plugin.sh            # both
#   sh tools/build_plugin.sh windows    # Windows only (needs the mingw-w64 "posix" compilers)
#   sh tools/build_plugin.sh linux      # Linux only (needs libgl1-mesa-dev, libx11-dev, libxcursor-dev, libxrandr-dev, libdbus-1-dev)
#
# Each target builds in its own temporary copy of plugin-src/, so the two never share objects.
set -e
ROOT=$(cd "$(dirname "$0")/.." && pwd)
TARGETS=${1:-linux windows}
JOBS=$(nproc 2>/dev/null || echo 4)

build() {
    target=$1; shift
    tmp=$(mktemp -d)
    (cd "$ROOT/plugin-src" && tar cf - --exclude=./build --exclude=./bin --exclude=./dpf/build .) | (cd "$tmp" && tar xf -)
    echo "== building $target in $tmp"
    make -C "$tmp" -j"$JOBS" "$@" >"$tmp/build.log" 2>&1 || { tail -40 "$tmp/build.log"; exit 1; }
    out="$ROOT/Plugin/$target"
    rm -rf "$out/NewMovieLibrary.vst3" "$out/NewMovieLibrary.clap"
    mkdir -p "$out"
    cp -r "$tmp/bin/NewMovieLibrary.vst3" "$tmp/bin/NewMovieLibrary.clap" "$out/"
    rm -rf "$tmp"
    echo "   -> $out"
}

for t in $TARGETS; do
    case $t in
        linux) build Linux ;;
        windows) build Windows WINDOWS=true CC=x86_64-w64-mingw32-gcc-posix CXX=x86_64-w64-mingw32-g++-posix \
                     AR=x86_64-w64-mingw32-ar
                 # the setup wizard (needs NSIS: apt install nsis)
                 if command -v makensis >/dev/null; then
                     makensis -V2 "$ROOT/plugin-src/installer/NewMovieLibrary.nsi" && echo "   -> Plugin/Windows/New Movie Library Setup.exe"
                 else
                     echo "   (makensis not found: setup wizard not rebuilt)"
                 fi ;;
        *) echo "unknown target $t"; exit 2 ;;
    esac
done
