"""room-icon, round 2: the user found the chosen bed icon weak ("this icon kinda sucks", 2026-10-06). Run:
    uv run python assets/room-icon/draw2.py [candidate...]

Round 1's bed was a flat side view, its panda a flat black-and-white sticker floating at the headboard, and its tan and
brown wood sat outside the set's palette. Round 2 draws straight in the frame palette (SITE letters) so every shade is
chosen, not mapped: periwinkle bodies, plum shadows and lit-side outlines, black shadow-side outlines, white highlights,
mauve half-light, pink and hot pink accents; tan only where the globe uses it. Light from the top left, one mid tone
plus the 50% checker, no anti-aliasing.

Candidates:
  tuckedin     Panda's plush tucked into bed, seen from the foot: the RPG-inn view, headboard behind, quilt to its chin.
  nightwindow  the room's window at night: crescent moon, city lights, curtains tied back, the plush on the sill.
  ajar         the bedroom door ajar, warm light through the gap, a panda nameplate.
  moonpanda    the plush's head against a crescent moon: Panda, at night. (A pink nightcap was tried and dropped:
               with a white band and pom-pom it read as a Santa hat, and the room already lost a Santa-hat creature.)
"""
import sys
from pathlib import Path

import numpy as np

from pc98 import palette as P
from pc98.pixel import Grid, rect, ellipse, poly, line, polyline, grow, shrink
from pc98.sheet import icon_sheet
from pc98.config import SITE

OUT = Path(__file__).parent / 'out2'
LEG = 'site+'
NEIGHBOURS = ['computer', 'cd_audio', 'envelope_closed', 'globe_map', 'blog']
# SITE -> VGA, for the Windows-98-style <name>.png that sits beside each recolour in img/icons (the site shows only
# the recolour; the original keeps the pair convention).
TO_VGA = {'K': 'K', 'W': 'W', 'p': 'S', 'u': 'G', 'a': 'S', 'b': 'n', 'k': 'm', 'h': 'R', 'y': 'y', 'e': 'y',
          'n': 'o', 'r': 'r', 'm': 'c', 't': 't'}


def shade(g, m, lit='u', dark='K'):
    """The set's outline: plum on the lit top/left, black on the shadow bottom/right."""
    g.edge(m, lit, 'tl')
    g.edge(m, dark, 'br')


# ---------------------------------------------------------------------------------------------------------------
# Panda's plush head, the shared sprite. Drawn by hand: at this size every pixel of an eye patch is a choice.
# W face, a mauve half-light down the right, k blush, K ears / patches / nose, plum lit-side rim.
# ---------------------------------------------------------------------------------------------------------------

HEAD_S = '''
.KKK.......KKK.
KKKKKuuuuuKKKKK
KKKuWWWWWWWpKKK
KKuWWWWWWWWWpKK
.uWWWWWWWWWWpWK
uWWKKWWWWWKKpWK
uWKKWKWWWKWKKpK
uWKKKKWWWKKKKWK
uWWKKWWKWWKKpWK
.uWkWWKKKWWkpK.
..uWWWWKWWWpK..
...KpWpWpWpK...
....KKKKKKK....
'''


def panda_head_small():
    return Grid.parse(HEAD_S)


# ---------------------------------------------------------------------------------------------------------------
# A. tuckedin: a bed from the foot, slightly from above (the RPG-inn view) and a little from the left, so its right
#    side shows in shadow (the computer's three-quarter). Periwinkle frame, pink quilt with a hot-pink check, the
#    sheet folded over it, Panda's head on the pillow and its paws on the quilt.
# ---------------------------------------------------------------------------------------------------------------

