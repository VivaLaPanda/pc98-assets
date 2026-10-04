"""Panda's Room, final art: a hand paint-over (rotoscope) of layout B at native 448x320.

Run: uv run python assets/panda-room/paint.py [passage]      (paints up to that passage; export.py writes the finals)

The underlay (refs/underlay.png: the image model's PC-98-style redraw of layout B, refs/gen/B_pc98_0.png, cropped to
the scene window's 740:528 and scaled to 448x320) is only something to trace. Every contour here is a hand-placed
polygon or polyline read off a gridded zoom of it (`pc98 zoom`); every surface gets inks chosen for its material, laid
flat, with light placed by hand as smooth fields cut into hard steps (one checker band where a light changes) and cel
shadows made from a shape minus itself moved toward the light. Black ink goes on contours, highlights and greebles are
placed by hand, and nothing is error-diffused. (cel(), which grades a surface along the underlay's blurred luminance,
survives only on the mug: on big surfaces it made blotches. NOTES.md has the whole account.)

The painting is done a passage at a time (shell, window, city, wall things, shelf, tv, bed, desk, chair, floor,
butterfly, finish); `paint.py <passage>` paints up to that passage and writes out/final/progress/<passage>.png beside the
underlay, so each passage is looked at before the next (the "step back and look" loop).

Prominence is light: window (Twitter) > phone (Signal/Discord) > PC (GitHub) > newspaper (Substack) > bookshelf
(reading list) > butterfly (Bluesky) > TV (Letterboxd); everything else sits in navy shadow.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

from pc98.pixel import Grid, rect, ellipse, poly, line, polyline, grow, shrink

HERE = Path(__file__).parent
OUT = HERE / 'out' / 'final'
W, H = 448, 320

# 16 inks, all on the 12-bit grid. Ramps: navy night field n N v V l L W; wood r b o y; cyan c C; neon h g.
LEGEND = {
    'K': (0x00, 0x00, 0x00),   # ink, deepest shadow
    'n': (0x11, 0x11, 0x33),   # night field
    'N': (0x22, 0x22, 0x55),   # walls in shadow
    'v': (0x33, 0x33, 0x77),   # indigo
    'V': (0x55, 0x44, 0x99),   # violet: city-lit surfaces
    'l': (0x88, 0x77, 0xCC),   # lavender
    'L': (0xCC, 0xBB, 0xEE),   # pale lavender: paper, lit cloth
    'W': (0xFF, 0xFF, 0xFF),   # white: screens, bulb, glints
    'c': (0x22, 0x66, 0xCC),   # blue: city windows, screen shading
    'C': (0x66, 0xEE, 0xFF),   # cyan: screen glow, phone, butterfly
    'r': (0x55, 0x22, 0x22),   # dark wood
    'b': (0xAA, 0x55, 0x33),   # wood
    'o': (0xEE, 0x99, 0x44),   # lamp-lit wood, warm windows
    'y': (0xFF, 0xEE, 0x99),   # lamp light
    'h': (0xFF, 0x44, 0xAA),   # pink neon
    'g': (0x33, 0xCC, 0x99),   # green neon, book spines
}

B4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]])
YY, XX = np.mgrid[0:H, 0:W]
BAYER = B4[YY % 4, XX % 4]

UNDER = Image.open(HERE / 'refs' / 'underlay.png').convert('RGB')
UA = np.asarray(UNDER, dtype=float) / 255
LUM = 0.3 * UA[..., 0] + 0.59 * UA[..., 1] + 0.11 * UA[..., 2]
LUM_SOFT = np.asarray(Image.fromarray((LUM * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(5))
                      .filter(ImageFilter.GaussianBlur(2.2)), dtype=float) / 255


def P(g, *pts):
    return poly(g, list(pts))


def tone(g, m, a, b, k):
    """Ink a, with ink b on the Bayer cells below k of 16 (4 = dot grid, 8 = checker, 12 = inverse dot grid)."""
    g.a[m] = a
    g.a[m & (BAYER < k)] = b


def bands(g, m, field, inks, steps=(0, 4, 8, 12, 16)):
    """Banded gradient through an ink ramp along a 0..1 field; each pair steps through the tile patterns."""
    field = np.clip(field, 0, 1)
    n = len(inks) - 1
    pos = field * n
    seg = np.minimum(pos.astype(int), n - 1)
    frac = pos - seg
    st = np.array(steps)
    k = st[np.clip(np.round(frac * (len(st) - 1)).astype(int), 0, len(st) - 1)]
    for i in range(n):
        sel = m & (seg == i)
        for kk in np.unique(k[sel]):
            tone(g, sel & (k == kk), inks[i], inks[i + 1], int(kk))


def cel(g, m, inks, lo=None, hi=None, steps=(0, 4, 8, 12, 16), gamma=1.0):
    """Grade a surface with its own ramp (dark -> light) along the underlay's light: the painter's eye on the
    reference, the hand's own inks and patterns."""
    v = LUM_SOFT[m]
    if not len(v):
        return
    lo = np.percentile(v, 4) if lo is None else lo
    hi = np.percentile(v, 96) if hi is None else hi
    t = np.clip((LUM_SOFT - lo) / max(hi - lo, 1e-3), 0, 1) ** gamma
    bands(g, m, t, inks, steps)


def radial(cx, cy, rx, ry):
    return np.sqrt(((XX - cx) / rx) ** 2 + ((YY - cy) / ry) ** 2)


def ink(g, m, c='K', sides='all'):
    g.edge(m, c, sides, inside=True)


def L_(g, pts, c='K', m=None):
    """A traced line (polyline), optionally clipped to a mask."""
    lm = polyline(g, pts)
    if m is not None:
        lm &= m
    g.fill(lm, c)
    return lm


def tilted(g, cx, cy, rx, ry, ang):
    """Ellipse at (cx, cy) with radii rx (across) and ry (along), its long axis turned ang degrees clockwise."""
    yy, xx = np.mgrid[0:g.h, 0:g.w]
    dx, dy = xx + .5 - cx, yy + .5 - cy
    c, s = np.cos(np.radians(ang)), np.sin(np.radians(ang))
    u, v = (dx * c + dy * s) / rx, (-dx * s + dy * c) / ry
    return u * u + v * v <= 1


def squircle(g, cx, cy, rx, ry, n=2.4):
    yy, xx = np.mgrid[0:g.h, 0:g.w]
    return np.abs((xx + .5 - cx) / rx) ** n + np.abs((yy + .5 - cy) / ry) ** n <= 1


def sh(m, dx, dy):
    """The mask moved by (dx, dy)."""
    out = np.zeros_like(m)
    H, W = m.shape
    out[max(dy, 0):H + min(dy, 0), max(dx, 0):W + min(dx, 0)] = m[max(-dy, 0):H + min(-dy, 0), max(-dx, 0):W + min(-dx, 0)]
    return out


def under_hex(x, y):
    r, gg, b = UNDER.getpixel((x, y))
    return r, gg, b


# =====================================================================================================================
# passages

