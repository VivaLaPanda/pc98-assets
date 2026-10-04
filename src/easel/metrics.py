"""Measures that separate professional PC-98 art from flat modern pixel art.

Measured on the site's genuine PC-98 interiors (Oct 2026) against our rejected room art:

                  thinline  edge   checker  flat   black
  pro interiors   .07-.21   .46-.75 .07-.32 .13-.46 varies (night scenes .25-.66)
  rejected room   .024      .37    .05     .47

thinline: share of 1px lines (a pixel darker or lighter than both its neighbours across it), i.e.
          how much line art and bevel-light there is. The rejected art had 4-8x too little.
edge:     share of pixels whose right or lower neighbour differs: detail density.
checker:  share of pixels in a 50% checkerboard (differs from its 4 neighbours, equals diagonals).
flat:     share of pixels equal to all 8 neighbours: big untextured areas.
black:    share of near-black pixels.
"""

from pathlib import Path

import numpy as np
from PIL import Image

from pc98.config import SITE

REFS = ['explore/places/night_musician_bedroom.png', 'explore/places/commandcenter.png',
        'explore/places/bedroom.png', 'explore/places/day_bedroom.png', 'explore/places/conbini.png',
        'explore/places/day_bedroom_cluttered.png', 'explore/places/night_cafe.png']

KEYS = ['colours', 'thinline', 'edge', 'checker', 'flat', 'black']


def measure(rgb):
    a = np.asarray(rgb)[..., :3].astype(np.int64)
    if a.shape[0] < 3 or a.shape[1] < 3:
        return {k: 0 for k in KEYS}
    k = a[..., 0] * 65536 + a[..., 1] * 256 + a[..., 2]
    L = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    c = k[1:-1, 1:-1]
    nb = [k[:-2, :-2], k[:-2, 1:-1], k[:-2, 2:], k[1:-1, :-2], k[1:-1, 2:], k[2:, :-2], k[2:, 1:-1], k[2:, 2:]]
    flat = np.all([c == n for n in nb], axis=0)
    chk = ((c != k[:-2, 1:-1]) & (c != k[2:, 1:-1]) & (c != k[1:-1, :-2]) & (c != k[1:-1, 2:])
           & (c == k[:-2, :-2]) & (c == k[2:, 2:]))
    Lc = L[1:-1, 1:-1]
    dark = ((Lc + 50 < L[1:-1, :-2]) & (Lc + 50 < L[1:-1, 2:])) | ((Lc + 50 < L[:-2, 1:-1]) & (Lc + 50 < L[2:, 1:-1]))
    light = ((Lc - 50 > L[1:-1, :-2]) & (Lc - 50 > L[1:-1, 2:])) | ((Lc - 50 > L[:-2, 1:-1]) & (Lc - 50 > L[2:, 1:-1]))
    # a 1px line, not a checkerboard: exclude pixels that are part of a checker
    thin = (dark | light) & ~chk
    edge = ((k[:, 1:] != k[:, :-1])[:-1, :] | (k[1:, :] != k[:-1, :])[:, :-1])
    return {
        'colours': int(len(np.unique(k))),
        'thinline': float(thin.mean()),
        'edge': float(edge.mean()),
        'checker': float(chk.mean()),
        'flat': float(flat.mean()),
        'black': float((a.max(axis=2) <= 0x22).mean()),
    }


_cache = {}


def reference_ranges(paths=None):
    paths = paths or REFS
    key = tuple(paths)
    if key in _cache:
        return _cache[key]
    rows = []
    for p in paths:
        f = Path(p) if Path(p).is_absolute() else SITE / 'img' / p
        if f.exists():
            rows.append(measure(np.asarray(Image.open(f).convert('RGB'))))
    rng = {k: (min(r[k] for r in rows), max(r[k] for r in rows)) for k in KEYS} if rows else {}
    _cache[key] = rng
    return rng


def report(m, rng):
    out = []
    for k in KEYS:
        v = m[k]
        if k in rng:
            lo, hi = rng[k]
            flag = '' if lo <= v <= hi else ('  LOW' if v < lo else '  HIGH')
            fmt = (lambda x: f'{x}') if k == 'colours' else (lambda x: f'{x:.3f}')
            out.append(f'{k:9} {fmt(v):>6}   pro {fmt(lo)}..{fmt(hi)}{flag}')
        else:
            out.append(f'{k:9} {v}')
    return out