def tuckedin():
    g = Grid(48, 48)
    # headboard behind: a panel with two posts and round caps
    hb = rect(g, 7, 6, 40, 17)
    g.fill(hb, 'p')
    g.dither(rect(g, 10, 9, 37, 15), 'p', 'a')
    g.fill(rect(g, 10, 8, 37, 8), 'u'); g.fill(rect(g, 9, 9, 9, 15), 'u')          # inset panel, carved edge
    g.fill(rect(g, 38, 9, 38, 15), 'W'); g.fill(rect(g, 10, 16, 37, 16), 'W')
    shade(g, hb)
    for x0 in (5, 39):
        post = rect(g, x0, 4, x0 + 3, 22)
        g.fill(post, 'p'); g.fill(rect(g, x0 + 2, 5, x0 + 3, 22), 'u'); g.fill(rect(g, x0 + 1, 5, x0 + 1, 21), 'W')
        shade(g, post)
        cap = ellipse(g, x0, 1, x0 + 3, 4)
        g.fill(cap, 'p'); g.fill(rect(g, x0 + 1, 2, x0 + 1, 2), 'W'); shade(g, cap)
    # pillow: mauve, lit at the top left, so the white face in front of it reads
    pil = rect(g, 10, 12, 37, 22) & ~(rect(g, 10, 12, 10, 12) | rect(g, 37, 12, 37, 12))
    g.fill(pil, 'a'); g.dither(rect(g, 11, 13, 22, 15), 'a', 'W')
    shade(g, pil)
    # quilt: pink, light near the fold, falling into shadow toward the right; dotted hot-pink quilting
    top = rect(g, 7, 22, 38, 40)
    g.fill(top, 'k')
    for y in range(30, 40, 4):
        g.dither(line(g, 8, y, 37, y), 'h', 'k', pattern='v')
    for x in range(12, 38, 6):
        g.dither(line(g, x, 27, x, 39), 'h', 'k', pattern='h')
    g.dither(rect(g, 33, 26, 38, 40), 'k', 'h', pattern='q1')
    # Panda's body under the quilt: a soft rise, lit on its upper left
    bump = ellipse(g, 12, 23, 35, 36) & top
    g.edge(bump & rect(g, 0, 0, 22, 47), 'W', 't'); g.edge(bump & rect(g, 24, 0, 47, 47), 'h', 't')
    shade(g, top)
    side = poly(g, [(39, 22), (42, 24), (42, 42), (39, 41)])
    g.fill(side, 'h'); g.dither(rect(g, 39, 31, 42, 42) & side, 'h', 'u')
    g.edge(side, 'K', 'br'); g.fill(line(g, 39, 22, 39, 41), 'u')
    # Panda's head on the pillow; the sheet folded over its chin; two paws on the fold
    g.paste(panda_head_small(), 16, 10)
    sheet = rect(g, 7, 21, 38, 25)
    g.fill(sheet, 'W'); g.fill(rect(g, 7, 25, 38, 25), 'a'); g.dither(rect(g, 30, 21, 38, 24), 'W', 'a')
    shade(g, sheet, 'a', 'u')
    for x in (16, 27):
        g.patch(x, 21, '''
            .KKK.
            KKKKK
            KKKKK
            .KuK.
        ''')
    # footboard: the near end, square to us, periwinkle with a lit rail; the quilt's hem hangs over it
    foot = rect(g, 5, 41, 42, 45)
    g.fill(foot, 'p'); g.fill(rect(g, 6, 42, 41, 42), 'W'); g.dither(rect(g, 6, 44, 41, 44), 'p', 'u')
    shade(g, foot)
    hem = rect(g, 7, 40, 38, 41)
    g.fill(hem, 'h'); g.dither(rect(g, 7, 41, 38, 41), 'h', 'k'); g.edge(hem, 'K', 'b')
    legs = rect(g, 6, 46, 9, 47) | rect(g, 38, 46, 41, 47)
    g.fill(legs, 'u'); g.edge(legs, 'K', 'br')
    return g


# ---------------------------------------------------------------------------------------------------------------
# B. nightwindow: the room's balcony window at night. Periwinkle frame, navy sky, crescent moon, a few lit windows
#    in a plum skyline, pink curtains tied back, Panda's plush on the sill with the moon behind it.
# ---------------------------------------------------------------------------------------------------------------

