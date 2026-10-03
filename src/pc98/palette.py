"""Palettes as legends (one character per colour), extraction from the site's art, and quantization.

A legend maps a single character to an RGB tuple; '.' is always transparent. Grids (pixel.py) store characters, so the
same drawing can be written out in any palette that shares its letters, and recolouring is a character mapping.

SITE  the frame's own palette: img/background-frame.png (a 640x400 PC-98 screen, shown at 2x) has exactly these 13
      colours. Every channel is a multiple of 0x11: it is a real PC-98 palette, 16 colours picked from the machine's
      4096 (4 bits per channel). Every _recolor icon is drawn from it. Mnemonic letters, so ASCII grids read well.
      Three of the 16 slots are free; EXTRA holds candidates (a deep teal close to the one the globe recolour used).
VGA   the Windows 98 16-colour palette the site's *original* icons (img/icons/*.png without _recolor) are drawn in.
      Not PC-98 (0x80 and 0xC0 aren't 4-bit levels): it exists so new icons can have an original in the same
      convention as the old ones. What's shown on the site is always SITE.

PC-98 is a palette discipline, not "pixel art": 16 colours per picture from a 12-bit space, gradients and textures
made from ordered dither patterns (the 50% checkerboard above all, never error diffusion), and anime illustration
drawn at 640x400. snap12() and pick16() enforce the first part; quantize(dither=...) the second.
"""
from collections import Counter
from pathlib import Path
import json

import numpy as np
from PIL import Image

T = '.'   # transparent

VGA = {
    'K': (0x00, 0x00, 0x00),  # black
    'r': (0x80, 0x00, 0x00),  # maroon
    'd': (0x00, 0x80, 0x00),  # dark green
    'o': (0x80, 0x80, 0x00),  # olive
    'n': (0x00, 0x00, 0x80),  # navy
    'p': (0x80, 0x00, 0x80),  # purple
    't': (0x00, 0x80, 0x80),  # teal
    'S': (0xC0, 0xC0, 0xC0),  # silver
    'G': (0x80, 0x80, 0x80),  # gray
    'R': (0xFF, 0x00, 0x00),  # red
    'g': (0x00, 0xFF, 0x00),  # lime
    'y': (0xFF, 0xFF, 0x00),  # yellow
    'B': (0x00, 0x00, 0xFF),  # blue
    'm': (0xFF, 0x00, 0xFF),  # magenta
    'c': (0x00, 0xFF, 0xFF),  # cyan
    'W': (0xFF, 0xFF, 0xFF),  # white
}

SITE = {
    'K': (0x00, 0x00, 0x00),  # black: outlines
    'W': (0xFF, 0xFF, 0xFF),  # white: highlights
    'p': (0x88, 0x99, 0xFF),  # periwinkle: the main body colour of every recoloured icon
    'u': (0x66, 0x44, 0x77),  # plum: shadow, and the light-side outline
    'a': (0xBB, 0xAA, 0xBB),  # mauve grey: half-light
    'b': (0x11, 0x33, 0xBB),  # royal blue (the frame's window borders)
    'k': (0xFF, 0xAA, 0xBB),  # pink
    'h': (0xFF, 0x00, 0x66),  # hot pink
    'y': (0xFF, 0xEE, 0x55),  # yellow
    'e': (0xFF, 0xAA, 0x77),  # peach
    'n': (0xCC, 0x88, 0x44),  # tan
    'r': (0x99, 0x44, 0x22),  # rust brown
    'm': (0x00, 0xEE, 0xBB),  # mint: the sidebar's background, so use it sparingly inside icons
}

# Candidates for the frame palette's three free slots (12-bit). The globe recolour used #007f64, which isn't 12-bit.
EXTRA = {
    't': (0x00, 0x77, 0x66),  # deep teal
}

# VGA letter -> SITE letter, as the existing recolours do it most of the time (cd_audio, envelope, globe). It is a
# starting point: each icon's recolour was chosen by hand, so an asset passes its own overrides (see recolor()).
VGA_TO_SITE = {
    'K': 'K', 'W': 'W', 'S': 'p', 'G': 'u', 'y': 'y', 'c': 'm', 'g': 'k', 'o': 'n', 'd': 't', 'm': 'k',
    'p': 'h', 't': 'u', 'n': 'b', 'B': 'b', 'r': 'r', 'R': 'h',
}

LEGENDS = {'vga': VGA, 'site': SITE, 'site+': {**SITE, **EXTRA}}


def snap12(rgb):
    """Nearest PC-98 colour: each channel to a multiple of 0x11."""
    return tuple(int(round(v / 17.0)) * 17 for v in rgb[:3])


def is_pc98(legend, max_colors=16):
    """(ok, problems): every colour 12-bit, and no more than 16 of them."""
    bad = [f'{k} {hexs(v)}' for k, v in legend.items() if snap12(v) != tuple(v[:3])]
    probs = ([f'not 12-bit: {", ".join(bad)}'] if bad else []) + \
            ([f'{len(legend)} colours > {max_colors}'] if len(legend) > max_colors else [])
    return not probs, probs


