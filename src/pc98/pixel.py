"""Exact pixel grids, drawn in code.

A Grid is a 2D array of palette characters ('.' = transparent). Shapes are boolean masks (rect, ellipse, poly, line)
so they can be combined, filled, dithered and edged; ASCII patches place pixels by hand. Nothing here resamples or
anti-aliases: what you draw is what ships.

    from pc98.pixel import Grid, rect, ellipse, poly, line
    g = Grid(48, 48)
    body = rect(g, 8, 10, 39, 41)
    g.fill(body, 'S')
    g.dither(rect(g, 8, 30, 39, 41), 'S', 'G')          # 50% checkerboard
    g.edge(body, 'K', 'br'); g.edge(body, 'G', 'tl')     # Windows 98 outline: dark below/right, grey above/left
    g.patch(20, 14, '''
        KK.
        KWK
    ''')                                                # '.' leaves a pixel alone, '_' clears it
    g.save('out/icon.png', 'vga')
"""
import textwrap
from pathlib import Path

import numpy as np
from PIL import Image

from . import palette as P

T = '.'


class Grid:
    def __init__(self, w, h=None, fill=T):
        h = w if h is None else h
        self.a = np.full((h, w), fill, dtype='<U1')

    # ---- construction / io ----
    @classmethod
    def parse(cls, text):
        """ASCII art -> Grid. Rows are lines; common indentation and blank edge lines are removed."""
        lines = [l.rstrip() for l in textwrap.dedent(text).strip('\n').splitlines()]
        w = max(len(l) for l in lines)
        g = cls(w, len(lines))
        for y, l in enumerate(lines):
            for x, ch in enumerate(l.ljust(w, T)):
                g.a[y, x] = T if ch == ' ' else ch
        return g

    @classmethod
    def load(cls, path):
        return cls.parse(Path(path).read_text())

    @classmethod
    def from_image(cls, img, legend, dither=None):
        """An image already on (or near) a palette -> Grid. Off-palette colours go to the nearest entry."""
        g = cls(1, 1)
        g.a = P.quantize(img if isinstance(img, Image.Image) else Image.open(img), legend, dither=dither)
        return g

    def copy(self):
        g = Grid(1, 1)
        g.a = self.a.copy()
        return g

    def __str__(self):
        return '\n'.join(''.join(r) for r in self.a)

    def dump(self, path):
        Path(path).write_text(str(self) + '\n')

    @property
    def w(self):
        return self.a.shape[1]

    @property
    def h(self):
        return self.a.shape[0]

    def image(self, legend):
        legend = P.get(legend)
        out = np.zeros((self.h, self.w, 4), dtype=np.uint8)
        missing = set(np.unique(self.a)) - set(legend) - {T}
        if missing:
            raise KeyError(f'characters not in palette: {sorted(missing)}')
        for k, rgb in legend.items():
            out[self.a == k] = (*rgb[:3], 255)
        return Image.fromarray(out, 'RGBA')

    def save(self, path, legend, mode='RGBA'):
        """mode 'RGBA' (like the site's _recolor icons) or 'P' (indexed, transparency at index 0, like the originals)."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        im = self.image(legend)
        if mode == 'P':
            legend = P.get(legend)
            used = [k for k in legend if (self.a == k).any()]
            pal = [(255, 0, 255)] + [legend[k][:3] for k in used]
            idx = np.zeros((self.h, self.w), dtype=np.uint8)
            for i, k in enumerate(used, 1):
                idx[self.a == k] = i
            im = Image.fromarray(idx, 'P')
            im.putpalette([c for rgb in pal for c in rgb])
            im.save(path, transparency=0)
        else:
            im.save(path)
        return path

    # ---- pixels ----
    def __getitem__(self, xy):
        x, y = xy
        return self.a[y, x]

    def __setitem__(self, xy, c):
        x, y = xy
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y, x] = c

    def mask(self, chars=None):
        """Where the grid is opaque (or is one of `chars`)."""
        return self.a != T if chars is None else np.isin(self.a, list(chars))

    def fill(self, m, c):
        self.a[m] = c
        return self

    def clear(self, m):
        self.a[m] = T
        return self

    def dither(self, m, c1, c2, phase=0, pattern='checker'):
        """Fill a mask with an ordered pattern of two colours. 'checker' (50%), 'h' / 'v' (alternate rows /
        columns), 'q1' (25%: c2 on one pixel in four) and 'q3' (75%). phase shifts the pattern by a pixel."""
        yy, xx = np.mgrid[0:self.h, 0:self.w]
        if pattern == 'checker':
            sel = (xx + yy + phase) % 2 == 1
        elif pattern == 'h':
            sel = (yy + phase) % 2 == 1
        elif pattern == 'v':
            sel = (xx + phase) % 2 == 1
        elif pattern in ('q1', 'q3'):
            # staggered 25%: every other row, every other pixel, shifted by one on alternate dotted rows
            sel = (yy % 2 == phase % 2) & ((xx + yy // 2 + phase) % 2 == 0)
            if pattern == 'q3':
                sel = ~sel
        else:
            raise ValueError(pattern)
        self.a[m & ~sel] = c1
        self.a[m & sel] = c2
        return self

    def replace(self, a, b, m=None):
        sel = self.a == a
        if m is not None:
            sel &= m
        self.a[sel] = b
        return self

    def recolor(self, mapping):
        """Character mapping -> a new Grid (unmapped characters are kept)."""
        g = self.copy()
        for a, b in mapping.items():
            g.a[self.a == a] = b
        return g

    def patch(self, x, y, text):
        """Hand-placed pixels: an ASCII block whose top-left lands at (x, y). '.' or ' ' leaves a pixel alone,
        '_' makes it transparent."""
        lines = [l.rstrip() for l in textwrap.dedent(text).strip('\n').splitlines()]
        for dy, l in enumerate(lines):
            for dx, ch in enumerate(l):
                if ch in '. ':
                    continue
                self[x + dx, y + dy] = T if ch == '_' else ch
        return self

    def paste(self, other, x, y):
        """Opaque pixels of another Grid onto this one."""
        for (yy, xx), ch in np.ndenumerate(other.a):
            if ch != T:
                self[x + xx, y + yy] = ch
        return self

    def edge(self, m, c, sides='all', inside=True):
        """Colour the boundary of a mask. inside=True recolours the mask's own edge pixels (the Windows 98 way);
        inside=False draws just outside it. sides: 'all', or any of 't', 'b', 'l', 'r' (e.g. 'br', 'tl')."""
        sides = 'tblr' if sides == 'all' else sides
        m = np.asarray(m, bool)
        sel = np.zeros_like(m)
        shifts = {'t': (1, 0), 'b': (-1, 0), 'l': (0, 1), 'r': (0, -1)}   # neighbour on that side, as a roll
        for s in sides:
            dy, dx = shifts[s]
            nb = np.roll(m, (dy, dx), (0, 1))
            if dy == 1: nb[0, :] = False
            if dy == -1: nb[-1, :] = False
            if dx == 1: nb[:, 0] = False
            if dx == -1: nb[:, -1] = False
            sel |= (m & ~nb) if inside else (~m & nb)
        self.a[sel] = c
        return self

    def outline(self, c='K', sides='all', light=None):
        """Outline everything opaque, from outside. light=<char> uses that colour on the top and left (Windows 98)."""
        m = self.mask()
        if light:
            self.edge(m, light, 'tl', inside=False)
            self.edge(m, c, 'br', inside=False)
        else:
            self.edge(m, c, sides, inside=False)
        return self

    def bbox(self):
        ys, xs = np.nonzero(self.a != T)
        return (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())) if len(xs) else None

    def crop(self, x0, y0, x1, y1):
        g = Grid(1, 1)
        g.a = self.a[y0:y1 + 1, x0:x1 + 1].copy()
        return g

    def flipx(self):
        g = self.copy(); g.a = g.a[:, ::-1].copy(); return g

    def skew(self, kx=4, ky=4):
        """A pixel-exact 'rotation' by two integer shears, so nothing is resampled: row y moves right by y // kx,
        then column x moves up by x // ky. kx = ky = 4 tilts a flat drawing about 14 degrees anticlockwise with clean
        1:4 steps on every edge and every line inside it. Use 0 to skip a shear. Returns a larger Grid."""
        a = self.a
        if kx:
            h, w = a.shape
            o = np.full((h, w + (h - 1) // kx), T, dtype='<U1')
            for y in range(h):
                o[y, y // kx:y // kx + w] = a[y]
            a = o
        if ky:
            h, w = a.shape
            top = (w - 1) // ky
            o = np.full((h + top, w), T, dtype='<U1')
            for x in range(w):
                s = top - x // ky
                o[s:s + h, x] = a[:, x]
            a = o
        g = Grid(1, 1)
        g.a = a
        return g

    def shift(self, dx, dy):
        g = Grid(self.w, self.h)
        return g.paste(self, dx, dy)

    def colors(self):
        u, n = np.unique(self.a, return_counts=True)
        return {k: int(v) for k, v in zip(u, n) if k != T}


# ---- shapes: boolean masks the size of a grid ---------------------------------------------------------------------

def _yx(g):
    return np.mgrid[0:g.h, 0:g.w]


def rect(g, x0, y0, x1, y1):
    """Inclusive pixel box."""
    yy, xx = _yx(g)
    return (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1)


def ellipse(g, x0, y0, x1, y1):
    """Ellipse inscribed in an inclusive pixel box, sampled at pixel centres (any width, odd or even)."""
    yy, xx = _yx(g)
    cx, cy = (x0 + x1 + 1) / 2, (y0 + y1 + 1) / 2
    rx, ry = (x1 - x0 + 1) / 2, (y1 - y0 + 1) / 2
    return ((xx + .5 - cx) / rx) ** 2 + ((yy + .5 - cy) / ry) ** 2 <= 1.0


def poly(g, pts):
    """Polygon (pixel-centre coordinates, i.e. a vertex at (3, 4) is the centre of that pixel), filled."""
    yy, xx = _yx(g)
    px, py = xx.astype(float), yy.astype(float)
    inside = np.zeros((g.h, g.w), bool)
    n = len(pts)
    for i in range(n):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
        cond = (y1 > py) != (y2 > py)
        with np.errstate(divide='ignore', invalid='ignore'):
            xint = (x2 - x1) * (py - y1) / (y2 - y1) + x1
        inside ^= cond & (px < xint)
    # include the edges themselves so thin shapes don't lose pixels
    for i in range(n):
        inside |= line(g, *pts[i], *pts[(i + 1) % n])
    return inside


def line(g, x0, y0, x1, y1):
    """Bresenham line as a mask (1 px, no anti-aliasing)."""
    m = np.zeros((g.h, g.w), bool)
    x0, y0, x1, y1 = map(int, map(round, (x0, y0, x1, y1)))
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        if 0 <= x0 < g.w and 0 <= y0 < g.h:
            m[y0, x0] = True
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy; x0 += sx
        if e2 <= dx:
            err += dx; y0 += sy
    return m


def polyline(g, pts):
    m = np.zeros((g.h, g.w), bool)
    for a, b in zip(pts, pts[1:]):
        m |= line(g, *a, *b)
    return m


def grow(m, n=1):
    """Dilate a mask by n pixels (4-connected)."""
    m = m.copy()
    for _ in range(n):
        o = m.copy()
        o[1:] |= m[:-1]; o[:-1] |= m[1:]; o[:, 1:] |= m[:, :-1]; o[:, :-1] |= m[:, 1:]
        m = o
    return m


def shrink(m, n=1):
    return ~grow(~m, n)