def shell(g, M, S):
    """Ceiling, the walls and the corner, the floor. Light comes from the window: the left wall's falloff is graded
    from the underlay; the right wall sits in navy with a warm wash under the shelf lamp."""
    ceil = P(g, (0, 0), (447, 0), (447, 6), (300, 33), (0, 6))
    lwall = P(g, (0, 6), (300, 33), (300, 250), (0, 268))
    rwall = P(g, (301, 33), (447, 6), (447, 250), (301, 250))
    floor = rect(g, 0, 240, 447, 319) & ~lwall & ~rwall
    S.update(ceil=ceil, lwall=lwall, rwall=rwall)
    g.fill(floor, 'n')
    # flat planes, as a PC-98 painter lays them: one ink per wall, a single checker band where the light changes
    g.fill(ceil, 'n')
    tone(g, ceil & (YY < 4), 'n', 'K', 8)
    g.fill(lwall, 'N')
    tone(g, lwall & (XX > 280) & (XX <= 290), 'N', 'n', 8)
    g.fill(lwall & (XX > 290), 'n')
    g.fill(rwall, 'v')
    top_r = YY - (33 - (XX - 301) * .185)                               # depth below the cornice
    g.fill(rwall & (top_r < 14), 'N'); tone(g, rwall & (top_r >= 14) & (top_r < 22), 'N', 'v', 8)
    tone(g, rwall & (XX > 432) & (top_r >= 14), 'v', 'N', 8)
    # the cornice: two lines and the corner post
    L_(g, [(0, 5), (300, 32), (447, 5)])
    L_(g, [(0, 9), (300, 36), (447, 9)], 'n')
    L_(g, [(300, 33), (300, 250)])
    L_(g, [(301, 37), (301, 250)], 'N')
    # the ceiling light: a flat disc seen from below
    disc = ellipse(g, 212, -6, 288, 7)
    g.fill(disc, 'N'); g.fill(ellipse(g, 220, -5, 280, 4), 'v'); ink(g, disc)
    L_(g, [(252, 7), (252, 48)], 'n')                        # pull cord
    g.fill(rect(g, 251, 48, 253, 50), 'N')


def window(g, M, S):
    """The window (rank 1, Twitter): frame, head, far jamb lit by the city, sill, mullion; glass is painted by city()."""
    frame = P(g, (20, 10), (240, 42), (243, 194), (20, 182))
    glass_l = P(g, (28, 30), (117, 41), (117, 180), (28, 176))
    glass_r = P(g, (124, 42), (207, 51), (207, 183), (124, 182))
    head = P(g, (22, 12), (238, 44), (238, 50), (22, 26))      # the frame's top face, catching light
    jamb = P(g, (208, 50), (238, 44), (243, 192), (208, 186))
    sill = P(g, (20, 178), (208, 185), (243, 192), (243, 198), (20, 188))
    S.update(glass=glass_l | glass_r, glass_l=glass_l, glass_r=glass_r, frame=frame, jamb=jamb, sill=sill)
    g.fill(frame, 'N')
    g.fill(head, 'v')
    tone(g, head & (YY > 18 + (XX - 22) * .147), 'v', 'N', 8)
    L_(g, [(22, 12), (238, 44)], 'V')
    # the far jamb: city light rakes across it in a diagonal shaft (painted in clean bands, as in the reference)
    shaft = (XX - 208) * 3.2 - (YY - 60)
    g.fill(jamb, 'v')
    g.fill(jamb & (shaft < 30) & (YY > 64), 'V')
    g.fill(jamb & (shaft < -36) & (YY > 110), 'l')
    L_(g, [(219, 66), (238, 126)], 'c', jamb)                             # the shaft's cold edge
    L_(g, [(208, 51), (208, 186)])
    L_(g, [(238, 44), (243, 192)])
    # sill: lit top edge, dark face
    g.fill(sill, 'v')
    bands(g, sill, np.clip((XX - 20) / 220, 0, 1), ['c', 'v', 'N'], steps=(0, 4, 8, 12, 16))
    L_(g, [(20, 178), (208, 185), (243, 192)], 'C')
    L_(g, [(20, 179), (208, 186), (243, 193)], 'l')
    L_(g, [(20, 188), (243, 198)])
    ink(g, frame)
    # mullion and the inner frame lines
    mull = P(g, (117, 40), (124, 41), (124, 183), (117, 181))
    g.fill(mull, 'N'); L_(g, [(119, 42), (119, 180)], 'v'); ink(g, mull)
    for gl in (glass_l, glass_r):
        ink(g, grow(gl, 1) & ~gl & frame, 'K')
    M['window'] = frame | sill | head | jamb


