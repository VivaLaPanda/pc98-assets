"""blog-icon: nav icon candidates for "Panda's Manifestos". Run: uv run pc98 render blog-icon [names...]

Each candidate is drawn by hand in code at 48x48 in VGA letters (the Windows 98 convention of the site's original
icons), then recoloured into the frame's PC-98 palette. Paper goes periwinkle in the recolour, as the user's own
envelope recolour did; white is kept for highlights. The generated references in refs/ were used only for
composition; no generated pixels are in these grids.

A drawing returns (grid, masks): masks name regions (the seal, the feather...) so the recolour can treat them
differently from the paper even where the original uses the same VGA colour.
"""
import sys
from pathlib import Path

import numpy as np

from pc98.pixel import Grid, rect, ellipse, poly, line, polyline, grow
from pc98 import icon, palette as P
from pc98.icon import PAPER, recolor, words, place

HERE = Path(__file__).parent
OUT = HERE / 'out'


# ---------------------------------------------------------------------------------------------------------------
# A. newspaper, square to the frame like the envelope: a front page over a second sheet, the bottom corner curling.
#    (A first version lay tilted, drawn flat and Grid.skew()ed 1:4; every edge and line became a staircase and it
#    looked busier than any original, so it was dropped. See brief.md.)
# ---------------------------------------------------------------------------------------------------------------

def newspaper():
    g = Grid(48, 48)
    m = {}
    back = rect(g, 11, 2, 43, 40)                            # the sheet behind, showing at the top and right
    g.fill(back, 'W')
    g.dither(rect(g, 11, 2, 43, 40) & ~rect(g, 11, 2, 42, 3), 'W', 'S')
    g.fill(rect(g, 12, 3, 42, 3), 'W')
    g.edge(back, 'G', 'tl'); g.edge(back, 'K', 'br')
    F = rect(g, 4, 6, 37, 45)                                # the front page
    curl = poly(g, [(31, 45), (37, 39), (37, 45)])           # bottom-right corner, curled up
    g.fill(F, 'W')
    g.clear(curl)
    F = F & ~curl
    g.edge(F, 'G', 'tl'); g.edge(F, 'K', 'br')
    flap = poly(g, [(31, 44), (36, 39), (31, 39)])
    g.fill(flap, 'S'); g.dither(flap & ~line(g, 31, 44, 36, 39), 'S', 'W', pattern='checker')
    g.edge(flap, 'G'); g.fill(line(g, 32, 44, 37, 39), 'K')
    m['paper'] = F | back
    g.fill(rect(g, 6, 8, 35, 12), 'K')                       # masthead
    g.patch(8, 10, 'WW.W.WW.WWW.W.WW.W.WWW.W.WW')            # the title, as type too small to read
    m['title'] = rect(g, 8, 10, 34, 10) & (g.a == 'W')
    g.fill(rect(g, 6, 14, 35, 14), 'G')                      # rule
    g.fill(rect(g, 6, 16, 22, 17) | rect(g, 24, 16, 32, 17), 'K')   # headline
    ph = rect(g, 6, 20, 18, 31)                              # photo
    g.fill(ph, 'c')
    g.dither(rect(g, 7, 21, 17, 23), 'c', 'W')
    g.fill(ellipse(g, 10, 22, 14, 26), 'G')
    g.fill(rect(g, 8, 27, 16, 30) & ellipse(g, 7, 27, 17, 36), 'G')
    g.edge(ph, 'K')
    m['photo'] = ph
    for i, n in enumerate([15, 14, 15, 11, 15, 13]):        # text
        g.fill(rect(g, 21, 20 + 2 * i, 21 + n - 1, 20 + 2 * i), 'G')
    for i, n in enumerate([13, 11, 13, 9, 12]):
        g.fill(rect(g, 6, 33 + 2 * i, 6 + n - 1, 33 + 2 * i), 'G')
    for i, n in enumerate([15, 12, 14]):
        g.fill(rect(g, 21, 33 + 2 * i, 21 + n - 1, 33 + 2 * i), 'G')
    g.fill(rect(g, 21, 39, 29, 39), 'G')
    return g, m