def pick16(img, n=16, keep=None):
    """Choose an n-colour 12-bit palette for an image (PIL median cut, then snap12, deduplicated), optionally keeping
    some fixed colours (e.g. the frame's black and white). The pc98ify step for scenes; icons use SITE as is."""
    keep = [tuple(c) for c in (keep or [])]
    im = img.convert('RGB')
    q = im.quantize(colors=max(1, n - len(keep)), method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[:3 * (n - len(keep))]
    cols = keep + [snap12(pal[i:i + 3]) for i in range(0, len(pal), 3)]
    out = []
    for c in cols:
        if c not in out:
            out.append(c)
    return legend_from_counts(Counter({c: len(out) - i for i, c in enumerate(out)}), n)


def get(name_or_legend):
    if isinstance(name_or_legend, dict):
        return name_or_legend
    if name_or_legend in LEGENDS:
        return LEGENDS[name_or_legend]
    p = Path(name_or_legend)
    if p.suffix == '.json' and p.exists():
        return {k: tuple(v) for k, v in json.loads(p.read_text()).items()}
    raise KeyError(f'unknown palette {name_or_legend!r} (vga, site, or a legend .json)')


def hexs(rgb):
    return '#%02x%02x%02x' % tuple(rgb[:3])


def extract(paths, alpha_min=128):
    """Count every opaque colour across images. Returns a Counter of RGB tuples."""
    c = Counter()
    for p in paths:
        im = Image.open(p).convert('RGBA')
        a = np.asarray(im).reshape(-1, 4)
        a = a[a[:, 3] >= alpha_min][:, :3]
        c.update(map(tuple, a.tolist()))
    return c


def legend_from_counts(counts, max_colors=16):
    """Give the most common colours single-character names (a-z then A-Z), most common first."""
    names = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJLMNOPQRSUVXYZ'
    return {names[i]: rgb for i, (rgb, _) in enumerate(counts.most_common(max_colors))}


def swatch(legend, path, cell=48, cols=8, counts=None):
    """A labelled swatch image of a legend."""
    from PIL import ImageDraw
    from .config import font
    items = list(legend.items())
    rows = (len(items) + cols - 1) // cols
    im = Image.new('RGB', (cols * cell * 2, rows * (cell + 26)), (24, 24, 24))
    d = ImageDraw.Draw(im)
    f = font(12)
    for i, (k, rgb) in enumerate(items):
        x, y = (i % cols) * cell * 2, (i // cols) * (cell + 26)
        d.rectangle([x + 4, y + 4, x + cell * 2 - 4, y + cell], fill=tuple(rgb))
        lab = f'{k} {hexs(rgb)}' + (f' {counts[tuple(rgb)]}' if counts else '')
        d.text((x + 4, y + cell + 6), lab, fill=(230, 230, 230), font=f)
    im.save(path)
    return path


# ---- quantization ----------------------------------------------------------------------------------------------

BAYER2 = np.array([[0, 2], [3, 1]]) / 4.0
BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
CHECKER = np.array([[0, 1], [1, 0]]) / 2.0 + 0.25   # 50% only: the Windows 98 / PC-98 checkerboard


def _arr(legend):
    keys = list(legend.keys())
    return keys, np.array([legend[k] for k in keys], dtype=np.float32)


def quantize(img, legend, dither=None, spread=48.0, alpha_min=128):
    """RGB(A) image -> 2D array of legend characters ('.' where transparent).

    dither: None (nearest colour), 'checker', 'bayer2' or 'bayer4' (ordered dithering: each pixel is nudged by its
    threshold times `spread` before choosing the nearest colour; spread ~ the gap between neighbouring palette
    colours). Ordered dither keeps the patterns regular, which is what PC-98 art does; error diffusion would not.
    """
    legend = get(legend)
    im = img.convert('RGBA')
    a = np.asarray(im).astype(np.float32)
    rgb, alpha = a[..., :3], a[..., 3]
    if dither:
        m = {'checker': CHECKER, 'bayer2': BAYER2, 'bayer4': BAYER4}[dither]
        h, w = alpha.shape
        th = np.tile(m, (h // m.shape[0] + 1, w // m.shape[1] + 1))[:h, :w]
        rgb = rgb + ((th - 0.5) * spread)[..., None]
    keys, pal = _arr(legend)
    # perceptual-ish weighting (redmean would be nicer; this is enough for 16 colours)
    wts = np.array([0.3, 0.59, 0.11], dtype=np.float32) * 3
    d = (((rgb[..., None, :] - pal[None, None]) ** 2) * wts).sum(-1)
    idx = d.argmin(-1)
    out = np.array(keys, dtype='<U1')[idx]
    out[alpha < alpha_min] = T
    return out


def nearest_char(rgb, legend):
    keys, pal = _arr(get(legend))
    return keys[int((((pal - np.array(rgb[:3], dtype=np.float32)) ** 2).sum(-1)).argmin())]
