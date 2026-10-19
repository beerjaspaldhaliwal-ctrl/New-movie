"""Instrument / group / zone specifications shared by the renderer, the KSP
script generator and the Creator Tools (Lua) build-script generator."""
from dataclasses import dataclass, field

LIB_NAME = "New Movie Library"
LIB_SHORT = "NML"

CAT_SYNTH = "01 Synths and Pads"
CAT_ORCH = "02 Orchestral and Band"
CAT_CINE = "03 Cinematic"

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note_name(m):
    """Kontakt convention: C3 = MIDI 60."""
    return f"{NOTE_NAMES[m % 12]}{m // 12 - 2}"


@dataclass
class Zone:
    group: str
    root: int
    lo: int
    hi: int
    vlo: int = 1
    vhi: int = 127
    seed: int = 0
    p: dict = field(default_factory=dict)  # recipe parameters (piece, layer, rr, length ...)
    # filled in by the renderer
    file: str = ""
    frames: int = 0
    loop: tuple = None


@dataclass
class Instrument:
    key: str            # short id, used in file names (no spaces)
    name: str           # display / .nki name
    category: str
    engine: str         # synth | artic | keys | drums
    recipe: str         # recipe function name in nml.recipes
    zones: list
    channels: int = 2
    norm: str = "rms"   # rms (sustained) | peak (percussive)
    level_db: float = -16.0
    cfg: dict = field(default_factory=dict)  # engine configuration for the KSP generator
    blurb: str = ""
    samples_from: str = ""  # reuse another instrument's samples (no rendering)

    @property
    def groups(self):
        seen = []
        for z in self.zones:
            if z.group not in seen:
                seen.append(z.group)
        return seen


def keymap(roots, lo_ext, hi_ext):
    """Split the keyboard between roots: each root covers up to the midpoint
    to its neighbours; the outer zones stretch to lo_ext / hi_ext."""
    roots = sorted(roots)
    out = []
    for i, r in enumerate(roots):
        lo = lo_ext if i == 0 else (roots[i - 1] + r) // 2 + 1
        hi = hi_ext if i == len(roots) - 1 else (r + roots[i + 1]) // 2
        out.append((r, lo, hi))
    return out


def zones_for(groups, roots, lo_ext, hi_ext, seed_base=0, **p):
    zs = []
    for gi, g in enumerate(groups):
        for zi, (r, lo, hi) in enumerate(keymap(roots, lo_ext, hi_ext)):
            zs.append(Zone(g, r, lo, hi, seed=seed_base + gi * 1000 + zi, p=dict(p)))
    return zs
