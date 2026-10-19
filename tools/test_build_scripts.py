#!/usr/bin/env python3
"""Dry-run every Creator Tools build script against a mock of the Creator
Tools Lua API (needs `pip install lupa`), and check the resulting instrument
against the manifest: group names, zone count, mapping, loops, sample paths
and the attached KSP script.

    python3 tools/test_build_scripts.py
"""
import glob
import json
import os
import sys

try:
    from lupa import lua54 as lupa_mod
except ImportError:  # older lupa
    import lupa as lupa_mod

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LIB = os.path.join(ROOT, "New Movie Library")

MOCK = r'''
function Vector(factory)
  local v = {items = {}, factory = factory}
  local mt = {}
  mt.__index = function(t, k)
    if type(k) == "number" then return rawget(t, "items")[k + 1] end
    return rawget(VectorMethods, k)
  end
  mt.__len = function(t) return #rawget(t, "items") end
  return setmetatable(v, mt)
end
VectorMethods = {
  add = function(self, obj) table.insert(self.items, obj) end,
  remove = function(self, i) table.remove(self.items, i + 1) end,
  resize = function(self, n)
    while #self.items < n do table.insert(self.items, self.factory()) end
    while #self.items > n do table.remove(self.items) end
  end,
  reset = function(self) self.items = {}; if self.factory == MakeGroup then table.insert(self.items, MakeGroup()) end end,
}
function MakeLoop() return {mode = 0, start = 0, length = 0, xfade = 0} end
function Zone()
  return {file = "", rootKey = 60, keyRange = {low = 0, high = 127}, velocityRange = {low = 1, high = 127},
          loops = Vector(MakeLoop)}
end
function MakeGroup() return {name = "", playbackMode = 0, zones = Vector(Zone)} end
Group = MakeGroup
PlaybackMode = {Sampler = 1, DirectFromDisk = 2}
function MakeScript() return {name = "", sourceCode = "", bypass = true} end
'''


def run(lua_path, with_scripts_vector):
    L = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    L.execute(MOCK)
    g = L.globals()
    fs = L.table()
    fs.parentPath = lambda p: os.path.dirname(p.rstrip("/\\"))
    fs.preferred = lambda p: p.replace("\\", "/")
    fs.exists = lambda p: os.path.exists(p)
    g.filesystem = fs
    g.scriptPath = os.path.dirname(lua_path) + "/"
    inst = L.eval("{groups = Vector(MakeGroup)}")
    L.execute("function _setup(inst, vec) inst.groups:reset(); if vec then inst.scripts = Vector(MakeScript); "
              "inst.scripts:resize(5) else inst.script = MakeScript() end end")
    g._setup(inst, with_scripts_vector)
    g.instrument = inst
    out = []
    g.print = lambda *a: out.append(" ".join(str(x) for x in a))
    with open(lua_path, encoding="utf-8") as f:
        L.execute(f.read())
    return L, inst, out


def items(L, vec):
    """Python list from a mock vector (lupa's len()/[] bypass Lua metatables)."""
    n = L.eval("function(v) return #v end")(vec)
    get = L.eval("function(v, i) return v[i] end")
    return [get(vec, i) for i in range(n)]


def main():
    man = json.load(open(os.path.join(LIB, "Documentation", "manifest.json")))
    by_name = {i["name"]: i for i in man["instruments"]}
    failures = 0
    for path in sorted(glob.glob(os.path.join(LIB, "Creator Tools", "Build *.lua"))):
        name = os.path.basename(path)[6:-4]
        spec = by_name[name]
        for vec in (True, False):
            L, inst, out = run(path, vec)
            groups = items(L, inst.groups)
            names = [gr.name for gr in groups]
            want = [gr["name"] for gr in spec["groups"]]
            errs = []
            if names != want:
                errs.append(f"groups {names} != {want}")
            for gr, sg in zip(groups, spec["groups"]):
                zones = items(L, gr.zones)
                if len(zones) != len(sg["zones"]):
                    errs.append(f"{gr.name}: {len(zones)} zones, expected {len(sg['zones'])}")
                for z, sz in zip(zones, sg["zones"]):
                    if not os.path.exists(z.file):
                        errs.append("missing " + z.file)
                    if (z.rootKey, z.keyRange.low, z.keyRange.high) != (sz["root"], sz["lo"], sz["hi"]):
                        errs.append(f"mapping mismatch {z.file}")
                    if sz["loop"]:
                        lp = items(L, z.loops)[0]
                        if (lp.mode, lp.start, lp.start + lp.length) != (1, sz["loop"][0], sz["loop"][1]):
                            errs.append(f"loop mismatch {z.file}")
                    elif items(L, z.loops):
                        errs.append(f"unexpected loop {z.file}")
            script = items(L, inst.scripts)[0] if vec else inst.script
            if "on init" not in script.sourceCode or script.bypass:
                errs.append("script not attached")
            if any("MISSING" in o or "WARNING" in o for o in out):
                errs.append("script printed warnings: " + "; ".join(out))
            status = "OK " if not errs else "FAIL"
            failures += bool(errs)
            nz = sum(len(items(L, gr.zones)) for gr in groups)
            print(f"{status} {name:26s} {'scripts[]' if vec else 'script  '} {len(groups):2d} groups {nz:4d} zones")
            for e in errs[:5]:
                print("     ", e)
    print(f"{failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
