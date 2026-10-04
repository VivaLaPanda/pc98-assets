"""Start a piece from a real picture: its 16 inks and index map, so a painting can be added to it in the same medium.

The site's library images are often resampled copies of PC-98 screens with thousands of colours. `quantize` recovers
a 16-ink frame the way the panda-room scout did: a median-cut start refined by k-means, snapped onto the 4096-colour
grid, every pixel mapped to its nearest ink with no dithering (PC-98 art places its dither by hand).
"""
from pathlib import Path

import numpy as np
from PIL import Image

from pc98.config import ROOT, SITE


def resolve(path):
    """A path as given, or relative to the site's img/, or to this repo."""
    p = Path(path)
    for c in (p, SITE / 'img' / p, ROOT / p):
        if c.exists():
            return c
    raise FileNotFoundError(path)


def quantize(path, n=16, iters=12):
    """(index map uint8 HxW, ['#rgb'] * n) for a real image."""
    src = Image.open(resolve(path)).convert('RGB')
    pal_img = src.quantize(colors=n, method=Image.MEDIANCUT, dither=Image.NONE)
    pal = np.array(pal_img.getpalette()[:n * 3], dtype=float).reshape(n, 3)
    px = np.asarray(src).reshape(-1, 3).astype(float)
    for _ in range(iters):
        lab = ((px[:, None] - pal[None]) ** 2).sum(-1).argmin(1)
        for k in range(n):
            if (lab == k).any():
                pal[k] = px[lab == k].mean(0)
    pal = np.round(pal / 17) * 17
    a = np.asarray(src).astype(float)
    idx = ((a[..., None, :] - pal[None, None]) ** 2).sum(-1).argmin(-1).astype(np.uint8)
    hexes = ['#%x%x%x' % tuple(int(v) // 17 for v in c) for c in pal]
    return idx, hexes