def city(g, M, S):
    """The skyline, traced from the underlay: towers placed where it has them, three depths (far haze, tall
    towers, near blocks), lit windows on clean regular grids, more of them where the underlay is bright; neon as
    abstract lit shapes at its sign positions (no lettering); aircraft lights; a street of lamps at the bottom."""
    glass = S['glass']
    bands(g, glass, np.clip((YY - 34) / 110, 0, 1), ['n', 'N', 'v', 'V'], steps=(0, 4, 8, 12, 16))
    rng = np.random.default_rng(98)
    lights = []

    def tower(x0, x1, top, body, cell=(3, 3), win=(2, 1), inks=('L', 'l'), p=.5, base=184, rim=None, crown=None):
        b = rect(g, x0, top, x1, base) & glass
        g.fill(b, body)
        if crown:                                  # a stepped top or a mast
            cx0, cx1, ch = crown
            g.fill(rect(g, cx0, top - ch, cx1, top - 1) & glass, body)
        if rim:                                    # the side that catches the sky glow
            g.fill(rect(g, x0, top, x0, base) & glass, rim)
        sx, sy = cell
        off = (x1 - x0 + 1 - win[0]) % sx // 2
        for wy in range(top + 2, base - 1, sy):
            for wx in range(x0 + 1 + off, x1 - win[0] + 1, sx):
                if not glass[wy:wy + win[1], wx:wx + win[0]].all():
                    continue
                bright = LUM[wy:wy + win[1] + 1, wx:wx + win[0] + 1].max()
                if rng.random() < p * (0.35 + 1.3 * bright):
                    c = inks[int(rng.integers(len(inks)))]
                    g.fill(rect(g, wx, wy, wx + win[0] - 1, wy + win[1] - 1), c)
                    lights.append((wx, wy, win[0], win[1], c))
        return b

    # far haze: a continuous low skyline behind everything
    for x0, x1, top in [(28, 36, 92), (37, 50, 86), (51, 63, 96), (64, 72, 90), (95, 106, 88), (107, 117, 96),
                        (124, 134, 90), (135, 146, 98), (162, 172, 86), (173, 181, 94), (200, 207, 90)]:
        tower(x0, x1, top, 'v', cell=(3, 3), win=(1, 1), inks=('V', 'l'), p=.25)
    # the tall towers
    tower(24, 40, 56, 'n', cell=(3, 3), win=(2, 1), inks=('L', 'C', 'l'), p=.6, rim='v', crown=(30, 34, 4))
    g[32, 51] = 'h'
    tower(62, 70, 68, 'N', cell=(3, 3), win=(1, 1), inks=('l',), p=.45, rim='V')
    tower(72, 95, 64, 'n', cell=(3, 2), win=(2, 1), inks=('L', 'y', 'l', 'L'), p=.65, rim='v', crown=(80, 86, 3))
    g[83, 59] = 'h'; g[83, 60] = 'K'
    tower(144, 161, 72, 'n', cell=(3, 3), win=(2, 1), inks=('L', 'l', 'C'), p=.6, rim='v', crown=(150, 155, 4))
    g[152, 67] = 'h'
    tower(176, 204, 76, 'n', cell=(4, 3), win=(2, 1), inks=('L', 'y', 'l'), p=.6, rim='v', crown=(186, 194, 3))
    g[190, 72] = 'h'
    tower(128, 142, 94, 'N', cell=(3, 3), win=(1, 2), inks=('l', 'C'), p=.5, rim='V')
    tower(163, 175, 88, 'N', cell=(3, 3), win=(1, 1), inks=('l', 'L'), p=.5)
    # near blocks: lit faces in indigo, rows of windows
    tower(24, 50, 108, 'v', cell=(4, 3), win=(2, 1), inks=('L', 'y', 'C'), p=.6, rim='V')
    tower(60, 76, 112, 'n', cell=(3, 3), win=(1, 1), inks=('l', 'C'), p=.5)
    tower(76, 98, 114, 'v', cell=(3, 3), win=(2, 1), inks=('L', 'l'), p=.55, rim='V')
    tower(98, 117, 110, 'N', cell=(3, 3), win=(2, 1), inks=('C', 'L'), p=.55)
    tower(124, 148, 112, 'v', cell=(3, 3), win=(2, 1), inks=('L', 'y', 'l'), p=.6, rim='V')
    tower(148, 180, 116, 'N', cell=(4, 3), win=(2, 1), inks=('l', 'L', 'C'), p=.55)
    tower(180, 207, 110, 'v', cell=(3, 3), win=(2, 1), inks=('L', 'C'), p=.55, rim='V')
    # the lowest, nearest blocks: dark, warm windows, the street-level signs
    tower(24, 52, 140, 'n', cell=(4, 4), win=(1, 3), inks=('L', 'y'), p=.5)
    tower(60, 98, 150, 'K', cell=(4, 3), win=(2, 1), inks=('y', 'o', 'L'), p=.55)
    tower(98, 117, 146, 'n', cell=(3, 3), win=(2, 1), inks=('l', 'L'), p=.5)
    tower(124, 146, 146, 'K', cell=(3, 3), win=(2, 1), inks=('y', 'L'), p=.55)
    tower(146, 182, 150, 'n', cell=(4, 3), win=(2, 1), inks=('L', 'y', 'C'), p=.5)
    tower(182, 207, 140, 'K', cell=(3, 3), win=(2, 1), inks=('y', 'L'), p=.5)

    DARK = {'h': 'r', 'C': 'c', 'g': 'c', 'l': 'V', 'L': 'l', 'V': 'v', 'y': 'o'}

    def neon(box, c, inner='K', art=None, halo=True):
        x0, y0, x1, y1 = box
        m = rect(g, x0, y0, x1, y1) & glass
        if halo:                                   # the glow: one solid ring a step darker, not a dither
            g.fill(grow(m, 1) & ~m & glass, DARK.get(c, 'v'))
        g.fill(m, inner)
        g.edge(m, c, 'all', inside=True)
        if art:
            art(x0, y0, x1, y1)
        return m

    def bars(c, step=3, gap=2):
        return lambda x0, y0, x1, y1: [g.fill(rect(g, x0 + gap, yy, x1 - gap, yy) & glass, c)
                                       for yy in range(y0 + gap + 1, y1 - gap + 1, step)]

    def slash(c):                                  # a board split on the diagonal in two colours (no glyph)
        return lambda x0, y0, x1, y1: g.fill(rect(g, x0 + 1, y0 + 1, x1 - 1, y1 - 1) & glass &
                                             ((XX - x0) * (y1 - y0) + (YY - y0) * (x1 - x0) > (x1 - x0) * (y1 - y0)), c)

    def ring(c):                                   # a round logo: a filled disc, not an O
        return lambda x0, y0, x1, y1: g.fill(ellipse(g, x0 + 3, y0 + 3, x1 - 3, y1 - 3) & glass, c)

    neon((52, 102, 58, 136), 'C', art=bars('C', 4))                         # tall cyan blade
    neon((53, 140, 58, 172), 'h', art=lambda x0, y0, x1, y1: g.fill(rect(g, x0 + 2, y0 + 3, x0 + 3, y1 - 3), 'L'))
    neon((64, 72, 68, 96), 'l', inner='N', art=bars('L', 4))              # the slender tower's sign
    neon((80, 133, 96, 140), 'g', inner='g', art=lambda x0, y0, x1, y1: g.fill(rect(g, x0 + 2, y0 + 2, x1 - 3, y0 + 3), 'W'))
    neon((80, 145, 94, 151), 'h', inner='h', art=lambda x0, y0, x1, y1: g.fill(rect(g, x0 + 2, y0 + 2, x1 - 5, y0 + 3), 'L'))
    neon((101, 101, 110, 111), 'h', inner='h', art=slash('W'))
    neon((106, 116, 114, 122), 'C', inner='c', art=bars('C', 3))
    neon((127, 101, 134, 111), 'h', inner='h', art=bars('L', 3))
    neon((172, 99, 183, 110), 'l', inner='L', art=slash('V'))
    neon((192, 94, 205, 110), 'h', inner='h', art=ring('W'))
    neon((183, 120, 191, 136), 'V', inner='V', art=slash('h'))
    neon((195, 127, 206, 136), 'C', art=bars('C', 3))
    neon((150, 153, 176, 163), 'C', inner='c', art=bars('C', 3, 2))
    neon((183, 144, 191, 172), 'L', inner='y', art=lambda x0, y0, x1, y1: g.fill(rect(g, x0 + 2, y1 - 6, x1 - 2, y1 - 3), 'V'))
    neon((196, 145, 206, 172), 'C', art=bars('L', 4))
    neon((132, 160, 144, 166), 'y', inner='o', halo=False)
    neon((30, 112, 40, 118), 'g', inner='K', art=bars('g', 3))
    neon((110, 150, 117, 172), 'h', art=bars('h', 4))
    # the street: lamps and tail lights along the bottom of the view
    road = glass & (YY >= 177)
    g.fill(road, 'K')
    for sx in range(30, 206, 6):
        if glass[178, sx]:
            g[sx, 178] = 'y'
    for sx in range(33, 204, 10):
        if glass[181, sx]:
            g.fill(rect(g, sx, 181, sx + 2, 181) & glass, 'h' if sx % 20 < 10 else 'L')
    S['lights'] = lights


