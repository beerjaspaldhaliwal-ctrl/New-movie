"""Instrument wallpapers (one per category), drawn procedurally.

Kontakt: 800 x 398 px PNG = the 800 x 330 px performance view plus the 68 px
instrument header. Set it in Instrument Options > Instrument > Wallpaper.
Decent Sampler: 812 x 375 px backgrounds used by the .dspreset files.
The artwork is kept dark and low-contrast so the knobs stay readable.
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .library import CATEGORIES

GOLD = (222, 182, 92)
FONT_PATHS = ["/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
ACCENT = {
    "01 Synths and Pads": (70, 190, 210),
    "02 Orchestral": (222, 182, 92),
    "03 Band and Keys": (210, 120, 80),
    "04 Cinematic": (200, 70, 60),
    "05 World": (120, 190, 110),
}


def _font(size):
    for p in FONT_PATHS:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def _base(w, h, seed):
    rng = np.random.default_rng(seed)
    y = np.linspace(0, 1, h)[:, None]
    x = np.linspace(0, 1, w)[None, :]
    top, bot = np.array([16, 17, 22]), np.array([27, 29, 36])
    img = top[None, None, :] * (1 - y[..., None]) + bot[None, None, :] * y[..., None]
    img = img + 0 * x[..., None]
    vign = 1 - 0.35 * (((x - 0.5) * 1.4) ** 2 + ((y - 0.45) * 1.8) ** 2)
    img = img * vign[..., None]
    img = img + rng.normal(0, 2.2, img.shape)  # film grain
    return img


def _overlay(img, layer, color, alpha):
    """Blend a grey-scale mask (0..1) in a colour."""
    return img * (1 - alpha * layer[..., None]) + np.array(color)[None, None, :] * alpha * layer[..., None]


def _motif(cat, w, h, seed):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    m = np.zeros((h, w))
    if cat == "01 Synths and Pads":  # layered waveforms
        for k in range(7):
            f = 1.5 + k * 0.7
            ph = rng.uniform(0, 6.28)
            amp = 28 + k * 9
            yc = h * 0.62 + amp * np.sin(xx[0] / w * f * 6.283 + ph) * np.sin(xx[0] / w * 3.14)
            m += np.exp(-((yy - yc[None, :]) ** 2) / (2 * (1.2 + k * 0.25) ** 2)) * (0.9 - k * 0.09)
    elif cat == "02 Orchestral":  # concert-hall arcs
        cx, cy = w * 0.78, h * 1.25
        r = np.hypot(xx - cx, yy - cy)
        for k in range(12):
            m += np.exp(-((r - (180 + k * 34)) ** 2) / (2 * 1.3 ** 2)) * (0.85 - k * 0.05)
        th = np.arctan2(yy - cy, xx - cx)
        m *= 0.55 + 0.45 * (np.cos(th * 18) > 0.6)
    elif cat == "03 Band and Keys":  # keyboard silhouette and strings
        kw = w / 52
        for i in range(53):
            m += np.exp(-((xx - i * kw) ** 2) / 1.2) * (yy > h * 0.80)
        for i in range(52):
            if i % 7 in (0, 1, 3, 4, 5):
                x0 = (i + 0.68) * kw
                m += ((xx > x0) & (xx < x0 + kw * 0.62) & (yy > h * 0.80) & (yy < h * 0.91)) * 0.8
        for k in range(6):  # guitar strings
            yc = h * 0.30 + k * 9 + 0.04 * (xx - w * 0.5)
            m += np.exp(-((yy - yc) ** 2) / 1.0) * 0.6 * (xx > w * 0.45)
    elif cat == "04 Cinematic":  # film strip and anamorphic flare
        for row in (h * 0.10, h * 0.90):
            band = np.abs(yy - row) < 14
            holes = (np.abs(((xx + 6) % 28) - 14) < 6) & (np.abs(yy - row) < 6)
            m += band * 0.35 - holes * 0.35
        m += np.exp(-((yy - h * 0.52) ** 2) / (2 * 2.0 ** 2)) * np.exp(-((xx - w * 0.68) ** 2) / (2 * 260 ** 2)) * 1.4
        m += np.exp(-(((xx - w * 0.68) ** 2) + (yy - h * 0.52) ** 2) / (2 * 30 ** 2)) * 1.2
    else:  # World: mandala
        cx, cy = w * 0.80, h * 0.56
        r = np.hypot(xx - cx, yy - cy)
        th = np.arctan2(yy - cy, xx - cx)
        for k, rad in enumerate((60, 95, 135, 180, 230)):
            m += np.exp(-((r - rad) ** 2) / (2 * 1.2 ** 2)) * 0.8
            petals = 8 + 4 * k
            m += np.exp(-((r - rad - 12 * np.cos(th * petals)) ** 2) / (2 * 1.0 ** 2)) * 0.45
        dots = (np.hypot(((xx % 22) - 11), ((yy % 22) - 11)) < 1.4) * 0.25
        m += dots * (r > 250)
    return np.clip(m, -1, 1.5)


def wallpaper(cat, w, h, seed=11, title=True):
    img = _base(w, h, seed)
    m = _motif(cat, w, h, seed)
    img = _overlay(img, np.clip(m, 0, 1.5) * 0.55, ACCENT[cat], 0.22)
    img = np.clip(img, 0, 255).astype(np.uint8)
    pil = Image.fromarray(img, "RGB")
    glow = pil.filter(ImageFilter.GaussianBlur(6))
    pil = Image.blend(pil, glow, 0.25)
    d = ImageDraw.Draw(pil)
    d.line([(0, 0), (w, 0)], fill=GOLD, width=2)
    d.line([(0, h - 2), (w, h - 2)], fill=tuple(int(c * 0.5) for c in GOLD), width=2)
    if title:
        name = cat.split(" ", 1)[1].upper()
        f1, f2 = _font(15), _font(11)
        tw = d.textlength("NEW MOVIE LIBRARY", font=f2)
        d.text((w - 18 - tw, h - 44), "NEW MOVIE LIBRARY", font=f2, fill=tuple(int(c * 0.8) for c in GOLD))
        tw = d.textlength(name, font=f1)
        d.text((w - 18 - tw, h - 30), name, font=f1, fill=(150, 154, 166))
    return pil


def export(lib_dir):
    out = os.path.join(lib_dir, "Resources", "pictures")
    os.makedirs(out, exist_ok=True)
    n = 0
    for cat in CATEGORIES:
        short = cat.split(" ", 1)[1]
        wallpaper(cat, 800, 398).save(os.path.join(out, f"NML Wallpaper - {short}.png"), optimize=True)
        bg = wallpaper(cat, 812, 375, title=False)
        bg = Image.blend(bg, Image.new("RGB", bg.size, (18, 19, 24)), 0.35)
        bg.save(os.path.join(out, f"NML Decent Sampler - {short}.png"), optimize=True)
        n += 2
    return n