def nightwindow():
    g = Grid(48, 48)
    frame = rect(g, 5, 2, 42, 38)
    glass = rect(g, 8, 5, 39, 35)
    g.fill(frame, 'p'); shade(g, frame)
    g.fill(rect(g, 6, 3, 41, 3), 'W'); g.fill(rect(g, 6, 3, 6, 37), 'W')
    g.dither(rect(g, 40, 4, 41, 37), 'p', 'u')
    g.edge(glass, 'u', 'tl', inside=False); g.edge(glass, 'W', 'br', inside=False)
    # sky, stars, a big crescent moon in the right pane
    g.fill(glass, 'b')
    for x, y in ((11, 8), (18, 11), (13, 15), (21, 7), (37, 22)):
        g[x, y] = 'W'
    moon = ellipse(g, 25, 7, 35, 17) & ~ellipse(g, 22, 5, 32, 15)
    g.fill(moon, 'y'); g.dither(moon & rect(g, 25, 14, 35, 17), 'y', 'e', pattern='q1'); g.edge(moon, 'W', 'tr')
    # the city: plum silhouettes along the bottom, a few lit windows
    city = rect(g, 8, 28, 12, 35) | rect(g, 13, 24, 17, 35) | rect(g, 18, 30, 21, 35) | rect(g, 22, 27, 26, 35) \
        | rect(g, 27, 31, 30, 35) | rect(g, 31, 25, 35, 35) | rect(g, 36, 29, 39, 35)
    g.fill(city & glass, 'u')
    for x, y in ((9, 30), (14, 26), (16, 28), (23, 29), (25, 32), (32, 27), (34, 29), (32, 32), (37, 31), (19, 33)):
        g[x, y] = 'y'
    # mullion
    g.fill(rect(g, 23, 5, 24, 35), 'p'); g.fill(rect(g, 24, 5, 24, 35), 'u'); g.fill(rect(g, 23, 5, 23, 35), 'W')
    # curtains, tied back
    for sd in (0, 1):
        pts = [(1, 0), (11, 0), (9, 14), (6, 21), (9, 27), (11, 38), (1, 38)]
        f = (lambda x: x) if not sd else (lambda x: 47 - x)
        cur = poly(g, [(f(x), y) for x, y in pts])
        g.fill(cur, 'k')
        g.fill(line(g, f(5), 1, f(5), 37) & cur, 'h')
        g.dither(line(g, f(3), 1, f(3), 37) & cur, 'W', 'k', pattern='h')
        shade(g, cur)
        tie = rect(g, f(9) if sd else 1, 20, f(1) if sd else 9, 22)
        g.fill(tie, 'h'); g.edge(tie, 'K', 'b'); g.edge(tie, 'W', 't')
    # sill, three-quarter: lit top, periwinkle front, plum underside
    sill = rect(g, 2, 39, 45, 43)
    g.fill(sill, 'p'); g.fill(rect(g, 2, 39, 45, 40), 'W'); g.dither(rect(g, 2, 40, 45, 40), 'W', 'a')
    g.fill(rect(g, 2, 44, 45, 45), 'u'); shade(g, sill | rect(g, 2, 44, 45, 45))
    # Panda on the sill: body, feet forward, head; a 1 px moonlit rim where it stands against the night
    pg = Grid(48, 48)
    body = ellipse(pg, 17, 32, 30, 42)
    pg.fill(body, 'K'); belly = ellipse(pg, 20, 34, 27, 41); pg.fill(belly, 'W'); pg.dither(belly & rect(pg, 24, 34, 27, 41), 'W', 'p')
    for x0 in (15, 28):
        foot = ellipse(pg, x0, 38, x0 + 4, 42); pg.fill(foot, 'K'); pg.fill(rect(pg, x0 + 1, 39, x0 + 2, 39), 'u')
    pg.paste(panda_head_small(), 16, 21)
    pm = pg.a != '.'
    rim = grow(pm, 1) & ~pm & glass
    g.fill(rim, 'p')
    g.a[pm] = pg.a[pm]
    return g


# ---------------------------------------------------------------------------------------------------------------
# C. ajar: the bedroom door, opened inward a little: the leaf turns away from us, warm light through the gap and in a
#    wedge on the floor; a pink nameplate with Panda's face hangs on the door.
# ---------------------------------------------------------------------------------------------------------------

def ajar():
    g = Grid(48, 48)
    casing = rect(g, 7, 1, 41, 46)
    opening = rect(g, 10, 4, 38, 46)
    g.fill(casing, 'p'); shade(g, casing)
    g.fill(rect(g, 8, 2, 40, 2), 'W'); g.fill(rect(g, 8, 2, 8, 45), 'W')
    g.dither(rect(g, 39, 3, 40, 45), 'p', 'u')
    # the room beyond, warm: lamp-yellow, peach toward the floor, and its night window in the back wall
    g.fill(opening, 'e')
    g.dither(rect(g, 10, 4, 38, 8), 'e', 'k')
    g.dither(rect(g, 10, 34, 38, 39), 'e', 'y')
    g.fill(rect(g, 10, 40, 38, 46), 'y')
    g.fill(rect(g, 37, 4, 38, 46), 'e')                                                  # the casing's shadow inside
    win = rect(g, 27, 9, 35, 19)
    g.fill(win, 'b'); g.edge(win, 'p', 'all')
    g.fill(rect(g, 31, 10, 31, 18), 'p')
    g.fill(rect(g, 33, 11, 33, 12) | rect(g, 34, 12, 34, 13), 'y')                      # a sliver of moon
    g[29, 12] = 'W'
    # Panda, peeking around the door from inside
    g.paste(panda_head_small(), 21, 20)
    # the leaf, hinged on the left, swung into the room: its free edge is further away, so shorter
    leaf = poly(g, [(10, 4), (22, 8), (22, 43), (10, 46)])
    g.fill(leaf, 'p')
    g.dither(poly(g, [(17, 6), (22, 8), (22, 43), (17, 44)]), 'p', 'u')
    g.edge(leaf, 'u', 't'); g.edge(leaf, 'K', 'r')
    g.fill(line(g, 23, 8, 23, 43), 'a')                                                  # its thickness, lit
    for pnl in (poly(g, [(12, 9), (19, 11), (19, 23), (12, 22)]), poly(g, [(12, 27), (19, 27), (19, 39), (12, 41)])):
        g.edge(pnl, 'u', 'tl'); g.edge(pnl, 'W', 'br')
    g.fill(rect(g, 19, 29, 20, 30), 'y'); g[20, 30] = 'n'                                 # knob
    g.patch(21, 31, '''
        .KKK
        KKKK
        KKKu
        .KK.
    ''')                                                                                   # a paw round the door's edge
    # the light, out across the floor toward us
    wedge = poly(g, [(24, 46), (37, 46), (46, 47), (25, 47)])
    g.fill(wedge, 'y')
    g.dither(poly(g, [(36, 46), (38, 46), (46, 47), (41, 47)]), 'y', '.', pattern='checker')
    return g