def wall_things(g, M, S):
    """Greebles on the walls: the calendar beside the window, the poster on the right wall, the edge of a poster at the
    far left, a socket, tape."""
    # calendar (between the window and the corner): a photo above a grid of days
    cal = P(g, (247, 104), (268, 106), (268, 148), (247, 146))
    g.fill(cal, 'l')
    photo = P(g, (249, 107), (266, 108), (266, 122), (249, 121))
    g.fill(photo, 'v'); bands(g, photo, np.clip((YY - 107) / 14, 0, 1), ['c', 'v', 'V'])
    L_(g, [(250, 119), (255, 114), (259, 117), (265, 111)], 'L')
    grid = P(g, (249, 125), (266, 126), (266, 145), (249, 144))
    g.fill(grid, 'L')
    for gx in range(251, 266, 3):
        L_(g, [(gx, 126), (gx, 144)], 'l', grid)
    for gy in range(128, 145, 3):
        L_(g, [(249, gy), (266, gy + 1)], 'l', grid)
    g[257, 134] = 'h'; g[258, 134] = 'h'                     # a circled date
    ink(g, cal)
    g.fill(rect(g, 256, 102, 257, 103), 'K')                 # the nail
    # poster on the right wall: a film or album print, a big moon over a dark skyline, a blank title band
    post = P(g, (406, 58), (447, 54), (447, 148), (406, 146))
    g.fill(post, 'v')
    g.fill(post & (YY > 100), 'V')
    moon = ellipse(g, 414, 66, 440, 92)
    g.fill(moon & post, 'L'); g.fill(moon & ~sh(ellipse(g, 414, 66, 440, 92), 4, -3) & post, 'l')   # its shaded rim
    sky = post & (YY > 104 + ((XX * 7) % 11 > 5) * 6 - ((XX // 5) % 3) * 4)
    g.fill(sky & (YY < 136), 'N')
    for wx, wy in [(412, 116), (418, 112), (426, 118), (434, 110), (440, 120), (416, 124), (430, 126)]:
        g[wx, wy] = 'y'                                           # lit windows in the print's skyline
    for sx, sy in [(410, 64), (443, 98), (409, 92)]:
        g[sx, sy] = 'W'
    band = post & (YY >= 136) & (YY <= 141)
    g.fill(band, 'h'); g.fill(post & (YY == 143), 'l')           # the title band and a credit line, no letters
    ink(g, post)
    for tx, ty in [(405, 57), (446, 53), (405, 146)]:            # tape corners
        g.fill(rect(g, tx, ty, tx + 2, ty + 1), 'l')
    # the left edge: part of another poster, cut by the frame
    lp = P(g, (0, 70), (10, 71), (10, 146), (0, 146))
    g.fill(lp, 'v'); tone(g, lp, 'v', 'V', 4)
    L_(g, [(2, 90), (7, 100), (3, 112), (8, 124)], 'l')
    ink(g, lp, 'K', 'r'); L_(g, [(0, 70), (10, 71)]); L_(g, [(0, 146), (10, 146)])
    # wall socket under the calendar, a cable from it
    sock = rect(g, 252, 196, 258, 203)
    g.fill(sock, 'V'); g[254, 199] = 'K'; g[256, 199] = 'K'; ink(g, sock)


def shelf(g, M, S):
    """The bookshelf (rank 5, reading list): dark wood, books in shadow, and one warm pool from the clamp lamp (a grey
    cone with its lit mouth turned down at the books, a gooseneck, a T-clamp on the board). Books stand, lean and lie
    in stacks. On top: a cardboard box, a stack of manga, a fern in a pot."""
    front_b = 236
    case = P(g, (270, 82), (358, 74), (358, front_b), (270, front_b))
    side = P(g, (358, 74), (392, 70), (392, 232), (358, front_b))
    g.fill(case, 'r')
    # the side panel: flat dark wood in shade, a lit front edge, long grain strokes, darker toward the back
    g.fill(side, 'r')
    g.fill(side & (XX > 386), 'K'); tone(g, side & (XX > 380) & (XX <= 386), 'r', 'K', 8)
    L_(g, [(359, 76), (359, 234)], 'b')
    for gr in [[(366, 84), (367, 120)], [(368, 150), (367, 196)], [(374, 100), (375, 140), (374, 170)],
               [(377, 196), (378, 226)], [(371, 210), (371, 228)]]:
        L_(g, gr, 'K', side)                                            # broken grain strokes
    inner = P(g, (275, 87), (353, 80), (353, 230), (275, 230))
    g.fill(inner, 'K')
    boards = [113, 140, 166, 192, 218]
    rows = [(87, 113), (116, 140), (143, 166), (169, 192), (195, 218)]
    lamp = (330, 124)
    warm = radial(lamp[0] - 4, lamp[1] + 10, 44, 34)
    rng = np.random.default_rng(7)
    for ri, ((ra, rb), bd) in enumerate(zip(rows, boards)):
        bay = inner & (YY > ra - 2) & (YY < rb)
        g.fill(bay, 'K')
        g.fill(bay & (warm < 1), 'r')
        tone(g, bay & (warm >= .88) & (warm < 1), 'r', 'K', 8)
        g.fill(bay & (warm < .55), 'b')
        tone(g, bay & (warm >= .55) & (warm < .68), 'r', 'b', 8)
        x = 278
        if ri == 1:                                                   # under the lamp: a stack lying flat
            for k, (cv, ed) in enumerate([('o', 'y'), ('b', 'o'), ('y', 'W'), ('o', 'y')]):
                yb = rb - 1 - k * 3
                bk = rect(g, 300 - k % 2, yb - 2, 320 + (k % 3), yb)
                g.fill(bk, cv); g.fill(rect(g, 300 - k % 2, yb - 2, 320 + (k % 3), yb - 2), ed)
                ink(g, bk, 'K', 'lr')
            g.fill(rect(g, 299, rb - 13, 321, rb - 13), 'K')
        while x < 350:
            if ri == 1 and 296 <= x <= 323:
                x = 324
                continue
            if rng.random() < .1:
                x += int(rng.integers(2, 5))
                continue
            bw = int(rng.integers(3, 6))
            bh = int(rng.integers(max(12, rb - ra - 12), rb - ra - 1))
            d = warm[rb - bh // 2, min(x + bw // 2, 447)]
            if d < .62:
                base, hi_ = [('b', 'o'), ('g', 'C'), ('V', 'l'), ('o', 'y'), ('c', 'C'), ('L', 'W')][int(rng.integers(6))]
            elif d < 1:
                base, hi_ = [('r', 'b'), ('v', 'V'), ('c', 'V'), ('N', 'v'), ('b', 'o')][int(rng.integers(5))]
            else:
                base, hi_ = [('N', 'v'), ('n', 'N'), ('r', 'r'), ('v', 'V')][int(rng.integers(4))]
            if rng.random() < .09 and x < 344:                         # a book leaning on its neighbour
                lean = 4
                bk = P(g, (x, rb - 1), (x + bw - 1, rb - 1), (x + bw - 1 + lean, rb - bh + 1), (x + lean, rb - bh + 1))
                g.fill(bk, base); L_(g, [(x, rb - 1), (x + lean, rb - bh + 1)], hi_); ink(g, bk)
                x += bw + lean
                continue
            spine = rect(g, x, rb - bh, x + bw - 1, rb - 1)
            g.fill(spine, base)
            g.fill(rect(g, x, rb - bh, x, rb - 1), hi_)                 # the lit edge
            if bw >= 4 and d < 1:
                g.fill(rect(g, x + 1, rb - bh + 3, x + bw - 2, rb - bh + 3), hi_)     # a title band, no letters
                g.fill(rect(g, x + 1, rb - 4, x + bw - 2, rb - 4), hi_)
            g.fill(rect(g, x + bw - 1, rb - bh, x + bw - 1, rb - 1), 'K')
            x += bw
        brd = P(g, (275, bd), (353, bd - 1), (353, bd + 2), (275, bd + 3))
        g.fill(brd, 'b')
        L_(g, [(275, bd), (353, bd - 1)], 'o' if abs(bd - 140) < 30 else 'b')
        L_(g, [(275, bd + 3), (353, bd + 2)], 'K')
    # the clamp lamp
    g.fill(inner & (radial(331, 126, 9, 7) < 1) & (g.a != 'K'), 'o')              # the hot spot it throws
    neck = [(345, 114), (350, 119), (353, 127), (353, 136), (352, 142)]
    L_(g, [(x + 1, y) for x, y in neck], 'K'); L_(g, neck, 'V'); L_(g, [(x - 1, y) for x, y in neck], 'K')
    clamp = rect(g, 346, 141, 358, 143) | rect(g, 350, 144, 353, 152)
    g.fill(clamp, 'V'); L_(g, [(346, 141), (358, 141)], 'l'); ink(g, clamp)
    g.fill(rect(g, 348, 151, 355, 152), 'v'); ink(g, rect(g, 348, 151, 355, 152))
    shade = P(g, (324, 115), (336, 109), (344, 110), (348, 115), (345, 123), (339, 129))
    g.fill(shade, 'V')
    g.fill(shade & (YY < 114), 'l'); L_(g, [(330, 112), (343, 109)], 'L')
    g.fill(shade & (XX > 343), 'v')
    mouth = tilted(g, 331.5, 122.5, 4.2, 8.5, -48)
    g.fill(mouth, 'y'); g.fill(tilted(g, 331.5, 122.5, 2.2, 5.0, -48), 'W')
    ink(g, shade | mouth)
    ink(g, case | side)
    L_(g, [(270, 83), (358, 75)], 'b')
    L_(g, [(358, 75), (392, 71)], 'r')
    # on top: a cardboard box, a stack of manga, a fern in a pot
    box = P(g, (278, 61), (306, 59), (310, 64), (310, 80), (278, 81))
    g.fill(box, 'V')
    g.fill(box & (YY < 66), 'l'); g.fill(box & (XX > 305), 'v')
    L_(g, [(278, 66), (310, 64)], 'K'); L_(g, [(279, 60), (306, 58)], 'L')
    g.fill(rect(g, 289, 70, 297, 71), 'K')                            # its hand hole
    ink(g, box)
    for i, cv in enumerate(['c', 'V', 'r', 'v', 'b']):                 # manga lying flat: covers and page edges
        yb = 79 - i * 3
        st = rect(g, 313 + (i % 2), yb - 2, 333 - (i % 3), yb)
        g.fill(st, 'L'); g.fill(rect(g, 313 + (i % 2), yb - 2, 333 - (i % 3), yb - 2), cv)
        g.fill(rect(g, 313 + (i % 2), yb - 2, 315 + (i % 2), yb), cv)  # the spine wraps round the left end
        ink(g, st, 'K', 'lr')
    L_(g, [(313, 64), (332, 64)], 'K')
    pot = P(g, (342, 64), (360, 64), (357, 78), (345, 78))
    leaves = np.zeros((H, W), bool)
    lit = np.zeros((H, W), bool)
    for k, (ang, ln) in enumerate([(-104, 17), (-80, 21), (-58, 22), (-36, 20), (-14, 18), (6, 19), (26, 21),
                                   (48, 22), (72, 21), (98, 17), (-46, 14), (36, 14)]):
        r = np.radians(ang)
        cx_, cy_ = 351 + np.sin(r) * ln / 2, 63 - np.cos(r) * ln / 2 * (.8 if abs(ang) > 60 else 1)
        lf = tilted(g, cx_, cy_, 2.4, ln / 2, ang)
        leaves |= lf
        if k % 3 != 2:
            lit |= lf & ~sh(lf, 0, -2)                                  # the upper face of each frond
    g.fill(leaves, 'N')
    g.fill(lit, 'v')
    g.fill(leaves & ~sh(leaves, 1, 1), 'g')                           # lit edges, toward the window
    ink(g, leaves)
    g.fill(pot, 'b'); g.fill(pot & (XX > 354), 'r'); g.fill(rect(g, 341, 62, 361, 65), 'o')
    ink(g, pot); ink(g, rect(g, 341, 62, 361, 65))
    M['bookshelf'] = case | side | grow(shade, 1) | box | rect(g, 312, 62, 334, 80) | leaves | pot | rect(g, 341, 62, 361, 65)


def tv(g, M, S):
    """The CRT (rank 7, Letterboxd): small and dim in the corner on a low cabinet; a boxy set seen nearly straight
    on, its side receding into the corner, a dark curved screen holding a faint reflection of the window, a pink
    standby light."""
    cab = P(g, (372, 224), (447, 221), (447, 244), (372, 246))
    g.fill(cab, 'r'); L_(g, [(372, 224), (447, 221)], 'b'); ink(g, cab)
    front = rect(g, 386, 177, 440, 223)
    for cx_, cy_ in [(386, 177), (440, 177), (386, 223), (440, 223)]:
        front[cy_, cx_] = False
    side = P(g, (441, 177), (447, 172), (447, 221), (441, 223))
    lid = P(g, (387, 176), (392, 172), (447, 169), (447, 172), (441, 176))
    g.fill(front, 'v'); g.fill(side, 'N'); g.fill(lid, 'V')
    L_(g, [(387, 178), (387, 222)], 'V')                                # the edge the window lights
    scr = rect(g, 392, 181, 433, 213)
    for cx_, cy_ in [(392, 181), (433, 181), (392, 213), (433, 213)]:
        scr[cy_, cx_] = False
    g.fill(scr, 'N')
    g.fill(scr & ~shrink(scr, 2), 'n')                                 # the glass curving away at its rim
    refl = P(g, (397, 186), (412, 185), (410, 200), (396, 201))        # the window, faintly, in the glass
    g.fill(refl, 'v'); L_(g, [(397, 186), (412, 185)], 'V'); L_(g, [(404, 186), (403, 200)], 'N')
    L_(g, [(395, 184), (399, 183)], 'L'); g[394, 185] = 'l'             # a glint
    ink(g, scr)
    for bx in (416, 422, 428):                                           # the control strip
        g.fill(rect(g, bx, 217, bx + 3, 218), 'N')
    g.fill(rect(g, 435, 217, 436, 218), 'h')                             # standby light
    L_(g, [(392, 216), (410, 216)], 'N'); L_(g, [(392, 219), (410, 219)], 'N')   # the speaker slots
    ink(g, front | side | lid)
    M['tv'] = front | side | lid | cab


def bed(g, M, S):
    """The bed (traced from the underlay): two planes, the blanket's top and the face where it hangs over the side to a
    wavy hem, with a lit rounded edge between them; wooden drawers below; a soft pillow at the head; the blanket
    turned down beside it. Light is laid in smooth hard-stepped fields (lamp from above the shelf, the phone's cold
    pool), not graded from the underlay, so the cloth reads as cloth. The panda plush sits by the wall."""
    frame = P(g, (198, 280), (447, 280), (447, 319), (198, 319))
    g.fill(frame, 'r')
    g.fill(frame & (YY > 312), 'K')
    for d0, d1 in [(212, 318), (328, 440)]:                          # two drawers, each with a pull
        dr = P(g, (d0, 297), (d1, 296), (d1, 312), (d0, 313))
        g.fill(dr, 'r'); L_(g, [(d0, 297), (d1, 296)], 'b'); ink(g, dr)
        hx = (d0 + d1) // 2
        g.fill(rect(g, hx - 8, 303, hx + 8, 304), 'K'); L_(g, [(hx - 8, 302), (hx + 8, 302)], 'b')
    top = P(g, (204, 236), (214, 226), (250, 222), (447, 218), (447, 254), (380, 258), (300, 262), (240, 262),
            (214, 258), (204, 250))
    face = P(g, (204, 250), (214, 258), (240, 262), (300, 262), (380, 258), (447, 254), (447, 292), (420, 291),
             (396, 294), (380, 292), (352, 295), (326, 293), (300, 296), (276, 293), (256, 295), (236, 292),
             (214, 288), (204, 278))
    # the top: violet, a broad lamp-lit band through the middle, darker at the far end and along the wall
    g.fill(top, 'v')
    lamp = radial(310, 236, 120, 24)
    g.fill(top & (lamp < 1), 'V')
    tone(g, top & (lamp >= 1) & (lamp < 1.18), 'v', 'V', 8)
    far = (XX - 400) + (YY - 236) * .9                                   # the far end, away from both lights
    g.fill(top & (far > 30), 'N'); tone(g, top & (far > 18) & (far <= 30), 'v', 'N', 8)
    g.fill(top & ~sh(top, 0, 3) & (YY < 232), 'N')                    # along the wall
    # the face: the blanket hanging down, in shade, darker toward the hem, with hanging folds
    g.fill(face, 'N')
    g.fill(face & (YY > 282), 'n')
    tone(g, face & (YY > 276) & (YY <= 282), 'N', 'n', 8)
    for f, sw in [([(226, 260), (230, 276), (228, 290)], 2), ([(276, 263), (281, 280), (279, 294)], 3),
                  ([(312, 266), (314, 282), (318, 294)], 1), ([(352, 262), (349, 280), (352, 295)], 3),
                  ([(404, 264), (410, 292)], 2)]:
        for d in range(1, sw + 1):                                     # each fold's shadow side
            L_(g, [(x + d, y) for x, y in f], 'n', face)
        L_(g, [(x - 1, y) for x, y in f[:2]], 'v', face)                 # and its lit ridge, near the edge
    # the rounded edge between them, lit
    edge = [(204, 250), (214, 258), (240, 262), (300, 262), (380, 258), (447, 254)]
    L_(g, edge, 'l')
    L_(g, [(x, y + 1) for x, y in edge], 'v')
    ink(g, top | face)
    L_(g, [(204, 236), (204, 278), (214, 288)], 'K')
    # wrinkles on the top: a shadow line with its lit lip above
    for w in [[(352, 244), (370, 240), (388, 242)], [(396, 234), (414, 230), (432, 232)], [(270, 252), (284, 249)],
              [(392, 250), (404, 247)], [(300, 228), (318, 226)]]:
        L_(g, w, 'N', top)
        L_(g, [(x, y - 1) for x, y in w], 'l' if w[0][0] < 380 else 'V', top)
    # the blanket turned down beside the pillow: a curved band, lit on top, its fold edge dark
    tb = P(g, (270, 224), (280, 223), (272, 236), (258, 252), (248, 262), (238, 262), (250, 248), (262, 234))
    g.fill(tb & top, 'l')
    g.fill(tb & top & (XX < 258 + (YY - 240) * -.8), 'V')
    L_(g, [(280, 223), (272, 236), (258, 252), (248, 262)], 'K', grow(top, 1))
    L_(g, [(281, 224), (273, 237), (259, 253), (249, 263)], 'N', top)
    sheet = top & (XX < 262 + (YY - 234) * -.9)                        # the sheet beyond it, pale and flat
    g.fill(sheet & ~tb, 'V')
    # the pillow: a soft rounded block, top face lit, its front in lavender, a dent, its shadow on the sheet
    pil = P(g, (206, 229), (211, 222), (220, 218), (244, 216), (264, 217), (274, 221), (278, 228), (276, 237),
            (270, 242), (246, 245), (218, 245), (208, 241))
    g.fill(sh(pil, 3, 2) & ~pil & top, 'v')
    g.fill(pil, 'l')
    g.fill(pil & (YY < 228), 'L')
    g.fill(pil & (YY > 237), 'V')
    g.fill(pil & ~sh(pil, -3, -1) & (XX > 262), 'V')
    L_(g, [(214, 222), (242, 218), (266, 219)], 'W')
    L_(g, [(236, 228), (246, 232), (256, 230)], 'V')                  # the dent
    L_(g, [(212, 236), (240, 238), (270, 236)], 'v')                  # the seam round its middle
    ink(g, pil)
    # phone (rank 2): bright screen, a cool pool of light on the blanket
    pool = radial(293, 256, 30, 11)
    poolm = top & (pool < 1) & ~pil
    bands(g, poolm, pool, ['W', 'L', 'l'], steps=(0, 8, 16))
    tone(g, top & (pool >= 1) & (pool < 1.3) & ~pil & np.isin(g.a, ['v', 'V']), 'V', 'l', 8)
    ph = P(g, (279, 252), (296, 245), (309, 258), (292, 266))
    sc = P(g, (281, 252), (296, 247), (306, 258), (292, 263))
    g.fill(ph, 'K'); g.fill(sc, 'C')
    bands(g, sc, radial(292, 254, 10, 6), ['W', 'C'], steps=(0, 8, 16))
    L_(g, [(287, 254), (296, 251)], 'c'); L_(g, [(289, 257), (300, 253)], 'c'); g[291, 260] = 'c'; g[293, 259] = 'c'
    M['phone'] = grow(ph, 3) & ~pil
    for k in ('tv', 'bookshelf'):                                # the bed hides the cabinet and the shelf's foot
        M[k] &= ~(frame | top | face | pil)
    S['bed_top'] = top
    panda(g, M, S)


def panda(g, M, S):
    """The panda plush, after the underlay's pose (sitting, arms at its sides, legs out, soles to us), drawn as a
    chibi plush: a wide head, ears and shoulder band in black, bean-shaped eye patches tilted down and out with the
    catchlights high on the inside, a nose and a small w mouth, blush. Hard cel shadows (shape minus itself moved
    toward the light), no dither on the fur; black fur against the black shelf goes navy with a lit top."""
    x0, y0 = 318, 201
    p = Grid(42, 57)
    yy, xx = np.mgrid[0:p.h, 0:p.w]
    E = lambda a, b, c, d: ellipse(p, a, b, c, d)
    cx = 20.5
    # back to front: legs, body, shoulder band and arms, ears, head
    leg_l = tilted(p, 9.5, 49, 6.5, 8.5, 62)
    leg_r = tilted(p, 31.5, 49, 6.5, 8.5, -62)
    body = E(8, 25, 32, 53)
    band = E(5, 25, 36, 37) & (yy <= 32)
    arm_l = tilted(p, 8, 37, 4.6, 8.5, 12)
    arm_r = tilted(p, 33, 37, 4.6, 8.5, -12)
    ear_l = E(2, 0, 13, 10)
    ear_r = E(28, 0, 39, 10)
    head = squircle(p, cx, 16.2, 15.5, 11.4, 2.3)
    arms = band | arm_l | arm_r
    white_body = body & ~(arms | leg_l | leg_r)
    p.fill(leg_l | leg_r, 'K')
    p.fill(body, 'L')
    p.fill(arms, 'K')
    p.a[grow(arm_l | arm_r, 1) & ~arms & (leg_l | leg_r)] = 'N'          # where an arm lies on a leg
    p.fill(ear_l | ear_r, 'K')
    p.fill(head, 'L')

    # cel shading on the white: lamp from above-left, so a hard shadow down the right and under the chin
    p.a[white_body & sh(head, 0, 3) & ~head] = 'l'                       # the chin's shadow on the belly
    p.a[white_body & ~sh(body, -4, -2)] = 'l'
    p.a[head & ~sh(head, -4, -3)] = 'l'
    p.a[head & ~sh(head, -2, -1) & (xx > 26)] = 'V'
    p.a[white_body & ~sh(body, -2, -1) & (xx > 24)] = 'V'
    p.a[head & ~sh(head, 1, 1) & (yy < 9) & (xx > 8) & (xx < 17)] = 'W'  # a short shine on the crown

    # the black parts: a short glint on each ear, a rim of lamp light on the shoulders and arms, phone light on the legs
    for ear in (ear_l, ear_r):                                # navy-black against the black shelf, lit on top
        e = ear & ~head
        p.a[e] = 'N'
        p.a[e & ~sh(ear, 0, 2)] = 'v'
        p.a[e & ~sh(ear, -2, -1)] = 'K'
    for part in (arm_l | band, arm_r):
        p.a[part & ~sh(part, 1, 1) & (p.a == 'K') & ~head & (yy > 26)] = 'v'
    for part in (leg_l, leg_r):
        p.a[part & ~sh(part, 1, -1) & (p.a == 'K')] = 'v'

    # face
    p.fill(tilted(p, 13.5, 17, 3.6, 5.2, 28), 'K')
    p.fill(tilted(p, 27.5, 17, 3.6, 5.2, -28), 'K')
    for ex, ey in [(13, 14), (26, 14)]:                                   # eyes: catchlights high on the inside
        p.patch(ex, ey, '''
            WW
            WW
        ''')
    p.a[18, 12] = 'l'; p.a[18, 28] = 'l'                                  # the small second glint
    p.patch(18, 20, '''
        KKKKK
        .KKK.
        ..K..
    ''')
    p.a[20, 19] = 'V'                                                     # a shine on the nose
    p.patch(17, 23, '''
        K.....K
        .KK.KK.
    ''')
    for bx, by in [(7, 21), (32, 21)]:                                   # blush
        p.patch(bx, by, '''
            h.h
            .h.
        ''')
    # soles: felt pads facing us, with three toe beans
    for fx in (5, 30):
        p.fill(E(fx, 48, fx + 6, 53), 'l')
        p.a[50, fx + 1] = 'L'
        for tx, ty in [(fx - 1, 46), (fx + 3, 45), (fx + 7, 46)]:
            if 0 <= tx < p.w:
                p.a[ty, tx] = 'l'
    p.outline('K')

    g.fill(ellipse(g, x0 + 1, y0 + 51, x0 + 42, y0 + 59) & S['bed_top'], 'N')
    g.paste(p, x0, y0)
    m = np.zeros((H, W), bool)
    m[y0:y0 + p.h, x0:x0 + p.w] = p.a != '.'
    M['plush'] = grow(m, 1)


def on_quad(A, B, D):
    """Coordinates (u, v) of every pixel in the parallelogram A, B, A + (D - A) + (B - A): u runs A -> B, v runs
    A -> D. For drawing flat things lying in perspective (a newspaper on a desk) in their own terms."""
    ax, ay = A
    m = np.array([[B[0] - ax, D[0] - ax], [B[1] - ay, D[1] - ay]], float)
    inv = np.linalg.inv(m)
    px, py = XX + .5 - ax, YY + .5 - ay
    return inv[0, 0] * px + inv[0, 1] * py, inv[1, 0] * px + inv[1, 1] * py


def desk(g, M, S):
    """The desk under the window (traced from the underlay): a wooden top with a thick lit front edge, the cold pool
    the monitor throws on it; the PC (rank 3: a pale tower, the CRT with a flat glowing screen, the keyboard), the
    newspaper (rank 4) lying flat in front of the tower, a mug, cables."""
    top = P(g, (0, 240), (37, 236), (130, 231), (206, 228), (206, 253), (0, 274))
    apron = P(g, (0, 274), (206, 253), (206, 261), (0, 283))
    under = P(g, (0, 283), (206, 261), (206, 319), (0, 319))
    g.fill(under, 'K'); tone(g, under & (YY < 296), 'K', 'n', 4)
    g.fill(top, 'r')
    pool = radial(70, 250, 74, 20)
    g.fill(top & (pool < 1), 'b')
    tone(g, top & (pool >= 1) & (pool < 1.25), 'r', 'b', 8)
    for gy in (244, 252, 260, 267):                                   # grain, along the front edge
        L_(g, [(0, gy), (206, gy - 21)], 'r', top & (pool < 1))
    g.fill(apron, 'r')
    ink(g, top | apron)
    L_(g, [(0, 274), (206, 253)], 'o')                               # the lit front edge
    L_(g, [(0, 275), (206, 254)], 'b')
    for lx in (28, 186):
        leg = rect(g, lx, 278 if lx < 100 else 262, lx + 6, 319)
        g.fill(leg, 'r'); L_(g, [(lx, 270), (lx, 319)], 'b', leg); ink(g, leg)
    L_(g, [(36, 306), (186, 292)], 'r')                               # the crossbar

    # PC tower: a pale case under the monitor's cold light, its side in shadow
    tw = P(g, (8, 176), (37, 175), (37, 248), (8, 251))
    tside = P(g, (0, 178), (8, 176), (8, 251), (0, 253))
    g.fill(tw, 'V')
    g.fill(tw & (XX > 31), 'l')                                       # the edge toward the monitor
    g.fill(tw & (YY > 236), 'v'); tone(g, tw & (YY > 228) & (YY <= 236), 'V', 'v', 8)
    L_(g, [(9, 177), (36, 176)], 'L')
    g.fill(tside, 'v'); g.fill(tside & (YY > 230), 'N')
    for yy in (183, 192):                                             # two drive bays, a button each
        bay = P(g, (12, yy), (33, yy - 1), (33, yy + 5), (12, yy + 6))
        g.fill(bay, 'v'); L_(g, [(12, yy + 6), (33, yy + 5)], 'l'); ink(g, bay)
        g.fill(rect(g, 28, yy + 2, 30, yy + 3), 'N')
    fl = P(g, (12, 206), (26, 205), (26, 210), (12, 211))
    g.fill(fl, 'v'); L_(g, [(14, 208), (24, 207)], 'K'); ink(g, fl)
    g.fill(rect(g, 30, 207, 32, 208), 'v')                            # the floppy's eject button
    g.fill(rect(g, 30, 218, 31, 219), 'g'); g.fill(rect(g, 26, 218, 27, 219), 'o')    # power and drive lights
    for yy in range(226, 246, 3):                                     # vents
        L_(g, [(13, yy + 1), (31, yy)], 'N', tw)
    ink(g, tw | tside)

    # monitor: a pale CRT with a crisp black silhouette against the city; the screen is flat and bright
    body = P(g, (38, 168), (44, 165), (44, 226), (38, 222))           # its side, in shadow
    bez = P(g, (44, 166), (120, 164), (122, 226), (42, 228))
    g.fill(body, 'v'); g.fill(bez, 'V')
    g.fill(bez & (YY > 219), 'v')
    L_(g, [(45, 167), (119, 165)], 'L'); L_(g, [(45, 168), (45, 226)], 'l')
    scr = P(g, (54, 175), (116, 173), (117, 217), (55, 219))
    g.fill(grow(scr, 1), 'K')
    g.fill(scr, 'C')
    g.fill(scr & ~sh(scr, -2, -2), 'c')                               # the curve of the glass, down and right
    glare = P(g, (57, 177), (78, 176), (64, 190), (57, 196))
    g.fill(glare & scr, 'W')
    g.fill(P(g, (82, 176), (88, 176), (70, 196), (65, 199)) & scr, 'W')
    rng = np.random.default_rng(3)
    for i, yy in enumerate(range(181, 213, 4)):                      # a terminal: indented runs, no letters
        ind = [0, 4, 4, 8, 8, 4, 0, 4][i % 8]
        x = 60 + ind
        while x < 108:
            n = int(rng.integers(3, 9))
            g.fill(rect(g, x, yy, min(x + n, 110), yy) & scr & (g.a != 'W'), 'c')
            x += n + 2
            if rng.random() < .28:
                break
    g.fill(rect(g, 60, 211, 62, 213), 'c')
    g.fill(rect(g, 110, 222, 113, 223), 'C'); g[114, 222] = 'g'        # the monitor's own power light
    ink(g, bez | body)
    stand = P(g, (72, 228), (90, 227), (92, 233), (70, 234))
    base = P(g, (62, 234), (100, 232), (104, 237), (60, 238))
    g.fill(stand | base, 'v'); L_(g, [(62, 234), (100, 232)], 'l'); ink(g, stand | base)
    # keyboard
    kb = P(g, (66, 240), (130, 229), (136, 240), (72, 251))
    g.fill(kb, 'N')
    for row in range(4):                     # rows of keys along the keyboard's slant: top face, lit edge
        for k in range(16):
            kx = 70 + row * 1.6 + k * 4
            ky = 240 - k * .68 + row * 2.6
            key = rect(g, int(kx), int(ky), int(kx) + 2, int(ky) + 1) & kb
            g.fill(key, 'v'); g.fill(rect(g, int(kx), int(ky), int(kx) + 2, int(ky)) & kb, 'V')
    g.fill(rect(g, 88, 248, 108, 249) & kb, 'v')        # space bar
    g.fill(polyline(g, [(66, 240), (130, 229)]), 'l')
    ink(g, kb)
    # mug
    mug = P(g, (131, 212), (143, 211), (143, 226), (131, 227))
    g.fill(mug, 'v'); cel(g, mug, ['N', 'v', 'l'], steps=(0, 8, 16))
    g.fill(ellipse(g, 131, 209, 143, 214), 'N'); g.fill(ellipse(g, 133, 210, 141, 213), 'K')
    L_(g, [(144, 215), (147, 216), (147, 221), (144, 222)], 'v')
    ink(g, mug | ellipse(g, 131, 209, 143, 214))
    M['pc'] = tw | tside | bez | body | stand | base | kb

    # newspaper (rank 4): lying flat on the desk in front of the tower, folded open; drawn in its own (u, v) so the
    # masthead, the photo and the columns of type lie in the desk's perspective. Lit from the monitor (right).
    A, B, D = (2, 254), (40, 241), (40, 269)
    u, v = on_quad(A, B, D)
    pap = (u >= 0) & (u <= 1) & (v >= 0) & (v <= 1)
    g.fill(sh(pap, 0, 2) & ~pap & top, 'K')                           # its shadow on the wood
    g.fill(pap, 'L')
    g.fill(pap & (u > .5), 'W')                                       # the right page faces the monitor
    g.fill(pap & (u < .18), 'l')
    g.fill(pap & (u > .07) & (u < .45) & (v > .1) & (v < .2), 'N')   # masthead: a dark band, no letters
    g.fill(pap & (u > .07) & (u < .45) & (v > .24) & (v < .27), 'v')
    g.fill(pap & (u > .57) & (u < .93) & (v > .1) & (v < .46), 'V')  # a photo
    g.fill(pap & (u > .57) & (u < .93) & (v > .3) & (v < .46) & (v > .6 - .5 * u), 'v')
    for v0 in np.arange(.34, .94, .085):                              # columns of type
        for u0, u1 in [(.07, .25), (.28, .45), (.57, .75), (.78, .93)]:
            if v0 < .5 and u0 > .5:
                continue
            g.fill(pap & (u > u0) & (u < u1) & (np.abs(v - v0) < .025), 'l' if u0 < .5 else 'L')
    g.fill(pap & (np.abs(u - .5) < .018), 'l')                         # the fold
    ink(g, pap)
    M['newspaper'] = pap


def chair(g, M, S):
    """The office chair, back to us, with the hoodie thrown over its backrest (traced from the underlay): the hood
    bunched over the top and hanging down the back in a U, the left sleeve dangling down the side, the body falling in
    long folds to a ribbed hem. Light comes from the monitor on the left: each fold is lit on its left and drops into a
    hard shadow on its right, and a cold rim runs down the left edge."""
    seat = ellipse(g, 100, 290, 168, 324)
    g.fill(seat, 'n'); g.fill(seat & (YY < 296), 'N')
    L_(g, [(104, 296), (124, 292), (150, 292)], 'v', seat)
    ink(g, seat)
    hoodie = P(g, (147, 223), (152, 220), (160, 218), (168, 217), (176, 216), (184, 217), (190, 219), (194, 224),
               (196, 232), (197, 250), (198, 270), (199, 290), (198, 306), (197, 319), (138, 319), (137, 306),
               (133, 299), (130, 284), (130, 268), (132, 252), (136, 240), (141, 230))
    sleeve = P(g, (141, 230), (147, 224), (150, 232), (147, 250), (144, 270), (143, 290), (140, 301), (133, 299),
               (130, 284), (130, 268), (132, 252), (136, 240))
    hood = P(g, (151, 224), (158, 220), (168, 218), (178, 217), (188, 219), (193, 226), (193, 236), (186, 244),
             (175, 249), (163, 246), (155, 239), (150, 231))
    body = hoodie & ~sleeve
    g.fill(hoodie, 'V')
    g.fill(body & (XX > 189), 'v')                                    # the right side turns away
    tone(g, body & (XX > 185) & (XX <= 189), 'V', 'v', 8)
    for f, sw in [([(153, 252), (150, 270), (151, 290), (154, 306)], 3), ([(166, 256), (164, 274), (165, 306)], 2),
                  ([(181, 251), (184, 268), (183, 290), (181, 306)], 3), ([(158, 280), (159, 306)], 1),
                  ([(173, 262), (175, 284), (174, 300)], 2), ([(190, 270), (192, 300)], 1)]:
        for d in range(1, sw + 1):                                   # the shadow side of each fold
            L_(g, [(x + d, y) for x, y in f], 'v', body)
        L_(g, f, 'n', body)
    for r in [[(152, 254), (149, 268)], [(180, 253), (183, 266)], [(165, 258), (163, 270)]]:
        L_(g, r, 'l', body)                                          # lit ridges where the folds start
    # the ribbed hem
    hem = P(g, (137, 306), (168, 309), (198, 306), (198, 314), (168, 317), (138, 314))
    g.fill(hem, 'v')
    for hx in range(139, 198, 3):
        L_(g, [(hx, 308), (hx, 316)], 'N', hem)
    L_(g, [(137, 306), (168, 309), (198, 306)], 'n')
    # the hood: lit crown, a seam down the middle, the far half in shade, a cast shadow under its U
    under = sh(hood, 0, 3) & ~hood & hoodie
    g.fill(under, 'v'); g.fill(under & sh(hood, 0, 1), 'N')
    g.fill(hood, 'V')
    g.fill(hood & (XX > 178), 'v'); tone(g, hood & (XX > 174) & (XX <= 178), 'V', 'v', 8)
    L_(g, [(153, 223), (160, 220), (170, 219), (184, 219)], 'l')
    L_(g, [(155, 222), (166, 220)], 'L')
    L_(g, [(172, 220), (173, 232), (175, 248)], 'n', hood)
    L_(g, [(158, 226), (164, 236), (172, 242)], 'v', hood)             # a soft crease in the bunched hood
    ink(g, hood)
    # the sleeve: lit, its inner edge against the body, a cuff
    g.fill(sleeve, 'V'); g.fill(sleeve & (XX < 136), 'l')
    L_(g, [(147, 226), (146, 250), (143, 272), (142, 292), (140, 300)], 'n')
    cuff = sleeve & (YY >= 293)
    g.fill(cuff, 'v')
    for cx_ in range(132, 142, 2):
        L_(g, [(cx_, 293), (cx_, 301)], 'N', cuff)
    L_(g, [(131, 292), (143, 293)], 'n')
    ink(g, hoodie)
    # the monitor's cold light down the left edge
    rim = [(147, 223), (141, 230), (136, 240), (132, 252), (130, 268), (130, 284), (133, 298)]
    L_(g, [(x + 1, y + 1) for x, y in rim], 'C', hoodie)
    L_(g, [(x + 2, y + 1) for x, y in rim[2:]], 'c', hoodie)
    S['chair'] = hoodie | seat
    M['pc'] &= ~(hoodie | seat)                                       # the chair stands in front of the desk


def floor_things(g, M, S):
    """A cable across the floor by the bed."""
    L_(g, [(206, 300), (214, 306), (222, 304)], 'N')


def butterfly(g, M, S):
    """The butterfly ornament on the sill (rank 6, Bluesky): glowing cyan wings on a little stand."""
    bx, by = 202, 166
    halo = radial(bx + 7, by + 7, 16, 12)
    hm = (halo < 1) & ~S['glass'] & ~S['frame'] | (halo < 1) & S['sill']
    tone(g, hm & (halo > .6) & np.isin(g.a, ['v', 'N', 'c']), 'v', 'c', 4)
    fly = Grid.parse('''
        .KK.........KK.
        KCCK.......KCCK
        KCWCK.....KCWCK
        KCWWCK...KCWWCK
        KCCWCCK.KCCWCCK
        .KCCCCKKKCCCCK.
        ..KCCCCKCCCCK..
        ..KcCCKKKCCcK..
        .KccCK.K.KCccK.
        .KccK..K..KccK.
        ..KK...K...KK..
        ......KKK......
        .....KNNNK.....
    ''')
    g.paste(fly, bx, by)
    m = np.zeros((H, W), bool)
    m[by:by + fly.h, bx:bx + fly.w] = fly.a != '.'
    M['butterfly'] = grow(m, 2)


def finish(g, M, S):
    """Last touches: glints."""
    # glints
    for x, y, c in [(118, 166, 'W'), (34, 177, 'L'), (136, 213, 'L'), (443, 173, 'l')]:
        g[x, y] = c


PASSAGES = ['shell', 'window', 'city', 'wall_things', 'shelf', 'tv', 'bed', 'desk', 'chair', 'floor_things',
            'butterfly', 'finish']
FUNCS = {'shell': shell, 'window': window, 'city': city, 'wall_things': wall_things, 'shelf': shelf, 'tv': tv,
         'bed': bed, 'desk': desk, 'chair': chair, 'floor_things': floor_things, 'butterfly': butterfly,
         'finish': finish}


def paint(upto=None):
    g = Grid(W, H, 'n')
    M, S = {}, {}
    for name in PASSAGES:
        FUNCS[name](g, M, S)
        if name == upto:
            break
    return g, M, S


def progress(g, name):
    """The painting beside the underlay, both at 2x: the look after each passage."""
    d = OUT / 'progress'
    d.mkdir(parents=True, exist_ok=True)
    a = g.image(LEGEND).convert('RGB').resize((W * 2, H * 2), Image.NEAREST)
    b = UNDER.resize((W * 2, H * 2), Image.NEAREST)
    sheet = Image.new('RGB', (W * 4 + 8, H * 2), (30, 30, 30))
    sheet.paste(a, (0, 0)); sheet.paste(b, (W * 2 + 8, 0))
    sheet.save(d / f'{name}.png')
    return d / f'{name}.png'


if __name__ == '__main__':
    upto = sys.argv[1] if len(sys.argv) > 1 else None
    g, M, S = paint(upto)
    print('wrote', progress(g, upto or 'all'))
    OUT.mkdir(parents=True, exist_ok=True)
    g.image(LEGEND).save(OUT / 'room_rgba.png')
    print('colours used:', len(g.colors()))
