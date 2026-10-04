"""The easel's medium: an indexed 16-colour canvas with period tools, and an underdrawing layer.

What the medium enforces (because period hardware and paint programs did):
- Every pixel is an index 0..15 into 16 palette registers. A register holds a 4096-colour value
  (4 bits per channel). Changing a register recolours every pixel that uses it, at once.
- Tools draw hard pixels: 1px pens, Bresenham lines, midpoint ellipses, scanline polygon fills,
  flood fills, and 8x8 tile patterns anchored to the screen. There is no anti-aliasing, no alpha
  and no RGB blending anywhere. "In-between" colours are tiles of two indices, as on the machine.
- Writes can be fenced by colour, the "mask colour" feature of period paint programs:
  `with cv.only_over(WALL):` paints only where the wall colour is, `with cv.never_over(INK):`
  leaves the line art alone, and `cv.protect(...)` fences colours until released.

The underdrawing (`cv.ud`) is a separate RGBA sketch layer for construction lines, vanishing
points and notes. It is shown in the easel's looks and never reaches the picture.
"""

from contextlib import contextmanager
from dataclasses import dataclass

import numpy as np

from . import patterns as P


# ----------------------------------------------------------------------------------- colours

def nib(color):
    """A palette value as three nibbles (0..15): '#rgb', '#rrggbb' on the 4096 grid, or a tuple."""
    if isinstance(color, (tuple, list)):
        r, g, b = (int(v) for v in color)
        if not all(0 <= v <= 15 for v in (r, g, b)):
            raise ValueError(f'{color}: nibbles are 0..15')
        return r, g, b
    s = color.lstrip('#')
    if len(s) == 3:
        return tuple(int(c, 16) for c in s)
    if len(s) == 6:
        vals = [int(s[i:i + 2], 16) for i in (0, 2, 4)]
        if any(v % 17 for v in vals):
            raise ValueError(f'{color} is off the PC-98 grid (each channel must be a multiple of 0x11)')
        return tuple(v // 17 for v in vals)
    raise ValueError(f'bad colour {color!r}')


@dataclass
class Tile:
    """A two-index tile: `ink` where the pattern is set, `ground` elsewhere. ground=None leaves the
    existing pixels showing through (an over-tile, the usual way to lay a dither shadow)."""
    pattern: object
    ground: object
    ink: int


def T(pattern, ground, ink):
    return Tile(pattern, ground, ink)


@dataclass
class Clip:
    idx: np.ndarray

    def flip(self, h=False, v=False):
        a = self.idx
        if h: a = a[:, ::-1]
        if v: a = a[::-1, :]
        return Clip(a.copy())

    def rot(self, quarter_turns):
        return Clip(np.rot90(self.idx, -quarter_turns).copy())


# ------------------------------------------------------------------------------- underdrawing

class Under:
    """The underdrawing: a sketch layer in RGBA. Construction only; it never reaches the picture."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.rgba = np.zeros((h, w, 4), np.uint8)
        self.labels = []          # (x, y, text, rgb), drawn by the look at its zoom

    @staticmethod
    def _rgba(col):
        s = col.lstrip('#')
        if len(s) in (3, 4):
            s = ''.join(c * 2 for c in s)
        if len(s) == 6:
            s += 'aa'
        return tuple(int(s[i:i + 2], 16) for i in range(0, 8, 2))

    def _put(self, pts, col):
        c = self._rgba(col)
        for x, y in pts:
            if 0 <= x < self.w and 0 <= y < self.h:
                self.rgba[y, x] = c

    def line(self, p0, p1, col='#f44'):
        self._put(bresenham(*p0, *p1), col)

    def poly(self, pts, col='#f44', closed=True):
        pts = [tuple(map(int, p)) for p in pts]
        for a, b in zip(pts, pts[1:] + (pts[:1] if closed else [])):
            self.line(a, b, col)

    def rect(self, x0, y0, x1, y1, col='#4af'):
        self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], col)

    def ellipse(self, cx, cy, rx, ry, col='#4af'):
        self._put(ellipse_points(cx, cy, rx, ry), col)

    def ray(self, vp, through, col='#8f8'):
        """A line from a vanishing point through a point, run to the canvas edge."""
        (x0, y0), (x1, y1) = vp, through
        dx, dy = x1 - x0, y1 - y0
        n = max(abs(dx), abs(dy)) or 1
        k = 4 * max(self.w, self.h) / n
        self.line((int(x0), int(y0)), (int(x0 + dx * k), int(y0 + dy * k)), col)

    def cross(self, x, y, col='#ff4', r=3):
        self.line((x - r, y), (x + r, y), col); self.line((x, y - r), (x, y + r), col)

    def label(self, x, y, text, col='#ff8'):
        self.labels.append((x, y, text, self._rgba(col)[:3]))


# --------------------------------------------------------------------------------- geometry

def bresenham(x0, y0, x1, y1):
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err, pts = dx + dy, []
    while True:
        pts.append((x0, y0))
        if x0 == x1 and y0 == y1:
            return pts
        e2 = 2 * err
        if e2 >= dy:
            err += dy; x0 += sx
        if e2 <= dx:
            err += dx; y0 += sy


def ellipse_points(cx, cy, rx, ry):
    """Midpoint ellipse outline (integer centre and radii), the shape period circle tools drew."""
    cx, cy, rx, ry = int(cx), int(cy), int(rx), int(ry)
    if rx == 0 or ry == 0:
        return bresenham(cx - rx, cy - ry, cx + rx, cy + ry)
    pts = set()
    x, y = 0, ry
    rx2, ry2 = rx * rx, ry * ry
    px, py = 0, 2 * rx2 * y
    p = ry2 - rx2 * ry + 0.25 * rx2

    def add(x, y):
        pts.update({(cx + x, cy + y), (cx - x, cy + y), (cx + x, cy - y), (cx - x, cy - y)})

    while px < py:
        add(x, y)
        x += 1; px += 2 * ry2
        if p < 0:
            p += ry2 + px
        else:
            y -= 1; py -= 2 * rx2; p += ry2 + px - py
    p = ry2 * (x + 0.5) ** 2 + rx2 * (y - 1) ** 2 - rx2 * ry2
    while y >= 0:
        add(x, y)
        y -= 1; py -= 2 * rx2
        if p > 0:
            p += rx2 - py
        else:
            x += 1; px += 2 * ry2; p += rx2 - py + px
    return sorted(pts)


# ----------------------------------------------------------------------------------- canvas

class Canvas:
    def __init__(self, w, h, ox=0, oy=0):
        """w x h pixels. (ox, oy) is where this canvas sits on the full screen: tiles are anchored to
        screen coordinates, so a piece painted as a crop of a bigger scene tiles seamlessly back in."""
        self.w, self.h, self.ox, self.oy = w, h, ox, oy
        self.idx = np.zeros((h, w), np.uint8)
        self.pal = np.zeros((16, 3), np.uint8)       # nibbles
        self.names = {}
        self.cycles = []                              # palette cycles: (indices, fps, name)
        self.ud = Under(w, h)
        self._fence = None                            # bool[16]: True = may be written over
        self._protected = set()
        self.base = None                              # the real picture this piece started from, if any

    # ---- palette
    def pal_set(self, i, color, name=None):
        self.pal[i] = nib(color)
        if name:
            self.names[name] = i
        return i

    def palette(self, entries):
        """entries: {index: (colour, name)} or a list of colours/(colour, name) in index order."""
        items = entries.items() if isinstance(entries, dict) else enumerate(entries)
        for i, e in items:
            col, name = (e if isinstance(e, tuple) and len(e) == 2 and isinstance(e[1], str) else (e, None))
            self.pal_set(i, col, name)
        return {n: i for n, i in self.names.items()}

    def start_from(self, idx, pal, names=None):
        """Begin on an existing 16-ink picture (see easel.base.quantize): the canvas takes the crop of the
        index map at (ox, oy) and its palette, and remembers it, so the render can also be written as a layer
        of only the changed pixels."""
        crop = np.asarray(idx)[self.oy:self.oy + self.h, self.ox:self.ox + self.w]
        if crop.shape != (self.h, self.w):
            raise ValueError(f'base is {np.asarray(idx).shape}, too small for this canvas')
        self.idx[:] = crop
        for i, c in enumerate(pal):
            self.pal_set(i, c)
        for n, i in (names or {}).items():
            self.names[n] = i
        self.base = self.idx.copy()

    def cycle(self, indices, fps=4, name='cycle'):
        """Mark registers that rotate their colours, like a palette-cycling CRT effect. The look shows
        the frames; exporters write the spec."""
        self.cycles.append((list(indices), fps, name))

    def rgb(self, idx=None):
        idx = self.idx if idx is None else idx
        return (self.pal[idx].astype(np.uint16) * 17).astype(np.uint8)

    def hex(self, i):
        r, g, b = self.pal[i]
        return '#%x%x%x' % (r, g, b)

    # ---- fences (period "mask colour" tools)
    def protect(self, *indices):
        self._protected |= set(indices)

    def release(self, *indices):
        self._protected -= set(indices or self._protected)

    @contextmanager
    def only_over(self, *indices):
        old = self._fence
        f = np.zeros(16, bool); f[list(indices)] = True
        self._fence = f if old is None else (old & f)
        try:
            yield
        finally:
            self._fence = old

    @contextmanager
    def never_over(self, *indices):
        old = self._fence
        f = np.ones(16, bool); f[list(indices)] = False
        self._fence = f if old is None else (old & f)
        try:
            yield
        finally:
            self._fence = old

    def _writable(self):
        ok = np.ones(16, bool) if self._fence is None else self._fence.copy()
        ok[list(self._protected)] = False
        return ok[self.idx]

    # ---- the one write path
    def _write(self, mask, c):
        mask = mask & self._writable()
        if isinstance(c, Tile):
            ink = P.field(c.pattern, self.w, self.h, self.ox, self.oy)
            if c.ground is None:
                self.idx[mask & ink] = c.ink
            else:
                self.idx[mask & ink] = c.ink
                self.idx[mask & ~ink] = c.ground
        else:
            self.idx[mask] = int(c)

    def _mask_pts(self, pts):
        m = np.zeros((self.h, self.w), bool)
        for x, y in pts:
            if 0 <= x < self.w and 0 <= y < self.h:
                m[y, x] = True
        return m

    # ---- pens
    def dot(self, x, y, c):
        self._write(self._mask_pts([(int(x), int(y))]), c)

    def dots(self, pts, c):
        self._write(self._mask_pts([(int(x), int(y)) for x, y in pts]), c)

    def line(self, x0, y0, x1, y1, c):
        self._write(self._mask_pts(bresenham(x0, y0, x1, y1)), c)

    def polyline(self, pts, c, closed=False):
        pts = [tuple(map(int, p)) for p in pts]
        segs = list(zip(pts, pts[1:] + (pts[:1] if closed else [])))
        allp = []
        for a, b in segs:
            allp += bresenham(*a, *b)
        self._write(self._mask_pts(allp), c)

    def rect(self, x0, y0, x1, y1, c, fill=True):
        """Inclusive corners."""
        x0, x1 = sorted((int(x0), int(x1))); y0, y1 = sorted((int(y0), int(y1)))
        if fill:
            m = np.zeros((self.h, self.w), bool)
            m[max(y0, 0):max(y1 + 1, 0), max(x0, 0):max(x1 + 1, 0)] = True
            self._write(m, c)
        else:
            self.polyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], c, closed=True)

    def ellipse(self, cx, cy, rx, ry, c, fill=False):
        pts = ellipse_points(cx, cy, rx, ry)
        if not fill:
            self._write(self._mask_pts(pts), c)
            return
        self._write(self.m_ellipse(cx, cy, rx, ry), c)

    def poly(self, pts, c):
        self._write(self.m_poly(pts), c)

    def fill(self, mask, c):
        self._write(mask, c)

    def flood(self, x, y, c, conn=4, within=None):
        m = self.m_region(x, y, conn, within)
        self._write(m, c)
        return m

    def stamp(self, x, y, text, key):
        """Hand-placed dots from rows of characters; key maps characters to indices (or Tiles).
        '.' and ' ' are transparent. This is the pen at the loupe, the finest tool there is."""
        rows = [r for r in text.strip('\n').splitlines()]
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch in '. ':
                    continue
                if ch not in key:
                    raise KeyError(f'stamp: no colour for {ch!r}')
                self.dot(x + dx, y + dy, key[ch])

    # ---- tiles and tile gradients
    def tile(self, mask, pattern, ground, ink):
        self._write(mask, Tile(pattern, ground, ink))

    def grad(self, mask, a, b, t, steps=None, offset=0.0):
        """A tile gradient from index a (t=0) to index b (t=1) over the masked area, in bands of the
        period tiles (none, 1/4, 1/2, 3/4, solid by default; P.STEPS_FINE for more). t is an array
        (see lin/rad) or a callable(x, y)."""
        steps = steps or P.STEPS
        if callable(t):
            ys, xs = np.mgrid[0:self.h, 0:self.w]
            t = t(xs, ys)
        t = np.clip(np.asarray(t, float) + offset, 0, 1)
        band = np.minimum((t * len(steps)).astype(int), len(steps) - 1)
        for k, name in enumerate(steps):
            self._write(mask & (band == k), Tile(name, a, b))

    def lin(self, p0, p1):
        """t field: 0 at p0, 1 at p1, along the line between them."""
        ys, xs = np.mgrid[0:self.h, 0:self.w]
        (x0, y0), (x1, y1) = p0, p1
        dx, dy = x1 - x0, y1 - y0
        L = dx * dx + dy * dy or 1
        return ((xs - x0) * dx + (ys - y0) * dy) / L

    def rad(self, c, r0, r1, sx=1.0, sy=1.0):
        """t field: 0 inside radius r0 of c, 1 beyond r1 (sx/sy squash it into an ellipse)."""
        ys, xs = np.mgrid[0:self.h, 0:self.w]
        d = np.hypot((xs - c[0]) / sx, (ys - c[1]) / sy)
        return (d - r0) / max(r1 - r0, 1e-6)

    def relight(self, mask, level, ramp, steps=None, tile_on=None):
        """Light falling on what's already painted, the period way: each ink steps up its own ramp (`ramp` maps an
        ink to the next lighter one) through banded tiles. `level` is a field of steps: 0 = untouched, 1 = one full
        step, 1.5 = one step plus a 1/2 tile of the next. Inks missing from `ramp` stay as they are (line art).
        `tile_on`: only these inks take the tiled partial step (a surface's base colour); the others (a texture's
        dots) step only at whole levels, so a patterned surface stays coherent inside the glow."""
        steps = steps or P.STEPS
        level = np.clip(np.asarray(level, float), 0, 8) * mask
        full = np.floor(level).astype(int)
        frac = level - full
        band = np.minimum((frac * (len(steps) - 1) + 0.5).astype(int), len(steps) - 1)   # nearest tile band
        extra = np.zeros_like(full)
        for k, name in enumerate(steps):
            extra[(band == k) & P.field(name, self.w, self.h, self.ox, self.oy)] = 1
        if tile_on is not None:
            extra[~np.isin(self.idx, list(tile_on))] = 0
        n = full + extra
        table = np.arange(256, dtype=np.uint8)
        for a, b in ramp.items():
            table[a] = b
        new = self.idx.copy()
        for k in range(1, int(n.max()) + 1 if n.size else 1):
            sel = n >= k
            new[sel] = table[new[sel]]
        m = mask & (new != self.idx) & self._writable()
        self.idx[m] = new[m]

    def dist_from(self, mask, max_d=64):
        """Rings around a selection: 0 on it, 1 on the pixels touching it, 2 on the next ring... (8-way), max_d
        beyond. For glows and halos that hug a shape's silhouette rather than a circle."""
        d = np.full((self.h, self.w), float(max_d))
        cur = mask.copy()
        d[cur] = 0
        for k in range(1, max_d):
            grown = cur.copy()
            grown[1:] |= cur[:-1]; grown[:-1] |= cur[1:]
            grown[:, 1:] |= grown[:, :-1].copy(); grown[:, :-1] |= grown[:, 1:].copy()
            new = grown & ~cur
            if not new.any():
                break
            d[new] = k
            cur = grown
        return d

    # ---- masks (selections)
    def m_all(self):
        return np.ones((self.h, self.w), bool)

    def m_rect(self, x0, y0, x1, y1):
        x0, x1 = sorted((int(x0), int(x1))); y0, y1 = sorted((int(y0), int(y1)))
        m = np.zeros((self.h, self.w), bool)
        m[max(y0, 0):max(y1 + 1, 0), max(x0, 0):max(x1 + 1, 0)] = True
        return m

    def m_poly(self, pts):
        """Scanline fill at pixel centres, even-odd rule: the pixels a period polygon fill paints."""
        pts = [(float(x), float(y)) for x, y in pts]
        m = np.zeros((self.h, self.w), bool)
        n = len(pts)
        for y in range(self.h):
            yc = y + 0.5
            xs = []
            for i in range(n):
                (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
                if (y0 <= yc < y1) or (y1 <= yc < y0):
                    xs.append(x0 + (yc - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for a, b in zip(xs[0::2], xs[1::2]):
                xa = max(int(np.ceil(a - 0.5)), 0)
                xb = min(int(np.floor(b - 0.5)), self.w - 1)
                if xb >= xa:
                    m[y, xa:xb + 1] = True
        # include the outline pixels too, so a filled polygon covers its own edge
        edge = []
        ip = [(int(round(x)), int(round(y))) for x, y in pts]
        for a, b in zip(ip, ip[1:] + ip[:1]):
            edge += bresenham(*a, *b)
        return m | self._mask_pts(edge)

    def m_ellipse(self, cx, cy, rx, ry):
        pts = ellipse_points(cx, cy, rx, ry)
        m = self._mask_pts(pts)
        rows = {}
        for x, y in pts:
            lo, hi = rows.get(y, (x, x)); rows[y] = (min(lo, x), max(hi, x))
        for y, (lo, hi) in rows.items():
            if 0 <= y < self.h:
                m[y, max(lo, 0):max(min(hi + 1, self.w), 0)] = True
        return m

    def m_where(self, *indices):
        return np.isin(self.idx, list(indices))

    def m_region(self, x, y, conn=4, within=None):
        """The connected area of the seed pixel's colour (what a flood fill would cover)."""
        x, y = int(x), int(y)
        target = self.idx[y, x]
        same = self.idx == target
        if within is not None:
            same &= within
        m = np.zeros_like(same)
        stack = [(x, y)]
        nb = [(1, 0), (-1, 0), (0, 1), (0, -1)] + ([(1, 1), (1, -1), (-1, 1), (-1, -1)] if conn == 8 else [])
        while stack:
            px, py = stack.pop()
            if 0 <= px < self.w and 0 <= py < self.h and same[py, px] and not m[py, px]:
                m[py, px] = True
                stack.extend((px + dx, py + dy) for dx, dy in nb)
        return m

    def m_line(self, x0, y0, x1, y1):
        return self._mask_pts(bresenham(x0, y0, x1, y1))

    def m_edge(self, mask, sides='all', inside=True):
        """The rim of a selection: its outermost pixels (inside) or the ring just outside it."""
        m = mask
        sh = {'top': (1, 0), 'bottom': (-1, 0), 'left': (0, 1), 'right': (0, -1)}
        pick = sh.keys() if sides == 'all' else sides.split(',')
        out = np.zeros_like(m)
        for s in pick:
            dy, dx = sh[s.strip()]
            nb = np.roll(np.roll(m, dy, 0), dx, 1)
            if dy == 1: nb[0, :] = False
            if dy == -1: nb[-1, :] = False
            if dx == 1: nb[:, 0] = False
            if dx == -1: nb[:, -1] = False
            out |= (m & ~nb) if inside else (nb & ~m)
        return out

    # ---- selections
    def copy(self, x0, y0, x1, y1):
        return Clip(self.idx[y0:y1 + 1, x0:x1 + 1].copy())

    def paste(self, clip, x, y, transparent=None):
        h, w = clip.idx.shape
        m = np.zeros((self.h, self.w), bool)
        vals = np.zeros((self.h, self.w), np.uint8)
        ys, xs = slice(max(y, 0), min(y + h, self.h)), slice(max(x, 0), min(x + w, self.w))
        src = clip.idx[ys.start - y:ys.stop - y, xs.start - x:xs.stop - x]
        vals[ys, xs] = src
        m[ys, xs] = True if transparent is None else (src != transparent)
        m &= self._writable()
        self.idx[m] = vals[m]

    def replace(self, a, b, mask=None):
        """Recolour index a to b (optionally inside a mask), as a palette-index swap tool."""
        m = self.idx == a
        if mask is not None:
            m &= mask
        self._write(m, b)