def newspaper_rc(g, m):
    out = recolor(g, {**PAPER, 'c': 'k'})
    out.fill(m['title'], 'p')
    return out


# ---------------------------------------------------------------------------------------------------------------
# B. scroll: a manifesto. Rolled at the top (spiral end on the right) and curling at the bottom (spiral on the
#    left), a proclamation, a wax seal with two notched ribbon tails.
# ---------------------------------------------------------------------------------------------------------------

SEAL = '''
....KKKK....
..KKRRRRKK..
.KRWWRRRRRK.
.KWRrrrrRRK.
KRRrRRRRRRRK
KRRrRRRRWRrK
KRRrRRRRWRrK
KRRRRRRRWRrK
.KRRWWWWRrK.
.KRRRRrrrrK.
..KKrrrrKK..
....KKKK....
'''


def scroll():
    g = Grid(48, 48)
    m = {}
    rng = np.random.default_rng(7)
    body = rect(g, 9, 8, 37, 39)                            # paper
    g.fill(body, 'W')
    g.dither(rect(g, 32, 9, 32, 38), 'W', 'S', pattern='q1')  # shading as the page turns away on the right:
    g.dither(rect(g, 33, 9, 34, 38), 'W', 'S')              #   sparse dots, a checker, then solid
    g.fill(rect(g, 35, 9, 36, 38), 'S')
    g.dither(rect(g, 36, 9, 36, 38), 'S', 'G')
    g.edge(body, 'G', 'l'); g.edge(body, 'K', 'r')
    roll = rect(g, 7, 2, 40, 9)                             # top roll, spiral end at the right
    g.fill(roll, 'W')
    g.dither(rect(g, 7, 5, 40, 5), 'W', 'S')                # light to shadow down the roll
    g.fill(rect(g, 7, 6, 40, 6), 'S')
    g.dither(rect(g, 7, 7, 40, 7), 'S', 'G')
    g.fill(rect(g, 7, 8, 40, 8), 'G')
    g.edge(roll, 'G', 'tl'); g.edge(roll, 'K', 'b')
    m['hi'] = rect(g, 8, 3, 39, 3)
    g.patch(38, 1, '''
        .KKKK.
        KWWSSK
        KWKKSGK
        KSK.KGK
        KSKKGGK
        KSGGGGK
        .KGGGK.
        ..KKK..
        ...KK..
    ''')
    bot = rect(g, 9, 38, 37, 44)                            # bottom curl, spiral at the left
    g.fill(bot, 'W')
    g.dither(rect(g, 9, 41, 37, 41), 'W', 'S')
    g.fill(rect(g, 9, 42, 37, 42), 'S')
    g.dither(rect(g, 9, 43, 37, 43), 'S', 'G')
    g.edge(bot, 'G', 't'); g.edge(bot, 'K', 'br')
    m['hi'] |= rect(g, 11, 39, 36, 39)
    g.patch(4, 37, '''
        ..KKKK.
        .KWWSSK
        KWKKKSK
        KSK.KGK
        KSGKKGK
        .KGGGK.
        ..KKK..
    ''')
    # the proclamation: a bold two-word title, two paragraphs of type, and a signature by the seal
    g.fill(rect(g, 13, 12, 21, 13) | rect(g, 24, 12, 31, 13), 'K')
    for y, ind, x1 in ((16, 2, 31), (18, 0, 31), (20, 0, 26), (23, 2, 31), (25, 0, 30), (27, 0, 19)):
        words(g, 13, x1, y, rng, indent=ind, lens=(2, 6))
    g.fill(polyline(g, [(12, 34), (13, 32), (14, 34), (15, 33), (16, 34), (17, 32), (18, 33), (20, 33)]), 'G')
    g.fill(rect(g, 12, 35, 20, 35), 'S')
    # ribbon tails: two broad bands splaying out from under the seal, notched at the ends; then the seal over them
    lt = poly(g, [(26, 37), (19, 44), (20, 46), (22, 44), (23, 47), (29, 40)])
    rt = poly(g, [(29, 38), (33, 47), (35, 45), (36, 47), (37, 44), (32, 36)])
    for t in (lt, rt):
        g.fill(t, 'R')
        g.edge(t, 'r', 'br')
        g.edge(t, 'K')
    tails = lt | rt
    m['seal'] = tails.copy()
    s = Grid.parse(SEAL)
    g.paste(s, 23, 29)
    sm = np.zeros((48, 48), bool)
    sm[29:29 + s.h, 23:23 + s.w] = s.a != '.'
    m['seal'] |= sm
    return g, m