# ---------------------------------------------------------------------------------------------------------------
# D. moonpanda: the plush's head, big, against a crescent moon behind its right ear.
# ---------------------------------------------------------------------------------------------------------------

def moonpanda():
    g = Grid(48, 48)
    # a big crescent moon behind, to the upper right
    moon = ellipse(g, 17, 0, 47, 30) & ~ellipse(g, 10, -6, 40, 24)
    g.fill(moon, 'y'); g.dither(moon & rect(g, 17, 20, 47, 30), 'y', 'e', pattern='q1')
    g.edge(moon, 'W', 'tr'); g.edge(moon, 'u', 'bl')
    for x, y in ((5, 4), (14, 2), (45, 36)):
        g.patch(x - 1, y - 1, '''
            .y.
            yWy
            .y.
        ''')
    # ears
    for x0 in (3, 29):
        ear = ellipse(g, x0, 10, x0 + 11, 21)
        g.fill(ear, 'K'); g.fill(rect(g, x0 + 3, 13, x0 + 4, 14), 'u')
    # head: white, the moonlit periwinkle half-light down the right and under the chin
    head = ellipse(g, 3, 13, 40, 47)
    g.fill(head, 'W')
    g.dither(head & ~ellipse(g, 1, 11, 37, 44), 'W', 'p')
    g.fill(head & ~ellipse(g, 0, 10, 38, 45), 'p')
    g.edge(head, 'u', 'tl'); g.edge(head, 'K', 'br')
    # eye patches, slanted down and out, with catchlights
    for flip in (0, 1):
        pts = [(14, 25), (18, 26), (19, 32), (16, 36), (11, 35), (10, 30)]
        if flip:
            pts = [(43 - x, y) for x, y in pts]
        g.fill(poly(g, pts), 'K')
        ex = 15 if not flip else 27
        g.fill(rect(g, ex, 29, ex + 1, 30), 'W')
    # nose and mouth, blush
    g.patch(19, 33, '''
        KKKKK
        .KKK.
        ..K..
        .K.K.
    ''')
    g.fill(rect(g, 8, 37, 10, 38), 'k'); g.fill(rect(g, 33, 37, 35, 38), 'k')
    return g


CANDIDATES = {'tuckedin': tuckedin, 'nightwindow': nightwindow, 'ajar': ajar, 'moonpanda': moonpanda}


def export(name, rc):
    used = {k: P.get(LEG)[k] for k in rc.colors()}
    ok, probs = P.is_pc98(used)
    if not ok:
        raise SystemExit(f'{name}: not PC-98: {probs}')
    OUT.mkdir(parents=True, exist_ok=True)
    rc.save(OUT / f'{name}_recolor.png', LEG)
    rc.dump(OUT / f'{name}_recolor.txt')
    rc.recolor(TO_VGA).save(OUT / f'{name}.png', 'vga', mode='P')
    return OUT / f'{name}_recolor.png'


def review(names):
    """Each candidate beside the five icons it will sit with: 1x, as shown (72 px), 6x."""
    site = [(n, SITE / f'img/icons/{n}_recolor.png') for n in NEIGHBOURS]
    paths = []
    for n in names:
        paths.append(icon_sheet(site + [(n, OUT / f'{n}_recolor.png')], OUT / 'review' / f'row_{n}.png',
                                title=f'room icon round 2: {n}'))
    paths.append(icon_sheet(site + [(n, OUT / f'{n}_recolor.png') for n in names] +
                            [('old bed2', SITE / 'img/icons/room_recolor.png')],
                            OUT / 'review' / 'sheet_all.png', title='room icon round 2: all candidates + the old one'))
    return paths


if __name__ == '__main__':
    names = sys.argv[1:] or list(CANDIDATES)
    for n in names:
        print('wrote', export(n, CANDIDATES[n]()))
    for p in review(list(CANDIDATES)):
        print('wrote', p)
