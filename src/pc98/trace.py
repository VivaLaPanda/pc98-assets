"""trace: a generated (or any) reference -> an exact pixel grid you can then edit by hand.

1. find the subject (alpha, or flood the background in from the borders);
2. crop to it and either
   - snap to the pixel grid the image already has (generated "pixel art" is drawn in uneven blocks: we find the block
     period from the edges and take each cell's median), or
   - box-resample it to fit `size`;
3. quantize to a palette with optional ordered dither;
4. write the grid as ASCII (for hand editing) plus a scaled-up preview.

The output is a draft. Tracing gets composition and proportions; the outline, shading and every pixel that matters
are redrawn by hand afterwards (see assets/*/draw.py).
"""
from collections import deque

import numpy as np
from PIL import Image

from . import palette as P
from .pixel import Grid


def subject_mask(img, tol=40):
    """Opaque where the subject is: alpha if present, else everything not connected to the border background."""
    im = img.convert('RGBA')
    a = np.asarray(im).astype(np.int32)
    if (a[..., 3] < 250).mean() > 0.01:
        return a[..., 3] >= 128
    rgb = a[..., :3]
    h, w = rgb.shape[:2]
    border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    bg = np.median(border, axis=0)
    near = (np.abs(rgb - bg).sum(-1) <= tol)
    seen = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if near[y, x] and not seen[y, x]:
                seen[y, x] = True; q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if near[y, x] and not seen[y, x]:
                seen[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= ny < h and 0 <= nx < w and near[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True; q.append((ny, nx))
    return ~seen


def block_period(img, lo=4, hi=80):
    """Estimate the size of the 'pixels' in an upscaled pixel-art image from where colour changes happen.
    Returns (period, x_phase, y_phase, score); score near 1 means a clean grid, near 0 means no grid."""
    a = np.asarray(img.convert('RGB')).astype(np.int32)
    gx = (np.abs(np.diff(a, axis=1)).sum(-1) > 30).sum(0)    # per column boundary
    gy = (np.abs(np.diff(a, axis=0)).sum(-1) > 30).sum(1)
    best = (0, 0, 0, 0.0)
    for p in np.arange(lo, hi + 1, 0.25):
        def fit(g):
            if g.sum() == 0:
                return 0, 0.0
            pos = np.arange(len(g)) + 1.0          # diff i is the boundary at x = i + 1
            z = (g * np.exp(2j * np.pi * pos / p)).sum()
            return (np.angle(z) / (2 * np.pi) * p) % p, np.abs(z) / g.sum()
        px, sx = fit(gx)
        py, sy = fit(gy)
        s = min(sx, sy)
        if s > best[3] + 0.02:       # prefer the smallest period that fits about as well
            best = (p, px, py, s)
    return best


def snap(img, period, px=0.0, py=0.0):
    """Sample an upscaled pixel-art image at its cell centres (median of the inner half of each cell)."""
    a = np.asarray(img.convert('RGBA'))
    h, w = a.shape[:2]
    xs = np.arange(px % period, w, period)
    ys = np.arange(py % period, h, period)
    out = np.zeros((len(ys) - 1, len(xs) - 1, 4), np.uint8)
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            x0, x1 = xs[i] + period * .25, xs[i] + period * .75
            y0, y1 = ys[j] + period * .25, ys[j] + period * .75
            cell = a[int(y0):max(int(y1), int(y0) + 1), int(x0):max(int(x1), int(x0) + 1)].reshape(-1, 4)
            out[j, i] = np.median(cell, axis=0)
    return Image.fromarray(out, 'RGBA')


def trace(path, size=48, legend='vga', dither=None, mode='auto', pad=0, tol=40, min_score=0.6):
    """Returns (Grid, info). mode: 'auto', 'snap' (find the image's own pixel grid) or 'fit' (resample to size)."""
    img = Image.open(path).convert('RGBA')
    m = subject_mask(img, tol)
    ys, xs = np.nonzero(m)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    rgba = np.asarray(img).copy()
    rgba[~m, 3] = 0
    img = Image.fromarray(rgba, 'RGBA').crop((x0, y0, x1 + 1, y1 + 1))
    info = {'bbox': (int(x0), int(y0), int(x1), int(y1))}
    period = None
    if mode in ('auto', 'snap'):
        p, ph_x, ph_y, s = block_period(img)
        info.update(period=float(p), score=round(float(s), 3))
        if mode == 'snap' or s >= min_score:
            period = p
    if period:
        small = snap(img, period, ph_x, ph_y)
        info['mode'] = 'snap'
    else:
        inner = size - 2 * pad
        k = inner / max(img.size)
        small = img.resize((max(1, round(img.width * k)), max(1, round(img.height * k))), Image.BOX)
        info['mode'] = 'fit'
    if max(small.size) > size:   # a snapped grid larger than the canvas: fit it
        k = size / max(small.size)
        small = small.resize((max(1, round(small.width * k)), max(1, round(small.height * k))), Image.BOX)
    g = Grid.from_image(small, legend, dither=dither)
    canvas = Grid(size, size)
    canvas.paste(g, (size - g.w) // 2, (size - g.h) // 2)
    info['grid'] = (g.w, g.h)
    return canvas, info