def scroll_rc(g, m):
    out = recolor(g, PAPER, [(m['seal'], {'R': 'h', 'r': 'u', 'W': 'k'})])
    out.fill(m['hi'] & (g.a == 'W'), 'W')                   # keep the lit tops of the rolls white
    return out


# ---------------------------------------------------------------------------------------------------------------
# C. quill: a feather pen standing in an ink bottle, in front of a written page.
# ---------------------------------------------------------------------------------------------------------------

def quill():
    g = Grid(48, 48)
    m = {}
    page = rect(g, 3, 1, 30, 40)                            # the page, top-right corner turned down
    g.fill(page, 'W')
    g.clear(poly(g, [(25, 1), (30, 1), (30, 6)]))
    page = g.mask()
    g.edge(page, 'G', 'tl'); g.edge(page, 'K', 'br')
    fold = poly(g, [(25, 1), (25, 6), (30, 6)])
    g.fill(fold, 'S'); g.edge(fold, 'G')
    g.dither(rect(g, 26, 8, 26, 38), 'W', 'S', pattern='q1')    # the page in light: shading toward the right,
    g.dither(rect(g, 27, 8, 28, 38), 'W', 'S')                  #   as the newspaper and scroll are shaded
    g.dither(rect(g, 5, 38, 25, 38), 'W', 'S', pattern='q1')
    rng = np.random.default_rng(3)
    hand = np.zeros((48, 48), bool)                         # the letter, as Windows 98 draws text: grey type lines
    for y, ind, x1 in ((9, 2, 26), (12, 0, 26), (15, 0, 25), (18, 0, 21), (22, 2, 26), (25, 0, 26), (28, 0, 15)):
        hand |= words(g, 7, x1, y, rng, lens=(3, 8))
    g.fill(hand, 'G')
    # the feather: a vane along a gently curved shaft, from the bottle up to the top right, with two splits in it
    base, tip = np.array([21.0, 34.0]), np.array([44.0, 2.0])
    d = tip - base; u = d / np.linalg.norm(d); n = np.array([u[1], -u[0]])        # n: to the upper left
    if n[1] > 0:
        n = -n
    bend = lambda t: 2.0 * np.sin(np.pi * t)                 # noqa: E731 - the curve of the shaft
    left, right = [], []
    for t in np.linspace(0.2, 1.0, 48):
        s = (t - 0.2) / 0.8
        w = np.sin(np.pi * s ** 0.8) ** 0.55
        p = base + d * t + n * bend(t)
        left.append(tuple(p + n * (7.0 * w)))
        right.append(tuple(p - n * (3.8 * w)))
    vane = poly(g, left + right[::-1])
    for t, depth in ((0.42, 4.5), (0.66, 4.0)):              # splits in the barbs, cut back toward the base
        p = base + d * t + n * bend(t)
        q = p + n * 8.0 - u * 1.5
        vane &= ~poly(g, [tuple(p + n * (7.5 - depth)), tuple(q), tuple(q - u * 2.2)])
    g.fill(vane, 'W')
    g.fill(hand & grow(vane, 1) & ~vane, 'W')               # the writing stops short of the feather
    yy, xx = np.mgrid[0:48, 0:48]
    rel = (xx - base[0]) * n[0] + (yy - base[1]) * n[1] - np.interp(
        ((xx - base[0]) * u[0] + (yy - base[1]) * u[1]) / np.linalg.norm(d), np.linspace(0, 1, 50),
        [bend(t) for t in np.linspace(0, 1, 50)])
    g.fill(vane & (rel < 0), 'S')                            # the shadowed half: one tone, so the form reads
    g.dither(vane & (rel < 0) & (rel > -1.2), 'W', 'S')      #   with a checker where it turns
    v = n + u * 0.9                                          # barbs sweep up and out from the shaft
    g.fill(vane & (rel > 1.5) & (np.floor(-v[1] * xx + v[0] * yy) % 4 == 0), 'S')   # barbs on the lit half
    m['vane'] = vane.copy()
    g.edge(vane, 'G', 'tl'); g.edge(vane, 'K', 'br')
    m['vane_edge'] = vane & np.isin(g.a, ['G'])
    g.fill(m['vane_edge'] & page, 'K')                      # over the white page the outline has to be dark
    shaft = polyline(g, [tuple(base + d * t + n * bend(t)) for t in np.linspace(0.0, 0.96, 16)])
    g.fill(shaft & vane, 'G')
    g.fill(shaft & ~vane, 'K')
    m['shaft'] = shaft & vane
    m['feather'] = vane | shaft
    # the bottle: squat glass with sloping shoulders, dark with ink, a short neck and a rim
    body = poly(g, [(17, 36), (27, 36), (32, 40), (32, 45), (31, 46), (13, 46), (12, 45), (12, 40)])
    g.fill(body, 'G')                                       # dark glass...
    g.fill(body & rect(g, 0, 42, 47, 46), 'K')              # ...half full of black ink
    g.dither(body & rect(g, 0, 41, 47, 41), 'G', 'K')       # the ink's surface seen through the glass
    g.dither(body & rect(g, 0, 37, 22, 38), 'S', 'G')       # light on the shoulder, from the left
    g.fill(rect(g, 14, 40, 14, 44) | rect(g, 15, 39, 15, 39), 'W')   # the shine
    g.dither(rect(g, 30, 40, 30, 45), 'G', 'K')             # the far edge of the glass
    g.fill(rect(g, 29, 42, 29, 44), 'S')                    # a reflection on the far side
    g.edge(body, 'K')
    neck = rect(g, 18, 32, 26, 36)
    g.fill(neck, 'G')
    g.fill(rect(g, 19, 33, 25, 33), 'S')
    g.fill(rect(g, 20, 34, 24, 35), 'K')
    g.edge(neck, 'K')
    g.fill(shaft & rect(g, 0, 28, 47, 34), 'K')
    m['bottle'] = body | neck
    return g, m


def quill_rc(g, m):
    out = recolor(g, PAPER, [(m['feather'], {'W': 'W', 'S': 'k', 'G': 'u'}),
                             (m['bottle'], {'W': 'W', 'S': 'a', 'G': 'u'})])
    out.fill(m['vane_edge'], 'u')
    out.fill(m['shaft'], 'h')
    return out


CANDIDATES = {
    'newspaper': (newspaper, newspaper_rc),
    'scroll': (scroll, scroll_rc),
    'quill': (quill, quill_rc),
}


def export(name, draw, rc):
    g, m = draw()
    return icon.export(name, g, rc(g, m), OUT)


if __name__ == '__main__':
    names = sys.argv[1:] or list(CANDIDATES)
    for n in names:
        print('wrote', *export(n, *CANDIDATES[n]))
    for p in icon.review(OUT, list(CANDIDATES)):
        print('wrote', p)
